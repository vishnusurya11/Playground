#!/usr/bin/env python3
"""Test script to verify plot expander setup before running"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

print("=" * 60)
print("PLOT EXPANDER SYSTEM TEST")
print("=" * 60)

# Test 1: Check environment
print("\n1. Checking environment variables...")
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✓ OPENAI_API_KEY found (length: {len(api_key)})")
else:
    print("✗ OPENAI_API_KEY not found! Please set it in .env file")
    sys.exit(1)

# Test 2: Check imports
print("\n2. Testing imports...")
try:
    from pydantic import BaseModel, Field
    print("✓ Pydantic imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pydantic: {e}")
    sys.exit(1)

try:
    from langchain_openai import ChatOpenAI
    print("✓ LangChain OpenAI imported successfully")
except ImportError as e:
    print(f"✗ Failed to import langchain_openai: {e}")
    sys.exit(1)

try:
    from langchain_core.messages import SystemMessage, HumanMessage
    print("✓ LangChain messages imported successfully")
except ImportError as e:
    print(f"✗ Failed to import langchain_core: {e}")
    sys.exit(1)

# Test 3: Check configuration files
print("\n3. Checking configuration files...")
config_files = ["model_config.py", "model_teams_config.json", "plot_expander.py"]
for file in config_files:
    if Path(file).exists():
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} not found!")
        sys.exit(1)

# Test 4: Test model initialization
print("\n4. Testing model initialization...")
try:
    # Test with gpt-4o-mini which should always be available
    test_model = ChatOpenAI(model="gpt-4o-mini-2024-07-18", temperature=0.7)
    print("✓ Successfully initialized gpt-4o-mini model")
except Exception as e:
    print(f"✗ Failed to initialize model: {e}")
    sys.exit(1)

# Test 5: Test structured output
print("\n5. Testing structured output...")
try:
    from plot_expander import ExpandedPlotProposal
    
    class TestOutput(BaseModel):
        message: str = Field(description="Test message")
        score: int = Field(description="Test score")
    
    structured_model = test_model.with_structured_output(TestOutput)
    print("✓ Structured output setup successful")
except Exception as e:
    print(f"✗ Failed to setup structured output: {e}")
    sys.exit(1)

# Test 6: Load and validate model configuration
print("\n6. Validating model configuration...")
try:
    import json
    with open("model_teams_config.json", "r") as f:
        config = json.load(f)
    
    # Check all model names
    models_to_check = set()
    
    # Get models from teams
    for team_key, team_config in config["expansion_teams"].items():
        model_name = team_config["model_name"]
        models_to_check.add(model_name)
        print(f"  Team {team_config['name']}: {model_name}")
    
    # Get models from voting council
    for agent_key, agent_config in config["voting_council"].items():
        model_name = agent_config["model_name"]
        models_to_check.add(model_name)
    
    print(f"\nUnique models used: {models_to_check}")
    
    # Check which models might not be available
    known_available = ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]
    potentially_unavailable = models_to_check - set(known_available)
    
    if potentially_unavailable:
        print(f"\n⚠ Warning: These models might not be available yet:")
        for model in potentially_unavailable:
            print(f"  - {model}")
        print("\nThe system will use fallbacks if these models fail.")
    
except Exception as e:
    print(f"✗ Failed to load config: {e}")
    sys.exit(1)

# Test 7: Cost estimation
print("\n7. Cost estimation for one plot...")
try:
    from model_config import MODELS
    
    # Estimate tokens (rough)
    # Each team: 3 agents * ~500 tokens input + ~500 tokens output = 3000 tokens per team
    # 5 teams = 15,000 tokens
    # Voting: 7 agents * ~1000 tokens input + ~200 tokens output = 8,400 tokens
    # Total: ~23,400 tokens
    
    total_input_tokens = 20000  # Conservative estimate
    total_output_tokens = 3400
    
    print(f"Estimated tokens per plot:")
    print(f"  Input: ~{total_input_tokens:,} tokens")
    print(f"  Output: ~{total_output_tokens:,} tokens")
    
    # Calculate cost for cheapest model
    cheapest_model = MODELS["gpt-4o-mini"]
    input_cost = (total_input_tokens / 1_000_000) * cheapest_model["input_price"]
    output_cost = (total_output_tokens / 1_000_000) * cheapest_model["output_price"]
    total_cost = input_cost + output_cost
    
    print(f"\nEstimated cost per plot (using gpt-4o-mini):")
    print(f"  Input: ${input_cost:.4f}")
    print(f"  Output: ${output_cost:.4f}")
    print(f"  Total: ${total_cost:.4f}")
    
    print(f"\nFor 3 plots: ~${total_cost * 3:.4f}")
    
except Exception as e:
    print(f"✗ Failed to estimate costs: {e}")

# Test 8: Small API test
print("\n8. Testing actual API call...")
try:
    response = test_model.invoke("Say 'API test successful' in exactly 4 words.")
    print(f"✓ API Response: {response.content}")
except Exception as e:
    print(f"✗ API call failed: {e}")
    print("\nPlease check:")
    print("  1. Your API key is valid")
    print("  2. You have credits in your OpenAI account")
    print("  3. Your network connection is working")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nYou can now run: uv run python plot_expander.py")
print("\nNote: Some newer models might not be available yet.")
print("The system will handle this gracefully with fallbacks."