# Spec — Multi-Model Comparison Tool

## Goal
Ask one question to four LLMs via OpenRouter and show each answer with its speed and cost.

## Input
A single question string.

## Output (per model)
- answer text
- latency
- input tokens
- output tokens
- cost

## Models
- openai/gpt-5.5
- anthropic/claude-opus-4.8
- google/gemini-3.1-pro
- qwen/qwen-3.7

## Pipeline

1. Load API key from .env
2. Send question to each model
3. Measure latency
4. Read token usage
5. Calculate cost
6. Display results

## Error Handling

Each model runs independently.

## Done When

- Four answers appear
- Cost appears
- Latency appears
- One failed model doesn't stop others