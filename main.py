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


def main():
    """Send a single hardcoded question to the specified model and print the reply.

    This implements Step 1 of the Multi-Model Comparison Tool specification:
    - Uses the OpenRouter endpoint via the OpenAI-compatible client
    - Sends the question "What is Artificial Intelligence?"
    - Uses the model 'anthropic/claude-opus-4.8'
    - Prints the model's answer
    """

    model = "anthropic/claude-opus-4.8"
    question = "What is Artificial Intelligence?"

    # Call the chat completions API with a conservative token limit to avoid
    # billing/credit errors from OpenRouter. Adjust `max_tokens` as needed.
    try:
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
        sys.exit(1)
    except Exception as e:
        print("Unexpected error calling the API:", str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
