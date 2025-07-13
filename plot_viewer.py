"""
EpicWeaver Plot Viewer - Visual UI for browsing plot expansions and analytics
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import PlotAnalytics

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
    "Cosmic Storytellers": COLORS["team_blue"],
    "Neural Narratives": COLORS["team_green"], 
    "Quantum Plotters": COLORS["team_purple"],
    "Mythic Forge": COLORS["team_orange"],
    "Echo Chamber": COLORS["team_pink"]
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
            data = json.load(f)
            
        # Validate required fields
        required_fields = ['genre', 'original_plot', 'all_expanded_plots', 'voting_results']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            st.warning(f"File is missing fields: {', '.join(missing_fields)}")
            
        return data
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON in file: {e}")
        return None
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

# Display analytics functions
def display_team_analytics(analytics: PlotAnalytics):
    """Display team performance analytics"""
    st.markdown("## 📊 Team Analytics")
    
    team_stats = analytics.get_team_stats()
    
    if not team_stats:
        st.warning("No team data available")
        return
    
    # Team performance overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Win rate chart
        team_names = list(team_stats.keys())
        win_rates = [stats['win_rate'] for stats in team_stats.values()]
        
        fig = px.bar(
            x=team_names,
            y=win_rates,
            title="Team Win Rates (%)",
            labels={'x': 'Team', 'y': 'Win Rate (%)'},
            color=win_rates,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Team summary stats
        st.markdown("### Team Summary")
        for team_name, stats in team_stats.items():
            with st.expander(f"{team_name}"):
                st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
                st.metric("Total Wins", stats['wins'])
                st.metric("Participations", stats['total_participations'])
                st.metric("Avg Complexity", f"{stats['avg_complexity']:.1f}")
    
    # Genre performance heatmap
    st.markdown("### Genre Performance")
    
    # Create genre performance matrix
    genres = set()
    for stats in team_stats.values():
        genres.update(stats['genre_performance'].keys())
    
    genre_data = []
    for team_name, stats in team_stats.items():
        for genre in genres:
            if genre in stats['genre_performance']:
                perf = stats['genre_performance'][genre]
                win_rate = (perf['wins'] / perf['participations'] * 100) if perf['participations'] > 0 else 0
                genre_data.append({
                    'Team': team_name,
                    'Genre': genre,
                    'Win Rate': win_rate,
                    'Participations': perf['participations']
                })
    
    if genre_data:
        df = pd.DataFrame(genre_data)
        pivot_df = df.pivot(index='Team', columns='Genre', values='Win Rate')
        
        fig = px.imshow(
            pivot_df,
            title="Team Performance by Genre (Win Rate %)",
            aspect="auto",
            color_continuous_scale="RdBu",
            text_auto='.1f'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Average votes per team
    st.markdown("### Average Votes Received")
    avg_votes = [stats['avg_votes_per_round'] for stats in team_stats.values()]
    
    fig = px.bar(
        x=team_names,
        y=avg_votes,
        title="Average Votes per Round",
        labels={'x': 'Team', 'y': 'Average Votes'},
        color=avg_votes,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig, use_container_width=True)

def display_voter_analytics(analytics: PlotAnalytics):
    """Display voter behavior analytics"""
    st.markdown("## 🗳️ Voter Analytics")
    
    voter_stats = analytics.get_voter_stats()
    
    if not voter_stats:
        st.warning("No voter data available")
        return
    
    # Voter accuracy overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Accuracy chart
        voter_names = list(voter_stats.keys())
        accuracy_rates = [stats['accuracy_rate'] for stats in voter_stats.values()]
        
        fig = px.bar(
            x=voter_names,
            y=accuracy_rates,
            title="Voter Accuracy Rates (%)",
            labels={'x': 'Voter', 'y': 'Accuracy Rate (%)'},
            color=accuracy_rates,
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Voting patterns
        patterns = analytics.get_voting_patterns()
        
        st.markdown("### Voting Patterns")
        
        # Consensus voters
        if patterns['consensus_voters']:
            st.markdown("**🎯 Most Accurate Voters:**")
            for voter in patterns['consensus_voters'][:3]:
                st.caption(f"• {voter['name']} ({voter['accuracy']:.1f}%)")
        
        # Contrarian voters
        if patterns['contrarian_voters']:
            st.markdown("**🎨 Most Independent Voters:**")
            for voter in patterns['contrarian_voters'][:3]:
                st.caption(f"• {voter['name']} ({voter['accuracy']:.1f}%)")
    
    # Team preferences heatmap
    st.markdown("### Voter-Team Preferences")
    
    # Create preference matrix
    teams = set()
    for stats in voter_stats.values():
        teams.update(stats['team_votes'].keys())
    
    pref_data = []
    for voter_name, stats in voter_stats.items():
        for team in teams:
            votes = stats['team_votes'].get(team, 0)
            pref_data.append({
                'Voter': voter_name,
                'Team': team,
                'Votes': votes
            })
    
    if pref_data:
        df = pd.DataFrame(pref_data)
        pivot_df = df.pivot(index='Voter', columns='Team', values='Votes')
        
        fig = px.imshow(
            pivot_df,
            title="Voter-Team Preference Matrix (Vote Count)",
            aspect="auto",
            color_continuous_scale="YlOrRd",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual voter details
    st.markdown("### Individual Voter Profiles")
    
    voter_cols = st.columns(3)
    for idx, (voter_name, stats) in enumerate(voter_stats.items()):
        col = voter_cols[idx % 3]
        with col:
            with st.expander(voter_name):
                st.metric("Accuracy", f"{stats['accuracy_rate']:.1f}%")
                st.metric("Total Votes", stats['total_votes_cast'])
                st.metric("Favorite Team", stats['favorite_team'])
                
                # Criteria preferences
                if stats['avg_criteria_scores']:
                    st.caption("**Average Criteria Scores:**")
                    for criterion, score in stats['avg_criteria_scores'].items():
                        st.progress(score/10, text=f"{criterion}: {score:.1f}")

def display_overall_statistics(analytics: PlotAnalytics):
    """Display system-wide statistics"""
    st.markdown("## 📈 Overall Statistics")
    
    stats = analytics.get_overall_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Plots Generated", stats['total_plots'])
    with col2:
        st.metric("Avg Processing Time", f"{stats['avg_processing_time']:.1f}s")
    with col3:
        st.metric("Avg Complexity", f"{stats['avg_complexity']:.1f}/10")
    with col4:
        st.metric("Unique Models Used", len(stats['models_used']))
    
    # Genre distribution
    col1, col2 = st.columns(2)
    
    with col1:
        if stats['genres']:
            fig = px.pie(
                values=list(stats['genres'].values()),
                names=list(stats['genres'].keys()),
                title="Genre Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if stats['models_used']:
            # Model usage
            models = list(stats['models_used'].keys())
            usage = list(stats['models_used'].values())
            
            fig = px.bar(
                x=models,
                y=usage,
                title="Model Usage Frequency",
                labels={'x': 'Model', 'y': 'Usage Count'}
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Processing time distribution
    if stats['processing_times']:
        fig = px.histogram(
            stats['processing_times'],
            nbins=20,
            title="Processing Time Distribution",
            labels={'value': 'Processing Time (s)', 'count': 'Frequency'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Complexity distribution
    if stats['complexity_distribution']:
        fig = px.histogram(
            stats['complexity_distribution'],
            nbins=10,
            title="Story Complexity Distribution",
            labels={'value': 'Complexity Score', 'count': 'Frequency'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Main app
def main():
    st.title("📚 EpicWeaver Dashboard")
    
    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["📖 Review", "📊 Analytics"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if mode == "📖 Review":
        # Original review functionality
        display_review_mode()
    else:
        # Analytics mode
        display_analytics_mode()

def display_review_mode():
    """Display the original plot review interface"""
    # Load all plot files
    plot_files = load_plot_files()
    
    if not plot_files:
        st.error("No plot files found in the forge directory.")
        st.info("Run `uv run python plot_expander.py` to generate some plots first!")
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
        st.markdown("## 🎭 Team Expansions")
        
        team_names = list(plot_data['all_expanded_plots'].keys())
        
        # Add team count info
        st.info(f"📊 {len(team_names)} teams competed for this plot")
        
        # Create tabs with better labels
        tab_labels = []
        for team_name in team_names:
            # Add winner emoji to winning team
            if team_name == plot_data['voting_results']['winning_team']:
                tab_labels.append(f"🏆 {team_name}")
            else:
                tab_labels.append(team_name)
        
        team_tabs = st.tabs(tab_labels)
        
        for tab, team_name in zip(team_tabs, team_names):
            with tab:
                try:
                    expansion = plot_data['all_expanded_plots'][team_name]
                    display_team_expansion(team_name, expansion)
                except Exception as e:
                    st.error(f"Error displaying {team_name}: {str(e)}")
                    st.json(plot_data['all_expanded_plots'][team_name])
        
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

def display_league_tables(analytics: PlotAnalytics):
    """Display competitive league tables"""
    st.markdown("## 🏆 League Tables")
    
    # Team League Table
    st.markdown("### Team League Standings")
    
    team_table = analytics.get_team_league_table()
    
    if team_table:
        # Create visual league table
        st.markdown("---")
        
        # Header
        cols = st.columns([0.5, 2.5, 0.8, 0.8, 0.8, 1, 1.5, 0.8, 1.2])
        cols[0].markdown("**Pos**")
        cols[1].markdown("**Team**")
        cols[2].markdown("**P**")
        cols[3].markdown("**W**")
        cols[4].markdown("**2nd**")
        cols[5].markdown("**Pts**")
        cols[6].markdown("**Form**")
        cols[7].markdown("**Bias**")
        cols[8].markdown("**Status**")
        
        # Add cutoff line after position 5
        for idx, team in enumerate(team_table):
            # Cutoff line
            if idx == 5:
                st.markdown("---")
                st.markdown("##### 🚫 Relegation Zone")
            
            cols = st.columns([0.5, 2.5, 0.8, 0.8, 0.8, 1, 1.5, 0.8, 1.2])
            
            # Position with change indicator
            pos_change = {"up": "↑", "down": "↓", "same": "→", "new": "🆕"}
            change_icon = pos_change.get(team["position_change"], "")
            cols[0].markdown(f"{team['position']} {change_icon}")
            
            # Team name with zone coloring
            if team['position'] == 1:
                cols[1].markdown(f"🥇 **{team['name']}**")
            elif team['position'] <= 5:
                cols[1].markdown(f"**{team['name']}**")
            else:
                cols[1].markdown(f"_{team['name']}_")
            
            # Stats
            cols[2].markdown(str(team['played']))
            cols[3].markdown(str(team['won']))
            cols[4].markdown(str(team['second']))
            cols[5].markdown(f"**{team['points']}**")
            
            # Form with color coding
            form_display = ""
            for result in team['form']:
                if result == 'W':
                    form_display += "🟢"
                elif result == 'S':
                    form_display += "🟡"
                else:
                    form_display += "🔴"
            cols[6].markdown(form_display)
            
            # Bias score with warning
            bias_score = team['bias_score']
            if bias_score > 0.6:
                cols[7].markdown(f"⚠️ {bias_score:.2f}")
            else:
                cols[7].markdown(f"{bias_score:.2f}")
            
            # Status
            if team['status'] == 'active':
                cols[8].markdown("✅ Active")
            else:
                cols[8].markdown("⏸️ Bench")
        
        # Team stats summary
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Active Teams:** Top {analytics.league_system.config['active_team_slots']} teams participate in plot expansion")
        with col2:
            st.info(f"**Points System:** Win = 3pts, 2nd = 1pt")
    else:
        st.warning("Not enough data for team league table (min 3 participations required)")
    
    # Voter League Table
    st.markdown("### Voter League Standings")
    
    voter_table = analytics.get_voter_league_table()
    
    if voter_table:
        st.markdown("---")
        
        # Header
        cols = st.columns([0.5, 2.5, 0.8, 0.8, 1, 1, 1.5, 0.8, 1.2])
        cols[0].markdown("**Pos**")
        cols[1].markdown("**Voter**")
        cols[2].markdown("**V**")
        cols[3].markdown("**✓**")
        cols[4].markdown("**Pts**")
        cols[5].markdown("**Acc%**")
        cols[6].markdown("**Form**")
        cols[7].markdown("**Bias**")
        cols[8].markdown("**Status**")
        
        # Add cutoff line after position 11
        for idx, voter in enumerate(voter_table):
            if idx == 11:
                st.markdown("---")
                st.markdown("##### 🚫 Bench Zone")
            
            cols = st.columns([0.5, 2.5, 0.8, 0.8, 1, 1, 1.5, 0.8, 1.2])
            
            # Position with change
            pos_change = {"up": "↑", "down": "↓", "same": "→", "new": "🆕"}
            change_icon = pos_change.get(voter["position_change"], "")
            cols[0].markdown(f"{voter['position']} {change_icon}")
            
            # Voter name
            if voter['position'] == 1:
                cols[1].markdown(f"🥇 **{voter['name']}**")
            elif voter['position'] <= 11:
                cols[1].markdown(f"**{voter['name']}**")
            else:
                cols[1].markdown(f"_{voter['name']}_")
            
            # Stats
            cols[2].markdown(str(voter['votes_cast']))
            cols[3].markdown(str(voter['correct_votes']))
            cols[4].markdown(f"**{voter['points']}**")
            cols[5].markdown(f"{voter['accuracy_rate']:.1f}%")
            
            # Form
            form_display = ""
            for result in voter['form']:
                if result == 'C':
                    form_display += "🟢"
                elif result == 'N':
                    form_display += "🟡"
                else:
                    form_display += "🔴"
            cols[6].markdown(form_display)
            
            # Bias
            bias_score = voter['bias_score']
            if bias_score > 0.6:
                cols[7].markdown(f"⚠️ {bias_score:.2f}")
            else:
                cols[7].markdown(f"{bias_score:.2f}")
            
            # Status
            if voter['status'] == 'active':
                cols[8].markdown("✅ Active")
            else:
                cols[8].markdown("⏸️ Bench")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Active Voters:** Top {analytics.league_system.config['active_voter_slots']} voters participate in voting")
        with col2:
            st.info(f"**Points System:** Correct = 3pts, 2nd = 1pt, +1 for consensus")
    else:
        st.warning("Not enough data for voter league table (min 3 participations required)")
    
    # Fairness Report
    st.markdown("### 🎯 Fairness & Bias Report")
    
    fairness_report = analytics.get_fairness_report()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fairness_score = fairness_report['overall_fairness_score']
        if fairness_score >= 80:
            st.success(f"**Fairness Score:** {fairness_score:.1f}%")
        elif fairness_score >= 60:
            st.warning(f"**Fairness Score:** {fairness_score:.1f}%")
        else:
            st.error(f"**Fairness Score:** {fairness_score:.1f}%")
    
    with col2:
        st.metric("Biased Teams", len(fairness_report['biased_teams']))
    
    with col3:
        st.metric("Biased Voters", len(fairness_report['biased_voters']))
    
    # Recommendations
    if fairness_report['recommendations']:
        st.markdown("**Recommendations:**")
        for rec in fairness_report['recommendations']:
            st.markdown(f"• {rec}")
    
    # Legend
    with st.expander("📖 Legend"):
        st.markdown("""
        **Positions:** ↑ Up | ↓ Down | → Same | 🆕 New
        
        **Form:** 🟢 Win/Correct | 🟡 2nd/Near | 🔴 Loss/Wrong
        
        **Bias Score:** Concentration of votes (0=diverse, 1=concentrated)
        
        **Columns:**
        - P = Played, W = Won, 2nd = Second Place
        - V = Votes Cast, ✓ = Correct Votes
        - Acc% = Accuracy Rate
        """)

def display_analytics_mode():
    """Display analytics interface"""
    # Initialize analytics
    analytics = PlotAnalytics()
    
    if not analytics.plots_data:
        st.error("No plot data found for analytics.")
        st.info("Generate some plots first using `python plot_expander.py`")
        return
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Team Analytics", "🗳️ Voter Analytics", "📈 Overall Statistics", "🏆 League Tables"])
    
    with tab1:
        display_team_analytics(analytics)
    
    with tab2:
        display_voter_analytics(analytics)
    
    with tab3:
        display_overall_statistics(analytics)
    
    with tab4:
        display_league_tables(analytics)
    
    # Additional analytics in sidebar
    with st.sidebar:
        st.markdown("## Analytics Summary")
        
        # Quick stats
        team_stats = analytics.get_team_stats()
        voter_stats = analytics.get_voter_stats()
        overall_stats = analytics.get_overall_statistics()
        
        st.metric("Total Plots", overall_stats['total_plots'])
        st.metric("Active Teams", len(team_stats))
        st.metric("Active Voters", len(voter_stats))
        
        # Top performer
        if team_stats:
            top_team = max(team_stats.items(), key=lambda x: x[1]['win_rate'])
            st.markdown("### 🏆 Top Team")
            st.info(f"{top_team[0]} ({top_team[1]['win_rate']:.1f}% win rate)")
        
        # Most accurate voter
        if voter_stats:
            top_voter = max(voter_stats.items(), key=lambda x: x[1]['accuracy_rate'])
            st.markdown("### 🎯 Most Accurate Voter")
            st.info(f"{top_voter[0]} ({top_voter[1]['accuracy_rate']:.1f}% accuracy)")

if __name__ == "__main__":
    main()