import html
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import streamlit as st

from main import ask

MODELS = [
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4",
    "meta-llama/llama-4-maverick",
    "qwen/qwen3-235b-a22b",
]

MODEL_ICONS = {
    "google/gemini-2.5-pro": "🤖",
    "anthropic/claude-sonnet-4": "🎵",
    "meta-llama/llama-4-maverick": "🦙",
    "qwen/qwen3-235b-a22b": "⚡",
}

st.set_page_config(
    page_title="Multi-Model Comparison Tool",
    page_icon="🤖",
    layout="wide",
)

PAGE_STYLE = """
<style>
:root {
    color-scheme: dark;
}

body {
    background: radial-gradient(circle at top left, rgba(99, 102, 241, 0.16), transparent 24%),
                radial-gradient(circle at 85% 12%, rgba(99, 102, 241, 0.08), transparent 18%),
                linear-gradient(180deg, #060b18 0%, #09131f 100%);
    color: #f8fafc;
}

.stApp {
    padding-top: 20px;
}

.hero-panel,
.control-panel,
.summary-card,
.model-card,
.disclaimer-panel {
    border-radius: 28px;
    background: rgba(12, 18, 39, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.16);
    box-shadow: 0 28px 60px rgba(8, 15, 38, 0.40);
}

.hero-panel {
    padding: 38px 42px;
    margin-bottom: 28px;
}

.hero-panel h1 {
    margin: 0;
    font-size: clamp(2.8rem, 5vw, 4rem);
    line-height: 1.02;
}

.hero-panel h1 .highlight {
    background: linear-gradient(90deg, #7c3aed, #4f46e5);
    -webkit-background-clip: text;
    color: transparent;
}

.hero-panel p {
    color: #cbd5e1;
    font-size: 1.05rem;
    margin-top: 18px;
    line-height: 1.75;
    max-width: 860px;
}

.control-panel {
    padding: 28px;
    margin-bottom: 24px;
}

.control-panel .section-title,
.summary-card .section-title,
.model-card .model-title {
    margin-bottom: 18px;
    font-size: 1rem;
    font-weight: 700;
    color: #eff6ff;
}

.stTextArea>div>div>textarea,
.stMultiSelect>div>div>div>button,
.stSelectbox>div>div>div>button,
.stTextInput>div>div>input {
    background: rgba(15, 23, 42, 0.96);
    color: #f8fafc;
    border: 1px solid rgba(148, 163, 184, 0.18);
}

.stTextArea>div>div>label,
.stMultiselect>div>label,
.stSelectbox>div>label,
.stTextInput>div>label {
    color: #cbd5e1;
}

.stButton>button {
    border-radius: 999px;
    padding: 0.95rem 1.9rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #ffffff;
    border: none;
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.28);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.stButton>button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 24px 42px rgba(99, 102, 241, 0.38);
}

.stButton>button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

.info-box {
    border-radius: 20px;
    padding: 18px 20px;
    background: rgba(15, 23, 42, 0.86);
    border: 1px solid rgba(96, 165, 250, 0.14);
    color: #c7d2fe;
}

.info-box strong {
    color: #e0e7ff;
}

.model-grid {
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.model-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 500px;
    overflow: hidden;
}

.model-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 36px 80px rgba(8, 15, 38, 0.45);
}

.model-card .model-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.model-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.8rem 1rem;
    border-radius: 18px;
    background: rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
    font-weight: 700;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.55rem 0.95rem;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 700;
}

.status-success {
    background: rgba(16, 185, 129, 0.16);
    color: #86efac;
}

.status-error {
    background: rgba(248, 113, 113, 0.16);
    color: #fecaca;
}

.response-preview {
    background: rgba(15, 23, 42, 0.88);
    border-radius: 20px;
    padding: 18px;
    min-height: 170px;
    max-height: 190px;
    overflow-y: auto;
    color: #cbd5e1;
    line-height: 1.7;
}

.response-preview::-webkit-scrollbar {
    width: 8px;
}

.response-preview::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.26);
    border-radius: 999px;
}

.metric-grid {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.metric-block {
    border-radius: 18px;
    padding: 16px;
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid rgba(148, 163, 184, 0.12);
}

.metric-label {
    color: #94a3b8;
    font-size: 0.82rem;
    margin-bottom: 8px;
    display: block;
}

.metric-value {
    font-size: 1rem;
    font-weight: 700;
    color: #f8fafc;
}

.disclaimer-panel {
    padding: 22px;
    border-left: 4px solid rgba(79, 70, 229, 0.72);
}

.disclaimer-panel p {
    margin: 0;
    color: #c7d2fe;
}

@media (max-width: 960px) {
    .model-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""

st.markdown(PAGE_STYLE, unsafe_allow_html=True)

for key, default in [
    ("processing", False),
    ("results", []),
    ("total_cost", 0.0),
    ("total_runtime", 0.0),
    ("question_input", "What is Artificial Intelligence?"),
    ("selected_models", MODELS.copy()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

openrouter_status = "Connected" if os.getenv("OPENROUTER_API_KEY") else "Not configured"

st.markdown(
    "<div class='hero-panel'>"
    "<h1>Multi-Model <span class='highlight'>Comparison Tool</span></h1>"
    "<p>Ask a question and compare responses, latency, and estimated cost from leading AI models.</p>"
    "</div>",
    unsafe_allow_html=True,
)


def format_cost(value):
    return f"${value:.6f}" if value is not None else "N/A"


def format_latency(value):
    return f"{value:.2f} ms" if value is not None else "N/A"


def format_token(value):
    return str(value) if value is not None else "N/A"


def run_model(model_name: str, prompt_text: str) -> dict:
    try:
        answer, latency_ms, input_tokens, output_tokens, cost_usd = ask(prompt_text, model_name)
        return {
            "model": model_name,
            "icon": MODEL_ICONS.get(model_name, "🤖"),
            "status": "success",
            "error": None,
            "answer": answer,
            "answer_preview": answer[:250] + ("..." if len(answer) > 250 else ""),
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
    except Exception as exc:
        return {
            "model": model_name,
            "icon": MODEL_ICONS.get(model_name, "⚠️"),
            "status": "error",
            "error": str(exc),
            "answer": "",
            "answer_preview": "",
            "latency_ms": None,
            "cost_usd": None,
            "input_tokens": None,
            "output_tokens": None,
        }


def compare_models(question: str, selected_models: List[str]):
    st.session_state.processing = True
    st.session_state.results = []
    st.session_state.total_cost = 0.0
    st.session_state.total_runtime = 0.0

    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max(1, len(selected_models))) as executor:
        futures = [executor.submit(run_model, model, question) for model in selected_models]
        for future in as_completed(futures):
            st.session_state.results.append(future.result())

    st.session_state.total_runtime = time.perf_counter() - start_time
    st.session_state.total_cost = sum(result["cost_usd"] or 0.0 for result in st.session_state.results)
    st.session_state.processing = False


with st.container():
    left, right = st.columns([3, 1], gap="large")

    with left:
        with st.form("compare_form"):
            st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Your question</div>", unsafe_allow_html=True)

            question = st.text_area(
                "",
                value=st.session_state.question_input,
                key="question_input",
                height=180,
            )

            selected_models = st.multiselect(
                "Select models",
                options=MODELS,
                default=st.session_state.selected_models,
                key="selected_models",
            )

            st.markdown(
                "<div class='info-box'>"
                "<strong>Tip:</strong> Pick the models you want to compare, then press Compare Models to see aligned results in cards below.</div>",
                unsafe_allow_html=True,
            )

            submit_button = st.form_submit_button(
                "Compare Models",
                disabled=st.session_state.processing or not question.strip() or len(selected_models) == 0,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        if submit_button:
            if question.strip() and selected_models:
                with st.spinner("Comparing AI models..."):
                    compare_models(question.strip(), selected_models)

    with right:
        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Run summary</div>", unsafe_allow_html=True)
        st.markdown(
            f"<p><strong>{len(st.session_state.results)}</strong> models compared</p>"
            f"<p>{len([r for r in st.session_state.results if r['status'] == 'success'])} success / {len([r for r in st.session_state.results if r['status'] == 'error'])} failed</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>OpenRouter status</div>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>{openrouter_status}</strong></p>", unsafe_allow_html=True)
        if openrouter_status != "Connected":
            st.markdown(
                "<p style='color:#fecdd3;'>Set OPENROUTER_API_KEY in .env to enable model queries.</p>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Latest metrics</div>", unsafe_allow_html=True)
        st.markdown(
            f"<p><strong>{format_cost(st.session_state.total_cost)}</strong></p>"
            f"<p>Estimated total cost</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p><strong>{st.session_state.total_runtime:.2f} sec</strong></p>"
            f"<p>Wall-clock runtime</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.results:
    st.markdown("<div class='model-grid'>", unsafe_allow_html=True)

    for result in st.session_state.results:
        status_class = "status-success" if result["status"] == "success" else "status-error"
        preview_text = html.escape(result["answer_preview"] or "")
        error_text = html.escape(result["error"] or "Model error")

        st.markdown("<div class='model-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='model-title'>"
            f"<div class='model-chip'><span>{result['icon']}</span><span>{html.escape(result['model'])}</span></div>"
            f"<span class='status-pill {status_class}'>{'Success' if result['status'] == 'success' else 'Error'}</span>"
            "</div>",
            unsafe_allow_html=True,
        )

        if result["status"] == "success":
            st.markdown(f"<div class='response-preview'>{preview_text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='response-preview'><span style='color:#fecdd3;'>{error_text}</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div class='metric-grid'>"
            f"<div class='metric-block'><span class='metric-label'>Latency</span><span class='metric-value'>{format_latency(result['latency_ms'])}</span></div>"
            f"<div class='metric-block'><span class='metric-label'>Estimated cost</span><span class='metric-value'>{format_cost(result['cost_usd'])}</span></div>"
            f"<div class='metric-block'><span class='metric-label'>Input tokens</span><span class='metric-value'>{format_token(result['input_tokens'])}</span></div>"
            f"<div class='metric-block'><span class='metric-label'>Output tokens</span><span class='metric-value'>{format_token(result['output_tokens'])}</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )

        if result["status"] == "success":
            with st.expander("View full response"):
                st.write(result["answer"])
        else:
            st.error(result["error"])

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='disclaimer-panel'>"
        "<p>Responses are generated by AI models and may not always be accurate. Verify important information before using it.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
