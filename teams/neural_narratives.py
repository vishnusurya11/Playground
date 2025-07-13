"""
Neural Narratives - AI-inspired structural innovators
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from schemas import ExpandedPlotProposal, CharacterInfo, StoryBeats
from config import config


class NeuralNarratives:
    """Structural innovators and masters of story design"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Narrative Architects")  # Support custom names
        self.model_name = model_config.get("model_name", "gpt-4.1-nano")
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
        """Expand plot with Narrative Architects approach"""
        
        # Team-specific creative direction
        creative_direction = """TEAM IDENTITY: You are the Narrative Architects - structural innovators and masters of story design.
Your strength lies in constructing intricate narrative frameworks with innovative structures and techniques.
You excel at non-linear storytelling, multiple perspectives, nested narratives, and experimental formats.
Focus on HOW the story is told as much as WHAT is told. Create architecturally beautiful stories.
AVOID: Being too abstract or experimental at the expense of emotional connection. Ground your innovations in human drama."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As the Narrative Architects, create a compelling plot expansion with your team's unique structural perspective.

Provide a complete story expansion with:
- A creative title that reflects your architectural approach
- A compelling one-sentence logline (max 30 words)
- 3-4 main characters with names, roles, and motivations
- A plot summary (300-400 words) that showcases innovative structure
- The central conflict and what's at stake
- Five key story beats (opening, catalyst, midpoint, crisis, resolution)
- How the story ends
- 3-5 key story elements that drive the plot
- 2-3 potential character arcs
- Major themes to explore
- What makes this version structurally unique (3-5 hooks)
- Complexity rating from 1-10

Remember to embody the Narrative Architects team's innovative structural approach."""
        
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
        # Narrative Architects focus on structural complexity
        if "non-linear" not in expansion.plot_summary.lower() and "perspective" not in expansion.plot_summary.lower():
            expansion.unique_hooks.append("Innovative narrative structure")
        return expansion
    
    def _create_fallback_expansion(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Create fallback expansion if main process fails"""
        return ExpandedPlotProposal(
            team_name=self.name,
            model_used=self.model_name,
            title="A Structural Masterpiece",
            logline="A story told through innovative narrative architecture.",
            main_characters=[
                CharacterInfo(
                    name="The Observer",
                    role="Narrative Lens",
                    description="A character whose perspective shapes the story's structure"
                )
            ],
            plot_summary=f"This {genre} narrative based on '{plot}' unfolds through an innovative structural approach...",
            central_conflict="A conflict revealed through structural innovation",
            story_beats=StoryBeats(
                opening="A structurally intriguing beginning",
                catalyst="An event that fragments the narrative",
                midpoint="A perspective shift",
                crisis="Structural convergence",
                resolution="Narrative threads unite"
            ),
            ending="The story's structure reveals its meaning",
            key_elements=["Non-linear timeline", "Multiple perspectives", "Structural innovation"],
            potential_arcs=["Perspective evolution", "Structural revelation"],
            themes=["The nature of perception", "Truth through structure"],
            estimated_complexity=9,
            unique_hooks=["Innovative structure", "Multiple timelines", "Nested narratives"]
        )