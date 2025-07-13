"""
Echo Chamber - Weavers of surreal, emotionally resonant narratives
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from schemas import ExpandedPlotProposal, CharacterInfo, StoryBeats
from config import config


class EchoChamber:
    """Weavers of surreal, emotionally resonant narratives"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "Echo Chamber")  # Support custom names
        self.model_name = model_config.get("model_name", "gpt-4o-2024-08-06")
        self.temperature = model_config.get("temperature", 0.9)  # Highest temp for dreamlike creativity
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
        """Expand plot with Echo Chamber approach"""
        
        # Team-specific creative direction
        creative_direction = """TEAM IDENTITY: You are the Echo Chamber - weavers of surreal, emotionally resonant narratives.
Your strength lies in creating dreamlike, atmospheric stories that blur reality and imagination.
You excel at psychological depth, symbolic imagery, and stories that work on multiple levels of meaning.
Craft narratives that feel like lucid dreams - vivid, emotional, and operating on dream logic.
AVOID: Being incomprehensible or losing the core story in abstract concepts."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As the Echo Chamber, create a compelling plot expansion with dreamlike, emotionally resonant qualities.

Provide a complete story expansion with:
- A creative title that evokes dreams and emotion
- A compelling one-sentence logline (max 30 words)
- 3-4 main characters with psychological depth
- A plot summary (300-400 words) with dreamlike atmosphere
- The central conflict on both literal and symbolic levels
- Five key story beats (opening, catalyst, midpoint, crisis, resolution)
- How the story ends with emotional resonance
- 3-5 key symbolic or surreal elements
- 2-3 potential psychological character arcs
- Major themes explored through symbolism
- What makes this dreamlike narrative unique (3-5 hooks)
- Complexity rating from 1-10

Remember to embody the Echo Chamber team's surreal, emotionally deep approach."""
        
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
        # Echo Chamber add surreal elements
        dream_keywords = ["dream", "surreal", "symbolic", "psychological", "subconscious"]
        if not any(keyword in expansion.plot_summary.lower() for keyword in dream_keywords):
            expansion.unique_hooks.append("Operates on dream logic")
        # Add thematic depth
        if len(expansion.themes) < 3:
            expansion.themes.append("The nature of reality and perception")
        return expansion
    
    async def expand_plot_async(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Async version - expand plot using ainvoke for parallel processing"""
        # Team-specific creative direction
        creative_direction = """TEAM IDENTITY: You are Echo Chamber - surreal, psychologically resonant storytellers.
Your strength lies in exploring the inner landscapes of the mind, where reality bends to emotional truth.
You excel at stories that work on multiple levels - literal and symbolic, conscious and subconscious.
AVOID: Pure realism. Embrace the strange, the symbolic, and the psychologically profound."""
        
        # Build expansion prompt
        prompt = f"""{creative_direction}

Team: {self.name}
Genre: {genre}
Original Plot: {plot}

As Echo Chamber, create a psychologically layered plot expansion.

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

Remember to embody Echo Chamber's surreal, psychological approach."""
        
        # Use structured output with async
        structured_model = self.model.with_structured_output(ExpandedPlotProposal)
        
        try:
            # Get expansion using async
            expansion = await structured_model.ainvoke(prompt)
            
            # Ensure team name and model are set
            expansion.team_name = self.name
            expansion.model_used = self.model_name
            
            # Add any team-specific post-processing
            return self._post_process_expansion(expansion)
            
        except Exception as e:
            print(f"Async error in {self.name} expansion: {e}")
            raise
    
    def _create_fallback_expansion(self, genre: str, plot: str) -> ExpandedPlotProposal:
        """Create fallback expansion if main process fails"""
        return ExpandedPlotProposal(
            team_name=self.name,
            model_used=self.model_name,
            title="The Dreaming Mind",
            logline="A journey through consciousness where reality bends to emotional truth.",
            main_characters=[
                CharacterInfo(
                    name="The Dreamer",
                    role="Consciousness Explorer",
                    description="A character navigating layers of reality and dream"
                )
            ],
            plot_summary=f"This dreamlike {genre} narrative based on '{plot}' unfolds across multiple planes of consciousness...",
            central_conflict="A conflict between perception and reality",
            story_beats=StoryBeats(
                opening="Reality begins to shimmer at the edges",
                catalyst="A breach in the wall between dream and wake",
                midpoint="The dreamer realizes they shape reality",
                crisis="Dream and reality collapse together",
                resolution="A new understanding emerges"
            ),
            ending="Reality and dream find harmony",
            key_elements=["Dream logic", "Symbolic imagery", "Emotional landscapes"],
            potential_arcs=["Journey through consciousness", "Integration of shadow self"],
            themes=["Reality vs perception", "The power of the subconscious", "Emotional truth"],
            estimated_complexity=8,
            unique_hooks=["Dreamlike narrative", "Multiple reality layers", "Emotional symbolism"]
        )