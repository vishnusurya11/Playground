"""
Voting agents for EpicWeaver
Each agent has its own unique evaluation perspective
"""

from .base_voter import BaseVoter
from .the_curator import TheCurator
from .genre_maven import GenreMaven
from .mind_reader import MindReader
from .trend_prophet import TrendProphet
from .architect_prime import ArchitectPrime
from .wisdom_keeper import WisdomKeeper
from .pulse_checker import PulseChecker
from .edge_walker import EdgeWalker
from .time_sage import TimeSage
from .voice_whisperer import VoiceWhisperer
from .world_builder import WorldBuilder

__all__ = [
    'BaseVoter',
    'TheCurator',
    'GenreMaven',
    'MindReader',
    'TrendProphet',
    'ArchitectPrime',
    'WisdomKeeper',
    'PulseChecker',
    'EdgeWalker',
    'TimeSage',
    'VoiceWhisperer',
    'WorldBuilder'
]