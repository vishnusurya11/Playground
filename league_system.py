"""
EpicWeaver League System - Competitive rankings with anti-bias mechanisms
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, deque
import statistics


class LeagueSystem:
    """Manages competitive league tables for teams and voters"""
    
    def __init__(self, league_file: str = "league_tables.json"):
        self.league_file = Path(league_file)
        self.league_data = self._load_league_data()
        
        # Configuration
        self.config = {
            "active_team_slots": 5,
            "active_voter_slots": 11,
            "points_for_win": 3,
            "points_for_second": 1,
            "min_participations": 3,
            "form_window": 5,
            "bias_threshold": 0.6,
            "consensus_bonus": 1
        }
    
    def _load_league_data(self) -> Dict[str, Any]:
        """Load existing league data or create new"""
        if self.league_file.exists():
            with open(self.league_file, 'r') as f:
                return json.load(f)
        
        return {
            "teams": {},
            "voters": {},
            "history": [],
            "season": 1,
            "last_updated": datetime.now().isoformat()
        }
    
    def save_league_data(self):
        """Save league data to file"""
        self.league_data["last_updated"] = datetime.now().isoformat()
        with open(self.league_file, 'w') as f:
            json.dump(self.league_data, f, indent=2)
    
    def update_team_result(self, plot_id: str, results: Dict[str, Any]):
        """Update team standings based on plot results"""
        vote_tally = results['vote_tally']
        winning_team = results['winning_team']
        
        # Sort teams by votes
        sorted_teams = sorted(vote_tally.items(), key=lambda x: x[1], reverse=True)
        
        # Award points
        for position, (team_name, votes) in enumerate(sorted_teams):
            if team_name not in self.league_data["teams"]:
                self.league_data["teams"][team_name] = self._create_team_entry(team_name)
            
            team = self.league_data["teams"][team_name]
            team["played"] += 1
            team["votes_for"] += votes
            team["votes_against"] += sum(vote_tally.values()) - votes
            
            # Points and position tracking
            if position == 0:  # Winner
                team["won"] += 1
                team["points"] += self.config["points_for_win"]
                team["form"].append("W")
            elif position == 1:  # Second place
                team["second"] += 1
                team["points"] += self.config["points_for_second"]
                team["form"].append("S")
            else:
                team["form"].append("L")
            
            # Keep form window size
            if len(team["form"]) > self.config["form_window"]:
                team["form"].pop(0)
            
            # Track vote sources for bias detection
            team["vote_sources"].append({
                "plot_id": plot_id,
                "voters": self._extract_voter_list(results)
            })
    
    def update_voter_result(self, plot_id: str, results: Dict[str, Any]):
        """Update voter standings based on voting accuracy"""
        winning_team = results['winning_team']
        vote_tally = results['vote_tally']
        sorted_teams = sorted(vote_tally.items(), key=lambda x: x[1], reverse=True)
        second_team = sorted_teams[1][0] if len(sorted_teams) > 1 else None
        
        # Track vote distribution for consensus
        vote_distribution = defaultdict(list)
        for vote in results['individual_votes']:
            vote_distribution[vote['vote_for_team']].append(vote['agent_name'])
        
        # Find majority vote
        majority_team = max(vote_distribution.keys(), key=lambda k: len(vote_distribution[k]))
        is_consensus = len(vote_distribution[majority_team]) > len(results['individual_votes']) / 2
        
        for vote in results['individual_votes']:
            voter_name = vote['agent_name']
            voted_for = vote['vote_for_team']
            
            if voter_name not in self.league_data["voters"]:
                self.league_data["voters"][voter_name] = self._create_voter_entry(voter_name)
            
            voter = self.league_data["voters"][voter_name]
            voter["votes_cast"] += 1
            
            # Award points based on accuracy
            if voted_for == winning_team:
                voter["correct_votes"] += 1
                voter["points"] += self.config["points_for_win"]
                voter["form"].append("C")  # Correct
                
                # Consensus bonus
                if is_consensus and voted_for == majority_team:
                    voter["points"] += self.config["consensus_bonus"]
                    voter["consensus_votes"] += 1
            elif voted_for == second_team:
                voter["points"] += self.config["points_for_second"]
                voter["form"].append("N")  # Near miss
            else:
                voter["form"].append("W")  # Wrong
            
            # Keep form window size
            if len(voter["form"]) > self.config["form_window"]:
                voter["form"].pop(0)
            
            # Track voting patterns for bias detection
            voter["team_preferences"][voted_for] = voter["team_preferences"].get(voted_for, 0) + 1
            
            # Update accuracy rate
            if voter["votes_cast"] > 0:
                voter["accuracy_rate"] = (voter["correct_votes"] / voter["votes_cast"]) * 100
    
    def calculate_bias_scores(self) -> Dict[str, Dict[str, float]]:
        """Calculate bias scores for teams and voters"""
        bias_scores = {"teams": {}, "voters": {}}
        
        # Team bias: How concentrated are their vote sources?
        for team_name, team_data in self.league_data["teams"].items():
            if team_data["played"] >= self.config["min_participations"]:
                voter_frequency = defaultdict(int)
                total_votes = 0
                
                for plot in team_data["vote_sources"]:
                    for voter in plot["voters"]:
                        voter_frequency[voter] += 1
                        total_votes += 1
                
                # Calculate concentration (Herfindahl index)
                if total_votes > 0:
                    concentration = sum((count/total_votes)**2 for count in voter_frequency.values())
                    bias_scores["teams"][team_name] = round(concentration, 3)
                else:
                    bias_scores["teams"][team_name] = 0.0
        
        # Voter bias: How concentrated are their team preferences?
        for voter_name, voter_data in self.league_data["voters"].items():
            if voter_data["votes_cast"] >= self.config["min_participations"]:
                total_votes = voter_data["votes_cast"]
                preferences = voter_data["team_preferences"]
                
                # Calculate preference concentration
                if total_votes > 0:
                    concentration = sum((count/total_votes)**2 for count in preferences.values())
                    bias_scores["voters"][voter_name] = round(concentration, 3)
                else:
                    bias_scores["voters"][voter_name] = 0.0
        
        return bias_scores
    
    def get_team_league_table(self) -> List[Dict[str, Any]]:
        """Generate sorted team league table"""
        bias_scores = self.calculate_bias_scores()
        
        table = []
        for team_name, team_data in self.league_data["teams"].items():
            if team_data["played"] >= self.config["min_participations"]:
                # Calculate additional metrics
                vote_difference = team_data["votes_for"] - team_data["votes_against"]
                win_rate = (team_data["won"] / team_data["played"] * 100) if team_data["played"] > 0 else 0
                
                table.append({
                    "name": team_name,
                    "played": team_data["played"],
                    "won": team_data["won"],
                    "second": team_data["second"],
                    "points": team_data["points"],
                    "votes_for": team_data["votes_for"],
                    "votes_against": team_data["votes_against"],
                    "vote_difference": vote_difference,
                    "win_rate": round(win_rate, 1),
                    "form": "".join(team_data["form"][-self.config["form_window"]:]),
                    "bias_score": bias_scores["teams"].get(team_name, 0.0),
                    "last_position": team_data.get("last_position", 0)
                })
        
        # Sort by points, then vote difference
        table.sort(key=lambda x: (x["points"], x["vote_difference"]), reverse=True)
        
        # Update positions and status
        for position, team in enumerate(table, 1):
            team["position"] = position
            team["status"] = "active" if position <= self.config["active_team_slots"] else "bench"
            
            # Position change indicator
            if team["last_position"] == 0:
                team["position_change"] = "new"
            elif team["last_position"] > position:
                team["position_change"] = "up"
            elif team["last_position"] < position:
                team["position_change"] = "down"
            else:
                team["position_change"] = "same"
            
            # Update last position for next time
            self.league_data["teams"][team["name"]]["last_position"] = position
        
        return table
    
    def get_voter_league_table(self) -> List[Dict[str, Any]]:
        """Generate sorted voter league table"""
        bias_scores = self.calculate_bias_scores()
        
        table = []
        for voter_name, voter_data in self.league_data["voters"].items():
            if voter_data["votes_cast"] >= self.config["min_participations"]:
                # Calculate influence score (how often in winning coalition)
                influence = (voter_data["consensus_votes"] / voter_data["votes_cast"] * 100) if voter_data["votes_cast"] > 0 else 0
                
                table.append({
                    "name": voter_name,
                    "votes_cast": voter_data["votes_cast"],
                    "correct_votes": voter_data["correct_votes"],
                    "points": voter_data["points"],
                    "accuracy_rate": round(voter_data["accuracy_rate"], 1),
                    "influence_score": round(influence, 1),
                    "consensus_votes": voter_data["consensus_votes"],
                    "form": "".join(voter_data["form"][-self.config["form_window"]:]),
                    "bias_score": bias_scores["voters"].get(voter_name, 0.0),
                    "last_position": voter_data.get("last_position", 0)
                })
        
        # Sort by points, then accuracy
        table.sort(key=lambda x: (x["points"], x["accuracy_rate"]), reverse=True)
        
        # Update positions and status
        for position, voter in enumerate(table, 1):
            voter["position"] = position
            voter["status"] = "active" if position <= self.config["active_voter_slots"] else "bench"
            
            # Position change indicator
            if voter["last_position"] == 0:
                voter["position_change"] = "new"
            elif voter["last_position"] > position:
                voter["position_change"] = "up"
            elif voter["last_position"] < position:
                voter["position_change"] = "down"
            else:
                voter["position_change"] = "same"
            
            # Update last position
            self.league_data["voters"][voter["name"]]["last_position"] = position
        
        return table
    
    def get_fairness_report(self) -> Dict[str, Any]:
        """Generate fairness and bias analysis report"""
        bias_scores = self.calculate_bias_scores()
        
        # Find potential bias issues
        biased_teams = {k: v for k, v in bias_scores["teams"].items() 
                       if v > self.config["bias_threshold"]}
        biased_voters = {k: v for k, v in bias_scores["voters"].items() 
                        if v > self.config["bias_threshold"]}
        
        # Analyze voting coalitions
        coalitions = self._detect_voting_coalitions()
        
        return {
            "biased_teams": biased_teams,
            "biased_voters": biased_voters,
            "voting_coalitions": coalitions,
            "overall_fairness_score": self._calculate_overall_fairness(),
            "recommendations": self._generate_fairness_recommendations(biased_teams, biased_voters)
        }
    
    def _create_team_entry(self, team_name: str) -> Dict[str, Any]:
        """Create new team entry"""
        return {
            "name": team_name,
            "played": 0,
            "won": 0,
            "second": 0,
            "points": 0,
            "votes_for": 0,
            "votes_against": 0,
            "form": [],
            "vote_sources": [],
            "last_position": 0,
            "joined_date": datetime.now().isoformat()
        }
    
    def _create_voter_entry(self, voter_name: str) -> Dict[str, Any]:
        """Create new voter entry"""
        return {
            "name": voter_name,
            "votes_cast": 0,
            "correct_votes": 0,
            "points": 0,
            "accuracy_rate": 0.0,
            "consensus_votes": 0,
            "form": [],
            "team_preferences": {},
            "last_position": 0,
            "joined_date": datetime.now().isoformat()
        }
    
    def _extract_voter_list(self, results: Dict[str, Any]) -> List[str]:
        """Extract list of voters who voted for each team"""
        voter_list = []
        for vote in results['individual_votes']:
            voter_list.append(vote['agent_name'])
        return voter_list
    
    def _detect_voting_coalitions(self) -> List[Dict[str, Any]]:
        """Detect potential voting coalitions or patterns"""
        coalitions = []
        
        # Analyze voter pairs that frequently vote together
        voter_pairs = defaultdict(int)
        total_plots = len(self.league_data.get("history", []))
        
        if total_plots > 5:  # Need sufficient data
            # Implementation for coalition detection
            # This is a placeholder for more sophisticated analysis
            pass
        
        return coalitions
    
    def _calculate_overall_fairness(self) -> float:
        """Calculate overall system fairness score (0-100)"""
        bias_scores = self.calculate_bias_scores()
        
        # Average bias across all participants
        all_biases = list(bias_scores["teams"].values()) + list(bias_scores["voters"].values())
        
        if all_biases:
            avg_bias = statistics.mean(all_biases)
            # Convert to fairness score (inverse of bias)
            fairness = (1 - avg_bias) * 100
            return round(fairness, 1)
        
        return 100.0  # Perfect fairness if no data
    
    def _generate_fairness_recommendations(self, biased_teams: Dict, biased_voters: Dict) -> List[str]:
        """Generate recommendations to improve fairness"""
        recommendations = []
        
        if biased_teams:
            recommendations.append(f"⚠️ {len(biased_teams)} teams show high vote concentration. Consider anonymous voting.")
        
        if biased_voters:
            recommendations.append(f"⚠️ {len(biased_voters)} voters show strong team preferences. Implement vote rotation.")
        
        if not recommendations:
            recommendations.append("✅ System shows good fairness. No immediate concerns.")
        
        return recommendations