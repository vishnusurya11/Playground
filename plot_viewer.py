"""
EpicWeaver Plot Viewer - Visual UI for browsing plot expansions
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="EpicWeaver Plot Viewer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Slate color palette from shadcn/ui for consistent, accessible design
SLATE = {
    "50": "#f8fafc",
    "100": "#f1f5f9",
    "200": "#e2e8f0",
    "300": "#cbd5e1",
    "400": "#94a3b8",
    "500": "#64748b",
    "600": "#475569",
    "700": "#334155",
    "800": "#1e293b",
    "900": "#0f172a",
    "950": "#020617"
}

# Core color palette
COLORS = {
    # Primary colors for actions and highlights
    "primary": "#3b82f6",     # Blue-500
    "success": "#10b981",     # Emerald-500
    "warning": "#f59e0b",     # Amber-500
    "error": "#ef4444",       # Red-500
    
    # Team colors (vibrant for visibility)
    "team_blue": "#3b82f6",   # Blue-500
    "team_green": "#10b981",  # Emerald-500
    "team_purple": "#8b5cf6", # Violet-500
    "team_orange": "#f97316", # Orange-500
    "team_pink": "#ec4899"    # Pink-500
}

# Genre colors - simple primary colors only
GENRE_COLORS = {
    "Sci-Fi": "#6366f1",      # Indigo-500
    "Horror": "#dc2626",      # Red-600
    "Fantasy": "#059669",     # Emerald-600
    "Mystery": "#7c3aed",     # Violet-600
    "Crime": "#374151",       # Gray-700
    "Adventure": "#ea580c",   # Orange-600
    "Cyberpunk": "#db2777",   # Pink-600
    "Romance": "#e11d48",     # Rose-600
    "Thriller": "#0f172a",    # Slate-900
    "Default": "#3b82f6"      # Blue-500
}

# Team name to color mapping
TEAM_COLORS = {
    "Visionary Scribes": COLORS["team_blue"],
    "Narrative Architects": COLORS["team_green"], 
    "Plot Weavers": COLORS["team_purple"],
    "Story Alchemists": COLORS["team_orange"],
    "Dream Crafters": COLORS["team_pink"]
}

def get_genre_color(genre):
    return GENRE_COLORS.get(genre, GENRE_COLORS["Default"])

# No custom CSS - use Streamlit defaults
def inject_custom_css(genre):
    pass  # Do nothing

# Initialize session state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

# Load all plot files
def load_plot_files():
    forge_dir = Path("forge")
    if not forge_dir.exists():
        st.error("❌ No 'forge' directory found. Please run plot_expander.py first to generate plots.")
        return []
    
    json_files = list(forge_dir.glob("plot_*.json"))
    if not json_files:
        st.warning("⚠️ No plot files found in the forge directory.")
        return []
    
    # Sort by timestamp (newest first)
    json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return json_files

# Load a specific plot file
def load_plot_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Display character information
def display_character(character):
    st.markdown(f"**{character['name']}** - *{character['role']}*")
    st.caption(character['description'])

# Display story beats
def display_story_beats(beats):
    st.markdown("---")
    cols = st.columns(5)
    beat_names = ['Opening', 'Catalyst', 'Midpoint', 'Crisis', 'Resolution']
    beat_keys = ['opening', 'catalyst', 'midpoint', 'crisis', 'resolution']
    
    for col, name, key in zip(cols, beat_names, beat_keys):
        with col:
            st.markdown(f"**{name}**")
            st.caption(beats[key][:100] + "..." if len(beats[key]) > 100 else beats[key])

# Display team expansion
def display_team_expansion(team_name, expansion):
    # Team header with color
    team_color = TEAM_COLORS.get(team_name, COLORS['primary'])
    
    # Title and logline
    st.markdown(f"### {expansion['title']}")
    st.markdown(f"*{expansion['logline']}*")
    
    # Complexity meter
    complexity = expansion['estimated_complexity']
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"""<div style='text-align: center;'>
            <div style='font-size: 2rem; font-weight: 700; color: {team_color};'>{complexity}</div>
            <div style='font-size: 0.75rem; color: #6c757d; text-transform: uppercase;'>Complexity</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.progress(complexity / 10)
    
    # Main content in columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Plot Summary
        st.markdown("#### Plot Summary")
        st.write(expansion['plot_summary'])
        
        # Story Beats
        st.markdown("#### Story Beats")
        display_story_beats(expansion['story_beats'])
        
        # Central Conflict
        st.markdown("#### Central Conflict")
        st.info(expansion['central_conflict'])
        
        # Ending
        st.markdown("#### Ending")
        st.write(expansion['ending'])
    
    with col2:
        # Characters
        st.markdown("#### Main Characters")
        for char in expansion['main_characters']:
            display_character(char)
        
        # Key Elements
        st.markdown("#### Key Elements")
        for element in expansion['key_elements']:
            st.write(f"• {element}")
        
        # Themes
        st.markdown("#### Themes")
        for theme in expansion['themes']:
            st.write(f"• {theme}")
        
        # Potential Arcs
        st.markdown("#### Potential Character Arcs")
        for arc in expansion['potential_arcs']:
            st.caption(f"• {arc}")
        
        # Unique Hooks
        st.markdown("#### Unique Hooks")
        for hook in expansion['unique_hooks']:
            st.success(hook)

# Display voting results
def display_voting_results(voting_results):
    st.markdown("## 🗳️ Voting Results")
    
    # Winner announcement
    winner = voting_results['winning_team']
    st.success(f"🏆 Winner: {winner}")
    
    # Vote distribution
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### Vote Distribution")
        vote_data = voting_results['vote_tally']
        
        # Create a visual vote display
        for team, vote_count in vote_data.items():
            team_color = TEAM_COLORS.get(team, '#3b82f6')
            percentage = (vote_count / voting_results['total_votes']) * 100
            
            st.markdown(f"**{team}** - {vote_count} votes ({percentage:.0f}%)")
            st.progress(percentage / 100)
        
        # Vote summary
        st.metric("Total Votes", voting_results['total_votes'])
    
    with col2:
        st.markdown("### Individual Votes")
        
        # Create tabs for each voter
        voter_tabs = st.tabs([vote['agent_name'] for vote in voting_results['individual_votes']])
        
        for tab, vote in zip(voter_tabs, voting_results['individual_votes']):
            with tab:
                st.markdown(f"**Voted for:** {vote['vote_for_team']}")
                
                # Score breakdown
                if 'score_breakdown' in vote:
                    st.markdown("**Score Breakdown:**")
                    for criterion, score in vote['score_breakdown'].items():
                        st.caption(f"{criterion.replace('_', ' ').title()}: {score}/10")
                
                # Reasoning
                with st.expander("View Reasoning"):
                    st.write(vote['reasoning'])

# Main app
def main():
    st.title("📚 EpicWeaver Plot Viewer")
    
    # Load all plot files
    plot_files = load_plot_files()
    
    if not plot_files:
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## Navigation")
        
        # File selector
        file_names = [f.name for f in plot_files]
        selected_index = st.selectbox(
            "Select a plot:",
            range(len(file_names)),
            format_func=lambda x: file_names[x],
            index=st.session_state.current_index
        )
        
        # Update current index
        st.session_state.current_index = selected_index
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀", disabled=(selected_index == 0)):
                st.session_state.current_index = selected_index - 1
                st.rerun()
        
        with col2:
            st.markdown(f"**{selected_index + 1} of {len(plot_files)}**")
        
        with col3:
            if st.button("▶", disabled=(selected_index == len(plot_files) - 1)):
                st.session_state.current_index = selected_index + 1
                st.rerun()
        
        # File info
        st.markdown("---")
        st.markdown("### File Info")
        current_file = plot_files[selected_index]
        st.caption(f"**File:** {current_file.name}")
        
        # Extract timestamp from filename
        timestamp_str = current_file.stem.split('_')[-1]
        st.caption(f"**Created:** {timestamp_str}")
    
    # Load and display current plot
    plot_data = load_plot_data(plot_files[selected_index])
    
    if plot_data:
        # Inject CSS with genre-specific colors
        inject_custom_css(plot_data['genre'])
        
        # Hero section with genre and original plot
        st.markdown("<div class='hero-section'>", unsafe_allow_html=True)
        
        # Genre badge
        st.markdown(f"<div style='text-align: center; margin-bottom: 1.5rem;'><span class='genre-badge'>{plot_data['genre']}</span></div>", unsafe_allow_html=True)
        
        # Original plot
        st.markdown(f"""
        <div class='original-plot-container'>
            <div class='original-plot-title'>Original Plot</div>
            <div class='original-plot-text'>
                {plot_data['original_plot']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            winner_team = plot_data['voting_results']['winning_team']
            winner_color = TEAM_COLORS.get(winner_team, COLORS['primary'])
            st.markdown(f"""
            <div class='stats-card'>
                <div class='stats-label'>Winner</div>
                <div class='stats-value' style='color: {winner_color};'>{winner_team}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class='stats-card'>
                <div class='stats-label'>Total Votes</div>
                <div class='stats-value'>{plot_data['voting_results']['total_votes']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='stats-card'>
                <div class='stats-label'>Processing Time</div>
                <div class='stats-value'>{plot_data['processing_time']:.1f}s</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class='stats-card'>
                <div class='stats-label'>Teams</div>
                <div class='stats-value'>{len(plot_data['all_expanded_plots'])}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Team expansions in tabs
        st.markdown("---")
        team_names = list(plot_data['all_expanded_plots'].keys())
        team_tabs = st.tabs(team_names)
        
        for tab, team_name in zip(team_tabs, team_names):
            with tab:
                expansion = plot_data['all_expanded_plots'][team_name]
                display_team_expansion(team_name, expansion)
        
        # Voting results section
        st.markdown("---")
        display_voting_results(plot_data['voting_results'])
        
        # Selected expansion details
        if 'selected_expansion' in plot_data:
            st.markdown("---")
            st.markdown("## ✨ Selected Expansion Details")
            
            selected = plot_data['selected_expansion']
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Winning Team", selected['team_name'])
                st.metric("Model Used", selected['model_used'])
            
            with col2:
                st.metric("Complexity", f"{selected['estimated_complexity']}/10")
                st.metric("Processing Time", f"{plot_data['processing_time']:.2f}s")

if __name__ == "__main__":
    main()