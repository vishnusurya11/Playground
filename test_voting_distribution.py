#!/usr/bin/env python3
"""Test voting distribution with cleaner output"""

from plot_expander import PlotExpander
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

# Test with a single plot
print("Testing plot expander voting distribution...")
print("="*60)

expander = PlotExpander()

# Single test plot
result = expander.expand_single_plot(
    "Mystery", 
    "A historian finds photographs of herself at ancient events she's never attended, each taken decades before she was born."
)

print("\n" + "="*60)
print("VOTING RESULTS:")
print("="*60)

# Show vote tally
print("\nVote Tally:")
for team, votes in sorted(result.voting_results.vote_tally.items(), key=lambda x: x[1], reverse=True):
    print(f"  {team}: {votes} votes {'🏆' if team == result.voting_results.winning_team else ''}")

# Show individual votes
print("\nIndividual Votes:")
for vote in result.voting_results.individual_votes:
    print(f"  {vote.agent_name} ({vote.model_used}) → {vote.vote_for_team}")
    print(f"    Scores: O:{vote.score_breakdown.get('originality', 0)} "
          f"C:{vote.score_breakdown.get('coherence', 0)} "
          f"M:{vote.score_breakdown.get('market_potential', 0)} "
          f"Ch:{vote.score_breakdown.get('character_depth', 0)} "
          f"T:{vote.score_breakdown.get('thematic_richness', 0)} "
          f"E:{vote.score_breakdown.get('expandability', 0)}")

# Show winning expansion details
print(f"\n{'='*60}")
print("WINNING EXPANSION DETAILS:")
print(f"{'='*60}")
print(f"Team: {result.voting_results.winning_team}")
print(f"Themes: {', '.join(result.selected_themes)}")
print(f"Unique Hooks: {', '.join(result.selected_unique_hooks)}")
print(f"Key Elements: {', '.join(result.selected_key_elements[:3])}...")
print(f"Character Arcs: {', '.join(result.selected_potential_arcs)}")
print(f"Complexity: {result.selected_estimated_complexity}/10")

print(f"\nOutput saved to: forge/")