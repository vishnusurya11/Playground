#!/usr/bin/env python3
"""Test the improved team-specific outputs"""

from plot_expander import PlotExpander
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

print("Testing improved team outputs...")
print("="*60)

expander = PlotExpander()

# Test plot that should showcase each team's strengths
test_plot = "A detective discovers that every unsolved case in her city follows a pattern only she can see."

print(f"\nTest Plot: {test_plot}")
print("="*60)

# Expand with all teams
result = expander.expand_single_plot("Mystery", test_plot)

print("\n" + "="*60)
print("TEAM OUTPUT ANALYSIS:")
print("="*60)

# Analyze each team's output
for team_name, proposal in result.all_expanded_plots.items():
    print(f"\n{team_name}:")
    print("-" * 40)
    print(f"Title: {proposal.title}")
    print(f"Unique approach: {proposal.unique_hooks[0] if proposal.unique_hooks else 'N/A'}")
    
    # Check for team-specific elements
    if team_name == "Narrative Architects":
        # Look for structural innovation
        structure_words = ["timeline", "perspective", "narrative", "structure", "telling"]
        has_structure = any(word in proposal.plot_summary.lower() for word in structure_words)
        print(f"Has structural innovation focus: {'✓' if has_structure else '✗'}")
        
    elif team_name == "Plot Weavers":
        # Look for mystery/twist elements
        mystery_words = ["twist", "reveal", "mystery", "connection", "thread"]
        has_mystery = any(word in proposal.plot_summary.lower() for word in mystery_words)
        print(f"Has intricate plotting focus: {'✓' if has_mystery else '✗'}")

print("\n" + "="*60)
print("VOTING RESULTS:")
print("="*60)

# Show voting distribution
print("\nVote Distribution:")
for team, votes in result.voting_results.vote_tally.items():
    print(f"  {team}: {votes} votes")

# Show if Narrative Architects or Plot Weavers got votes
na_votes = result.voting_results.vote_tally.get("Narrative Architects", 0)
pw_votes = result.voting_results.vote_tally.get("Plot Weavers", 0)

print(f"\nImprovement Status:")
print(f"  Narrative Architects: {na_votes} votes {'✓ IMPROVED!' if na_votes > 0 else '✗ Still needs work'}")
print(f"  Plot Weavers: {pw_votes} votes {'✓ IMPROVED!' if pw_votes > 0 else '✗ Still needs work'}")

print(f"\n\nFull output saved to: forge/")