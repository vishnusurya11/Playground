"""
Team Manager for EpicWeaver
Coordinates expansion teams and voting agents
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import importlib
import asyncio
import time
from config import config
from schemas import ExpandedPlotProposal, VotingResults
from voting_strategies import VotingStrategyFactory


class TeamManager:
    """Manages expansion teams and voting agents"""
    
    def __init__(self, model_config_path: str = "model_teams_config.json"):
        self.model_config = self._load_model_config(model_config_path)
        self.expansion_teams = {}
        self.voting_agents = {}
        self._initialize_teams()
    
    def _load_model_config(self, config_path: str) -> Dict[str, Any]:
        """Load model configuration"""
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _initialize_teams(self):
        """Initialize active teams based on configuration"""
        # Get active teams from config
        active_expansion = config.get_active_teams("expansion")
        active_voting = config.get_active_teams("voting")
        
        # Initialize expansion teams
        for team_key, team_info in active_expansion.items():
            team_name = team_info['name']
            
            # Get model config for this team
            model_config = self._get_team_model_config(team_key, "expansion")
            
            # Create team instance
            try:
                # Add team name to config
                model_config['name'] = team_name
                
                # Dynamic import based on team name
                module_name = team_key  # e.g., 'cosmic_storytellers'
                class_name = ''.join(word.capitalize() for word in team_name.split())  # e.g., 'CosmicStorytellers'
                
                try:
                    # Import the module
                    module = importlib.import_module(f'teams.{module_name}')
                    # Get the class
                    team_class = getattr(module, class_name)
                    # Create instance
                    self.expansion_teams[team_name] = team_class(model_config)
                except (ImportError, AttributeError) as e:
                    print(f"Warning: Could not load team {team_name} from teams.{module_name}: {e}")
                    
            except Exception as e:
                print(f"Error initializing team {team_name}: {e}")
        
        # Initialize voting agents
        for voter_key, voter_info in active_voting.items():
            voter_name = voter_info['name']
            
            # Get model config for this voter
            model_config = self._get_voter_model_config(voter_name, "voting")
            
            # Create voter instance
            try:
                # Add voter name to config
                model_config['name'] = voter_name
                
                # Dynamic import based on voter name
                module_name = voter_key  # e.g., 'the_curator'
                # Handle "The Curator" -> "TheCurator" properly
                class_name = voter_name.replace(' ', '')  # e.g., 'TheCurator'
                
                try:
                    # Import the module
                    module = importlib.import_module(f'voters.{module_name}')
                    # Get the class
                    voter_class = getattr(module, class_name)
                    # Create instance
                    voter_instance = voter_class(model_config)
                    self.voting_agents[voter_name] = voter_instance
                    print(f"✓ Initialized voter: {voter_name}")
                except (ImportError, AttributeError) as e:
                    # Fallback to base voter
                    print(f"⚠ Could not load voter {voter_name} (module: {module_name}, class: {class_name}): {e}")
                    print(f"  Using BaseVoter fallback for {voter_name}")
                    from voters.base_voter import BaseVoter
                    fallback_voter = BaseVoter(model_config)
                    self.voting_agents[voter_name] = fallback_voter
                
            except Exception as e:
                print(f"Error initializing voter {voter_name}: {e}")
                # Skip this voter
                continue
    
    def _get_team_model_config(self, team_key: str, team_type: str) -> Dict[str, Any]:
        """Get model configuration for a team"""
        # Try to get from model_teams_config.json
        if team_type == "expansion" and "expansion_teams" in self.model_config:
            for config_key, config_data in self.model_config["expansion_teams"].items():
                if config_data.get("name", "") in team_key or team_key in config_key:
                    return config_data
        
        # Default config
        return {
            "model_name": "gpt-4o-mini-2024-07-18",
            "temperature": 0.7
        }
    
    def _get_voter_model_config(self, voter_key: str, team_type: str) -> Dict[str, Any]:
        """Get model configuration for a voter"""
        # Try to get from model_teams_config.json
        if "voting_council" in self.model_config:
            for config_key, config_data in self.model_config["voting_council"].items():
                # Match by name
                if config_data.get("name", "") == voter_key:
                    return config_data
        
        # Default config
        return {
            "model_name": "gpt-4o-mini-2024-07-18",
            "temperature": 0.3,
            "voting_criteria_weights": {
                "originality": 0.15,
                "coherence": 0.15,
                "market_potential": 0.15,
                "character_depth": 0.15,
                "thematic_richness": 0.15,
                "expandability": 0.25
            }
        }
    
    def expand_plot(self, genre: str, plot: str) -> Dict[str, ExpandedPlotProposal]:
        """Have all teams expand the plot"""
        expansions = {}
        
        for team_name, team in self.expansion_teams.items():
            print(f"Team {team_name} is expanding the plot...")
            try:
                expansion = team.expand_plot(genre, plot)
                expansions[team_name] = expansion
            except Exception as e:
                print(f"Error in {team_name} expansion: {e}")
        
        return expansions
    
    async def _retry_with_backoff(self, coro_func, team_name: str, *args, **kwargs):
        """Retry async function with exponential backoff on connection errors"""
        retry_config = config.get_async_retry_config()
        
        if not retry_config.get('enabled', True):
            # Retries disabled, just run once
            return await coro_func(*args, **kwargs)
        
        max_retries = retry_config.get('max_retries', 3)
        backoff_factor = retry_config.get('backoff_factor', 2.0)
        initial_delay = retry_config.get('initial_delay', 1.0)
        retry_on_errors = retry_config.get('retry_on_errors', ['ConnectionError', 'TimeoutError'])
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await coro_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_str = str(e)
                error_type = type(e).__name__
                
                # Check if this is a retryable error
                is_retryable = any(
                    err in error_str or err in error_type 
                    for err in retry_on_errors
                )
                
                if is_retryable and attempt < max_retries:
                    delay = initial_delay * (backoff_factor ** attempt)
                    print(f"⚠️  {team_name} connection error (attempt {attempt + 1}/{max_retries + 1}): {error_type}")
                    print(f"   Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    # Not retryable or max retries reached
                    raise
        
        # Should not reach here, but just in case
        raise last_exception
    
    async def expand_plot_async(self, genre: str, plot: str) -> Dict[str, ExpandedPlotProposal]:
        """Parallel team expansion - all teams at once with retry logic"""
        tasks = []
        for team_name, team in self.expansion_teams.items():
            # Check if team has async method, otherwise run sync in thread
            if hasattr(team, 'expand_plot_async'):
                # Wrap async method with retry logic
                task = self._retry_with_backoff(team.expand_plot_async, team_name, genre, plot)
            else:
                # For sync methods, we can't retry as easily, just run in thread
                task = asyncio.to_thread(team.expand_plot, genre, plot)
            tasks.append((team_name, task))
        
        # Run all teams in parallel
        print(f"Running {len(tasks)} teams in parallel...")
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Build expansions dict
        expansions = {}
        fallback_count = 0
        
        for (team_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                print(f"❌ {team_name} failed after retries: {result}")
                # Try sync fallback as last resort
                team = self.expansion_teams[team_name]
                if hasattr(team, 'expand_plot'):
                    try:
                        print(f"   Attempting sync fallback for {team_name}...")
                        expansion = await asyncio.to_thread(team.expand_plot, genre, plot)
                        expansions[team_name] = expansion
                        print(f"   ✓ {team_name} sync fallback succeeded")
                        fallback_count += 1
                    except Exception as e2:
                        print(f"   ❌ {team_name} sync fallback also failed: {e2}")
            else:
                expansions[team_name] = result
                print(f"✓ {team_name} completed")
        
        if fallback_count > 0:
            print(f"ℹ️  {fallback_count} teams used sync fallback after async failures")
        
        return expansions
    
    def conduct_voting(self, 
                      expansions: Dict[str, ExpandedPlotProposal],
                      voting_strategy: str = "standard") -> VotingResults:
        """Conduct voting using specified strategy"""
        
        # Get voting strategy
        strategy = VotingStrategyFactory.create(voting_strategy)
        
        # Get list of voting agents
        voting_agent_list = list(self.voting_agents.values())
        
        # Ensure odd number of voters if configured
        if config.get_team_count_limits().get("require_odd_voters", True):
            if len(voting_agent_list) % 2 == 0 and len(voting_agent_list) > 1:
                print(f"Adjusting to odd number of voters ({len(voting_agent_list)} -> {len(voting_agent_list) - 1})")
                voting_agent_list = voting_agent_list[:-1]
        
        print(f"\nVoting council of {len(voting_agent_list)} agents is evaluating expansions...")
        
        # Conduct voting
        return strategy.conduct_voting(expansions, voting_agent_list)
    
    async def conduct_voting_async(self, 
                                  expansions: Dict[str, ExpandedPlotProposal],
                                  voting_strategy: str = "standard") -> VotingResults:
        """Parallel voting - all voters at once"""
        # Get voting strategy
        strategy = VotingStrategyFactory.create(voting_strategy)
        
        # Get list of voting agents
        voting_agent_list = list(self.voting_agents.values())
        
        # Ensure odd number of voters if configured
        if config.get_team_count_limits().get("require_odd_voters", True):
            if len(voting_agent_list) % 2 == 0 and len(voting_agent_list) > 1:
                print(f"Adjusting to odd number of voters ({len(voting_agent_list)} -> {len(voting_agent_list) - 1})")
                voting_agent_list = voting_agent_list[:-1]
        
        print(f"\nVoting council of {len(voting_agent_list)} agents evaluating (in parallel)...")
        
        # Check if strategy has async support
        if hasattr(strategy, 'conduct_voting_async'):
            return await strategy.conduct_voting_async(expansions, voting_agent_list)
        else:
            # Fallback: run sync strategy in thread
            return await asyncio.to_thread(strategy.conduct_voting, expansions, voting_agent_list)
    
    def get_team_count(self) -> Dict[str, int]:
        """Get current team counts"""
        return {
            "expansion_teams": len(self.expansion_teams),
            "voting_agents": len(self.voting_agents)
        }
    
    def get_team_info(self) -> Dict[str, List[str]]:
        """Get information about active teams"""
        return {
            "expansion_teams": list(self.expansion_teams.keys()),
            "voting_agents": list(self.voting_agents.keys())
        }