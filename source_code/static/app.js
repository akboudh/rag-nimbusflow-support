const examplesEl = document.getElementById("examples");
const logsEl = document.getElementById("logs");
const askButton = document.getElementById("ask");
const queryInput = document.getElementById("query");
const answerEl = document.getElementById("answer");
const chunksEl = document.getElementById("chunks");
const contradictionsEl = document.getElementById("contradictions");
const usageEl = document.getElementById("usage");
const runtimePillEl = document.getElementById("runtime-pill");
const embeddingModelEl = document.getElementById("embedding-model");
const responseModelEl = document.getElementById("response-model");
const cacheCountEl = document.getElementById("cache-count");
const runtimeNoteEl = document.getElementById("runtime-note");
const copyAnswerEl = document.getElementById("copy-answer");
const traceSummaryEl = document.getElementById("trace-summary");
const retrievalStepsEl = document.getElementById("retrieval-steps");
const queryCountEl = document.getElementById("query-count");
const clearQueryEl = document.getElementById("clear-query");
let initialQuery = "Do personal API tokens expire after NimbusFlow 4.2?";
let allExamples = [];
let selectedExampleQuery = "";
let allowInitialPrefill = true;
let pipelineTimer = null;
let pipelineStep = 0;

const SOURCE_LABELS = {
  documentation: "Official Docs",
  forum: "Community Threads",
  blog: "Engineering Notes",
};

const SOURCE_COLORS = {
  documentation: "#79d6ef",
  forum: "#c7aa72",
  blog: "#ebb94d",
};

const SOURCE_AUTHORITY = {
  documentation: "Authoritative product source",
  forum: "Community signal",
  blog: "Engineering guidance",
};

const PIPELINE_STEPS = [
  "Embedding query",
  "Searching sources",
  "Reranking evidence",
  "Resolving conflicts",
  "Generating answer",
];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleTimeString([], {hour: "numeric", minute: "2-digit"});
}

function updateQueryCount() {
  const count = queryInput.value.length;
  queryCountEl.textContent = `${count} character${count === 1 ? "" : "s"}`;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderAnswer(answer) {
  const paragraphs = String(answer).trim().split(/\n\s*\n/).filter(Boolean);
  if (!paragraphs.length) {
    answerEl.innerHTML = `<p class="empty-state">Run a query to see the response.</p>`;
    return;
  }

  answerEl.innerHTML = paragraphs
    .map((paragraph, index) => {
      const className = index === 0 ? "answer-lead" : "answer-paragraph";
      return `<p class="${className}">${escapeHtml(paragraph).replaceAll("\n", "<br />")}</p>`;
    })
    .join("");
}

function renderUsage(usage, topChunks = []) {
  usageEl.innerHTML = "";
  const entries = Object.entries(usage).filter(([, count]) => count > 0);
  if (!entries.length) {
    usageEl.innerHTML = `<p class="empty-state">Source usage appears after the first answer.</p>`;
    return;
  }

  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  const rankedCount = topChunks.length;

  const wrapper = document.createElement("div");
  wrapper.className = "evidence-stack";
  wrapper.innerHTML = `
    <div class="evidence-summary">
      <strong>${rankedCount}</strong>
      <span>ranked chunks reviewed across ${entries.length} source types</span>
    </div>
    <p class="evidence-note">Percentages show the source mix in the top ranked evidence, not confidence.</p>
    <div class="evidence-source-list">
      ${entries.map(([source, count]) => {
        const weight = count / total;
        const percent = Math.round(weight * 100);
        return `
          <article class="source-card" style="--source-color: ${SOURCE_COLORS[source] || "#79d6ef"}">
            <div class="source-card-top">
              <strong>${escapeHtml(SOURCE_LABELS[source] || source)}</strong>
              <span>${percent}%</span>
            </div>
            <p>${escapeHtml(SOURCE_AUTHORITY[source] || "Retrieved evidence")}</p>
            <div class="source-meter"><span style="width: ${percent}%"></span></div>
          </article>
        `;
      }).join("")}
    </div>
  `;
  usageEl.appendChild(wrapper);
}

function renderChunks(chunks) {
  chunksEl.innerHTML = "";
  if (!chunks.length) {
    chunksEl.innerHTML = `<p class="empty-state">Top retrieved chunks appear after a query runs.</p>`;
    return;
  }

  chunks.forEach((chunk) => {
    const rerank = Number(chunk.rerank_score) || 0;
    const width = Math.max(10, Math.round(rerank * 100));
    const row = document.createElement("article");
    row.className = "chunk-row";
    row.setAttribute("role", "listitem");
    row.innerHTML = `
      <div class="chunk-header">
        <span class="chunk-tag ${escapeHtml(chunk.source_type)}">${escapeHtml(SOURCE_LABELS[chunk.source_type] || chunk.source_type)}</span>
        <span class="score-number">${rerank.toFixed(2)}</span>
      </div>
      <div class="chunk-title">${escapeHtml(chunk.title)}</div>
      <details class="chunk-details">
        <summary>Excerpt</summary>
        <p class="chunk-copy">${escapeHtml(chunk.text)}</p>
      </details>
      <div class="chunk-score">
        <span class="log-meta">${escapeHtml(chunk.section_title)}</span>
        <div class="score-track"><span style="width: ${width}%"></span></div>
      </div>
    `;
    chunksEl.appendChild(row);
  });
}

function renderContradictions(contradictions) {
  contradictionsEl.innerHTML = "";
  const conflictCopy = contradictions.length
    ? `${contradictions.length} conflict${contradictions.length === 1 ? "" : "s"} detected. Resolution follows the configured source authority order.`
    : "No contradictions were detected in the retrieved evidence.";

  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <div class="contradiction-summary">
      <div>
        <strong>${contradictions.length ? "Conflicts found" : "No conflicts"}</strong>
        <span>${escapeHtml(conflictCopy)}</span>
      </div>
      <span class="conflict-count">${contradictions.length}</span>
    </div>
  `;
  contradictionsEl.appendChild(wrapper);

  if (!contradictions.length) {
    const empty = document.createElement("div");
    empty.className = "contradiction-stack";
    empty.innerHTML = `<div class="contradiction-item"><span class="empty-state">No contradictions detected for the latest answer.</span></div>`;
    contradictionsEl.appendChild(empty);
    return;
  }

  const stack = document.createElement("div");
  stack.className = "contradiction-stack";
  contradictions.forEach((item) => {
    const alternatives = item.alternatives
      .map((alt) => `
        <span>
          <strong>${escapeHtml(SOURCE_LABELS[alt.source_type] || alt.source_type)}</strong>
          ${escapeHtml(alt.value)}
        </span>
      `)
      .join("");
    const card = document.createElement("div");
    card.className = "contradiction-item";
    card.innerHTML = `
      <div class="conflict-card-title">
        <span>Conflict topic</span>
        <strong>${escapeHtml(item.topic)}</strong>
      </div>
      <div class="conflict-grid">
        <span>Winning source</span>
        <strong>${escapeHtml(SOURCE_LABELS[item.preferred.source_type] || item.preferred.source_type)}</strong>
        <span>Decision</span>
        <strong>${escapeHtml(item.preferred.value)}</strong>
      </div>
      <div class="conflict-alternatives">
        <span class="conflict-subhead">Conflicting evidence</span>
        ${alternatives}
      </div>
    `;
    stack.appendChild(card);
  });
  contradictionsEl.appendChild(stack);
}

function renderLogs(logs) {
  logsEl.innerHTML = "";
  if (!logs.length) {
    logsEl.innerHTML = `<p class="empty-state">No retrieval logs yet.</p>`;
    return;
  }

  [...logs].reverse().slice(0, 5).forEach((log) => {
    const totalSources = Object.values(log.source_usage).reduce((sum, value) => sum + value, 0);
    const row = document.createElement("article");
    row.className = "log-card";
    row.setAttribute("role", "listitem");
    row.innerHTML = `
      <div class="log-top">
        <span class="log-query">${escapeHtml(log.query)}</span>
        <span class="log-meta">${formatTime(log.logged_at)}</span>
      </div>
      <div class="log-foot">
        <span>${escapeHtml(log.runtime?.retrieval_provider || "unknown")} • ${escapeHtml(log.runtime?.answer_provider || "unknown")}</span>
        <span class="log-score">${totalSources} sources</span>
      </div>
    `;
    logsEl.appendChild(row);
  });
}

function renderRuntime(runtime) {
  embeddingModelEl.textContent = runtime.embedding_model || "n/a";
  responseModelEl.textContent = runtime.response_model || "n/a";
  if (cacheCountEl) {
    cacheCountEl.textContent = `${runtime.cached_embeddings || 0} / ${runtime.total_chunks || 0}`;
  }

  const configured = Boolean(runtime.openai_configured);
  const ready = runtime.embedding_status === "ready";
  if (configured && ready) {
    runtimePillEl.dataset.state = "ready";
    runtimePillEl.textContent = "Online";
    runtimeNoteEl.textContent = `${runtime.embedding_model} for embeddings and ${runtime.response_model} for answer generation.`;
  } else if (configured) {
    runtimePillEl.dataset.state = "pending";
    runtimePillEl.textContent = "Warming";
    runtimeNoteEl.textContent = runtime.warning || "The first real query will build chunk embeddings.";
  } else {
    runtimePillEl.dataset.state = "fallback";
    runtimePillEl.textContent = "Fallback";
    runtimeNoteEl.textContent = "Add `OPENAI_API_KEY` in `.env` or the shell environment, then restart `python3 server.py`.";
  }

  if (runtime.warning) {
    runtimeNoteEl.textContent = runtime.warning;
  }
}

async function loadExamples() {
  const data = await fetchJson("/api/example-queries");
  allExamples = data.examples;
  renderExamples();
}

function renderExamples() {
  examplesEl.innerHTML = "";
  if (allExamples.length) {
    initialQuery = allExamples[0].query;
    if (allowInitialPrefill && !queryInput.value.trim()) {
      queryInput.value = initialQuery;
      selectedExampleQuery = initialQuery;
      updateQueryCount();
    }
  }

  if (!allExamples.length) {
    return;
  }

  const activeExample = allExamples.find((example) => example.query === selectedExampleQuery);
  const customQuery = queryInput.value.trim();
  const hasSelectedExample = Boolean(activeExample);
  const featuredQuery = hasSelectedExample ? activeExample.query : customQuery || "Write your own support question.";
  const secondaryExamples = hasSelectedExample
    ? allExamples.filter((example) => example.query !== activeExample.query)
    : allExamples;

  const featuredButton = document.createElement("button");
  featuredButton.type = "button";
  featuredButton.className = `example-feature${hasSelectedExample ? " is-active" : ""}`;
  featuredButton.setAttribute("aria-pressed", hasSelectedExample ? "true" : "false");
  if (hasSelectedExample) {
    featuredButton.setAttribute("aria-current", "true");
  }
  featuredButton.innerHTML = `<span>${hasSelectedExample ? "Selected prompt" : "Custom question"}</span><strong>${escapeHtml(featuredQuery)}</strong>`;
  featuredButton.addEventListener("click", () => {
    if (hasSelectedExample) {
      queryInput.value = activeExample.query;
      selectedExampleQuery = activeExample.query;
      allowInitialPrefill = false;
      updateQueryCount();
    }
    queryInput.focus();
  });
  const featuredItem = document.createElement("div");
  featuredItem.setAttribute("role", "listitem");
  featuredItem.appendChild(featuredButton);
  examplesEl.appendChild(featuredItem);

  const list = document.createElement("div");
  list.className = "example-list";

  secondaryExamples.forEach((example) => {
    const item = document.createElement("div");
    item.setAttribute("role", "listitem");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "example-row";
    button.setAttribute("aria-pressed", "false");
    button.textContent = example.query;
    button.addEventListener("click", () => {
      queryInput.value = example.query;
      selectedExampleQuery = example.query;
      allowInitialPrefill = false;
      updateQueryCount();
      renderExamples();
      queryInput.focus();
    });
    item.appendChild(button);
    list.appendChild(item);
  });

  examplesEl.appendChild(list);
}

async function loadLogs() {
  const data = await fetchJson("/api/logs");
  renderLogs(data.logs);
}

async function loadHealth() {
  const data = await fetchJson("/api/health");
  renderRuntime(data);
}

function setLoading(isLoading) {
  document.body.classList.toggle("is-running", isLoading);
  document.getElementById("main").setAttribute("aria-busy", isLoading ? "true" : "false");
  answerEl.setAttribute("aria-busy", isLoading ? "true" : "false");
  traceSummaryEl.setAttribute("aria-busy", isLoading ? "true" : "false");
  askButton.disabled = isLoading;
  askButton.setAttribute("aria-busy", isLoading ? "true" : "false");
  askButton.textContent = isLoading ? "Retrieving..." : "Run Retrieval";
  if (isLoading) {
    startPipeline();
  } else {
    finishPipeline();
  }
}

function updatePipeline(activeIndex, complete = false) {
  const steps = retrievalStepsEl.querySelectorAll("li");
  steps.forEach((step, index) => {
    const state = complete || index < activeIndex
      ? "done"
      : index === activeIndex
        ? "active"
        : "pending";
    step.dataset.state = state;
    step.style.setProperty("--step-delay", `${index * 90}ms`);
  });

  const denominator = Math.max(1, PIPELINE_STEPS.length - 1);
  const progress = complete ? 100 : Math.round((activeIndex / denominator) * 100);
  retrievalStepsEl.style.setProperty("--pipeline-progress", `${progress}%`);
}

function startPipeline() {
  window.clearInterval(pipelineTimer);
  pipelineStep = 0;
  retrievalStepsEl.hidden = false;
  retrievalStepsEl.innerHTML = PIPELINE_STEPS
    .map((step, index) => `<li><span>${index + 1}</span>${escapeHtml(step)}</li>`)
    .join("");
  updatePipeline(0);
  pipelineTimer = window.setInterval(() => {
    pipelineStep = Math.min(pipelineStep + 1, PIPELINE_STEPS.length - 1);
    updatePipeline(pipelineStep);
  }, 850);
}

function finishPipeline() {
  window.clearInterval(pipelineTimer);
  updatePipeline(PIPELINE_STEPS.length - 1, true);
  window.setTimeout(() => {
    if (!document.body.classList.contains("is-running")) {
      retrievalStepsEl.hidden = true;
    }
  }, 900);
}

async function runQuery() {
  const query = queryInput.value.trim();
  if (!query) {
    return;
  }

  setLoading(true);
  try {
    const payload = await fetchJson("/api/query", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({query}),
    });

    renderAnswer(payload.answer);
    renderUsage(payload.source_usage, payload.top_chunks);
    renderChunks(payload.top_chunks);
    renderContradictions(payload.contradictions);
    traceSummaryEl.textContent = `${payload.top_chunks.length} ranked chunks • ${Object.values(payload.source_usage).reduce((sum, value) => sum + value, 0)} cited sources`;
    if (payload.runtime) {
      renderRuntime(payload.runtime);
    } else {
      await loadHealth();
    }
    await loadLogs();
  } catch (error) {
    renderAnswer(`Error: ${error.message}`);
    traceSummaryEl.textContent = "Query failed.";
  } finally {
    setLoading(false);
  }
}

function clearResults() {
  renderAnswer("Run a query to see the response.");
  usageEl.innerHTML = `<p class="empty-state">Source usage appears after the first answer.</p>`;
  chunksEl.innerHTML = `<p class="empty-state">Top retrieved chunks appear after a query runs.</p>`;
  contradictionsEl.innerHTML = `<p class="empty-state">Contradiction analysis appears after a query runs.</p>`;
  traceSummaryEl.textContent = "Ready for the next support question.";
}

function resetWorkspace() {
  queryInput.value = "";
  selectedExampleQuery = "";
  allowInitialPrefill = true;
  updateQueryCount();
  clearResults();
  queryInput.focus();
}

askButton.addEventListener("click", runQuery);
clearQueryEl.addEventListener("click", () => {
  queryInput.value = "";
  selectedExampleQuery = "";
  allowInitialPrefill = false;
  updateQueryCount();
  clearResults();
  renderExamples();
  queryInput.focus();
});

queryInput.addEventListener("input", () => {
  selectedExampleQuery = "";
  allowInitialPrefill = false;
  updateQueryCount();
  renderExamples();
});

queryInput.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    runQuery();
  }
});

copyAnswerEl.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(answerEl.innerText.trim());
    copyAnswerEl.textContent = "Copied";
    window.setTimeout(() => {
      copyAnswerEl.textContent = "Copy";
    }, 1200);
  } catch {
    copyAnswerEl.textContent = "Unavailable";
    window.setTimeout(() => {
      copyAnswerEl.textContent = "Copy";
    }, 1200);
  }
});

resetWorkspace();
loadExamples().catch(console.error);
loadLogs().catch(console.error);
loadHealth().catch(console.error);
