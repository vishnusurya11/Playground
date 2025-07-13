#!/usr/bin/env python3
"""Test script to verify all dependencies are installed correctly"""

print("Testing imports...")

try:
    import pydantic
    print("✓ pydantic imported successfully")
except ImportError as e:
    print(f"✗ Failed to import pydantic: {e}")

try:
    import langchain
    print("✓ langchain imported successfully")
except ImportError as e:
    print(f"✗ Failed to import langchain: {e}")

try:
    import langchain_openai
    print("✓ langchain_openai imported successfully")
except ImportError as e:
    print(f"✗ Failed to import langchain_openai: {e}")

try:
    import dotenv
    print("✓ python-dotenv imported successfully")
except ImportError as e:
    print(f"✗ Failed to import dotenv: {e}")

print("\nTesting basic functionality...")

try:
    from pydantic import BaseModel, Field
    
    class TestModel(BaseModel):
        name: str = Field(description="Test field")
    
    test = TestModel(name="Test")
    print(f"✓ Pydantic model creation works: {test}")
except Exception as e:
    print(f"✗ Pydantic test failed: {e}")

print("\nAll tests completed!")
print("\nTo run the plot expander: uv run python plot_expander.py")