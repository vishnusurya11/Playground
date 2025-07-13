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
import random

# Load environment variables
load_dotenv()

# Known available models (fallbacks)
FALLBACK_MODELS = {
    "gpt-4.1-nano-2025-04-14": "gpt-4o-mini-2024-07-18",  # Not available yet
    "gpt-4.1-mini-2025-04-14": "gpt-4o-mini-2024-07-18",  # Not available yet
    "gpt-4.1-2025-04-14": "gpt-4o-2024-08-06",  # Not available yet
    "o3-mini-2025-01-31": "o1-mini-2024-09-12",  # Use o1-mini instead
    "o4-mini-2025-04-16": "o1-mini-2024-09-12",  # Use o1-mini instead
    "o3-2025-04-16": "gpt-4o-2024-08-06",  # Not available yet
}

# Structured Output Models
class CharacterInfo(BaseModel):
    name: str = Field(description="Character name")
    role: str = Field(description="Character's role in the story")
    description: str = Field(description="Personality and motivation")

class StoryBeats(BaseModel):
    opening: str = Field(description="How the story begins - the hook")
    catalyst: str = Field(description="The event that launches the main story")
    midpoint: str = Field(description="Major revelation or turn that changes everything")
    crisis: str = Field(description="The darkest moment before the climax")
    resolution: str = Field(description="How the conflict resolves and characters change")

class ExpandedPlotProposal(BaseModel):
    team_name: str = Field(description="Name of the expansion team")
    model_used: str = Field(description="Model used for expansion")
    title: str = Field(description="Story title")
    logline: str = Field(description="One-sentence hook (max 30 words)")
    main_characters: List[CharacterInfo] = Field(description="Main character details")
    plot_summary: str = Field(description="The main plot narrative (300-400 words)")
    central_conflict: str = Field(description="Core conflict and stakes")
    story_beats: StoryBeats = Field(description="Key story beats")
    ending: str = Field(description="How the story concludes")
    key_elements: List[str] = Field(description="Main story elements")
    potential_arcs: List[str] = Field(description="Character arc possibilities")
    themes: List[str] = Field(description="Potential themes to explore")
    estimated_complexity: int = Field(description="Story complexity 1-10", ge=1, le=10)
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
    
    def _get_team_creative_direction(self, team_name: str) -> str:
        """Get team-specific creative direction based on team name"""
        team_directions = {
            "Visionary Scribes": """TEAM IDENTITY: You are the Visionary Scribes - masters of expansive, imaginative storytelling.
Your strength lies in creating rich, detailed worlds with complex character relationships and ambitious scope.
You excel at finding the epic potential in any story seed, transforming simple concepts into sweeping narratives.
AVOID: Being too generic or safe. Push boundaries while maintaining coherence.""",
            
            "Narrative Architects": """TEAM IDENTITY: You are the Narrative Architects - structural innovators and masters of story design.
Your strength lies in constructing intricate narrative frameworks with innovative structures and techniques.
You excel at non-linear storytelling, multiple perspectives, nested narratives, and experimental formats.
Focus on HOW the story is told as much as WHAT is told. Create architecturally beautiful stories.
AVOID: Being too abstract or experimental at the expense of emotional connection. Ground your innovations in human drama.""",
            
            "Plot Weavers": """TEAM IDENTITY: You are the Plot Weavers - masters of intricate plotting and satisfying twists.
Your strength lies in creating tightly-woven narratives where every thread matters and connects brilliantly.
You excel at mysteries within mysteries, clever misdirection, and plots that reward careful attention.
Focus on creating "aha!" moments and satisfying reveals that recontextualize everything that came before.
AVOID: Overcomplicating for complexity's sake. Every twist should feel inevitable in hindsight.""",
            
            "Story Alchemists": """TEAM IDENTITY: You are the Story Alchemists - transformative storytellers who blend genres and tones.
Your strength lies in unexpected combinations and genre-bending approaches that create something entirely new.
You excel at finding surprising angles and mixing elements that shouldn't work but somehow do brilliantly.
AVOID: Being predictable or following standard genre conventions too closely.""",
            
            "Dream Crafters": """TEAM IDENTITY: You are the Dream Crafters - weavers of surreal, emotionally resonant narratives.
Your strength lies in creating dreamlike, atmospheric stories that blur reality and imagination.
You excel at psychological depth, symbolic imagery, and stories that work on multiple levels of meaning.
AVOID: Being incomprehensible or losing the core story in abstract concepts."""
        }
        
        return team_directions.get(team_name, "Create your unique team perspective on this story.")
    
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
        
        # Step 1: Direct structured expansion with team-specific guidance
        
        # Get team-specific creative direction
        team_guidance = self._get_team_creative_direction(team_name)
        
        final_prompt = f"""You are part of {team_name}, a creative team expanding plot ideas.

Team: {team_name}
Genre: {genre}
Original Plot: {plot}

{team_guidance}

As {team_name}, create a compelling plot expansion with your team's unique perspective.

Provide a complete story expansion with:
- A creative title that reflects your team's approach
- A compelling one-sentence logline (max 30 words)
- 3-4 main characters with names, roles, and motivations
- A plot summary (300-400 words) that expands the original concept
- The central conflict and what's at stake
- Five key story beats (opening, catalyst, midpoint, crisis, resolution)
- How the story ends
- 3-5 key story elements that drive the plot
- 2-3 potential character arcs
- Major themes to explore
- What makes this version unique (3-5 hooks)
- Complexity rating from 1-10

Remember to embody the {team_name} team's unique style and perspective."""

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
            
            # Create fallback data
            return ExpandedPlotProposal(
                team_name=team_name,
                model_used=team_config["model_name"],
                title="Untitled Story",
                logline="A compelling story about the given plot.",
                main_characters=[
                    CharacterInfo(
                        name="Protagonist",
                        role="Main Character",
                        description="Driven by the central conflict"
                    )
                ],
                plot_summary="Plot expansion failed - using fallback. The story follows the original plot concept.",
                central_conflict="The main conflict revolves around the core premise.",
                story_beats=StoryBeats(
                    opening="The story begins with the discovery",
                    catalyst="The event that changes everything",
                    midpoint="A major revelation",
                    crisis="The darkest moment",
                    resolution="How it all resolves"
                ),
                ending="The story concludes with resolution.",
                key_elements=[
                    "Core mystery",
                    "Character growth", 
                    "Technology element"
                ],
                potential_arcs=[
                    "Protagonist's journey",
                    "Supporting character development"
                ],
                themes=[
                    "Central theme",
                    "Secondary theme"
                ],
                estimated_complexity=5,
                unique_hooks=[
                    "Unique premise",
                    "Compelling mystery"
                ]
            )
    
    def conduct_voting(self, expanded_plots: Dict[str, ExpandedPlotProposal]) -> VotingResults:
        """7 agents vote on best expansion with detailed reasoning"""
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        votes = []
        vote_tally = {team_name: 0 for team_name in expanded_plots.keys()}
        
        # Prepare expansions text for voting with randomized order
        team_order = list(expanded_plots.keys())
        random.shuffle(team_order)  # Randomize to avoid order bias
        
        expansions_text = ""
        for team_name in team_order:
            proposal = expanded_plots[team_name]
            expansions_text += f"\n{'='*60}\n"
            expansions_text += f"TEAM: {team_name}\n"
            expansions_text += f"Title: {proposal.title}\n"
            expansions_text += f"Logline: {proposal.logline}\n\n"
            
            # Characters
            expansions_text += f"Main Characters:\n"
            for char in proposal.main_characters:
                expansions_text += f"- {char.name} ({char.role}): {char.description}\n"
            
            expansions_text += f"\nPlot Summary:\n{proposal.plot_summary}\n\n"
            expansions_text += f"Central Conflict: {proposal.central_conflict}\n\n"
            
            # Story beats
            expansions_text += f"Story Beats:\n"
            expansions_text += f"- Opening: {proposal.story_beats.opening}\n"
            expansions_text += f"- Catalyst: {proposal.story_beats.catalyst}\n"
            expansions_text += f"- Midpoint: {proposal.story_beats.midpoint}\n"
            expansions_text += f"- Crisis: {proposal.story_beats.crisis}\n"
            expansions_text += f"- Resolution: {proposal.story_beats.resolution}\n\n"
            
            expansions_text += f"Ending: {proposal.ending}\n\n"
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
            voting_bias = agent_config.get("voting_bias", "balanced evaluation")
            
            voting_prompt = f"""You are {agent_config['name']}.

{agent_config.get('system_prompt', 'You are a voting council member evaluating plot expansions.')}

IMPORTANT VOTING GUIDANCE:
- As {agent_config['name']}, you have a unique perspective: {voting_bias}
- Don't simply choose what seems "best overall" - vote based on YOUR specific expertise and biases
- It's GOOD to disagree with what others might choose. The council needs diverse opinions.
- Trust your instincts and professional judgment, even if it goes against conventional wisdom.

Here are all the plot expansions to evaluate (presented in random order):
{expansions_text}

Your voting criteria and personal weights (these reflect YOUR priorities, not universal standards):
- Originality ({criteria_weights.get('originality', 0.15)*100:.0f}%): How unique and fresh is the concept?
- Coherence ({criteria_weights.get('coherence', 0.15)*100:.0f}%): How well does the plot hold together?
- Market Potential ({criteria_weights.get('market_potential', 0.15)*100:.0f}%): Will readers want to read this?
- Character Depth ({criteria_weights.get('character_depth', 0.15)*100:.0f}%): Are the characters compelling?
- Thematic Richness ({criteria_weights.get('thematic_richness', 0.15)*100:.0f}%): Does it explore meaningful themes?
- Expandability ({criteria_weights.get('expandability', 0.15)*100:.0f}%): Can this sustain a 100k+ word novel?

Remember: Your weights show what YOU value most. A {criteria_weights.get('character_depth', 0.15)*100:.0f}% weight on character depth means that's how much it matters to YOU specifically.

Please evaluate all expansions and vote for the best one according to YOUR perspective.

You MUST respond in the following JSON format:
{{
  "vote_for_team": "Team Name Here",
  "reasoning": "Your detailed reasoning here, explaining why THIS choice aligns with YOUR specific perspective and biases",
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
- Your reasoning should reflect YOUR unique perspective as {agent_config['name']}
- Don't try to be "fair" or "balanced" - be true to your role
- Rate each criterion from 1-10 based on YOUR standards
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
        print(f"Title: {selected['title']}")
        print(f"Logline: {selected['logline']}")
        print(f"Main Characters: {len(selected['main_characters'])}")
        for char in selected['main_characters'][:2]:  # Show first 2 characters
            print(f"  - {char['name']} ({char['role']})")
        print(f"Themes: {', '.join(selected['themes'])}")
        print(f"Unique Hooks: {', '.join(selected['unique_hooks'][:2])}")  # Show first 2 hooks
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
            "team_name": winning_expansion.team_name,
            "model_used": winning_expansion.model_used,
            "title": winning_expansion.title,
            "logline": winning_expansion.logline,
            "main_characters": [
                {
                    "name": char.name,
                    "role": char.role,
                    "description": char.description
                } for char in winning_expansion.main_characters
            ],
            "plot_summary": winning_expansion.plot_summary,
            "central_conflict": winning_expansion.central_conflict,
            "story_beats": {
                "opening": winning_expansion.story_beats.opening,
                "catalyst": winning_expansion.story_beats.catalyst,
                "midpoint": winning_expansion.story_beats.midpoint,
                "crisis": winning_expansion.story_beats.crisis,
                "resolution": winning_expansion.story_beats.resolution
            },
            "ending": winning_expansion.ending,
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
    # plots = [
    #     ("Sci-Fi", "A satellite technician notices a transmission loop that shouldn’t exist—one that contains a recording of her own death, scheduled for next week."),
    #     ("Mystery", "A historian finds photographs of herself at ancient events she's never attended, each taken decades before she was born."),
    #     ("Psychological Thriller", "A voice actor starts hearing his own voice in strangers' conversations—saying things he never recorded, predicting events that soon come true.")
    # ]
    # plots = [
    #     ("Horror", "A man moves into a new apartment and realizes the mirrors show a version of his life where he made a single, catastrophic mistake—and that version wants out."),
    #     ("Sci-Fi", "A cryogenics engineer finds a frozen capsule labeled with his own name and today's date—inside is someone who looks exactly like him, claiming to be from the future."),
    #     ("Supernatural Mystery", "A journalist investigating a ghost town realizes that the town repopulates every night with people who vanish by dawn—and one of them knows his name.")
    # ]
    plots = [
        ("Sci-Fi", "A quantum physicist finds a message embedded in cosmic background radiation—signed with her name and dated five minutes into the future."),
        ("Mystery", "An antique collector finds a diary that describes a murder from 1912—written in his own handwriting."),
        ("Horror", "A babysitter realizes the nursery rhymes the child sings are recounting her darkest memories, word for word."),
        ("Fantasy", "A librarian discovers a hidden shelf that lends books no one else can see—each one recounting a life she never lived."),
        ("Historical Fiction", "A Civil War soldier’s letters start predicting battles days before they occur—signed by a general who never existed."),
        ("Crime", "A forensic accountant discovers a series of shell companies whose board members have all been missing persons for decades."),
        ("Psychological Thriller", "A woman wakes up each morning in a new version of her apartment—same layout, but different memories and relationships."),
        ("Noir", "A private investigator is hired to follow someone—only to realize he's tailing himself in a version of the city that shouldn't exist."),
        ("Adventure", "A spelunker finds ancient carvings of modern machines deep in a cave system untouched for millennia."),
        ("Post-Apocalyptic", "A survivor in a flooded Earth finds a functioning lighthouse—run by an AI still waiting for a captain that never returned."),
        ("Romantic Suspense", "A man starts receiving love letters from someone who claims to have known him in a past life—letters written in his own style."),
        ("Urban Fantasy", "A delivery driver realizes his route maps out forgotten ley lines—and each package changes the energy of the city."),
        ("Political Thriller", "An intern discovers that classified files from different eras all refer to the same mysterious advisor—who hasn't aged in seventy years."),
        ("Supernatural", "A radio repairman hears broadcasts from people who died years ago—reporting news that hasn’t happened yet."),
        ("Cyberpunk", "A street-level hacker stumbles onto a neural ad-stream that starts inserting memories of a life he never lived—one he wants back.")
    ]


    
    expander = PlotExpander()
    results = expander.expand_plot_list(plots)
    
    print(f"\n\nProcessed {len(results)} plots successfully!")
    print(f"All outputs saved to 'forge' directory")