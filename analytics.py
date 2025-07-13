"""
EpicWeaver Analytics Module - Analyzes team and voter patterns across all plots
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Tuple
import pandas as pd
from league_system import LeagueSystem


class PlotAnalytics:
    """Analyzes plot data to extract team and voter insights"""
    
    def __init__(self, forge_dir: str = "forge"):
        self.forge_dir = Path(forge_dir)
        self.plots_data = []
        self.league_system = LeagueSystem()
        self._load_all_plots()
        self._update_league_standings()
    
    def _load_all_plots(self):
        """Load all plot JSON files from forge directory"""
        json_files = list(self.forge_dir.glob("plot_*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Add metadata
                    data['_file_name'] = file_path.name
                    data['_file_path'] = str(file_path)
                    # Extract timestamp from filename
                    timestamp_str = file_path.stem.split('_')[-1]
                    data['_timestamp'] = timestamp_str
                    self.plots_data.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        # Sort by timestamp
        self.plots_data.sort(key=lambda x: x['_timestamp'], reverse=True)
    
    def _update_league_standings(self):
        """Update league standings based on all plots"""
        # Process each plot in chronological order for accurate standings
        for plot in reversed(self.plots_data):  # Process oldest first
            plot_id = plot['_file_name']
            self.league_system.update_team_result(plot_id, plot['voting_results'])
            self.league_system.update_voter_result(plot_id, plot['voting_results'])
        
        # Save updated standings
        self.league_system.save_league_data()
    
    def get_team_stats(self) -> Dict[str, Dict[str, Any]]:
        """Calculate comprehensive team statistics"""
        team_stats = defaultdict(lambda: {
            'total_participations': 0,
            'wins': 0,
            'total_votes_received': 0,
            'vote_history': [],
            'complexity_scores': [],
            'genre_performance': defaultdict(lambda: {'participations': 0, 'wins': 0}),
            'model_usage': defaultdict(int)
        })
        
        for plot in self.plots_data:
            genre = plot['genre']
            winning_team = plot['voting_results']['winning_team']
            vote_tally = plot['voting_results']['vote_tally']
            
            # Process each team's data
            for team_name, expansion in plot['all_expanded_plots'].items():
                stats = team_stats[team_name]
                stats['total_participations'] += 1
                
                # Track votes
                votes_received = vote_tally.get(team_name, 0)
                stats['total_votes_received'] += votes_received
                stats['vote_history'].append(votes_received)
                
                # Track wins
                if team_name == winning_team:
                    stats['wins'] += 1
                    stats['genre_performance'][genre]['wins'] += 1
                
                # Track complexity
                stats['complexity_scores'].append(expansion['estimated_complexity'])
                
                # Track genre participation
                stats['genre_performance'][genre]['participations'] += 1
                
                # Track model usage
                model_used = expansion.get('model_used', 'unknown')
                stats['model_usage'][model_used] += 1
        
        # Calculate derived statistics
        for team_name, stats in team_stats.items():
            if stats['total_participations'] > 0:
                stats['win_rate'] = (stats['wins'] / stats['total_participations']) * 100
                stats['avg_votes_per_round'] = stats['total_votes_received'] / stats['total_participations']
                stats['avg_complexity'] = sum(stats['complexity_scores']) / len(stats['complexity_scores'])
            else:
                stats['win_rate'] = 0
                stats['avg_votes_per_round'] = 0
                stats['avg_complexity'] = 0
        
        return dict(team_stats)
    
    def get_voter_stats(self) -> Dict[str, Dict[str, Any]]:
        """Calculate comprehensive voter statistics"""
        voter_stats = defaultdict(lambda: {
            'total_votes_cast': 0,
            'correct_predictions': 0,
            'team_votes': defaultdict(int),
            'model_usage': defaultdict(int),
            'criteria_scores': defaultdict(list),
            'vote_history': []
        })
        
        for plot in self.plots_data:
            winning_team = plot['voting_results']['winning_team']
            
            for vote in plot['voting_results']['individual_votes']:
                voter_name = vote['agent_name']
                voted_for = vote['vote_for_team']
                
                stats = voter_stats[voter_name]
                stats['total_votes_cast'] += 1
                stats['team_votes'][voted_for] += 1
                
                # Track accuracy
                if voted_for == winning_team:
                    stats['correct_predictions'] += 1
                
                # Track model usage
                model_used = vote.get('model_used', 'unknown')
                stats['model_usage'][model_used] += 1
                
                # Track criteria scores
                if 'score_breakdown' in vote:
                    for criterion, score in vote['score_breakdown'].items():
                        stats['criteria_scores'][criterion].append(score)
                
                # Track vote history
                stats['vote_history'].append({
                    'genre': plot['genre'],
                    'voted_for': voted_for,
                    'won': voted_for == winning_team,
                    'timestamp': plot['_timestamp']
                })
        
        # Calculate derived statistics
        for voter_name, stats in voter_stats.items():
            if stats['total_votes_cast'] > 0:
                stats['accuracy_rate'] = (stats['correct_predictions'] / stats['total_votes_cast']) * 100
                
                # Calculate average criteria scores
                stats['avg_criteria_scores'] = {}
                for criterion, scores in stats['criteria_scores'].items():
                    if scores:
                        stats['avg_criteria_scores'][criterion] = sum(scores) / len(scores)
                
                # Find favorite team
                if stats['team_votes']:
                    stats['favorite_team'] = max(stats['team_votes'], key=stats['team_votes'].get)
            else:
                stats['accuracy_rate'] = 0
                stats['avg_criteria_scores'] = {}
                stats['favorite_team'] = 'None'
        
        return dict(voter_stats)
    
    def get_voting_patterns(self) -> Dict[str, Any]:
        """Analyze voting patterns and relationships"""
        patterns = {
            'voting_blocs': defaultdict(list),
            'contrarian_voters': [],
            'consensus_voters': [],
            'team_rivalries': defaultdict(lambda: defaultdict(int)),
            'genre_preferences': defaultdict(lambda: defaultdict(int))
        }
        
        # Analyze each plot's voting patterns
        for plot in self.plots_data:
            votes = plot['voting_results']['individual_votes']
            winning_team = plot['voting_results']['winning_team']
            genre = plot['genre']
            
            # Group voters by their choice
            vote_groups = defaultdict(list)
            for vote in votes:
                vote_groups[vote['vote_for_team']].append(vote['agent_name'])
            
            # Track voting blocs (voters who voted together)
            for team, voters in vote_groups.items():
                if len(voters) > 1:
                    for i in range(len(voters)):
                        for j in range(i + 1, len(voters)):
                            bloc_key = tuple(sorted([voters[i], voters[j]]))
                            patterns['voting_blocs'][bloc_key].append({
                                'plot': plot['original_plot'][:50] + '...',
                                'team': team,
                                'genre': genre
                            })
            
            # Track team rivalries (head-to-head performance)
            vote_tally = plot['voting_results']['vote_tally']
            teams = list(vote_tally.keys())
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    if vote_tally[teams[i]] > vote_tally[teams[j]]:
                        patterns['team_rivalries'][teams[i]][teams[j]] += 1
                    elif vote_tally[teams[j]] > vote_tally[teams[i]]:
                        patterns['team_rivalries'][teams[j]][teams[i]] += 1
            
            # Track genre preferences
            for vote in votes:
                patterns['genre_preferences'][vote['agent_name']][genre] += 1
        
        # Identify contrarian and consensus voters
        voter_stats = self.get_voter_stats()
        for voter_name, stats in voter_stats.items():
            if stats['accuracy_rate'] < 30 and stats['total_votes_cast'] >= 5:
                patterns['contrarian_voters'].append({
                    'name': voter_name,
                    'accuracy': stats['accuracy_rate'],
                    'votes_cast': stats['total_votes_cast']
                })
            elif stats['accuracy_rate'] > 70 and stats['total_votes_cast'] >= 5:
                patterns['consensus_voters'].append({
                    'name': voter_name,
                    'accuracy': stats['accuracy_rate'],
                    'votes_cast': stats['total_votes_cast']
                })
        
        # Convert defaultdicts to regular dicts for JSON serialization
        patterns['voting_blocs'] = dict(patterns['voting_blocs'])
        patterns['team_rivalries'] = {k: dict(v) for k, v in patterns['team_rivalries'].items()}
        patterns['genre_preferences'] = {k: dict(v) for k, v in patterns['genre_preferences'].items()}
        
        return patterns
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Calculate system-wide statistics"""
        stats = {
            'total_plots': len(self.plots_data),
            'genres': defaultdict(int),
            'models_used': defaultdict(int),
            'processing_times': [],
            'vote_distributions': [],
            'complexity_distribution': []
        }
        
        for plot in self.plots_data:
            # Genre distribution
            stats['genres'][plot['genre']] += 1
            
            # Processing times
            if 'processing_time' in plot:
                stats['processing_times'].append(plot['processing_time'])
            
            # Vote distributions
            total_votes = plot['voting_results']['total_votes']
            vote_tally = plot['voting_results']['vote_tally']
            if total_votes > 0:
                vote_percentages = [votes/total_votes * 100 for votes in vote_tally.values()]
                stats['vote_distributions'].extend(vote_percentages)
            
            # Model usage across all teams and voters
            for expansion in plot['all_expanded_plots'].values():
                model = expansion.get('model_used', 'unknown')
                stats['models_used'][model] += 1
            
            for vote in plot['voting_results']['individual_votes']:
                model = vote.get('model_used', 'unknown')
                stats['models_used'][model] += 1
            
            # Complexity distribution
            for expansion in plot['all_expanded_plots'].values():
                stats['complexity_distribution'].append(expansion['estimated_complexity'])
        
        # Calculate averages
        if stats['processing_times']:
            stats['avg_processing_time'] = sum(stats['processing_times']) / len(stats['processing_times'])
        else:
            stats['avg_processing_time'] = 0
        
        if stats['complexity_distribution']:
            stats['avg_complexity'] = sum(stats['complexity_distribution']) / len(stats['complexity_distribution'])
        else:
            stats['avg_complexity'] = 0
        
        # Convert defaultdicts
        stats['genres'] = dict(stats['genres'])
        stats['models_used'] = dict(stats['models_used'])
        
        return stats
    
    def get_team_head_to_head(self, team1: str, team2: str) -> Dict[str, Any]:
        """Get head-to-head statistics between two teams"""
        h2h = {
            'team1': team1,
            'team2': team2,
            'total_encounters': 0,
            'team1_wins': 0,
            'team2_wins': 0,
            'vote_comparison': [],
            'genre_breakdown': defaultdict(lambda: {'team1_wins': 0, 'team2_wins': 0, 'encounters': 0})
        }
        
        for plot in self.plots_data:
            if team1 in plot['all_expanded_plots'] and team2 in plot['all_expanded_plots']:
                h2h['total_encounters'] += 1
                
                vote_tally = plot['voting_results']['vote_tally']
                team1_votes = vote_tally.get(team1, 0)
                team2_votes = vote_tally.get(team2, 0)
                
                h2h['vote_comparison'].append({
                    'plot': plot['original_plot'][:50] + '...',
                    'genre': plot['genre'],
                    'team1_votes': team1_votes,
                    'team2_votes': team2_votes,
                    'winner': plot['voting_results']['winning_team']
                })
                
                genre = plot['genre']
                h2h['genre_breakdown'][genre]['encounters'] += 1
                
                if plot['voting_results']['winning_team'] == team1:
                    h2h['team1_wins'] += 1
                    h2h['genre_breakdown'][genre]['team1_wins'] += 1
                elif plot['voting_results']['winning_team'] == team2:
                    h2h['team2_wins'] += 1
                    h2h['genre_breakdown'][genre]['team2_wins'] += 1
        
        # Convert defaultdict
        h2h['genre_breakdown'] = dict(h2h['genre_breakdown'])
        
        return h2h
    
    def get_timeline_data(self) -> List[Dict[str, Any]]:
        """Get data organized by timeline for trend analysis"""
        timeline = []
        
        for plot in self.plots_data:
            timeline.append({
                'timestamp': plot['_timestamp'],
                'genre': plot['genre'],
                'winner': plot['voting_results']['winning_team'],
                'total_votes': plot['voting_results']['total_votes'],
                'processing_time': plot.get('processing_time', 0),
                'vote_distribution': plot['voting_results']['vote_tally']
            })
        
        return timeline
    
    def get_team_league_table(self) -> List[Dict[str, Any]]:
        """Get team league table from league system"""
        return self.league_system.get_team_league_table()
    
    def get_voter_league_table(self) -> List[Dict[str, Any]]:
        """Get voter league table from league system"""
        return self.league_system.get_voter_league_table()
    
    def get_fairness_report(self) -> Dict[str, Any]:
        """Get fairness and bias analysis report"""
        return self.league_system.get_fairness_report()