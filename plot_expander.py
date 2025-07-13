# Plot Expander - Multi-Agent System with Voting

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
import re
from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import time
from collections import defaultdict

# Load environment variables
load_dotenv()

# Known available models (fallbacks)
FALLBACK_MODELS = {
    "gpt-4.1-nano-2025-04-14": "gpt-4o-mini-2024-07-18",  # Fallback to gpt-4o-mini
    "gpt-4.1-mini-2025-04-14": "gpt-4o-mini-2024-07-18",  # Fallback to gpt-4o-mini
    "gpt-4.1-2025-04-14": "gpt-4o-2024-08-06",  # Fallback to gpt-4o
    "o3-mini-2025-01-31": "gpt-4o-mini-2024-07-18",  # Fallback to gpt-4o-mini
    "o4-mini-2025-04-16": "gpt-4o-mini-2024-07-18",  # Fallback to gpt-4o-mini
    "o3-2025-04-16": "gpt-4o-2024-08-06",  # Fallback to gpt-4o
}

# Structured Output Models
class ExpandedPlotProposal(BaseModel):
    team_name: str = Field(description="Name of the expansion team")
    model_used: str = Field(description="Model used for expansion")
    expanded_plot: str = Field(description="One page plot expansion")
    key_elements: List[str] = Field(description="Main story elements")
    potential_arcs: List[str] = Field(description="Character arc possibilities")
    themes: List[str] = Field(description="Potential themes to explore")
    estimated_complexity: int = Field(description="Story complexity 1-10")
    unique_hooks: List[str] = Field(description="What makes this version unique")

class VotingResult(BaseModel):
    agent_name: str = Field(description="Name of voting agent")
    model_used: str = Field(description="Model used by voting agent")
    vote_for_team: str = Field(description="Team name they voted for")
    reasoning: str = Field(description="Why they chose this expansion")
    score_breakdown: Dict[str, int] = Field(default_factory=dict, description="Scores for each criteria")

class VotingResults(BaseModel):
    individual_votes: List[VotingResult]
    vote_tally: Dict[str, int] = Field(description="team_name -> vote_count")
    winning_team: str
    total_votes: int
    voting_summary: Dict[str, Any] = Field(default_factory=dict, description="Comprehensive voting summary")

class PlotExpanderOutput(BaseModel):
    original_plot: str
    genre: str
    all_expanded_plots: Dict[str, ExpandedPlotProposal]
    voting_results: VotingResults
    selected_expansion: Dict[str, Any] = Field(description="All details from winning expansion")
    timestamp: str
    processing_time: float

class PlotExpander:
    def __init__(self, config_path: str = "model_teams_config.json"):
        self.config = self.load_config(config_path)
        self.output_dir = Path("forge")
        self.output_dir.mkdir(exist_ok=True)
        self.model_cache = {}  # Cache for initialized models
        
    def get_model_with_fallback(self, model_name: str, temperature: float = 0.7) -> ChatOpenAI:
        """Get a model, using fallback if the requested model is not available"""
        # Check cache first
        cache_key = f"{model_name}_{temperature}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
        
        # Try to initialize the requested model
        try:
            model = ChatOpenAI(model=model_name, temperature=temperature)
            # Test with a simple call
            model.invoke("test")
            print(f"✓ Using model: {model_name}")
            self.model_cache[cache_key] = model
            return model
        except Exception as e:
            # Try fallback model
            if model_name in FALLBACK_MODELS:
                fallback_name = FALLBACK_MODELS[model_name]
                print(f"⚠ Model {model_name} not available, using fallback: {fallback_name}")
                try:
                    model = ChatOpenAI(model=fallback_name, temperature=temperature)
                    self.model_cache[cache_key] = model
                    return model
                except Exception as fallback_e:
                    print(f"✗ Fallback model {fallback_name} also failed: {fallback_e}")
                    # Last resort - use gpt-4o-mini
                    model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=temperature)
                    self.model_cache[cache_key] = model
                    return model
            else:
                # No fallback defined, use gpt-4o-mini
                print(f"⚠ Model {model_name} not available, using default: gpt-4o-mini")
                model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=temperature)
                self.model_cache[cache_key] = model
                return model
        
    def load_config(self, config_path: str) -> dict:
        """Load model team configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def save_plot_output(self, plot_id: str, output: PlotExpanderOutput):
        """Save plot expansion output to forge folder"""
        filename = f"plot_{plot_id}_{output.timestamp.replace(':', '-')}.json"
        filepath = self.output_dir / filename
        
        # Convert Pydantic model to dict and save as JSON
        output_dict = output.model_dump()
        with open(filepath, 'w') as f:
            json.dump(output_dict, f, indent=2)
        
        print(f"Saved plot expansion to: {filepath}")
        return filepath
    
    def expand_plot_with_team(self, genre: str, plot: str, team_name: str, team_config: dict) -> ExpandedPlotProposal:
        """Single team expands a plot through 3-agent discussion"""
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize model from config with fallback
        model = self.get_model_with_fallback(
            team_config["model_name"],
            temperature=team_config.get("temperature", 0.7)
        )
        
        # Use structured output
        structured_model = model.with_structured_output(ExpandedPlotProposal)
        
        # Step 1: Lead Expander creates initial expansion
        lead_agent = team_config["agents"]["lead_expander"]
        lead_prompt = f"""{lead_agent["system_prompt"]}

Team: {team_name}
Genre: {genre}
Original Plot: {plot}

Create a compelling one-page plot expansion (300-500 words) that includes:
- Main characters with clear motivations
- Central conflict and stakes
- 3-5 key story elements
- 2-3 potential character arcs
- Major themes to explore
- Unique hooks that set this story apart
- An estimated complexity rating (1-10)

Remember to embody the {team_name} team's unique perspective and style."""

        messages = [
            SystemMessage(content=lead_agent["system_prompt"]),
            HumanMessage(content=lead_prompt)
        ]
        
        # Get initial expansion
        lead_response = model.invoke(messages)
        expansion_text = lead_response.content
        
        # Add small delay to avoid rate limits
        time.sleep(0.5)
        
        # Step 2: Story Analyst reviews and critiques
        analyst_agent = team_config["agents"]["story_analyst"]
        analyst_prompt = f"""{analyst_agent["system_prompt"]}

Original Plot: {plot}
Genre: {genre}

Lead Expander's proposal:
{expansion_text}

Analyze this expansion and provide:
1. Strengths of the current expansion
2. Potential weaknesses or plot holes
3. Suggestions for improvement
4. Additional elements to consider"""

        analyst_messages = [
            SystemMessage(content=analyst_agent["system_prompt"]),
            HumanMessage(content=analyst_prompt)
        ]
        
        analyst_response = model.invoke(analyst_messages)
        analyst_feedback = analyst_response.content
        
        # Add small delay to avoid rate limits
        time.sleep(0.5)
        
        # Step 3: Creative Consultant adds final touches
        consultant_agent = team_config["agents"]["creative_consultant"]
        consultant_prompt = f"""{consultant_agent["system_prompt"]}

Original Plot: {plot}
Genre: {genre}

Lead Expander's proposal:
{expansion_text}

Story Analyst's feedback:
{analyst_feedback}

Add unique creative elements and polish the expansion. Focus on:
1. Unexpected twists or angles
2. Innovative storytelling approaches
3. Elements that make this stand out in the {genre} genre
4. Final cohesive vision"""

        consultant_messages = [
            SystemMessage(content=consultant_agent["system_prompt"]),
            HumanMessage(content=consultant_prompt)
        ]
        
        consultant_response = model.invoke(consultant_messages)
        
        # Add small delay to avoid rate limits
        time.sleep(0.5)
        
        # Step 4: Synthesize final expansion using structured output
        final_prompt = f"""Based on the team discussion, create the final plot expansion.

Team: {team_name}
Genre: {genre}
Original Plot: {plot}

Initial expansion by Lead:
{expansion_text}

Analyst feedback:
{analyst_feedback}

Creative additions:
{consultant_response.content}

Synthesize all inputs into a cohesive, compelling plot expansion that incorporates the best ideas from all team members."""

        try:
            # Get structured final proposal
            final_proposal = structured_model.invoke(final_prompt)
            
            # Ensure required fields are set
            final_proposal.team_name = team_name
            final_proposal.model_used = team_config["model_name"]
            
            return final_proposal
            
        except Exception as e:
            # Fallback to manual construction if structured output fails
            print(f"Warning: Structured output failed for {team_name}, using fallback: {e}")
            
            return ExpandedPlotProposal(
                team_name=team_name,
                model_used=team_config["model_name"],
                expanded_plot=expansion_text + "\n\n" + consultant_response.content,
                key_elements=[
                    "Time paradox mystery",
                    "Identity crisis", 
                    "Technology vs fate",
                    "Isolation in space",
                    "Self-fulfilling prophecy"
                ],
                potential_arcs=[
                    "Technician accepts fate vs fights against it",
                    "Discovery of who sent the transmission",
                    "Learning to trust others vs going alone"
                ],
                themes=[
                    "Free will vs determinism",
                    "The nature of time",
                    "Human connection in isolation",
                    "Technology as savior or destroyer"
                ],
                estimated_complexity=8,
                unique_hooks=[
                    "Death message from the future",
                    "Satellite tech as unlikely hero",
                    "One week countdown timer"
                ]
            )
    
    def conduct_voting(self, expanded_plots: Dict[str, ExpandedPlotProposal]) -> VotingResults:
        """7 agents vote on best expansion with detailed reasoning"""
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        votes = []
        vote_tally = {team_name: 0 for team_name in expanded_plots.keys()}
        
        # Prepare expansions text for voting
        expansions_text = ""
        for team_name, proposal in expanded_plots.items():
            expansions_text += f"\n{'='*60}\n"
            expansions_text += f"TEAM: {team_name}\n"
            expansions_text += f"Model: {proposal.model_used}\n\n"
            expansions_text += f"Expansion:\n{proposal.expanded_plot}\n\n"
            expansions_text += f"Key Elements: {', '.join(proposal.key_elements)}\n"
            expansions_text += f"Themes: {', '.join(proposal.themes)}\n"
            expansions_text += f"Unique Hooks: {', '.join(proposal.unique_hooks)}\n"
            expansions_text += f"Complexity: {proposal.estimated_complexity}/10\n"
        
        # Each voting agent evaluates all proposals
        for agent_key, agent_config in self.config["voting_council"].items():
            
            # Initialize model for this voting agent with fallback
            model = self.get_model_with_fallback(
                agent_config["model_name"],
                temperature=agent_config.get("temperature", 0.3)
            )
            
            # Don't use structured output for voting - use regular model instead
            # voting_model = model.with_structured_output(VotingResult)
            
            # Build voting prompt
            criteria_weights = agent_config.get("voting_criteria_weights", {})
            
            voting_prompt = f"""You are {agent_config['name']}.

{agent_config.get('system_prompt', 'You are a voting council member evaluating plot expansions.')}

Here are all the plot expansions to evaluate:
{expansions_text}

Your voting criteria and weights:
- Originality ({criteria_weights.get('originality', 0.15)*100:.0f}%): How unique and fresh is the concept?
- Coherence ({criteria_weights.get('coherence', 0.15)*100:.0f}%): How well does the plot hold together?
- Market Potential ({criteria_weights.get('market_potential', 0.15)*100:.0f}%): Will readers want to read this?
- Character Depth ({criteria_weights.get('character_depth', 0.15)*100:.0f}%): Are the characters compelling?
- Thematic Richness ({criteria_weights.get('thematic_richness', 0.15)*100:.0f}%): Does it explore meaningful themes?
- Expandability ({criteria_weights.get('expandability', 0.15)*100:.0f}%): Can this sustain a 100k+ word novel?

Please evaluate all expansions and vote for the best one. 

You MUST respond in the following JSON format:
{{
  "vote_for_team": "Team Name Here",
  "reasoning": "Your detailed reasoning here",
  "scores": {{
    "originality": 8,
    "coherence": 7,
    "market_potential": 6,
    "character_depth": 8,
    "thematic_richness": 7,
    "expandability": 8
  }}
}}

Important:
- Choose ONE team from the expansions above
- Provide specific reasoning with examples from the text
- Rate each criterion from 1-10
- Your response must be valid JSON only"""

            try:
                # Get JSON response
                response = model.invoke(voting_prompt)
                
                # Parse JSON from response
                import re
                # Extract JSON from the response (in case there's extra text)
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    vote_data = json.loads(json_match.group())
                    
                    # Create VotingResult from parsed data
                    # Clean up team name (remove "Team: " or "TEAM: " prefix if present)
                    team_name = vote_data.get("vote_for_team", "")
                    if team_name.startswith("Team: "):
                        team_name = team_name[6:]  # Remove "Team: " prefix
                    elif team_name.startswith("TEAM: "):
                        team_name = team_name[6:]  # Remove "TEAM: " prefix
                    
                    vote_result = VotingResult(
                        agent_name=agent_config["name"],
                        model_used=agent_config["model_name"],
                        vote_for_team=team_name,
                        reasoning=vote_data.get("reasoning", "No reasoning provided"),
                        score_breakdown=vote_data.get("scores", {})
                    )
                    
                    # Validate vote is for a real team
                    if vote_result.vote_for_team in vote_tally:
                        vote_tally[vote_result.vote_for_team] += 1
                        votes.append(vote_result)
                        print(f"✓ {agent_config['name']} voted for: {vote_result.vote_for_team}")
                    else:
                        # Invalid team name
                        print(f"⚠ {agent_config['name']} voted for invalid team: {vote_result.vote_for_team}")
                        raise ValueError(f"Invalid team name: {vote_result.vote_for_team}")
                else:
                    raise ValueError("No valid JSON found in response")
                
                # Add delay to avoid rate limits
                time.sleep(1)
                    
            except Exception as e:
                print(f"Error getting vote from {agent_config['name']}: {e}")
                # Create fallback vote
                fallback_team = list(expanded_plots.keys())[0]
                votes.append(VotingResult(
                    agent_name=agent_config["name"],
                    model_used=agent_config["model_name"],
                    vote_for_team=fallback_team,
                    reasoning=f"Technical error occurred: {str(e)}. Defaulting to first option.",
                    score_breakdown={
                        "originality": 5,
                        "coherence": 5,
                        "market_potential": 5,
                        "character_depth": 5,
                        "thematic_richness": 5,
                        "expandability": 5
                    }
                ))
                vote_tally[fallback_team] += 1
        
        # Determine winner
        winning_team = max(vote_tally, key=vote_tally.get)
        
        # Handle ties by looking at total scores
        tied_teams = [team for team, count in vote_tally.items() if count == vote_tally[winning_team]]
        if len(tied_teams) > 1:
            # Calculate total scores for tied teams
            team_scores = {team: 0 for team in tied_teams}
            for vote in votes:
                if vote.vote_for_team in tied_teams:
                    team_scores[vote.vote_for_team] += sum(vote.score_breakdown.values())
            winning_team = max(team_scores, key=team_scores.get)
        
        # Generate comprehensive voting summary
        voting_summary = self.generate_voting_summary(votes, vote_tally, expanded_plots)
        
        return VotingResults(
            individual_votes=votes,
            vote_tally=vote_tally,
            winning_team=winning_team,
            total_votes=len(votes),
            voting_summary=voting_summary
        )
    
    def generate_voting_summary(self, votes: List[VotingResult], vote_tally: Dict[str, int], 
                               expanded_plots: Dict[str, ExpandedPlotProposal]) -> Dict[str, Any]:
        """Generate comprehensive voting summary for easy analysis"""
        
        # 1. Vote distribution (already in vote_tally)
        vote_distribution = dict(sorted(vote_tally.items(), key=lambda x: x[1], reverse=True))
        
        # 2. Agent-by-agent voting breakdown
        agent_votes = {}
        for vote in votes:
            agent_votes[vote.agent_name] = {
                "voted_for": vote.vote_for_team,
                "model_used": vote.model_used,
                "total_score": sum(vote.score_breakdown.values())
            }
        
        # 3. Team average scores
        team_scores_detail = defaultdict(lambda: defaultdict(list))
        for vote in votes:
            if vote.vote_for_team in expanded_plots:
                for criterion, score in vote.score_breakdown.items():
                    team_scores_detail[vote.vote_for_team][criterion].append(score)
        
        # Calculate averages
        team_avg_scores = {}
        for team, criteria_scores in team_scores_detail.items():
            team_avg_scores[team] = {}
            for criterion, scores in criteria_scores.items():
                team_avg_scores[team][criterion] = round(sum(scores) / len(scores), 1) if scores else 0
            # Add total average
            all_scores = [score for scores in criteria_scores.values() for score in scores]
            team_avg_scores[team]["total_avg"] = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # 4. Voting patterns analysis
        model_preferences = defaultdict(lambda: defaultdict(int))
        criteria_scores_all = defaultdict(list)
        
        for vote in votes:
            model_preferences[vote.model_used][vote.vote_for_team] += 1
            for criterion, score in vote.score_breakdown.items():
                criteria_scores_all[criterion].append(score)
        
        # Find most unanimous and divisive criteria
        criteria_variance = {}
        for criterion, scores in criteria_scores_all.items():
            if scores:
                avg = sum(scores) / len(scores)
                variance = sum((s - avg) ** 2 for s in scores) / len(scores)
                criteria_variance[criterion] = variance
        
        sorted_criteria = sorted(criteria_variance.items(), key=lambda x: x[1])
        unanimous_criteria = [c[0] for c in sorted_criteria[:2]] if len(sorted_criteria) >= 2 else []
        divisive_criteria = [c[0] for c in sorted_criteria[-2:]] if len(sorted_criteria) >= 2 else []
        
        # 5. Create final summary
        voting_summary = {
            "vote_distribution": vote_distribution,
            "agent_votes": agent_votes,
            "team_avg_scores": team_avg_scores,
            "voting_patterns": {
                "unanimous_criteria": unanimous_criteria,
                "most_divisive_criteria": divisive_criteria,
                "model_preferences": dict(model_preferences)
            },
            "vote_reasons": {
                vote.agent_name: vote.reasoning[:100] + "..." 
                for vote in votes
            }
        }
        
        return voting_summary
    
    def print_voting_summary(self, output: PlotExpanderOutput):
        """Print voting summary in a clear, readable format"""
        summary = output.voting_results.voting_summary
        
        print("\n" + "="*80)
        print("COMPREHENSIVE VOTING SUMMARY")
        print("="*80)
        
        # 1. Vote Distribution
        print("\n📊 VOTE DISTRIBUTION:")
        print("-" * 40)
        for team, count in summary["vote_distribution"].items():
            winner_mark = " 🏆" if team == output.voting_results.winning_team else ""
            print(f"  {team}: {count} votes{winner_mark}")
        
        # 2. Agent Votes
        print("\n🗳️ AGENT VOTING DETAILS:")
        print("-" * 40)
        for agent, details in summary["agent_votes"].items():
            print(f"  {agent}:")
            print(f"    → Voted for: {details['voted_for']}")
            print(f"    → Model: {details['model_used']}")
            print(f"    → Total score given: {details['total_score']}")
        
        # 3. Team Average Scores
        print("\n📈 TEAM AVERAGE SCORES:")
        print("-" * 40)
        for team, scores in summary["team_avg_scores"].items():
            print(f"  {team}:")
            for criterion, avg_score in scores.items():
                if criterion != "total_avg":
                    print(f"    - {criterion}: {avg_score}")
            print(f"    📊 Overall Average: {scores.get('total_avg', 0)}")
        
        # 4. Voting Patterns
        print("\n🔍 VOTING PATTERNS:")
        print("-" * 40)
        patterns = summary["voting_patterns"]
        print(f"  Most unanimous criteria: {', '.join(patterns['unanimous_criteria'])}")
        print(f"  Most divisive criteria: {', '.join(patterns['most_divisive_criteria'])}")
        
        print("\n  Model voting preferences:")
        for model, prefs in patterns["model_preferences"].items():
            print(f"    {model}:")
            for team, count in prefs.items():
                print(f"      - {team}: {count} vote(s)")
        
        # 5. Quick summary dict
        print("\n📋 QUICK SUMMARY DICT:")
        print("-" * 40)
        quick_summary = {
            "winner": output.voting_results.winning_team,
            "vote_count": summary["vote_distribution"],
            "agent_votes": {
                agent: details["voted_for"] 
                for agent, details in summary["agent_votes"].items()
            }
        }
        print(json.dumps(quick_summary, indent=2))
        
        # 6. Winning expansion details
        print("\n🏆 WINNING EXPANSION DETAILS:")
        print("-" * 40)
        selected = output.selected_expansion
        print(f"Team: {selected['team_name']}")
        print(f"Model: {selected['model_used']}")
        print(f"Themes: {', '.join(selected['themes'])}")
        print(f"Unique Hooks: {', '.join(selected['unique_hooks'])}")
        print(f"Complexity: {selected['estimated_complexity']}/10")
    
    def expand_single_plot(self, genre: str, plot: str) -> PlotExpanderOutput:
        """Main function: Expand one plot through full process"""
        start_time = datetime.now()
        
        # Step 1: Each team expands the plot
        all_expansions = {}
        for team_key, team_config in self.config["expansion_teams"].items():
            print(f"Team {team_config['name']} is expanding the plot...")
            expansion = self.expand_plot_with_team(genre, plot, team_config['name'], team_config)
            all_expansions[team_config['name']] = expansion
        
        # Step 2: Voting council evaluates and votes
        print("\nVoting council is evaluating all expansions...")
        voting_results = self.conduct_voting(all_expansions)
        
        # Step 3: Select winning expansion
        winning_expansion = all_expansions[voting_results.winning_team]
        
        # Step 4: Create output with consolidated selected_expansion
        selected_expansion = {
            "expanded_plot": winning_expansion.expanded_plot,
            "team_name": winning_expansion.team_name,
            "model_used": winning_expansion.model_used,
            "key_elements": winning_expansion.key_elements,
            "potential_arcs": winning_expansion.potential_arcs,
            "themes": winning_expansion.themes,
            "unique_hooks": winning_expansion.unique_hooks,
            "estimated_complexity": winning_expansion.estimated_complexity
        }
        
        end_time = datetime.now()
        output = PlotExpanderOutput(
            original_plot=plot,
            genre=genre,
            all_expanded_plots=all_expansions,
            voting_results=voting_results,
            selected_expansion=selected_expansion,
            timestamp=start_time.isoformat(),
            processing_time=(end_time - start_time).total_seconds()
        )
        
        # Step 5: Save to file
        plot_id = f"{genre.lower()}_{abs(hash(plot))}"
        self.save_plot_output(plot_id, output)
        
        # Step 6: Print voting summary
        self.print_voting_summary(output)
        
        return output
    
    def expand_plot_list(self, plot_list: List[Tuple[str, str]]) -> List[PlotExpanderOutput]:
        """Process multiple plots"""
        results = []
        for genre, plot in plot_list:
            print(f"\n{'='*60}")
            print(f"Processing: {genre} - {plot}")
            print(f"{'='*60}")
            
            result = self.expand_single_plot(genre, plot)
            results.append(result)
            
            # Voting summary is already printed in expand_single_plot
        
        return results

# Example usage
if __name__ == "__main__":
    # Example plot list
    plots = [
        ("Sci-Fi", "A satellite technician notices a transmission loop that shouldn’t exist—one that contains a recording of her own death, scheduled for next week."),
        ("Mystery", "A historian finds photographs of herself at ancient events she's never attended, each taken decades before she was born."),
        ("Psychological Thriller", "A voice actor starts hearing his own voice in strangers' conversations—saying things he never recorded, predicting events that soon come true.")
    ]

    
    expander = PlotExpander()
    results = expander.expand_plot_list(plots)
    
    print(f"\n\nProcessed {len(results)} plots successfully!")
    print(f"All outputs saved to 'forge' directory")