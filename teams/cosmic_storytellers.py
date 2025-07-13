"""
Cosmic Storytellers - Masters of expansive, universe-spanning narratives
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from schemas import ExpandedPlotProposal, CharacterInfo, StoryBeats
from config import config


class CosmicStorytellers:
    """Masters of expansive, imaginative storytelling"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Visionary Scribes")  # Support custom names
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
        """Expand plot with Visionary Scribes approach"""
        
        # Team-specific creative direction
        team_identity = "Cosmic Storytellers" if "Cosmic" in self.name else "Visionary Scribes"
        creative_direction = f"""TEAM IDENTITY: You are the {team_identity} - masters of expansive, imaginative storytelling.
Your strength lies in creating rich, detailed worlds with complex character relationships and ambitious scope.
You excel at finding the epic potential in any story seed, transforming simple concepts into sweeping narratives.
AVOID: Being too generic or safe. Push boundaries while maintaining coherence."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As the Visionary Scribes, create a compelling plot expansion with your team's unique perspective.

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

Remember to embody the Visionary Scribes team's unique style and perspective."""
        
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
        # Visionary Scribes might add epic scale elements
        if expansion.estimated_complexity < 7:
            expansion.estimated_complexity = 7  # They tend toward complex narratives
        return expansion
    
    def _create_fallback_expansion(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Create fallback expansion if main process fails"""
        return ExpandedPlotProposal(
            team_name=self.name,
            model_used=self.model_name,
            title="An Epic Tale",
            logline="A sweeping narrative that explores the depths of human experience.",
            main_characters=[
                CharacterInfo(
                    name="The Protagonist",
                    role="Central Hero",
                    description="A complex character driven by powerful motivations"
                )
            ],
            plot_summary=f"In this expansive {genre} narrative based on the concept '{plot}', we follow a protagonist through an epic journey...",
            central_conflict="A conflict of grand proportions",
            story_beats=StoryBeats(
                opening="An epic beginning",
                catalyst="A world-changing event",
                midpoint="A stunning revelation",
                crisis="The darkest hour",
                resolution="A transformative conclusion"
            ),
            ending="The story concludes with profound change",
            key_elements=["Epic scope", "Complex relationships", "World-building"],
            potential_arcs=["Hero's transformation", "Secondary character growth"],
            themes=["The nature of power", "Human resilience"],
            estimated_complexity=8,
            unique_hooks=["Expansive world", "Complex character web", "Epic scale"]
        )