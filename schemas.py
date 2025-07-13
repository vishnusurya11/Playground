"""
Input/Output schemas for EpicWeaver
Defines the contracts between teams and the system
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


# Input schemas
class PlotInput(BaseModel):
    """Schema for plot expansion input"""
    genre: str = Field(description="Genre of the plot")
    plot: str = Field(description="Original plot idea to expand")


# Character and story component schemas
class CharacterInfo(BaseModel):
    """Schema for character information"""
    name: str = Field(description="Character name")
    role: str = Field(description="Character's role in the story")
    description: str = Field(description="Personality and motivation")


class StoryBeats(BaseModel):
    """Schema for story structure beats"""
    opening: str = Field(description="How the story begins - the hook")
    catalyst: str = Field(description="The event that launches the main story")
    midpoint: str = Field(description="Major revelation or turn that changes everything")
    crisis: str = Field(description="The darkest moment before the climax")
    resolution: str = Field(description="How the conflict resolves and characters change")


# Output schemas
class ExpandedPlotProposal(BaseModel):
    """Schema for team expansion output - the contract all teams must fulfill"""
    team_name: str = Field(description="Name of the expansion team")
    model_used: str = Field(description="Model used for expansion")
    title: str = Field(description="Story title")
    logline: str = Field(description="One-sentence hook (max 30 words)")
    main_characters: List[CharacterInfo] = Field(description="Main character details")
    plot_summary: str = Field(description="The main plot narrative (300-400 words)")
    central_conflict: str = Field(description="Core conflict and stakes")
    story_beats: StoryBeats = Field(description="Key story beats")
    ending: str = Field(description="How the story concludes")
    key_elements: List[str] = Field(description="Main story elements")
    potential_arcs: List[str] = Field(description="Character arc possibilities")
    themes: List[str] = Field(description="Potential themes to explore")
    estimated_complexity: int = Field(description="Story complexity 1-10", ge=1, le=10)
    unique_hooks: List[str] = Field(description="What makes this version unique")


class VotingResult(BaseModel):
    """Schema for individual voting result"""
    agent_name: str = Field(description="Name of voting agent")
    model_used: str = Field(description="Model used by voting agent")
    vote_for_team: str = Field(description="Team name they voted for")
    reasoning: str = Field(description="Why they chose this expansion")
    score_breakdown: Dict[str, int] = Field(default_factory=dict, description="Scores for each criteria")


class VotingResults(BaseModel):
    """Schema for aggregated voting results"""
    individual_votes: List[VotingResult]
    vote_tally: Dict[str, int] = Field(description="team_name -> vote_count")
    winning_team: str
    total_votes: int
    voting_summary: Dict[str, Any] = Field(default_factory=dict, description="Comprehensive voting summary")


class PlotExpanderOutput(BaseModel):
    """Schema for complete plot expander output"""
    original_plot: str
    genre: str
    all_expanded_plots: Dict[str, ExpandedPlotProposal]
    voting_results: VotingResults
    selected_expansion: Dict[str, Any] = Field(description="All details from winning expansion")
    timestamp: str
    processing_time: float