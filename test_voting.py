#!/usr/bin/env python3
"""Test the voting mechanism separately"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json

# Load environment variables
load_dotenv()

# Check API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not set!")
    exit(1)

# Test voting with a simple example
model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0.3)

# Sample expansions
expansions = {
    "Team A": "A thrilling story about time travel...",
    "Team B": "An emotional journey through space...",
    "Team C": "A mystery that challenges reality..."
}

# Build voting prompt
voting_prompt = f"""You are a literary critic evaluating story expansions.

Here are the expansions to evaluate:

Team A: {expansions['Team A']}
Team B: {expansions['Team B']}
Team C: {expansions['Team C']}

Please evaluate all expansions and vote for the best one. 

You MUST respond in the following JSON format:
{{
  "vote_for_team": "Team Name Here",
  "reasoning": "Your detailed reasoning here",
  "scores": {{
    "originality": 8,
    "coherence": 7,
    "market_potential": 6,
    "character_depth": 8,
    "thematic_richness": 7,
    "expandability": 8
  }}
}}

Important:
- Choose ONE team from the expansions above (Team A, Team B, or Team C)
- Provide specific reasoning
- Rate each criterion from 1-10
- Your response must be valid JSON only"""

print("Testing voting mechanism...")
print("="*60)

try:
    # Get response
    response = model.invoke(voting_prompt)
    print("Raw response:")
    print(response.content)
    print("\n" + "="*60)
    
    # Try to parse JSON
    import re
    json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
    
    if json_match:
        vote_data = json.loads(json_match.group())
        print("\nParsed vote:")
        print(f"Team: {vote_data.get('vote_for_team')}")
        print(f"Reasoning: {vote_data.get('reasoning')[:100]}...")
        print(f"Scores: {vote_data.get('scores')}")
        print("\n✓ Voting mechanism works!")
    else:
        print("✗ No JSON found in response")
        
except Exception as e:
    print(f"✗ Error: {e}")