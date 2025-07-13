# Project Requirements and Musts

## CRITICAL REQUIREMENTS - ALWAYS FOLLOW

### 1. Model Selection
- **ONLY use models that cost $2.50 or less per million input tokens**
- Default to `gpt-4o-mini` for best cost/performance ratio
- Switch models using the `model_config.py` file

### 2. Output Requirements
- **ALWAYS provide formatted output, NEVER empty responses**
- Structure all outputs clearly with headers, sections, and proper formatting
- Use markdown for documentation
- Use proper indentation and comments in code

### 3. Development Approach
- **ONE STEP AT A TIME** - Don't rush ahead or overcomplicate
- Wait for explicit instructions before moving to next steps
- Keep solutions simple and straightforward
- Don't "act smart" - follow instructions exactly

### 4. File Organization
- Create reference files in `/research` folder
- Keep agent templates simple and extensible
- Use clear, descriptive file names

### 5. Multi-Agent System Design
- Use supervisor agents for coordination
- Use swarm agents for dynamic handoffs
- Implement agent councils for collaborative decisions
- Multiple supervisor levels as needed

### 6. Novel Writing Focus
- Target: 100,000+ word novels (Brandon Sanderson scale)
- Agents must critique and debate each other
- Voting mechanisms for important decisions
- Focus on quality and depth

## Dependency Management

### MUST Use UV for Project Management
- **Use `uv` for ALL dependency management**
- **Create virtual environments with `uv venv`**
- **Add dependencies with `uv add <package>`**
- **Use `pyproject.toml` for project configuration**

### UV Commands Reference
```bash
# Create new project
uv init

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Add dependencies
uv add langchain openai pydantic

# Install from pyproject.toml
uv sync

# Add dev dependencies
uv add --dev pytest black ruff
```

## Quick Reference

### Available Models (Under $2.50/M input)
1. `gpt-4-nano` - $0.10/M input (cheapest)
2. `gpt-4o-mini` - $0.15/M input (best value)
3. `gpt-4-mini` - $0.40/M input
4. `o3-mini`/`o4-mini` - $1.10/M input (reasoning)
5. `codex-mini` - $1.50/M input (code)
6. `gpt-4-base`/`o3` - $2.00/M input
7. `gpt-4o` - $2.50/M input (at limit)

### Project Structure
```
/
├── research/
│   ├── langgraph-multi-agent.md
│   ├── story-wants-vs-needs.md
│   ├── story-endings-types.md
│   ├── character-arc-types.md
│   └── story-structure-beats.md
├── plots.py
├── model_config.py
└── project_requirements.md
```

## Process Order
1. **Plot Generation** - Create initial plot ideas
2. **Plot Expander** - Expand plots into detailed structures
3. **Character Development** - Create characters based on expanded plots
4. **World Building** - Develop settings and environments
5. **Chapter Planning** - Break down into chapter outlines
6. **Scene Writing** - Write individual scenes
7. **Revision & Editing** - Review and improve

## Structured Output Requirements

### CRITICAL: All Agents Must Use Structured Output
- **Use Pydantic models for ALL agent outputs**
- **Use LangChain's `with_structured_output()` method**
- **NEVER return unformatted text**

### Example Structure for Agent Output:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class AgentResponse(BaseModel):
    content: str = Field(description="Main response content")
    confidence: float = Field(description="Confidence score 0-1")
    suggestions: List[str] = Field(description="Additional suggestions")
    needs_revision: bool = Field(description="Whether output needs revision")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
```

### LangChain Structured Output Pattern:
```python
# Define schema
class PlotExpansion(BaseModel):
    original_plot: str
    three_acts: dict
    character_arcs: List[dict]
    major_beats: List[str]
    themes: List[str]

# Use with model
model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(PlotExpansion)
result = structured_model.invoke("Expand this plot: ...")
```

## Remember
- Simple first, complex later
- **ALWAYS use structured output (Pydantic + with_structured_output)**
- Stay under budget ($2.50/M input tokens)
- One step at a time
- Follow instructions exactly
- Check LangChain documentation for structured output patterns