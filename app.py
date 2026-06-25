import html
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    print("Error: OPENROUTER_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

# Models available for comparison
AVAILABLE_MODELS = [
    {"id": "google/gemini-2.5-pro", "name": "Gemini 2.5 Pro", "icon": "🤖", "provider": "Google"},
    {"id": "anthropic/claude-sonnet-4", "name": "Claude Sonnet 4", "icon": "🎵", "provider": "Anthropic"},
    {"id": "meta-llama/llama-4-maverick", "name": "Llama 4 Maverick", "icon": "🦙", "provider": "Meta"},
    {"id": "qwen/qwen3-235b-a22b", "name": "Qwen 3 235B", "icon": "⚡", "provider": "Qwen"},
]

# Pricing per million tokens (input, output)
PRICES = {
    "google/gemini-2.5-pro": {"input": 0.075, "output": 0.30},
    "anthropic/claude-sonnet-4": {"input": 3.00, "output": 15.00},
    "meta-llama/llama-4-maverick": {"input": 0.50, "output": 0.50},
    "qwen/qwen3-235b-a22b": {"input": 0.50, "output": 0.50},
}

app = Flask(__name__)


def ask_model(question: str, model: str) -> Dict:
    """Send a question to a model via OpenRouter and return metrics."""
    start_time = time.perf_counter()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": question}],
            max_tokens=512,
            timeout=60.0,
        )

        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        try:
            answer = response.choices[0].message.content
        except Exception:
            answer = response.choices[0]["message"]["content"]

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        prices = PRICES.get(model, {"input": 0, "output": 0})
        cost_usd = (input_tokens * prices["input"] + output_tokens * prices["output"]) / 1_000_000

        return {
            "status": "success",
            "answer": answer,
            "latency_ms": round(latency_ms, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": round(cost_usd, 8),
            "error": None,
        }

    except Exception as e:
        return {
            "status": "error",
            "answer": None,
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "cost_usd": None,
            "error": str(e),
        }


@app.route("/")
def index():
    return render_template("compare.html", models=AVAILABLE_MODELS)


@app.route("/api/models")
def get_models():
    """Return available models for the frontend."""
    return jsonify(AVAILABLE_MODELS)


@app.route("/api/compare", methods=["POST"])
def compare():
    """Compare multiple models with the given question."""
    data = request.get_json()
    question = data.get("question", "").strip()
    selected_models = data.get("models", [])

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    if not selected_models:
        return jsonify({"error": "Please select at least one model."}), 400

    # Validate model IDs
    valid_ids = {m["id"] for m in AVAILABLE_MODELS}
    for model_id in selected_models:
        if model_id not in valid_ids:
            return jsonify({"error": f"Invalid model: {model_id}"}), 400

    results = []
    total_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=len(selected_models)) as executor:
        futures = {executor.submit(ask_model, question, mid): mid for mid in selected_models}
        for future in as_completed(futures):
            model_id = futures[future]
            result = future.result()
            result["model_id"] = model_id
            results.append(result)

    total_runtime = round(time.perf_counter() - total_start, 3)
    total_cost = round(sum(r["cost_usd"] or 0 for r in results), 8)
    total_success = sum(1 for r in results if r["status"] == "success")
    total_failed = sum(1 for r in results if r["status"] == "error")

    return jsonify({
        "results": results,
        "summary": {
            "total_models": len(selected_models),
            "success_count": total_success,
            "failed_count": total_failed,
            "total_cost": total_cost,
            "total_runtime": total_runtime,
        }
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)