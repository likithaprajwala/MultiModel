import os
import sys
import time
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from a .env file
load_dotenv()

# Read the OpenRouter API key from the environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

# Create an OpenAI-compatible client that points at OpenRouter
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

# List of OpenRouter model IDs to query
MODELS = [
    "openai/gpt-5.5",
    "anthropic/claude-opus-4.8",
    "google/gemini-2.5-pro",
    "qwen/qwen3-235b-a22b",
]

# Pricing per million tokens (input, output) for each model
PRICES = {
    "openai/gpt-5.5": {"input": 0.075, "output": 0.30},
    "anthropic/claude-opus-4.8": {"input": 3.00, "output": 15.00},
    "google/gemini-2.5-pro": {"input": 0.075, "output": 0.30},
    "qwen/qwen3-235b-a22b": {"input": 0.50, "output": 0.50},
}


def ask(question: str, model: str) -> tuple:
    """Send a question to a model via OpenRouter and return metrics.

    Args:
        question: The question to ask.
        model: The OpenRouter model ID.

    Returns:
        Tuple of (answer, latency_ms, input_tokens, output_tokens, cost_usd)

    Raises:
        openai.APIStatusError: For API errors (e.g., insufficient credits).
        Exception: For unexpected errors.
    """
    # Measure latency
    start_time = time.perf_counter()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        max_tokens=512,
        timeout=60.0,  # 60-second timeout for the request
    )
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    # Extract the assistant reply from the response object
    try:
        answer = response.choices[0].message.content
    except Exception:
        # Fallback in case the response shape is a dict
        answer = response.choices[0]["message"]["content"]

    # Extract token usage
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    # Calculate cost based on model pricing
    prices = PRICES.get(model, {"input": 0, "output": 0})
    cost_usd = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

    return answer, latency_ms, input_tokens, output_tokens, cost_usd


def main():
    """Ask a hardcoded question to each model and print a comparison table.

    This implements Step 1 of the Multi-Model Comparison Tool:
    - Sends the question "What is Artificial Intelligence?"
    - Queries each model in MODELS
    - Displays results in a formatted comparison table
    """
    question = "What is Artificial Intelligence?"
    results = []

    # Collect results from all models
    for model in MODELS:
        try:
            answer, latency_ms, input_tokens, output_tokens, cost_usd = ask(question, model)
            # Truncate answer preview to 60 characters
            answer_preview = (answer[:60] + "...") if len(answer) > 60 else answer
            results.append({
                "model": model,
                "preview": answer_preview,
                "latency": latency_ms,
                "cost": cost_usd,
                "error": None,
            })

        except openai.APITimeoutError as e:
            results.append({
                "model": model,
                "preview": "TIMEOUT",
                "latency": None,
                "cost": None,
                "error": f"Request timeout",
            })

        except openai.APIStatusError as e:
            results.append({
                "model": model,
                "preview": "API ERROR",
                "latency": None,
                "cost": None,
                "error": getattr(e, "user_message", str(e)),
            })

        except Exception as e:
            results.append({
                "model": model,
                "preview": "ERROR",
                "latency": None,
                "cost": None,
                "error": f"{type(e).__name__}: {str(e)}",
            })

    # Print formatted comparison table
    print(f"\n{'='*120}")
    print("COMPARISON TABLE")
    print(f"{'='*120}")
    print(f"{'Model':<35} {'Answer Preview':<62} {'Latency':<12} {'Cost':<10}")
    print(f"{'-'*35} {'-'*62} {'-'*12} {'-'*10}")

    for result in results:
        if result["error"]:
            print(f"{result['model']:<35} {result['preview']:<62} {'N/A':<12} {'N/A':<10}")
            print(f"  └─ Error: {result['error']}")
        else:
            latency_str = f"{result['latency']:.2f} ms"
            cost_str = f"${result['cost']:.6f}"
            print(f"{result['model']:<35} {result['preview']:<62} {latency_str:<12} {cost_str:<10}")

    print(f"{'='*120}\n")


if __name__ == "__main__":
    main()
