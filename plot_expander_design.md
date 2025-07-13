# Plot Expander System Design

## Overview

The Plot Expander takes simple plot ideas and expands them through a collaborative multi-agent system. It uses 5 teams of agents to create different expansions, then a council of 7 agents votes on the best version.

## System Architecture

```
Input: (genre, plot) tuple
         ↓
┌─────────────────────────────┐
│   5 Expansion Teams         │
├─────────────────────────────┤
│ Team 1: Model A → Expansion │
│ Team 2: Model B → Expansion │
│ Team 3: Model C → Expansion │
│ Team 4: Model D → Expansion │
│ Team 5: Model E → Expansion │
└─────────────────────────────┘
         ↓
    All 5 Expansions
         ↓
┌─────────────────────────────┐
│   7-Agent Voting Council    │
├─────────────────────────────┤
│ Each agent evaluates all 5  │
│ Provides reasoning & vote   │
└─────────────────────────────┘
         ↓
    Vote Tallying
         ↓
Output: {
  original_plot,
  genre,
  all_expansions,
  voting_results,
  selected_expansion
}
```

## Input/Output Specification

### Input Format
```python
plots = [
    ("Mystery", "A detective discovers the victim is still alive"),
    ("Sci-Fi", "Two enemies must work together to survive"),
    ("Fantasy", "A merchant finds a map to a legendary treasure")
]
```

### Output Structure
```python
class ExpandedPlotProposal(BaseModel):
    team_name: str
    model_used: str
    expanded_plot: str  # One page expansion
    key_elements: List[str]  # Main story elements
    potential_arcs: List[str]  # Character arc possibilities
    themes: List[str]  # Potential themes
    estimated_complexity: int  # 1-10 scale

class VotingResult(BaseModel):
    agent_name: str
    model_used: str
    vote_for_team: str
    reasoning: str
    score_breakdown: Dict[str, int]  # Criteria -> Score

class VotingResults(BaseModel):
    individual_votes: List[VotingResult]
    vote_tally: Dict[str, int]  # team_name -> vote_count
    winning_team: str
    total_votes: int

class PlotExpanderOutput(BaseModel):
    original_plot: str
    genre: str
    all_expanded_plots: Dict[str, ExpandedPlotProposal]
    voting_results: VotingResults
    selected_expanded_plot: str
    timestamp: str
    processing_time: float
```

## Expansion Teams Configuration

Each team consists of 3 agents with different roles:

### Team Structure
1. **Lead Expander**: Main plot expansion
2. **Story Analyst**: Analyzes potential and challenges
3. **Creative Consultant**: Adds unique elements

### Team Discussion Process
1. Lead Expander creates initial expansion
2. Story Analyst critiques and suggests improvements
3. Creative Consultant adds unique twists
4. Team finalizes one-page expansion

### Expansion Guidelines
Each expansion should include:
- **Plot Summary** (2-3 paragraphs)
- **Main Characters** (brief descriptions)
- **Key Conflict** and stakes
- **Potential Subplots**
- **Unique Hook** that sets it apart
- **Target Audience** appeal

## Voting Council Configuration

### Voting Criteria
Each voting agent evaluates based on:
1. **Originality** (1-10): How unique is the expansion?
2. **Coherence** (1-10): Does it make logical sense?
3. **Market Potential** (1-10): Will readers want this?
4. **Character Depth** (1-10): Are characters compelling?
5. **Thematic Richness** (1-10): Does it explore meaningful themes?
6. **Expandability** (1-10): Can this sustain 100k words?

### Voting Process
1. Each agent reads all 5 expansions
2. Scores each expansion on all criteria
3. Selects their top choice with reasoning
4. All votes are tallied
5. Highest vote count wins (ties broken by total scores)

## Model Configuration Strategy

### Flexible Provider Support
The system supports multiple LLM providers through configuration:
- OpenAI (gpt-4o-mini, gpt-4-nano, etc.)
- Anthropic (claude-3-haiku, claude-3-sonnet)
- Google (gemini-1.5-flash, gemini-1.5-pro)
- Ollama (local models)

### Cost Optimization
- Expansion teams use cheaper models for brainstorming
- Voting council can use slightly better models for judgment
- All models stay under $2.50/M input tokens

### Configuration Structure
```json
{
  "expansion_teams": {
    "team_1": {
      "name": "Visionary Scribes",
      "model_provider": "openai",
      "model_name": "gpt-4o-mini",
      "temperature": 0.8
    },
    ...
  },
  "voting_council": {
    "agent_1": {
      "name": "Chief Critic",
      "model_provider": "openai",
      "model_name": "gpt-4-mini",
      "temperature": 0.3
    },
    ...
  }
}
```

## Data Persistence & Debugging

### Saved Data Structure
```
plot_expansions/
├── session_[timestamp]/
│   ├── input.json
│   ├── team_1_expansion.json
│   ├── team_2_expansion.json
│   ├── team_3_expansion.json
│   ├── team_4_expansion.json
│   ├── team_5_expansion.json
│   ├── voting_details.json
│   ├── final_output.json
│   └── debug_log.txt
```

### Debugging Features
1. **Full Conversation Logs**: Every agent interaction saved
2. **Timing Metrics**: Track processing time per team
3. **Model Performance**: Track which models produce winning expansions
4. **Voting Patterns**: Analyze which agents vote together

## Implementation Flow

1. **Initialize System**
   - Load model configurations
   - Create expansion teams
   - Create voting council

2. **Process Each Plot**
   - Distribute to 5 teams in parallel
   - Each team discusses internally (3 rounds max)
   - Collect all expansions

3. **Voting Phase**
   - Present all expansions to voting council
   - Each agent evaluates independently
   - Collect and tally votes

4. **Output Generation**
   - Package all data into structured output
   - Save to disk for debugging
   - Return selected expansion

## Error Handling

- **Model Failures**: Retry with backup model
- **Timeout Handling**: 60-second timeout per expansion
- **Invalid Outputs**: Validation and re-prompting
- **Consensus Failures**: Use score-based tiebreaking

## Future Enhancements

1. **Learning System**: Track which expansions lead to successful novels
2. **Style Adaptation**: Teams can specialize in different genres
3. **Human Override**: Allow human to break voting ties
4. **Quality Metrics**: Track downstream success of selected plots