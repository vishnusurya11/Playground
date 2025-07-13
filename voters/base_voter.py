"""
Base voter class that all voters inherit from
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from schemas import VotingResult, ExpandedPlotProposal
from config import config
import json
import re
import random


class BaseVoter:
    """Base class for all voting agents"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Voter")
        self.model_name = model_config.get("model_name", "gpt-4o-mini-2024-07-18")
        self.temperature = model_config.get("temperature", 0.3)
        self.system_prompt = model_config.get("system_prompt", "You are a voting council member evaluating plot expansions.")
        self.criteria_weights = model_config.get("voting_criteria_weights", {
            "originality": 0.15,
            "coherence": 0.15,
            "market_potential": 0.15,
            "character_depth": 0.15,
            "thematic_richness": 0.15,
            "expandability": 0.25
        })
        self.voting_bias = model_config.get("voting_bias", "balanced evaluation")
        self.model = self._initialize_model()
    
    def _initialize_model(self) -> ChatOpenAI:
        """Initialize model with fallback support"""
        try:
            model = ChatOpenAI(model=self.model_name, temperature=self.temperature)
            model.invoke("test")
            return model
        except:
            fallback = config.get_model_fallback(self.model_name)
            if fallback:
                print(f"Using fallback model {fallback} for {self.name}")
                self.model_name = fallback
                return ChatOpenAI(model=fallback, temperature=self.temperature)
            # Last resort
            self.model_name = "gpt-4o-mini-2024-07-18"
            return ChatOpenAI(model=self.model_name, temperature=self.temperature)
    
    def vote(self, expansions: Dict[str, ExpandedPlotProposal]) -> VotingResult:
        """Cast vote based on agent's unique perspective"""
        
        # Prepare expansions text
        expansions_text = self._prepare_expansions_text(expansions)
        
        # Build voting prompt
        prompt = f"""You are {self.name}.

{self.system_prompt}

IMPORTANT VOTING GUIDANCE:
- As {self.name}, you have a unique perspective: {self.voting_bias}
- Don't simply choose what seems "best overall" - vote based on YOUR specific expertise and biases
- It's GOOD to disagree with what others might choose. The council needs diverse opinions.
- Trust your instincts and professional judgment, even if it goes against conventional wisdom.

Here are all the plot expansions to evaluate (presented in random order):
{expansions_text}

Your voting criteria and personal weights (these reflect YOUR priorities, not universal standards):
- Originality ({self.criteria_weights.get('originality', 0.15)*100:.0f}%): How unique and fresh is the concept?
- Coherence ({self.criteria_weights.get('coherence', 0.15)*100:.0f}%): How well does the plot hold together?
- Market Potential ({self.criteria_weights.get('market_potential', 0.15)*100:.0f}%): Will readers want to read this?
- Character Depth ({self.criteria_weights.get('character_depth', 0.15)*100:.0f}%): Are the characters compelling?
- Thematic Richness ({self.criteria_weights.get('thematic_richness', 0.15)*100:.0f}%): Does it explore meaningful themes?
- Expandability ({self.criteria_weights.get('expandability', 0.15)*100:.0f}%): Can this sustain a 100k+ word novel?

Remember: Your weights show what YOU value most. A {self.criteria_weights.get('character_depth', 0.15)*100:.0f}% weight on character depth means that's how much it matters to YOU specifically.

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
- Your reasoning should reflect YOUR unique perspective as {self.name}
- Don't try to be "fair" or "balanced" - be true to your role
- Rate each criterion from 1-10 based on YOUR standards
- Your response must be valid JSON only"""
        
        try:
            # Get vote
            response = self.model.invoke(prompt)
            vote_data = self._parse_vote_response(response.content)
            
            return VotingResult(
                agent_name=self.name,
                model_used=self.model_name,
                vote_for_team=self._clean_team_name(vote_data["vote_for_team"]),
                reasoning=vote_data["reasoning"],
                score_breakdown=vote_data.get("scores", {})
            )
            
        except Exception as e:
            print(f"Error in {self.name} voting: {e}")
            return self._create_fallback_vote(expansions)
    
    def _prepare_expansions_text(self, expansions: Dict[str, ExpandedPlotProposal]) -> str:
        """Format expansions for voting"""
        team_order = list(expansions.keys())
        random.shuffle(team_order)  # Randomize to avoid bias
        
        text = ""
        for team_name in team_order:
            expansion = expansions[team_name]
            text += f"\n{'='*60}\n"
            text += f"TEAM: {team_name}\n"
            text += f"Title: {expansion.title}\n"
            text += f"Logline: {expansion.logline}\n\n"
            
            # Characters
            text += f"Main Characters:\n"
            for char in expansion.main_characters[:3]:  # Limit to 3
                text += f"- {char.name} ({char.role}): {char.description}\n"
            
            text += f"\nPlot Summary:\n{expansion.plot_summary}\n\n"
            text += f"Central Conflict: {expansion.central_conflict}\n\n"
            
            # Story beats
            text += f"Story Beats:\n"
            text += f"- Opening: {expansion.story_beats.opening}\n"
            text += f"- Catalyst: {expansion.story_beats.catalyst}\n"
            text += f"- Midpoint: {expansion.story_beats.midpoint}\n"
            text += f"- Crisis: {expansion.story_beats.crisis}\n"
            text += f"- Resolution: {expansion.story_beats.resolution}\n\n"
            
            text += f"Ending: {expansion.ending}\n\n"
            text += f"Key Elements: {', '.join(expansion.key_elements)}\n"
            text += f"Themes: {', '.join(expansion.themes)}\n"
            text += f"Unique Hooks: {', '.join(expansion.unique_hooks)}\n"
            text += f"Complexity: {expansion.estimated_complexity}/10\n"
        
        return text
    
    def _parse_vote_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from model"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("No valid JSON found in response")
    
    def _clean_team_name(self, team_name: str) -> str:
        """Clean team name from response"""
        if team_name.startswith("Team: "):
            return team_name[6:]
        if team_name.startswith("TEAM: "):
            return team_name[6:]
        return team_name
    
    async def vote_async(self, expansions: Dict[str, ExpandedPlotProposal]) -> VotingResult:
        """Async version - cast vote using ainvoke for parallel processing"""
        
        # Prepare expansions text
        expansions_text = self._prepare_expansions_text(expansions)
        
        # Build voting prompt (same as sync version)
        prompt = f"""You are {self.name}.

{self.system_prompt}

IMPORTANT VOTING GUIDANCE:
- As {self.name}, you have a unique perspective: {self.voting_bias}
- Don't simply choose what seems "best overall" - vote based on YOUR specific expertise and biases
- It's GOOD to disagree with what others might choose. The council needs diverse opinions.
- Trust your instincts and professional judgment, even if it goes against conventional wisdom.

Here are all the plot expansions to evaluate (presented in random order):
{expansions_text}

Your voting criteria and personal weights (these reflect YOUR priorities, not universal standards):
- Originality ({self.criteria_weights.get('originality', 0.15)*100:.0f}%): How unique and fresh is the concept?
- Coherence ({self.criteria_weights.get('coherence', 0.15)*100:.0f}%): How well does the plot hold together?
- Market Potential ({self.criteria_weights.get('market_potential', 0.15)*100:.0f}%): Will readers want to read this?
- Character Depth ({self.criteria_weights.get('character_depth', 0.15)*100:.0f}%): Are the characters compelling?
- Thematic Richness ({self.criteria_weights.get('thematic_richness', 0.15)*100:.0f}%): Does it explore meaningful themes?
- Expandability ({self.criteria_weights.get('expandability', 0.15)*100:.0f}%): Can this sustain a 100k+ word novel?

Remember: Your weights show what YOU value most. A {self.criteria_weights.get('character_depth', 0.15)*100:.0f}% weight on character depth means that's how much it matters to YOU specifically.

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
- Your reasoning should reflect YOUR unique perspective as {self.name}
- Don't try to be "fair" or "balanced" - be true to your role
- Rate each criterion from 1-10 based on YOUR standards
- Your response must be valid JSON only"""
        
        try:
            # Get vote using async
            response = await self.model.ainvoke(prompt)
            vote_data = self._parse_vote_response(response.content)
            
            return VotingResult(
                agent_name=self.name,
                model_used=self.model_name,
                vote_for_team=self._clean_team_name(vote_data["vote_for_team"]),
                reasoning=vote_data["reasoning"],
                score_breakdown=vote_data.get("scores", {})
            )
            
        except Exception as e:
            print(f"Async error in {self.name} voting: {e}")
            raise
    
    def _create_fallback_vote(self, expansions: Dict[str, ExpandedPlotProposal]) -> VotingResult:
        """Create fallback vote if voting fails"""
        team_names = list(expansions.keys())
        return VotingResult(
            agent_name=self.name,
            model_used=self.model_name,
            vote_for_team=team_names[0] if team_names else "Unknown",
            reasoning=f"Technical error occurred during {self.name} evaluation",
            score_breakdown={
                "originality": 5,
                "coherence": 5,
                "market_potential": 5,
                "character_depth": 5,
                "thematic_richness": 5,
                "expandability": 5
            }
        )