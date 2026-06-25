# Multi-Model Comparison Tool

Compare responses from multiple AI models side-by-side — powered by [OpenRouter](https://openrouter.ai).

Ask a single question and see how different LLMs answer, along with latency, token usage, and estimated cost.

## Features

- 🤖 Compare 4+ AI models simultaneously via OpenRouter
- ⚡ Concurrent model queries for fast comparison
- 📊 Real-time metrics: latency, cost, token usage
- 🌙 Dark theme with polished UI
- 📱 Fully responsive design

## Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key

## Setup

```bash
# 1. Navigate to the project
cd "TechVest AI/MultiModel"

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
#    Open .env and set:
#    OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Run

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
MultiModel/
├── app.py                 ← Flask web application (entry point)
├── main.py                ← CLI version of the comparison tool
├── app_rewrite.py         ← Streamlit version (alternative UI)
├── templates/
│   └── compare.html       ← HTML template
├── static/
│   ├── style.css          ← Dark theme styles
│   └── script.js          ← Frontend logic
├── .env                   ← OpenRouter API key (never commit)
├── requirements.txt
└── README.md
```

## Usage

1. Enter your question in the text area
2. Select which models to query
3. Click **Compare Models**
4. View responses, latency, cost, and token usage for each model
5. Click **View Full Response** to see complete answers

## Models

| Model | Provider |
|-------|----------|
| Gemini 2.5 Pro | Google |
| Claude Sonnet 4 | Anthropic |
| Llama 4 Maverick | Meta |
| Qwen 3 235B | Qwen |