# EpicWeaver 🧵📚

An advanced multi-agent AI system for weaving epic stories. EpicWeaver uses teams of specialized AI agents to expand plot ideas into rich, detailed narratives suitable for 100,000+ word novels.

## 🌟 Features

- **Multi-Agent Architecture**: 5 specialized expansion teams with unique perspectives
- **Democratic Voting System**: 7-member council evaluates and selects best expansions
- **Comprehensive Story Elements**: Character arcs, themes, plot mechanics, and hooks
- **Cost-Effective**: Uses models under $2.50/M input tokens
- **Detailed Analytics**: Voting summaries and pattern analysis
- **Structured Output**: All expansion details in easy-to-access format

## 🏛️ Architecture

EpicWeaver employs a sophisticated multi-agent system:

### Expansion Teams
1. **Visionary Scribes** - Focus on grand narratives and epic scope
2. **Narrative Architects** - Structure and story architecture specialists
3. **Plot Weavers** - Intricate plot threading and connections
4. **Story Alchemists** - Transform concepts into compelling narratives
5. **Dream Crafters** - Innovative and imaginative approaches

### Voting Council
- Chief Literary Critic
- Genre Specialist
- Character Psychologist
- Market Analyst
- Story Structure Expert
- Theme Philosopher
- Reader Experience Advocate

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- UV package manager
- OpenAI API key

### Installation

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/vishnusurya11/EpicWeaver.git
   cd EpicWeaver
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

### Basic Usage

```bash
# Run with example plots
uv run python plot_expander.py

# Test the system first
uv run python test_plot_expander.py
```

### Python API

```python
from plot_expander import PlotExpander

# Initialize
expander = PlotExpander()

# Expand a single plot
result = expander.expand_single_plot(
    genre="Sci-Fi",
    plot="A satellite technician discovers a transmission loop containing her own death, scheduled for next week."
)

# Access results
print(f"Winner: {result.voting_results.winning_team}")
print(f"Themes: {result.selected_expansion['themes']}")
print(f"Complexity: {result.selected_expansion['estimated_complexity']}/10")
```

## 📊 Output Format

Each expansion includes:
```json
{
  "selected_expansion": {
    "expanded_plot": "Full one-page plot expansion...",
    "team_name": "Winning team name",
    "model_used": "Model that created it",
    "key_elements": ["Element 1", "Element 2", ...],
    "potential_arcs": ["Character arc 1", "Character arc 2", ...],
    "themes": ["Theme 1", "Theme 2", ...],
    "unique_hooks": ["Hook 1", "Hook 2", ...],
    "estimated_complexity": 8
  },
  "voting_summary": {
    "vote_distribution": {"Team A": 3, "Team B": 2, ...},
    "agent_votes": {...},
    "team_avg_scores": {...}
  }
}
```

## 🛠️ Configuration

### Model Configuration
Edit `model_teams_config.json` to customize:
- Team personalities and approaches
- Model assignments
- Voting criteria weights
- Agent system prompts

### Available Models
All models under $2.50/M input tokens:
- gpt-4o-mini ($0.15/M input)
- gpt-4.1-mini ($0.40/M input)
- gpt-4.1-nano ($0.10/M input)
- And more...

## 📁 Project Structure

```
EpicWeaver/
├── plot_expander.py      # Main expansion system
├── model_config.py       # Model pricing and configuration
├── model_teams_config.json # Team and agent configurations
├── research/             # Story structure research
│   ├── character-arc-types.md
│   ├── story-structure-beats.md
│   └── ...
├── tests/                # Test scripts
└── forge/                # Output directory (git-ignored)
```

## 🧪 Testing

```bash
# Test setup and API
uv run python test_plot_expander.py

# Test voting mechanism
uv run python test_voting.py

# Test with single plot
uv run python test_single_plot.py
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with LangChain and OpenAI
- Inspired by collaborative storytelling and swarm intelligence
- Research on story structure from various narrative theorists

## 📧 Contact

Project Link: [https://github.com/vishnusurya11/EpicWeaver](https://github.com/vishnusurya11/EpicWeaver)

---

*"Where stories are woven by the collective intelligence of specialized AI agents"*