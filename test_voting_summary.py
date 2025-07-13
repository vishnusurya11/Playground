#!/usr/bin/env python3
"""Test the new voting summary functionality"""

from plot_expander import PlotExpander
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

# Test with a single plot
print("Testing enhanced voting summary...")
print("="*60)

expander = PlotExpander()

# Single test plot
result = expander.expand_single_plot(
    "Sci-Fi", 
    "A satellite technician notices a transmission loop that shouldn't exist—one that contains a recording of her own death, scheduled for next week."
)

# The print_voting_summary is already called in expand_single_plot
print("\n" + "="*60)
print("ACCESSING VOTING SUMMARY DATA DIRECTLY:")
print("="*60)

# Access the voting summary dict directly
voting_summary = result.voting_results.voting_summary

print("\n1. Just the vote distribution:")
print(json.dumps(voting_summary["vote_distribution"], indent=2))

print("\n2. Just the agent votes (simplified):")
agent_votes_simple = {
    agent: details["voted_for"] 
    for agent, details in voting_summary["agent_votes"].items()
}
print(json.dumps(agent_votes_simple, indent=2))

print("\n3. Team average scores summary:")
for team, scores in voting_summary["team_avg_scores"].items():
    print(f"{team}: Overall avg = {scores.get('total_avg', 0)}")

print("\n4. Model preferences:")
print(json.dumps(voting_summary["voting_patterns"]["model_preferences"], indent=2))

print(f"\nVoting summary successfully stored and accessible!")
print(f"Output saved to: forge/")