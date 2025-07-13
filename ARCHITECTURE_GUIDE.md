# EpicWeaver Architecture Guide

## Complete Multi-Agent Creative System Documentation

This guide provides everything you need to understand and reuse the EpicWeaver modular multi-agent architecture for any creative task, including adapting it for character development, world-building, or other creative applications.

---

## 1. System Overview

EpicWeaver is a modular multi-agent system that:
- Takes creative input (plot, character, concept)
- Has multiple **expansion teams** create different versions/approaches
- Uses a **voting council** to evaluate and select the best result
- Outputs structured, high-quality creative content

### Core Philosophy
- **Modular**: Each team/voter is a separate file for easy addition/removal
- **Configurable**: Everything controlled through config files
- **Extensible**: Add new teams or voters without changing core code
- **Clean Contracts**: Input/output schemas ensure consistency

---

## 2. Architecture Components

### Core Files
```
├── config.py              # All configuration (teams, voters, models, criteria)
├── schemas.py             # Input/output contracts (Pydantic models)
├── team_manager.py        # Coordinates teams and voting
├── voting_strategies.py   # Pluggable voting algorithms
├── plot_expander.py       # Main orchestrator
├── model_teams_config.json # Model assignments per team/voter
└── ARCHITECTURE_GUIDE.md  # This documentation
```

### Team Structure
```
teams/
├── __init__.py
├── cosmic_storytellers.py    # Each team = separate file
├── neural_narratives.py      # Easy to add new teams
├── quantum_plotters.py
├── mythic_forge.py
└── echo_chamber.py
```

### Voting Structure
```
voters/
├── __init__.py
├── base_voter.py            # Base class with voting logic
├── the_curator.py           # Each voter = separate file
├── genre_maven.py           # Easy to add new voters
├── mind_reader.py
├── trend_prophet.py
├── architect_prime.py
├── wisdom_keeper.py
├── pulse_checker.py
├── edge_walker.py
├── time_sage.py
├── voice_whisperer.py
└── world_builder.py
```

---

## 3. How Teams Work

### Team Contract (Input/Output)
Every team must:
1. Accept: `expand_plot(genre: str, plot: str)` 
2. Return: `ExpandedPlotProposal` (defined in schemas.py)
3. Handle: Model initialization, fallbacks, error cases

### Team Implementation Pattern
```python
class MyTeam:
    def __init__(self, model_config: Dict[str, Any]):
        self.name = model_config.get("name", "My Team")
        self.model_name = model_config.get("model_name", "gpt-4o-mini-2024-07-18")
        self.temperature = model_config.get("temperature", 0.7)
        self.model = self._initialize_model()
    
    def expand_plot(self, genre: str, plot: str) -> ExpandedPlotProposal:
        # Team-specific creative direction
        # Build prompt with team identity
        # Use structured output
        # Return ExpandedPlotProposal
```

### Adding New Teams
1. Create new file in `teams/` folder
2. Implement the team class with required methods
3. Add to `config.py` TEAM_CONFIG section
4. Add import to `teams/__init__.py`

---

## 4. How Voting Works

### Voting Contract
Every voter must:
1. Accept: `vote(expansions: Dict[str, ExpandedPlotProposal])`
2. Return: `VotingResult` with vote choice and reasoning
3. Use: Unique perspective, criteria weights, system prompt

### Voting Implementation Pattern
```python
class MyVoter(BaseVoter):
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        # Inherit voting logic from BaseVoter
        # Customize system_prompt, criteria_weights, voting_bias
```

### Adding New Voters
1. Create new file in `voters/` folder  
2. Inherit from `BaseVoter` (or implement vote method)
3. Add to `config.py` TEAM_CONFIG voting_council section
4. Add import to `voters/__init__.py`

---

## 5. Configuration System

### Main Config (`config.py`)

#### Team Configuration
```python
TEAM_CONFIG = {
    "expansion_teams": {
        "my_new_team": {
            "name": "My New Team",
            "active": True,  # Set to False to disable
            "description": "What this team specializes in"
        }
    },
    "voting_council": {
        "my_new_voter": {
            "name": "My New Voter", 
            "active": True,
            "description": "What this voter evaluates"
        }
    }
}
```

#### File Naming
```python
FILE_NAME_CONFIG = {
    "template": "plot_{genre}_{hash}_{timestamp}.json",
    "output_directory": "forge"
}
```

#### Voting Criteria
```python
VOTING_CRITERIA = {
    "originality": {"weight": 0.15, "description": "How unique is it?"},
    "coherence": {"weight": 0.15, "description": "Does it hold together?"},
    # Add your own criteria here
}
```

### Model Configuration (`model_teams_config.json`)
```json
{
  "expansion_teams": {
    "cosmic_storytellers": {
      "model_name": "gpt-4o-2024-08-06",
      "temperature": 0.8
    }
  },
  "voting_council": {
    "the_curator": {
      "model_name": "gpt-4o-mini-2024-07-18",
      "temperature": 0.3,
      "system_prompt": "Custom prompt for this voter",
      "voting_criteria_weights": {
        "originality": 0.2,
        "coherence": 0.3
      }
    }
  }
}
```

---

## 6. Schema System (Input/Output Contracts)

### Core Schemas (`schemas.py`)

The schemas define the contracts between components:

```python
class ExpandedPlotProposal(BaseModel):
    """What every team must return"""
    team_name: str
    model_used: str
    title: str
    logline: str
    main_characters: List[CharacterInfo]
    plot_summary: str
    central_conflict: str
    story_beats: StoryBeats
    ending: str
    key_elements: List[str]
    potential_arcs: List[str]
    themes: List[str]
    estimated_complexity: int
    unique_hooks: List[str]

class VotingResult(BaseModel):
    """What every voter must return"""
    agent_name: str
    model_used: str
    vote_for_team: str
    reasoning: str
    score_breakdown: Dict[str, int]
```

### Modifying Schemas for New Use Cases

To adapt for character development:
1. Create new schemas (e.g., `CharacterAnalysis`, `CharacterNeeds`)
2. Update team contracts to return new schema
3. Update voter contracts to evaluate new schema
4. Keep the same modular structure

---

## 7. Character Development Use Case

### Complete Adaptation Guide

Here's how to adapt the plot expansion system for character development (needs/wants generation):

#### 1. Define New Schemas
```python
class CharacterInput(BaseModel):
    plot_context: str = Field(description="Plot context for character")
    character_description: str = Field(description="Basic character info")

class CharacterNeedsWants(BaseModel):
    team_name: str
    model_used: str
    character_name: str
    surface_want: str = Field(description="What character thinks they want")
    deep_need: str = Field(description="What character actually needs")
    internal_conflict: str = Field(description="Want vs need tension")
    motivation_source: str = Field(description="Why they want/need this")
    character_arc: str = Field(description="How need/want resolves")
    key_scenes: List[str] = Field(description="Scenes that reveal need/want")
    supporting_elements: List[str] = Field(description="Plot elements that support arc")
    psychological_depth: int = Field(description="Character complexity 1-10")
    thematic_connections: List[str] = Field(description="How needs connect to themes")
```

#### 2. Create Character Development Teams
```python
class CharacterPsychologist:
    """Team focused on psychological depth and authenticity"""
    
    def analyze_character(self, plot_context: str, character_desc: str) -> CharacterNeedsWants:
        prompt = f"""You are the Character Psychologist team.
        
        Plot Context: {plot_context}
        Character: {character_desc}
        
        Analyze this character's deep psychological needs vs surface wants.
        Focus on:
        - Unconscious motivations
        - Psychological wounds driving behavior  
        - Internal contradictions
        - Growth opportunities
        
        Create compelling need/want tension that drives character development."""
        
        # Use structured output to return CharacterNeedsWants
```

#### 3. Create Character Voting Council
```python
class PsychologyExpert(BaseVoter):
    """Evaluates psychological authenticity"""
    
    def __init__(self, model_config):
        model_config.update({
            "system_prompt": "You are a psychology expert evaluating character depth",
            "voting_criteria_weights": {
                "psychological_authenticity": 0.3,
                "need_want_tension": 0.25,
                "character_growth_potential": 0.2,
                "thematic_integration": 0.15,
                "narrative_utility": 0.1
            }
        })
        super().__init__(model_config)
```

#### 4. Update Configuration
```python
# In config.py
CHARACTER_TEAMS = {
    "character_psychologist": {
        "name": "Character Psychologist",
        "active": True,
        "description": "Deep psychological analysis specialist"
    },
    "relationship_expert": {
        "name": "Relationship Expert", 
        "active": True,
        "description": "Interpersonal dynamics and motivations"
    },
    "arc_architect": {
        "name": "Arc Architect",
        "active": True,
        "description": "Character development and growth trajectories"
    }
}

CHARACTER_VOTERS = {
    "psychology_expert": {
        "name": "Psychology Expert",
        "active": True,
        "description": "Psychological authenticity and depth"
    },
    "reader_advocate": {
        "name": "Reader Advocate",
        "active": True,
        "description": "Character likability and relatability"
    },
    "story_integration": {
        "name": "Story Integration",
        "active": True,
        "description": "How well character serves the plot"
    }
}

CHARACTER_CRITERIA = {
    "psychological_authenticity": {"weight": 0.25, "description": "Does this feel real?"},
    "need_want_tension": {"weight": 0.25, "description": "Compelling internal conflict?"},
    "character_growth_potential": {"weight": 0.2, "description": "Clear arc opportunity?"},
    "thematic_integration": {"weight": 0.15, "description": "Supports story themes?"},
    "narrative_utility": {"weight": 0.15, "description": "Drives plot forward?"}
}
```

#### 5. Create Character Main Script
```python
# character_developer.py
def develop_character(plot_context: str, character_desc: str):
    """Main function for character development"""
    
    # Initialize team manager with character config
    manager = CharacterTeamManager()
    
    # Get character analyses from all teams
    analyses = manager.analyze_character(plot_context, character_desc)
    
    # Conduct voting
    results = manager.conduct_character_voting(analyses)
    
    # Return winning character analysis
    return results
```

---

## 8. Voting Strategies

### Current Strategies (`voting_strategies.py`)

1. **StandardVoting**: Each agent gets one vote, majority wins
2. **RankedChoiceVoting**: (Future) Agents rank all options
3. **WeightedVoting**: (Future) Votes weighted by expertise

### Adding New Voting Strategies
```python
class ConsensusVoting(VotingStrategy):
    """Requires consensus above threshold"""
    
    def conduct_voting(self, expansions, voting_agents) -> VotingResults:
        # Custom voting logic
        # Must return VotingResults schema
```

---

## 9. Quick Start Guide

### For New Use Cases (e.g., World Building)

1. **Define Your Domain**
   - What's the input? (plot, character, setting)
   - What's the output? (expanded world, cultures, locations)

2. **Create Schemas**
   ```python
   class WorldBuildingInput(BaseModel):
       genre: str
       basic_setting: str
   
   class WorldExpansion(BaseModel):
       team_name: str
       # ... your domain-specific fields
   ```

3. **Create Teams**
   ```python
   # teams/geography_expert.py
   class GeographyExpert:
       def expand_world(self, genre, setting) -> WorldExpansion:
           # Team logic
   ```

4. **Create Voters** 
   ```python
   # voters/worldbuilding_critic.py
   class WorldbuildingCritic(BaseVoter):
       # Inherits voting logic, customize criteria
   ```

5. **Update Config**
   ```python
   # Add to config.py
   WORLD_TEAMS = { ... }
   WORLD_VOTERS = { ... }
   WORLD_CRITERIA = { ... }
   ```

6. **Create Main Script**
   ```python
   # world_builder.py  
   def build_world(genre, basic_setting):
       # Initialize WorldTeamManager
       # Get expansions from teams
       # Conduct voting
       # Return results
   ```

---

## 10. File Structure Reference

### Current Structure
```
EpicWeaver/
├── config.py                 # System configuration
├── schemas.py                # Input/output contracts  
├── team_manager.py           # Team coordination
├── voting_strategies.py      # Voting algorithms
├── plot_expander.py          # Main plot orchestrator
├── plot_viewer.py            # Results viewer
├── model_teams_config.json   # Model assignments
├── ARCHITECTURE_GUIDE.md     # This guide
├── forge/                    # Output directory
│   └── plot_*.json          # Generated results
├── research/                 # Reference materials
│   ├── character-arc-types.md
│   ├── story-structure-beats.md
│   └── story-wants-vs-needs.md
├── teams/                    # Expansion teams
│   ├── __init__.py
│   ├── cosmic_storytellers.py
│   ├── neural_narratives.py
│   ├── quantum_plotters.py
│   ├── mythic_forge.py
│   └── echo_chamber.py
└── voters/                   # Voting council
    ├── __init__.py
    ├── base_voter.py
    ├── the_curator.py
    ├── genre_maven.py
    ├── mind_reader.py
    ├── trend_prophet.py
    ├── architect_prime.py
    ├── wisdom_keeper.py
    ├── pulse_checker.py
    ├── edge_walker.py
    ├── time_sage.py
    ├── voice_whisperer.py
    └── world_builder.py
```

### For Character Development
```
CharacterWeaver/               # Adapted version
├── character_config.py        # Character-specific config
├── character_schemas.py       # Character contracts
├── character_team_manager.py  # Character team coordination
├── character_developer.py     # Main character orchestrator
├── character_analysis/        # Output directory
├── character_teams/           # Character analysis teams
│   ├── character_psychologist.py
│   ├── relationship_expert.py
│   └── arc_architect.py
└── character_voters/          # Character evaluation council
    ├── psychology_expert.py
    ├── reader_advocate.py
    └── story_integration.py
```

---

## 11. Model Management

### Model Fallbacks
```python
MODEL_FALLBACKS = {
    "gpt-4.1-nano-2025-04-14": "gpt-4o-mini-2024-07-18",
    "o3-mini-2025-01-31": "o1-mini-2024-09-12",
    # Add your fallbacks
}
```

### Model Assignment Per Team
```json
{
  "expansion_teams": {
    "cosmic_storytellers": {
      "model_name": "gpt-4o-2024-08-06",
      "temperature": 0.8
    }
  }
}
```

### Dynamic Model Selection
Teams automatically handle:
- Model initialization
- Fallback on model unavailability  
- Error handling and recovery

---

## 12. Troubleshooting

### Common Issues

1. **Import Errors**
   - Check file names match config keys
   - Verify `__init__.py` imports
   - Ensure class names follow convention

2. **Voting Failures**
   - Check voter class names (spaces removed)
   - Verify base_voter.py inheritance
   - Review JSON parsing in vote responses

3. **Schema Validation**
   - Ensure all required fields provided
   - Check field types match Pydantic definitions
   - Validate nested object structures

4. **Model Issues**
   - Set fallback models in config
   - Check API keys and rate limits
   - Monitor temperature settings

### Debugging Tips
- Enable `verbose_logging` in SYSTEM_CONFIG
- Check generated output files in forge/
- Use fallback creation methods in teams/voters
- Test individual components before full system

---

## 13. Advanced Usage

### Custom Voting Criteria
```python
CUSTOM_CRITERIA = {
    "my_criterion": {
        "weight": 0.2,
        "description": "My specific evaluation standard"
    }
}
```

### Team Specialization
```python
def _post_process_expansion(self, expansion):
    """Team-specific enhancements"""
    if expansion.estimated_complexity < self.min_complexity:
        expansion.estimated_complexity = self.min_complexity
    return expansion
```

### Multi-Stage Voting
```python
class MultiStageVoting(VotingStrategy):
    def conduct_voting(self, expansions, voters):
        # Elimination rounds
        # Final voting
        # Consensus building
```

---

## Summary

This architecture provides:
- **Modularity**: Easy to add/remove teams and voters
- **Flexibility**: Adaptable to any creative domain
- **Scalability**: Handle any number of teams/voters
- **Quality**: Structured outputs and evaluation
- **Maintainability**: Clean separation of concerns

The system has been battle-tested through 24+ hours of development and refinement. Use this guide to quickly adapt it for character development, world-building, or any other creative multi-agent task without recreating the foundational work.

### Key Success Factors
1. Define clear input/output contracts (schemas)
2. Create specialized teams with unique perspectives  
3. Build diverse voting council with different expertise
4. Configure appropriate evaluation criteria
5. Test iteratively and refine prompts

You now have everything needed to recreate and extend this multi-agent creative system for any domain.