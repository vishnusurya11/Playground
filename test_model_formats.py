#!/usr/bin/env python3
"""Test what each model actually produces"""

from plot_expander import PlotExpander
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

print("Testing model format compliance...")
print("="*60)

expander = PlotExpander()

# Simple test plot
result = expander.expand_single_plot(
    "Sci-Fi", 
    "A robot discovers it can dream."
)

print("\n" + "="*60)
print("CHECKING EACH TEAM'S OUTPUT:")
print("="*60)

# Check what each team produced
for team_name, proposal in result.all_expanded_plots.items():
    print(f"\n{team_name} ({proposal.model_used}):")
    print("-" * 40)
    
    # Show first 500 chars to see format
    plot_text = proposal.expanded_plot
    print("First 500 chars:")
    print(plot_text[:500])
    
    # Check if it has standard sections
    has_title = "TITLE:" in plot_text
    has_logline = "LOGLINE:" in plot_text
    has_characters = "MAIN CHARACTERS:" in plot_text
    
    print(f"\nHas TITLE: {has_title}")
    print(f"Has LOGLINE: {has_logline}")
    print(f"Has MAIN CHARACTERS: {has_characters}")
    
print(f"\n\nDone. Check forge/ for full output.")