# MultiModel

A Python application that routes prompts to multiple AI models via OpenRouter.

## Prerequisites

- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key

## Setup

```bash
# 1. Clone / open the project folder
cd "TechVest AI/MultiModel"

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
#    Open .env and replace the placeholder value:
#    OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Run

```bash
python main.py
```

## Project Structure

```
MultiModel/
├─ .env              ← OpenRouter API key  (never commit)
├─ .gitignore
├─ spec.md           ← application specification
├─ requirements.txt
├─ main.py           ← entry point
└─ README.md
```
