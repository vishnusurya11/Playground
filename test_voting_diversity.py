#!/usr/bin/env python3
"""Test voting diversity after prompt improvements"""

from plot_expander import PlotExpander
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

# Test with multiple plots to see voting patterns
print("Testing voting diversity with enhanced prompts...")
print("="*60)

expander = PlotExpander()

# Test plots
test_plots = [
    ("Literary Fiction", "A retired librarian discovers that every book she ever recommended has subtly altered the lives of readers in ways that mirror the plots, and now the stories are demanding their endings."),
    ("Commercial Thriller", "A CIA analyst discovers that his Spotify playlist is actually a series of coded messages from a deep-cover agent who's been missing for five years."),
    ("Philosophical Sci-Fi", "A philosopher proves that free will doesn't exist, then must decide whether to publish the proof, knowing it will fundamentally change human behavior."),
]

for genre, plot in test_plots:
    print(f"\n{'='*60}")
    print(f"Testing: {genre}")
    print(f"Plot: {plot[:60]}...")
    print("="*60)
    
    result = expander.expand_single_plot(genre, plot)
    
    # The print_voting_summary is called automatically
    # Let's also check for voting diversity
    vote_distribution = result.voting_results.vote_tally
    votes = result.voting_results.individual_votes
    
    print("\nVoting Analysis:")
    print(f"- Unique teams voted for: {len([t for t in vote_distribution.values() if t > 0])}")
    print(f"- Highest vote count: {max(vote_distribution.values())}")
    print(f"- Unanimous vote: {'Yes' if max(vote_distribution.values()) == 7 else 'No'}")
    
    # Check for contrarian votes
    winning_team = result.voting_results.winning_team
    contrarians = [v.agent_name for v in votes if v.vote_for_team != winning_team]
    if contrarians:
        print(f"- Contrarian voters: {', '.join(contrarians)}")
    
    print(f"\nSaved to: forge/")

print("\n" + "="*60)
print("VOTING DIVERSITY TEST COMPLETE")
print("="*60)