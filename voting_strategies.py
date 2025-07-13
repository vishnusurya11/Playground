"""
Voting strategies for EpicWeaver
Pluggable voting implementations to allow future improvements
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from schemas import ExpandedPlotProposal, VotingResults, VotingResult
from collections import defaultdict
import asyncio


class VotingStrategy(ABC):
    """Abstract base class for voting strategies"""
    
    @abstractmethod
    def conduct_voting(self, 
                      expansions: Dict[str, ExpandedPlotProposal], 
                      voting_agents: List[Any]) -> VotingResults:
        """Conduct voting and return results"""
        pass


class StandardVoting(VotingStrategy):
    """Standard voting where each agent gets one vote"""
    
    def conduct_voting(self, 
                      expansions: Dict[str, ExpandedPlotProposal], 
                      voting_agents: List[Any]) -> VotingResults:
        """Each agent votes once, majority wins"""
        
        # Try async voting if available
        try:
            import asyncio
            return asyncio.run(self._conduct_voting_async(expansions, voting_agents))
        except Exception as e:
            print(f"Async voting not available ({e}), using standard voting...")
            return self._conduct_voting_sync(expansions, voting_agents)
    
    async def _conduct_voting_async(self, 
                                   expansions: Dict[str, ExpandedPlotProposal], 
                                   voting_agents: List[Any]) -> VotingResults:
        """Async version - conduct voting in parallel"""
        
        vote_tally = {team_name: 0 for team_name in expansions.keys()}
        
        # Prepare voting tasks
        print(f"\nCollecting votes from {len(voting_agents)} agents (async parallel)...")
        tasks = []
        for i, agent in enumerate(voting_agents, 1):
            if hasattr(agent, 'vote_async'):
                task = agent.vote_async(expansions)
            else:
                # Fallback to sync in thread
                task = asyncio.to_thread(agent.vote, expansions)
            tasks.append((i, agent.name, task))
        
        # Execute all voting tasks in parallel
        results = await asyncio.gather(*[task for _, _, task in tasks], return_exceptions=True)
        
        # Process results
        votes = []
        for (i, agent_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"    ❌ Error getting vote from {agent_name}: {result}")
            else:
                vote = result
                if vote.vote_for_team in vote_tally:
                    vote_tally[vote.vote_for_team] += 1
                    votes.append(vote)
                    print(f"    ✓ {agent_name} voted for: {vote.vote_for_team}")
                else:
                    print(f"    ⚠ {agent_name} voted for invalid team: {vote.vote_for_team}")
                    print(f"      Valid teams: {list(vote_tally.keys())}")
        
        print(f"  Collected {len(votes)} votes successfully")
        
        # Determine winner
        winning_team = max(vote_tally, key=vote_tally.get)
        
        # Handle ties by looking at total scores
        tied_teams = [team for team, count in vote_tally.items() if count == vote_tally[winning_team]]
        if len(tied_teams) > 1:
            winning_team = self._break_tie(tied_teams, votes)
        
        # Generate voting summary
        voting_summary = self._generate_voting_summary(votes, vote_tally, expansions)
        
        return VotingResults(
            individual_votes=votes,
            vote_tally=vote_tally,
            winning_team=winning_team,
            total_votes=len(votes),
            voting_summary=voting_summary
        )
    
    def _conduct_voting_sync(self, 
                            expansions: Dict[str, ExpandedPlotProposal], 
                            voting_agents: List[Any]) -> VotingResults:
        """Sync version - original sequential voting"""
        
        votes = []
        vote_tally = {team_name: 0 for team_name in expansions.keys()}
        
        # Collect votes from all agents
        print(f"\nCollecting votes from {len(voting_agents)} agents...")
        for i, agent in enumerate(voting_agents, 1):
            try:
                print(f"  [{i}/{len(voting_agents)}] {agent.name} is voting...")
                vote = agent.vote(expansions)
                if vote.vote_for_team in vote_tally:
                    vote_tally[vote.vote_for_team] += 1
                    votes.append(vote)
                    print(f"    ✓ {agent.name} voted for: {vote.vote_for_team}")
                else:
                    print(f"    ⚠ {agent.name} voted for invalid team: {vote.vote_for_team}")
                    print(f"      Valid teams: {list(vote_tally.keys())}")
            except Exception as e:
                print(f"    ❌ Error getting vote from {agent.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Determine winner
        winning_team = max(vote_tally, key=vote_tally.get)
        
        # Handle ties by looking at total scores
        tied_teams = [team for team, count in vote_tally.items() if count == vote_tally[winning_team]]
        if len(tied_teams) > 1:
            winning_team = self._break_tie(tied_teams, votes)
        
        # Generate voting summary
        voting_summary = self._generate_voting_summary(votes, vote_tally, expansions)
        
        return VotingResults(
            individual_votes=votes,
            vote_tally=vote_tally,
            winning_team=winning_team,
            total_votes=len(votes),
            voting_summary=voting_summary
        )
    
    def _break_tie(self, tied_teams: List[str], votes: List[VotingResult]) -> str:
        """Break tie by total scores"""
        team_scores = {team: 0 for team in tied_teams}
        for vote in votes:
            if vote.vote_for_team in tied_teams:
                team_scores[vote.vote_for_team] += sum(vote.score_breakdown.values())
        return max(team_scores, key=team_scores.get)
    
    def _generate_voting_summary(self, votes: List[VotingResult], vote_tally: Dict[str, int], 
                                expanded_plots: Dict[str, ExpandedPlotProposal]) -> Dict[str, Any]:
        """Generate comprehensive voting summary"""
        
        # Vote distribution
        vote_distribution = dict(sorted(vote_tally.items(), key=lambda x: x[1], reverse=True))
        
        # Agent-by-agent breakdown
        agent_votes = {}
        for vote in votes:
            agent_votes[vote.agent_name] = {
                "voted_for": vote.vote_for_team,
                "model_used": vote.model_used,
                "total_score": sum(vote.score_breakdown.values())
            }
        
        # Team average scores
        team_scores_detail = defaultdict(lambda: defaultdict(list))
        for vote in votes:
            if vote.vote_for_team in expanded_plots:
                for criterion, score in vote.score_breakdown.items():
                    team_scores_detail[vote.vote_for_team][criterion].append(score)
        
        # Calculate averages
        team_avg_scores = {}
        for team, criteria_scores in team_scores_detail.items():
            team_avg_scores[team] = {}
            for criterion, scores in criteria_scores.items():
                team_avg_scores[team][criterion] = round(sum(scores) / len(scores), 1) if scores else 0
            # Add total average
            all_scores = [score for scores in criteria_scores.values() for score in scores]
            team_avg_scores[team]["total_avg"] = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
        
        # Voting patterns
        model_preferences = defaultdict(lambda: defaultdict(int))
        criteria_scores_all = defaultdict(list)
        
        for vote in votes:
            model_preferences[vote.model_used][vote.vote_for_team] += 1
            for criterion, score in vote.score_breakdown.items():
                criteria_scores_all[criterion].append(score)
        
        # Find unanimous and divisive criteria
        criteria_variance = {}
        for criterion, scores in criteria_scores_all.items():
            if scores:
                avg = sum(scores) / len(scores)
                variance = sum((s - avg) ** 2 for s in scores) / len(scores)
                criteria_variance[criterion] = variance
        
        sorted_criteria = sorted(criteria_variance.items(), key=lambda x: x[1])
        unanimous_criteria = [c[0] for c in sorted_criteria[:2]] if len(sorted_criteria) >= 2 else []
        divisive_criteria = [c[0] for c in sorted_criteria[-2:]] if len(sorted_criteria) >= 2 else []
        
        return {
            "vote_distribution": vote_distribution,
            "agent_votes": agent_votes,
            "team_avg_scores": team_avg_scores,
            "voting_patterns": {
                "unanimous_criteria": unanimous_criteria,
                "most_divisive_criteria": divisive_criteria,
                "model_preferences": dict(model_preferences)
            },
            "vote_reasons": {
                vote.agent_name: vote.reasoning[:200] + "..." 
                for vote in votes
            }
        }


class RankedChoiceVoting(VotingStrategy):
    """Ranked choice voting strategy (future implementation)"""
    
    def conduct_voting(self, 
                      expansions: Dict[str, ExpandedPlotProposal], 
                      voting_agents: List[Any]) -> VotingResults:
        """Ranked choice voting - each agent ranks all options"""
        # Future implementation
        # For now, fall back to standard voting
        print("Ranked choice voting not yet implemented, using standard voting")
        return StandardVoting().conduct_voting(expansions, voting_agents)


class WeightedVoting(VotingStrategy):
    """Weighted voting based on agent expertise (future implementation)"""
    
    def conduct_voting(self, 
                      expansions: Dict[str, ExpandedPlotProposal], 
                      voting_agents: List[Any]) -> VotingResults:
        """Weighted voting - votes have different weights based on expertise"""
        # Future implementation
        # For now, fall back to standard voting
        print("Weighted voting not yet implemented, using standard voting")
        return StandardVoting().conduct_voting(expansions, voting_agents)


# Factory for voting strategies
class VotingStrategyFactory:
    """Factory for creating voting strategies"""
    
    _strategies = {
        "standard": StandardVoting,
        "ranked_choice": RankedChoiceVoting,
        "weighted": WeightedVoting
    }
    
    @classmethod
    def create(cls, strategy_name: str = "standard") -> VotingStrategy:
        """Create a voting strategy by name"""
        strategy_class = cls._strategies.get(strategy_name, StandardVoting)
        return strategy_class()
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """Register a new voting strategy"""
        cls._strategies[name] = strategy_class