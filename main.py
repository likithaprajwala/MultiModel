import os
import sys
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


def ask(question: str, model: str) -> str:
    """Send a question to a model via OpenRouter and return the answer text.

    Args:
        question: The question to ask.
        model: The OpenRouter model ID.

    Returns:
        The assistant's reply as a string.

    Raises:
        openai.APIStatusError: For API errors (e.g., insufficient credits).
        Exception: For unexpected errors.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": question}],
        max_tokens=512,
    )

    # Extract the assistant reply from the response object
    try:
        answer = response.choices[0].message.content
    except Exception:
        # Fallback in case the response shape is a dict
        answer = response.choices[0]["message"]["content"]

    return answer


def main():
    """Ask a hardcoded question to each model and print results.

    This implements Step 1 of the Multi-Model Comparison Tool:
    - Sends the question "What is Artificial Intelligence?"
    - Queries each model in MODELS
    - Prints each model's name and answer
    """
    question = "What is Artificial Intelligence?"

    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"Model: {model}")
        print(f"{'='*60}")

        try:
            answer = ask(question, model)
            print(answer)

        except openai.APIStatusError as e:
            # Handle billing/credit errors (HTTP 402) from OpenRouter gracefully.
            print(
                "OpenRouter API error:",
                getattr(e, "user_message", str(e)),
                file=sys.stderr,
            )
            print("This may indicate insufficient credits or an oversized `max_tokens`.", file=sys.stderr)
            print("Check your OpenRouter credits at https://openrouter.ai/settings/credits", file=sys.stderr)
            continue

        except Exception as e:
            print("Unexpected error calling the API:", str(e), file=sys.stderr)
            continue


if __name__ == "__main__":
    main()
