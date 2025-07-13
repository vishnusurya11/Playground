# OpenAI Model Configuration
# Models priced at $2.50 or less per million input tokens

MODELS = {
    "gpt-4o-mini": {
        "name": "gpt-4o-mini-2024-07-18",
        "input_price": 0.15,  # per million tokens
        "output_price": 0.60,  # per million tokens
        "context_window": 128000,
        "max_output": 16000,
        "description": "Most cost-effective model with good performance"
    },
    "gpt-4-mini": {
        "name": "gpt-4.1-mini-2025-04-14",
        "input_price": 0.40,
        "output_price": 1.60,
        "context_window": 128000,
        "max_output": 16000,
        "description": "Enhanced mini model with better reasoning"
    },
    "gpt-4-nano": {
        "name": "gpt-4.1-nano-2025-04-14",
        "input_price": 0.10,
        "output_price": 0.40,
        "context_window": 128000,
        "max_output": 16000,
        "description": "Cheapest option for simple tasks"
    },
    "gpt-4-base": {
        "name": "gpt-4.1-2025-04-14",
        "input_price": 2.00,
        "output_price": 8.00,
        "context_window": 128000,
        "max_output": 16000,
        "description": "Standard GPT-4 model"
    },
    "gpt-4o": {
        "name": "gpt-4o-2024-08-06",
        "input_price": 2.50,
        "output_price": 10.00,
        "context_window": 128000,
        "max_output": 16000,
        "description": "GPT-4 optimized model (at price limit)"
    },
    "o3": {
        "name": "o3-2025-04-16",
        "input_price": 2.00,
        "output_price": 8.00,
        "context_window": 200000,
        "max_output": 100000,
        "description": "Reasoning model for complex tasks"
    },
    "o3-mini": {
        "name": "o3-mini-2025-01-31",
        "input_price": 1.10,
        "output_price": 4.40,
        "context_window": 200000,
        "max_output": 100000,
        "description": "Mini reasoning model"
    },
    "o4-mini": {
        "name": "o4-mini-2025-04-16",
        "input_price": 1.10,
        "output_price": 4.40,
        "context_window": 200000,
        "max_output": 100000,
        "description": "Latest mini reasoning model"
    },
    "codex-mini": {
        "name": "codex-mini-latest",
        "input_price": 1.50,
        "output_price": 6.00,
        "context_window": 128000,
        "max_output": 16000,
        "description": "Code-optimized mini model"
    }
}

# Easy model switching
CURRENT_MODEL = "gpt-4o-mini"  # Change this to switch models

def get_model():
    """Get current model configuration"""
    return MODELS[CURRENT_MODEL]

def get_model_name(config_key):
    """Get the actual model name from config key"""
    if config_key in MODELS:
        return MODELS[config_key]["name"]
    # If not found, return the key itself (might be a direct model name)
    return config_key

def calculate_cost(input_tokens, output_tokens, model_name=None):
    """Calculate cost for given tokens"""
    model = MODELS[model_name or CURRENT_MODEL]
    input_cost = (input_tokens / 1_000_000) * model["input_price"]
    output_cost = (output_tokens / 1_000_000) * model["output_price"]
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": input_cost + output_cost
    }

def list_models_by_price():
    """List models sorted by input price"""
    sorted_models = sorted(MODELS.items(), key=lambda x: x[1]["input_price"])
    for name, config in sorted_models:
        print(f"{name}: ${config['input_price']}/M input, ${config['output_price']}/M output - {config['description']}")

# Example usage
if __name__ == "__main__":
    print(f"Current model: {CURRENT_MODEL}")
    print(f"Configuration: {get_model()}")
    print("\nAll available models under $2.50/M input:")
    list_models_by_price()