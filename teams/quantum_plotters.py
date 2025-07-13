"""
Quantum Plotters - Masters of intricate plotting and satisfying twists
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from schemas import ExpandedPlotProposal, CharacterInfo, StoryBeats
from config import config


class QuantumPlotters:
    """Masters of intricate plotting and satisfying twists"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Quantum Plotters")  # Support custom names
        self.model_name = model_config.get("model_name", "gpt-4o-mini-2024-07-18")
        self.temperature = model_config.get("temperature", 0.7)
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
    
    def expand_plot(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Expand plot with Quantum Plotters approach"""
        
        # Team-specific creative direction
        creative_direction = """TEAM IDENTITY: You are the Quantum Plotters - masters of intricate plotting and satisfying twists.
Your strength lies in creating tightly-woven narratives where every thread matters and connects brilliantly.
You excel at mysteries within mysteries, clever misdirection, and plots that reward careful attention.
Focus on creating "aha!" moments and satisfying reveals that recontextualize everything that came before.
AVOID: Overcomplicating for complexity's sake. Every twist should feel inevitable in hindsight."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As the Quantum Plotters, create a compelling plot expansion with your team's intricate plotting expertise.

Provide a complete story expansion with:
- A creative title that hints at the plot's complexity
- A compelling one-sentence logline (max 30 words)
- 3-4 main characters with names, roles, and hidden motivations
- A plot summary (300-400 words) with layered mysteries and connections
- The central conflict and hidden stakes
- Five key story beats (opening, catalyst, midpoint, crisis, resolution)
- How the story ends with satisfying reveals
- 3-5 key plot elements that interconnect
- 2-3 potential character arcs with hidden depths
- Major themes woven throughout
- What makes this plot intricately crafted (3-5 hooks)
- Complexity rating from 1-10

Remember to embody the Quantum Plotters team's mastery of intricate, satisfying plotting."""
        
        # Use structured output
        structured_model = self.model.with_structured_output(ExpandedPlotProposal)
        
        try:
            # Get expansion
            expansion = structured_model.invoke(prompt)
            
            # Ensure team name and model are set
            expansion.team_name = self.name
            expansion.model_used = self.model_name
            
            # Add any team-specific post-processing
            return self._post_process_expansion(expansion)
            
        except Exception as e:
            print(f"Error in {self.name} expansion: {e}")
            return self._create_fallback_expansion(genre, plot)
    
    def _post_process_expansion(self, expansion: ExpandedPlotProposal) -> ExpandedPlotProposal:
        """Team-specific post-processing"""
        # Quantum Plotters ensure high complexity
        if expansion.estimated_complexity < 8:
            expansion.estimated_complexity = 8
        # Add twist element if not present
        twist_keywords = ["twist", "reveal", "hidden", "secret"]
        if not any(keyword in expansion.plot_summary.lower() for keyword in twist_keywords):
            expansion.unique_hooks.append("Carefully planted revelations")
        return expansion
    
    def _create_fallback_expansion(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Create fallback expansion if main process fails"""
        return ExpandedPlotProposal(
            team_name=self.name,
            model_used=self.model_name,
            title="The Woven Mystery",
            logline="A tale where every thread connects to reveal a stunning truth.",
            main_characters=[
                CharacterInfo(
                    name="The Investigator",
                    role="Truth Seeker",
                    description="A character uncovering layers of interconnected mysteries"
                )
            ],
            plot_summary=f"This intricately plotted {genre} story based on '{plot}' weaves multiple mysteries together...",
            central_conflict="A web of conflicts with hidden connections",
            story_beats=StoryBeats(
                opening="A seemingly simple beginning with hidden clues",
                catalyst="A discovery that opens multiple mysteries",
                midpoint="A revelation that changes everything",
                crisis="All threads converge",
                resolution="The satisfying unveiling of truth"
            ),
            ending="Every mystery resolved in a satisfying cascade",
            key_elements=["Hidden connections", "Layered mysteries", "Clever misdirection"],
            potential_arcs=["Uncovering truth", "Hidden identity revelation"],
            themes=["Truth beneath surfaces", "Interconnected fate"],
            estimated_complexity=9,
            unique_hooks=["Multiple mystery layers", "Everything connects", "Satisfying reveals"]
        )