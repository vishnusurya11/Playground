#!/usr/bin/env python3
"""Test standardized plot format"""

from plot_expander import PlotExpander
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

print("Testing standardized plot format...")
print("="*60)

expander = PlotExpander()

# Test plot
result = expander.expand_single_plot(
    "Sci-Fi", 
    "A satellite technician notices a transmission loop that shouldn't exist—one that contains a recording of her own death, scheduled for next week."
)

print("\n" + "="*60)
print("FORMAT VALIDATION RESULTS:")
print("="*60)

# Check format for each team
for team_name, proposal in result.all_expanded_plots.items():
    is_valid = expander.validate_plot_format(proposal.expanded_plot)
    print(f"\n{team_name}:")
    print(f"  Format Valid: {'✓' if is_valid else '✗'}")
    
    if is_valid:
        # Extract sections to verify
        plot_text = proposal.expanded_plot
        
        # Extract title
        if "TITLE:" in plot_text:
            title_start = plot_text.find("TITLE:") + 6
            title_end = plot_text.find("\n", title_start)
            title = plot_text[title_start:title_end].strip()
            print(f"  Title: {title}")
        
        # Extract logline
        if "LOGLINE:" in plot_text:
            logline_start = plot_text.find("LOGLINE:") + 8
            logline_end = plot_text.find("\n", logline_start)
            logline = plot_text[logline_start:logline_end].strip()
            print(f"  Logline: {logline[:50]}..." if len(logline) > 50 else f"  Logline: {logline}")
        
        # Check for all required sections
        sections = ["TITLE:", "LOGLINE:", "MAIN CHARACTERS:", "PLOT SUMMARY:", 
                   "CENTRAL CONFLICT:", "KEY STORY BEATS:", "ENDING:"]
        missing = [s for s in sections if s not in plot_text]
        if missing:
            print(f"  Missing sections: {', '.join(missing)}")
    else:
        print("  Plot does not follow standard format")
        # Show first 200 chars to debug
        print(f"  First 200 chars: {proposal.expanded_plot[:200]}...")

print(f"\n\nOutput saved to: forge/")