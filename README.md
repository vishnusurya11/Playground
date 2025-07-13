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
- Python 3.10+ (3.10, 3.11, or 3.12 recommended)
- UV package manager (cross-platform Python package manager)
- OpenAI API key
- Git (for cloning the repository)

### Installation

1. **Install UV** (Python package manager):
   ```bash
   # Option 1: Using pip (works on all platforms)
   pip install uv
   
   # Option 2: Platform-specific installers
   # macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
   # Windows: irm https://astral.sh/uv/install.ps1 | iex
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
   # Copy the example environment file
   python -c "import shutil; shutil.copy('.env.example', '.env')"
   
   # Then edit .env and add your OpenAI API key
   ```

### Basic Usage

```bash
# Test the system first (recommended)
uv run python test_plot_expander.py

# Run with example plots
uv run python plot_expander.py

# View generated plots in visual UI
uv run streamlit run plot_viewer.py
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

## 🖥️ Visual Plot Viewer

EpicWeaver includes a beautiful web-based UI for browsing and analyzing generated plots:

### Features
- 📁 **Auto-loads** all plots from the forge directory
- ⬅️➡️ **Navigation** with Previous/Next buttons and dropdown
- 📑 **5 Team Tabs** to compare all expansions side-by-side
- 📊 **Visual voting results** with charts and score breakdowns
- 🎨 **Clean, modern UI** with responsive design
- 🏆 **Winner highlighting** and detailed analysis

### Running the Viewer
```bash
# Make sure dependencies are installed
uv sync

# Launch the viewer
uv run streamlit run plot_viewer.py

# Opens automatically in your browser at http://localhost:8501
```

### Viewer Navigation
- Use the **dropdown** to select any plot file
- Click **◀ ▶** buttons to browse sequentially
- Each team's expansion is in its own **tab**
- **Voting results** show at the bottom with interactive charts
- **Expandable sections** for detailed reasoning

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

## 🔧 Troubleshooting

### Common Issues

**UV Installation Failed:**
- **Windows:** Ensure you're running PowerShell as Administrator
- **macOS/Linux:** You may need to add `~/.cargo/bin` to your PATH
- **All platforms:** Try the pip installation method: `pip install uv`

**OpenAI API Key Not Found:**
- Ensure your `.env` file is in the project root directory
- Check that the key is correctly formatted: `OPENAI_API_KEY=sk-...`
- On Windows, make sure the file is named `.env` not `.env.txt`

**Permission Errors:**
- **macOS/Linux:** Use `chmod +x` for any scripts if needed
- **Windows:** Run your terminal as Administrator

**Path/File Not Found Errors:**
- Ensure you're in the correct directory (`EpicWeaver` folder)
- Use `cd` (or `Set-Location` in PowerShell) to navigate to the project root

### Platform-Specific Notes

**Windows Users:**
- Use PowerShell or Command Prompt (PowerShell recommended)
- File paths use backslashes, but the code handles this automatically
- If using WSL, follow the Linux instructions instead

**macOS Users:**
- May need to install Xcode Command Line Tools: `xcode-select --install`
- M1/M2 Macs: All dependencies are compatible with Apple Silicon

**Linux Users:**
- Ensure Python development headers are installed
- Ubuntu/Debian: `sudo apt-get install python3-dev`
- Fedora/RHEL: `sudo dnf install python3-devel`

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