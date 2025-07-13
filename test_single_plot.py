#!/usr/bin/env python3
"""Test with a single plot to verify the system works"""

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
print("Testing plot expander with single plot...")
print("="*60)

expander = PlotExpander()

# Single test plot
result = expander.expand_single_plot(
    "Sci-Fi", 
    "A satellite technician notices a transmission loop that shouldn't exist—one that contains a recording of her own death, scheduled for next week."
)

print("\n" + "="*60)
print("RESULTS:")
print("="*60)
print(f"Winner: {result.voting_results.winning_team}")
print(f"Vote distribution: {result.voting_results.vote_tally}")
print(f"\nWinning plot themes: {', '.join(result.selected_themes[:3])}")
print(f"Unique hooks: {', '.join(result.selected_unique_hooks[:2])}")
print(f"Complexity: {result.selected_estimated_complexity}/10")
print("\nVoting details:")
for vote in result.voting_results.individual_votes:
    print(f"- {vote.agent_name} voted for {vote.vote_for_team}")
print(f"\nOutput saved to: forge/")