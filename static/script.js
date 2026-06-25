// ============================================================
// Multi-Model Comparison Tool — Frontend Application Logic
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // ---- State -------------------------------------------------
    let models = [];
    let results = [];
    let isProcessing = false;

    // ---- DOM References ----------------------------------------
    const questionInput = document.getElementById('questionInput');
    const charCount = document.getElementById('charCount');
    const modelGrid = document.getElementById('modelGrid');
    const selectAllBtn = document.getElementById('selectAllBtn');
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    const compareBtn = document.getElementById('compareBtn');
    const clearBtn = document.getElementById('clearBtn');
    const loadingState = document.getElementById('loadingState');
    const errorDisplay = document.getElementById('errorDisplay');
    const errorMsg = document.getElementById('errorMsg');
    const summaryPanel = document.getElementById('summaryPanel');
    const resultsGrid = document.getElementById('resultsGrid');

    // Summary spans
    const totalModels = document.getElementById('totalModels');
    const successCount = document.getElementById('successCount');
    const failedCount = document.getElementById('failedCount');
    const totalCost = document.getElementById('totalCost');
    const totalRuntime = document.getElementById('totalRuntime');

    // ---- Helpers -----------------------------------------------
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function show(element) {
        element.style.display = '';
    }

    function hide(element) {
        element.style.display = 'none';
    }

    function getSelectedModels() {
        const checkboxes = modelGrid.querySelectorAll('.model-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    function formatLatency(ms) {
        if (ms === null || ms === undefined) return 'N/A';
        if (ms < 1000) return `${ms.toFixed(2)} ms`;
        return `${(ms / 1000).toFixed(2)} s`;
    }

    function formatCost(cost) {
        if (cost === null || cost === undefined) return 'N/A';
        if (cost < 0.0001) return `$${cost.toFixed(8)}`;
        if (cost < 0.01) return `$${cost.toFixed(6)}`;
        return `$${cost.toFixed(4)}`;
    }

    function formatTokens(val) {
        if (val === null || val === undefined) return 'N/A';
        return val.toLocaleString();
    }

    function getModelInfo(modelId) {
        return models.find(m => m.id === modelId) || {
            name: modelId,
            icon: '🤖',
            provider: 'Unknown'
        };
    }

    // ---- Character Counter -------------------------------------
    questionInput.addEventListener('input', function() {
        charCount.textContent = `${this.value.length} characters`;
    });
    charCount.textContent = `${questionInput.value.length} characters`;

    // ---- Model Select / Deselect All ----------------------------
    selectAllBtn.addEventListener('click', function() {
        modelGrid.querySelectorAll('.model-checkbox').forEach(cb => cb.checked = true);
    });

    deselectAllBtn.addEventListener('click', function() {
        modelGrid.querySelectorAll('.model-checkbox').forEach(cb => cb.checked = false);
    });

    // ---- Compare Button ----------------------------------------
    compareBtn.addEventListener('click', function() {
        if (isProcessing) return;

        const question = questionInput.value.trim();
        if (!question) {
            showError('Please enter a question.');
            return;
        }

        const selected = getSelectedModels();
        if (selected.length === 0) {
            showError('Please select at least one model.');
            return;
        }

        isProcessing = true;
        compareBtn.disabled = true;
        compareBtn.querySelector('.btn-text').textContent = 'Querying...';
        hide(errorDisplay);
        hide(summaryPanel);
        resultsGrid.innerHTML = '';
        show(loadingState);

        fetch('/api/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question, models: selected })
        })
        .then(response => response.json())
        .then(data => {
            hide(loadingState);

            if (data.error) {
                showError(data.error);
                return;
            }

            results = data.results;
            displaySummary(data.summary);
            displayResults(results);
            show(summaryPanel);
        })
        .catch(err => {
            hide(loadingState);
            showError('Network error. Please try again.');
        })
        .finally(() => {
            isProcessing = false;
            compareBtn.disabled = false;
            compareBtn.querySelector('.btn-text').textContent = 'Compare Models';
        });
    });

    // ---- Clear Button ------------------------------------------
    clearBtn.addEventListener('click', function() {
        hide(errorDisplay);
        hide(summaryPanel);
        resultsGrid.innerHTML = '';
        results = [];
    });

    // ---- Display Summary ---------------------------------------
    function displaySummary(summary) {
        totalModels.textContent = summary.total_models;
        successCount.textContent = summary.success_count;
        failedCount.textContent = summary.failed_count;
        totalCost.textContent = formatCost(summary.total_cost);
        totalRuntime.textContent = `${summary.total_runtime.toFixed(2)}s`;
    }

    // ---- Display Results ---------------------------------------
    function displayResults(results) {
        resultsGrid.innerHTML = '';

        // Sort: successes first
        const sorted = [...results].sort((a, b) => {
            if (a.status === 'success' && b.status !== 'success') return -1;
            if (a.status !== 'success' && b.status === 'success') return 1;
            return 0;
        });

        sorted.forEach((result, index) => {
            const modelInfo = getModelInfo(result.model_id);
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${index * 0.06}s`;

            const isSuccess = result.status === 'success';
            const badgeClass = isSuccess ? 'badge-success' : 'badge-error';
            const badgeText = isSuccess ? 'Success' : 'Error';
            const previewText = isSuccess && result.answer
                ? escapeHtml(result.answer.slice(0, 280) + (result.answer.length > 280 ? '...' : ''))
                : `<span class="response-error">${escapeHtml(result.error || 'Unknown error')}</span>`;

            const latencyVal = formatLatency(result.latency_ms);
            const costVal = formatCost(result.cost_usd);
            const inputVal = formatTokens(result.input_tokens);
            const outputVal = formatTokens(result.output_tokens);

            card.innerHTML = `
                <div class="result-card-header">
                    <div class="result-model-info">
                        <span class="result-model-icon">${modelInfo.icon}</span>
                        <span class="result-model-name">${escapeHtml(modelInfo.name)}</span>
                    </div>
                    <span class="${badgeClass}">${badgeText}</span>
                </div>
                <div class="result-body">
                    <div class="response-preview">${previewText}</div>
                    <div class="result-metrics">
                        <div class="metric-block">
                            <span class="metric-label">Latency</span>
                            <span class="metric-value">${latencyVal}</span>
                        </div>
                        <div class="metric-block">
                            <span class="metric-label">Estimated Cost</span>
                            <span class="metric-value">${costVal}</span>
                        </div>
                        <div class="metric-block">
                            <span class="metric-label">Input Tokens</span>
                            <span class="metric-value">${inputVal}</span>
                        </div>
                        <div class="metric-block">
                            <span class="metric-label">Output Tokens</span>
                            <span class="metric-value">${outputVal}</span>
                        </div>
                    </div>
                </div>
                ${isSuccess ? `
                <div class="result-actions">
                    <button class="expand-toggle" data-index="${index}">📄 View Full Response</button>
                </div>
                <div class="full-response" id="fullResponse-${index}">
                    <div class="full-response-content">${escapeHtml(result.answer)}</div>
                </div>
                ` : ''}
            `;

            resultsGrid.appendChild(card);
        });

        // Attach expand/collapse handlers
        document.querySelectorAll('.expand-toggle').forEach(btn => {
            btn.addEventListener('click', function() {
                const idx = this.dataset.index;
                const panel = document.getElementById(`fullResponse-${idx}`);
                const isOpen = panel.classList.contains('open');
                panel.classList.toggle('open');
                this.textContent = isOpen ? '📄 View Full Response' : '📄 Hide Full Response';
            });
        });
    }

    // ---- Error Display -----------------------------------------
    function showError(message) {
        errorMsg.textContent = message;
        show(errorDisplay);

        // Auto-hide after 8 seconds
        setTimeout(() => {
            hide(errorDisplay);
        }, 8000);
    }
});