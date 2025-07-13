"""
Mythic Forge - Transformative storytellers who blend genres and tones
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from schemas import ExpandedPlotProposal, CharacterInfo, StoryBeats
from config import config


class MythicForge:
    """Transformative storytellers who blend genres and tones"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Mythic Forge")  # Support custom names
        self.model_name = model_config.get("model_name", "gpt-4.1-mini")
        self.temperature = model_config.get("temperature", 0.8)  # Higher temp for creativity
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
        """Expand plot with Mythic Forge approach"""
        
        # Team-specific creative direction
        creative_direction = """TEAM IDENTITY: You are the Mythic Forge - transformative storytellers who blend genres and tones.
Your strength lies in unexpected combinations and genre-bending approaches that create something entirely new.
You excel at finding surprising angles and mixing elements that shouldn't work but somehow do brilliantly.
Transform the base plot into gold by combining unexpected elements - mix genres, blend tones, create unique hybrids.
AVOID: Being predictable or following standard genre conventions too closely."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As the Mythic Forge, create a compelling plot expansion that transforms and blends genres unexpectedly.

Provide a complete story expansion with:
- A creative title that hints at your alchemical transformation
- A compelling one-sentence logline (max 30 words)
- 3-4 main characters from different genre archetypes
- A plot summary (300-400 words) that blends genres and tones
- The central conflict that transcends genre boundaries
- Five key story beats (opening, catalyst, midpoint, crisis, resolution)
- How the story ends with genre-defying satisfaction
- 3-5 key elements from different genres
- 2-3 potential character arcs that cross genres
- Major themes that emerge from genre fusion
- What makes this alchemical blend unique (3-5 hooks)
- Complexity rating from 1-10

Remember to embody the Mythic Forge team's transformative, genre-blending approach."""
        
        # Use structured output
        structured_model = self.model.with_structured_output(ExpandedPlotProposal)
        
        try:
            # Get expansion
            expansion = structured_model.invoke(prompt)
            
            # Ensure team name and model are set
            expansion.team_name = self.name
            expansion.model_used = self.model_name
            
            # Add any team-specific post-processing
            return self._post_process_expansion(expansion, genre)
            
        except Exception as e:
            print(f"Error in {self.name} expansion: {e}")
            return self._create_fallback_expansion(genre, plot)
    
    def _post_process_expansion(self, expansion: ExpandedPlotProposal, original_genre: str) -> ExpandedPlotProposal:
        """Team-specific post-processing"""
        # Mythic Forge always add genre-blending elements
        genre_blend_keywords = ["blend", "fusion", "hybrid", "mix", "cross"]
        if not any(keyword in expansion.plot_summary.lower() for keyword in genre_blend_keywords):
            expansion.unique_hooks.append(f"Unexpected {original_genre} genre transformation")
        # They tend toward moderate-high complexity
        if expansion.estimated_complexity < 6:
            expansion.estimated_complexity = 7
        return expansion
    
    def _create_fallback_expansion(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Create fallback expansion if main process fails"""
        return ExpandedPlotProposal(
            team_name=self.name,
            model_used=self.model_name,
            title="The Alchemical Transformation",
            logline="A genre-defying tale that transforms expectations into gold.",
            main_characters=[
                CharacterInfo(
                    name="The Catalyst",
                    role="Genre-Crossing Protagonist",
                    description="A character who embodies multiple genre archetypes"
                )
            ],
            plot_summary=f"This alchemical transformation of the {genre} plot '{plot}' blends unexpected genre elements...",
            central_conflict="A conflict that transcends genre boundaries",
            story_beats=StoryBeats(
                opening="A familiar genre setup with unexpected elements",
                catalyst="Genre boundaries begin to dissolve",
                midpoint="Complete genre transformation",
                crisis="Genre elements clash and merge",
                resolution="A new genre hybrid emerges"
            ),
            ending="Genre expectations transformed into something new",
            key_elements=["Genre fusion", "Tonal shifts", "Unexpected combinations"],
            potential_arcs=["Genre transformation", "Archetype evolution"],
            themes=["Transformation", "Breaking boundaries"],
            estimated_complexity=7,
            unique_hooks=["Genre-bending narrative", "Unexpected tonal shifts", "Alchemical story transformation"]
        )