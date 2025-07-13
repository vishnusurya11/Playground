"""
Configuration system for EpicWeaver
Centralized configuration for file naming and system settings
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


# File naming configuration
FILE_NAME_CONFIG = {
    "template": "plot_{genre}_{hash}_{timestamp}.json",
    "timestamp_format": "%Y-%m-%dT%H-%M-%S.%f",
    "hash_length": 16,  # Number of digits for the hash
    "output_directory": "forge"
}


# System configuration
SYSTEM_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1.0,  # seconds
    "default_temperature": 0.7,
    "voting_temperature": 0.3,
    "cache_models": True,
    "verbose_logging": True
}


# Model fallback configuration
MODEL_FALLBACKS = {
    "gpt-4.1-nano-2025-04-14": "gpt-4o-mini-2024-07-18",
    "gpt-4.1-mini-2025-04-14": "gpt-4o-mini-2024-07-18",
    "gpt-4.1-2025-04-14": "gpt-4o-2024-08-06",
    "o3-mini-2025-01-31": "o1-mini-2024-09-12",
    "o4-mini-2025-04-16": "o1-mini-2024-09-12",
    "o3-2025-04-16": "gpt-4o-2024-08-06",
}


# Team configurations with better names
TEAM_CONFIG = {
    "expansion_teams": {
        # Active teams (set active: true to use)
        "cosmic_storytellers": {
            "name": "Cosmic Storytellers",
            "active": True,
            "description": "Masters of expansive, universe-spanning narratives"
        },
        "neural_narratives": {
            "name": "Neural Narratives", 
            "active": True,
            "description": "AI-inspired structural innovators"
        },
        "quantum_plotters": {
            "name": "Quantum Plotters",
            "active": True,
            "description": "Masters of interconnected, multi-layered plots"
        },
        "mythic_forge": {
            "name": "Mythic Forge",
            "active": True,
            "description": "Transformative genre-blending alchemists"
        },
        "echo_chamber": {
            "name": "Echo Chamber",
            "active": True,
            "description": "Surreal, psychologically resonant storytellers"
        },
        # Additional teams (set active: true to enable)
        "temporal_weavers": {
            "name": "Temporal Weavers",
            "active": False,
            "description": "Time-bending narrative specialists"
        },
        "shadow_syndicate": {
            "name": "Shadow Syndicate",
            "active": False,
            "description": "Dark, noir-inspired storytellers"
        }
    },
    "voting_council": {
        # Active voters (set active: true to use)
        "the_curator": {
            "name": "The Curator",
            "active": True,
            "description": "Literary excellence and artistic vision"
        },
        "genre_maven": {
            "name": "Genre Maven",
            "active": True,
            "description": "Genre conventions and innovation"
        },
        "mind_reader": {
            "name": "Mind Reader",
            "active": True,
            "description": "Character psychology and authenticity"
        },
        "trend_prophet": {
            "name": "Trend Prophet",
            "active": True,
            "description": "Market potential and reader appeal"
        },
        "architect_prime": {
            "name": "Architect Prime",
            "active": True,
            "description": "Story structure and pacing"
        },
        "wisdom_keeper": {
            "name": "Wisdom Keeper",
            "active": True,
            "description": "Thematic depth and meaning"
        },
        "pulse_checker": {
            "name": "Pulse Checker",
            "active": True,
            "description": "Reader experience and engagement"
        },
        # Additional voters (set active: true to enable)
        "edge_walker": {
            "name": "Edge Walker",
            "active": True,
            "description": "Experimental and boundary-pushing narratives"
        },
        "time_sage": {
            "name": "Time Sage",
            "active": True,
            "description": "Pacing and temporal flow mastery"
        },
        "voice_whisperer": {
            "name": "Voice Whisperer",
            "active": True,
            "description": "Dialogue authenticity and narrative voice"
        },
        "world_builder": {
            "name": "World Builder",
            "active": True,
            "description": "Setting, atmosphere, and world consistency"
        }
    },
    # Configuration for team counts
    "team_settings": {
        "min_expansion_teams": 3,
        "max_expansion_teams": 10,
        "min_voting_agents": 3,
        "max_voting_agents": 15,
        "require_odd_voters": True  # Ensure odd number for tie-breaking
    },
    # Async retry configuration
    "async_retry": {
        "enabled": True,
        "max_retries": 3,
        "backoff_factor": 2.0,  # Exponential backoff: 1s, 2s, 4s
        "initial_delay": 1.0,   # Initial retry delay in seconds
        "retry_on_errors": [
            "ConnectionError",
            "TimeoutError", 
            "ClientConnectorError",
            "ServerDisconnectedError",
            "Connection aborted",
            "Connection reset"
        ]
    }
}


# Voting criteria configuration
VOTING_CRITERIA = {
    "originality": {
        "weight": 0.15,
        "description": "How unique and fresh is the concept?"
    },
    "coherence": {
        "weight": 0.15,
        "description": "How well does the plot hold together?"
    },
    "market_potential": {
        "weight": 0.15,
        "description": "Will readers want to read this?"
    },
    "character_depth": {
        "weight": 0.15,
        "description": "Are the characters compelling?"
    },
    "thematic_richness": {
        "weight": 0.15,
        "description": "Does it explore meaningful themes?"
    },
    "expandability": {
        "weight": 0.25,
        "description": "Can this sustain a 100k+ word novel?"
    }
}


class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.custom_config = {}
        if config_file and Path(config_file).exists():
            self.load_custom_config()
    
    def load_custom_config(self):
        """Load custom configuration from file"""
        with open(self.config_file, 'r') as f:
            self.custom_config = json.load(f)
    
    def get_file_name(self, genre: str, plot: str) -> str:
        """Generate filename based on configuration"""
        template = self.custom_config.get('file_name_template', FILE_NAME_CONFIG['template'])
        timestamp = datetime.now().strftime(FILE_NAME_CONFIG['timestamp_format'])
        plot_hash = str(abs(hash(plot)))[:FILE_NAME_CONFIG['hash_length']]
        
        return template.format(
            genre=genre.lower().replace(' ', '_'),
            hash=plot_hash,
            timestamp=timestamp
        )
    
    def get_output_directory(self) -> Path:
        """Get output directory path"""
        dir_name = self.custom_config.get('output_directory', FILE_NAME_CONFIG['output_directory'])
        return Path(dir_name)
    
    def get_system_config(self, key: str, default: Any = None) -> Any:
        """Get system configuration value"""
        return self.custom_config.get(key, SYSTEM_CONFIG.get(key, default))
    
    def get_model_fallback(self, model_name: str) -> Optional[str]:
        """Get fallback model for a given model name"""
        return self.custom_config.get('model_fallbacks', {}).get(
            model_name, 
            MODEL_FALLBACKS.get(model_name)
        )
    
    def get_active_teams(self, team_type: str) -> Dict[str, Dict[str, Any]]:
        """Get active teams by type"""
        if team_type == "expansion":
            teams = self.custom_config.get('expansion_teams', TEAM_CONFIG['expansion_teams'])
            return {k: v for k, v in teams.items() if v.get('active', True)}
        elif team_type == "voting":
            council = self.custom_config.get('voting_council', TEAM_CONFIG['voting_council'])
            return {k: v for k, v in council.items() if v.get('active', True)}
        return {}
    
    def get_team_count_limits(self) -> Dict[str, int]:
        """Get team count configuration"""
        settings = self.custom_config.get('team_settings', TEAM_CONFIG.get('team_settings', {}))
        return settings
    
    def get_voting_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Get voting criteria configuration"""
        return self.custom_config.get('voting_criteria', VOTING_CRITERIA)
    
    def get_async_retry_config(self) -> Dict[str, Any]:
        """Get async retry configuration"""
        return self.custom_config.get('async_retry', TEAM_CONFIG.get('async_retry', {
            'enabled': True,
            'max_retries': 3,
            'backoff_factor': 2.0,
            'initial_delay': 1.0,
            'retry_on_errors': ['ConnectionError', 'TimeoutError']
        }))
    
    def save_custom_config(self, config_dict: Dict[str, Any]):
        """Save custom configuration to file"""
        if self.config_file:
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            self.custom_config = config_dict


# Global config instance
config = Config()