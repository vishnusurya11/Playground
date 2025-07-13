#!/usr/bin/env python3
"""Test the new structured output format"""

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

print("Testing new structured output format...")
print("="*60)

expander = PlotExpander()

# Test plot
result = expander.expand_single_plot(
    "Sci-Fi", 
    "A robot discovers it can dream."
)

print("\n" + "="*60)
print("STRUCTURED OUTPUT VERIFICATION:")
print("="*60)

# Check selected expansion structure
sel = result.selected_expansion
print(f"\n✓ Title: {sel['title']}")
print(f"✓ Logline: {sel['logline']}")
print(f"✓ Main Characters: {len(sel['main_characters'])} characters")
for char in sel['main_characters']:
    print(f"  - {char['name']} ({char['role']}): {char['description'][:50]}...")

print(f"\n✓ Plot Summary Length: {len(sel['plot_summary'])} chars")
print(f"  First 100 chars: {sel['plot_summary'][:100]}...")

print(f"\n✓ Central Conflict: {sel['central_conflict'][:80]}...")

print(f"\n✓ Story Beats:")
for beat, desc in sel['story_beats'].items():
    print(f"  - {beat.capitalize()}: {desc[:50]}...")

print(f"\n✓ Ending: {sel['ending'][:80]}...")

print(f"\n✓ Key Elements: {len(sel['key_elements'])} items")
print(f"  Examples: {', '.join(sel['key_elements'][:3])}")

print(f"\n✓ Themes: {len(sel['themes'])} themes")
print(f"  Examples: {', '.join(sel['themes'][:3])}")

print(f"\n✓ Unique Hooks: {len(sel['unique_hooks'])} hooks")
print(f"  Examples: {', '.join(sel['unique_hooks'][:2])}")

print(f"\n✓ Complexity: {sel['estimated_complexity']}/10")

# Verify all teams produced structured output
print("\n" + "="*60)
print("TEAM OUTPUT VERIFICATION:")
print("="*60)
for team_name, proposal in result.all_expanded_plots.items():
    print(f"\n{team_name}:")
    print(f"  ✓ Title: {proposal.title}")
    print(f"  ✓ Characters: {len(proposal.main_characters)}")
    print(f"  ✓ Plot Summary: {len(proposal.plot_summary)} chars")
    print(f"  ✓ Has all story beats: {hasattr(proposal.story_beats, 'opening')}")

print(f"\n\nOutput saved to: forge/")