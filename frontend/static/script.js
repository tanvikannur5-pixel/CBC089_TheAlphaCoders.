/**
 * Intelligent Customer Intent Detector - Client Application
 */

const API_BASE = ""; // Same origin

let supportedIntents = [];
let activePrediction = null;
let intentChartInstance = null;
let statusChartInstance = null;
let langChartInstance = null;

// Safe DOM element builder
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined && text !== null) {
    node.textContent = String(text);
  }
  if (className) {
    node.className = className;
  }
  return node;
}

// API request wrapper with timeout and error handling
async function api(path, options = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 12000);
  try {
    const res = await fetch(API_BASE + path, {
      ...options,
      signal: ctrl.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error?.message || `Request failed with status ${res.status}`);
    }
    return data;
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Server took too long to respond. Please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

// Alert banner display
function showBanner(message, retryFn = null) {
  const container = document.getElementById("banner-container");
  const msgEl = document.getElementById("banner-message");
  if (!container || !msgEl) return;
  msgEl.textContent = message;
  container.style.display = "block";
}

function hideBanner() {
  const container = document.getElementById("banner-container");
  if (container) container.style.display = "none";
}

// Hash-based client router
function initRouter() {
  function handleRoute() {
    const hash = window.location.hash || "#home";
    const route = hash.replace("#", "") || "home";

    document.querySelectorAll(".view-section").forEach((sec) => {
      sec.style.display = "none";
    });
    document.querySelectorAll(".nav-item").forEach((link) => {
      link.classList.remove("active");
    });

    const targetSec = document.getElementById(`view-${route}`);
    const targetNav = document.getElementById(`nav-${route}`);

    if (targetSec) targetSec.style.display = "block";
    if (targetNav) targetNav.classList.add("active");

    window.scrollTo({ top: 0, behavior: "smooth" });

    if (route === "review") loadReviewQueue();
    if (route === "dashboard") loadDashboard();
  }

  window.addEventListener("hashchange", handleRoute);
  handleRoute();
}

// Load system health & supported intents
async function loadSystemMetadata() {
  try {
    const health = await api("/api/health");
    const statusText = document.getElementById("system-status-text");
    const modeBadge = document.getElementById("model-mode-badge");

    if (statusText) {
      statusText.textContent = health.detector_mode === "trained" ? "Model Trained" : "Keyword Fallback";
    }
    if (modeBadge) {
      modeBadge.textContent = `Model: ${health.detector_mode.replace("_", " ").toUpperCase()}`;
      if (health.detector_mode === "keyword_fallback") {
        modeBadge.className = "badge badge-needs_clarification";
      }
    }

    const data = await api("/api/intents");
    supportedIntents = data.intents || [];
    populateIntentsDropdown();
  } catch (err) {
    console.warn("Could not load initial metadata:", err.message);
  }
}

function populateIntentsDropdown() {
  const select = document.getElementById("correct-intent-select");
  if (!select) return;
  select.replaceChildren();

  const defOpt = document.createElement("option");
  defOpt.value = "";
  defOpt.textContent = "Select Correction...";
  select.appendChild(defOpt);

  supportedIntents.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item.label;
    opt.textContent = item.display;
    select.appendChild(opt);
  });
}

// Setup Analyze Form and Message Input
function initAnalyzeForm() {
  const input = document.getElementById("message-input");
  const counter = document.getElementById("char-counter");
  const form = document.getElementById("analyze-form");
  const clearBtn = document.getElementById("btn-clear-input");

  if (input && counter) {
    input.addEventListener("input", () => {
      const len = input.value.length;
      counter.textContent = `${len} / 1000`;
      if (len > 1000) {
        counter.classList.add("limit-exceeded");
      } else {
        counter.classList.remove("limit-exceeded");
      }
      document.getElementById("field-error-hint").textContent = "";
    });
  }

  if (clearBtn && input) {
    clearBtn.addEventListener("click", () => {
      input.value = "";
      counter.textContent = "0 / 1000";
      input.focus();
    });
  }

  // Pre-load benchmark sample chips
  document.querySelectorAll(".chip-btn").forEach((chip) => {
    chip.addEventListener("click", () => {
      const msg = chip.getAttribute("data-msg");
      if (input && msg) {
        input.value = msg;
        input.dispatchEvent(new Event("input"));
        input.focus();
      }
    });
  });

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await onAnalyzeSubmit();
    });
  }

  // Human feedback action listeners
  const confirmBtn = document.getElementById("btn-confirm-prediction");
  const correctBtn = document.getElementById("btn-submit-correction");

  if (confirmBtn) {
    confirmBtn.addEventListener("click", () => sendFeedback("confirm"));
  }
  if (correctBtn) {
    correctBtn.addEventListener("click", () => {
      const select = document.getElementById("correct-intent-select");
      if (!select || !select.value) {
        alert("Please choose an intent from the dropdown first.");
        return;
      }
      sendFeedback("correct", select.value);
    });
  }
}

async function onAnalyzeSubmit() {
  const input = document.getElementById("message-input");
  const btn = document.getElementById("btn-analyze");
  const spinner = document.getElementById("analyze-spinner");
  const btnText = document.getElementById("analyze-btn-text");
  const errorHint = document.getElementById("field-error-hint");

  const message = input.value.trim();
  if (!message) {
    errorHint.textContent = "Please enter a message to analyze.";
    errorHint.className = "form-hint error";
    return;
  }

  btn.disabled = true;
  spinner.style.display = "inline-block";
  btnText.textContent = "Analyzing...";
  hideBanner();

  try {
    const result = await api("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ message, save: true }),
    });
    activePrediction = result;
    renderAnalysisResult(result);
  } catch (err) {
    showBanner(`Analysis failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    spinner.style.display = "none";
    btnText.textContent = "Analyze Intent";
  }
}

// Render Result Card
function renderAnalysisResult(result) {
  const placeholder = document.getElementById("empty-results-placeholder");
  const content = document.getElementById("result-card-content");
  if (placeholder) placeholder.style.display = "none";
  if (content) content.style.display = "block";

  // Badges & Status
  const statusBadge = document.getElementById("res-status-badge");
  statusBadge.textContent = result.status.replace("_", " ").toUpperCase();
  statusBadge.className = `badge badge-${result.status}`;

  const langBadge = document.getElementById("res-lang-badge");
  const langNames = { en: "English", kn: "Kannada", "kn-latn": "Kanglish", mixed: "Mixed Script", unknown: "Unknown" };
  langBadge.textContent = langNames[result.language] || result.language;

  const urgentBadge = document.getElementById("res-urgency-badge");
  urgentBadge.style.display = result.urgency === "high" ? "inline-flex" : "none";

  const idTag = document.getElementById("res-id-tag");
  idTag.textContent = result.id ? `ID: #${result.id}` : "Unsaved";

  // Primary Intent & Model Score
  const topIntent = result.intents[0] || { label: "unknown", display: "Unknown", confidence: 0 };
  document.getElementById("res-intent-title").textContent = topIntent.display;

  const scorePct = Math.round(topIntent.confidence * 100);
  const scoreEl = document.getElementById("res-score-percent");
  const scoreBar = document.getElementById("res-score-bar");
  scoreEl.textContent = `${scorePct}%`;
  scoreBar.style.width = `${Math.max(5, scorePct)}%`;

  if (topIntent.confidence >= 0.55) {
    scoreBar.style.backgroundColor = "var(--status-ok)";
    scoreEl.style.color = "var(--status-ok)";
  } else if (topIntent.confidence >= 0.35) {
    scoreBar.style.backgroundColor = "var(--status-warn)";
    scoreEl.style.color = "var(--status-warn)";
  } else {
    scoreBar.style.backgroundColor = "var(--status-bad)";
    scoreEl.style.color = "var(--status-bad)";
  }

  // Multi-intent Breakdown
  const multiBlock = document.getElementById("res-multi-block");
  const multiList = document.getElementById("res-multi-list");
  if (result.multi_intent && result.intents.length >= 2) {
    multiBlock.style.display = "block";
    multiList.replaceChildren();
    result.intents.forEach((item) => {
      const itemEl = el("div", "", "multi-intent-item");
      const titleSpan = el("strong", `${item.display} (${Math.round(item.confidence * 100)}%) `);
      itemEl.appendChild(titleSpan);
      if (item.clause) {
        const clauseSpan = el("span", `– "${item.clause}"`, "clause-text");
        itemEl.appendChild(clauseSpan);
      }
      multiList.appendChild(itemEl);
    });
  } else {
    multiBlock.style.display = "none";
  }

  // Alternatives / Runner-up
  const altBlock = document.getElementById("res-alternatives-block");
  const altText = document.getElementById("res-alternatives-text");
  if (result.alternatives && result.alternatives.length > 0) {
    altBlock.style.display = "block";
    const alt = result.alternatives[0];
    altText.textContent = `${alt.display} (${Math.round(alt.confidence * 100)}%)`;
  } else {
    altBlock.style.display = "none";
  }

  // Extracted Entities
  const entityContainer = document.getElementById("res-entities-container");
  entityContainer.replaceChildren();
  if (result.entities && result.entities.length > 0) {
    result.entities.forEach((ent) => {
      const chip = el("span", "", "entity-chip");
      chip.appendChild(el("strong", `${ent.type}:`));
      chip.appendChild(document.createTextNode(` ${ent.value}`));
      entityContainer.appendChild(chip);
    });
  } else {
    entityContainer.appendChild(el("span", "None detected", "empty-entity-hint"));
  }

  // Clarification Prompts
  const clarifyBox = document.getElementById("res-clarification-box");
  const clarifyText = document.getElementById("res-clarification-text");
  if (result.clarification_question) {
    clarifyBox.style.display = "block";
    clarifyText.textContent = result.clarification_question;
  } else {
    clarifyBox.style.display = "none";
  }

  // Routing Team & Priority
  const teams = result.route_to?.teams || [];
  const routingTarget = document.getElementById("res-routing-target");
  routingTarget.textContent = teams.length > 0 ? teams.join(", ") : "No routing required";

  const routingPriority = document.getElementById("res-routing-priority");
  routingPriority.textContent = (result.route_to?.priority || "Normal").toUpperCase();
  routingPriority.style.color = result.route_to?.priority === "high" ? "var(--status-urgent)" : "var(--text-secondary)";

  // Masked Text & PII Summary
  const maskedPre = document.getElementById("res-masked-text");
  maskedPre.textContent = result.message_masked || "";

  const piiCountBadge = document.getElementById("res-pii-counts");
  const piiKeys = Object.keys(result.pii_masked || {});
  if (piiKeys.length > 0) {
    const sum = Object.values(result.pii_masked).reduce((a, b) => a + b, 0);
    piiCountBadge.textContent = `${sum} PII item(s) masked (${piiKeys.join(", ")})`;
    piiCountBadge.style.color = "var(--status-ok)";
  } else {
    piiCountBadge.textContent = "0 PII tokens detected";
    piiCountBadge.style.color = "var(--text-muted)";
  }

  // Feedback action bar reset
  document.getElementById("feedback-status-msg").textContent = "";
  const confirmBtn = document.getElementById("btn-confirm-prediction");
  const correctBtn = document.getElementById("btn-submit-correction");
  const select = document.getElementById("correct-intent-select");

  confirmBtn.disabled = !result.id;
  correctBtn.disabled = !result.id;
  select.disabled = !result.id;
  select.value = "";
}

// Submit Human Review Feedback
async function sendFeedback(action, correctedIntent = null) {
  if (!activePrediction || !activePrediction.id) {
    alert("This prediction has not been saved in the database.");
    return;
  }
  const feedbackMsg = document.getElementById("feedback-status-msg");
  feedbackMsg.textContent = "Saving review...";
  feedbackMsg.style.color = "var(--text-muted)";

  try {
    const payload = { prediction_id: activePrediction.id, action };
    if (action === "correct") payload.corrected_intent = correctedIntent;

    const res = await api("/api/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    feedbackMsg.textContent = action === "confirm" ? "✓ Confirmed by reviewer!" : `✓ Corrected to ${correctedIntent}!`;
    feedbackMsg.style.color = "var(--status-ok)";

    // Update queue badge if open
    loadReviewQueueCount();
  } catch (err) {
    feedbackMsg.textContent = `Error: ${err.message}`;
    feedbackMsg.style.color = "var(--status-bad)";
  }
}

// Load and Render Review Queue
async function loadReviewQueue() {
  const container = document.getElementById("review-queue-list");
  if (!container) return;

  try {
    const data = await api("/api/history?limit=30&review=pending");
    const items = data.items || [];
    container.replaceChildren();

    // Update badge counter
    const badge = document.getElementById("nav-review-badge");
    if (badge) badge.textContent = String(items.length);

    if (items.length === 0) {
      const emptyCard = el("div", "", "empty-queue-card card");
      emptyCard.appendChild(el("span", "✅", "empty-icon"));
      emptyCard.appendChild(el("h3", "Review Queue Is Clear"));
      emptyCard.appendChild(el("p", "No messages waiting for human review at this time."));
      container.appendChild(emptyCard);
      return;
    }

    items.forEach((item) => {
      const card = el("div", "", "review-queue-item card");
      const header = el("div", "", "review-queue-header");

      const idBadge = el("span", `Prediction #${item.id}`, "prediction-id-tag");
      const statusBadge = el("span", item.status.replace("_", " "), `badge badge-${item.status}`);
      header.append(idBadge, statusBadge);

      const msgPre = el("pre", item.message_masked, "masked-text-pre");
      const intentInfo = el(
        "p",
        `Predicted: ${item.top_intent} (Model score: ${Math.round(item.confidence * 100)}%)`,
        "intent-info-line"
      );

      const actionRow = el("div", "", "review-actions-group");
      actionRow.style.marginTop = "0.75rem";

      const btnConfirm = el("button", "Confirm ✓", "btn btn-sm btn-success");
      btnConfirm.addEventListener("click", async () => {
        await api("/api/feedback", {
          method: "POST",
          body: JSON.stringify({ prediction_id: item.id, action: "confirm" }),
        });
        loadReviewQueue();
      });

      const selCorrect = el("select", "", "form-select form-select-sm");
      supportedIntents.forEach((si) => {
        const opt = document.createElement("option");
        opt.value = si.label;
        opt.textContent = si.display;
        if (si.label === item.top_intent) opt.selected = true;
        selCorrect.appendChild(opt);
      });

      const btnCorrect = el("button", "Save Correction", "btn btn-sm btn-outline");
      btnCorrect.addEventListener("click", async () => {
        await api("/api/feedback", {
          method: "POST",
          body: JSON.stringify({
            prediction_id: item.id,
            action: "correct",
            corrected_intent: selCorrect.value,
          }),
        });
        loadReviewQueue();
      });

      actionRow.append(btnConfirm, selCorrect, btnCorrect);
      card.append(header, msgPre, intentInfo);

      if (item.clarification_question) {
        const qBox = el("div", item.clarification_question, "clarification-text");
        qBox.style.color = "#fcd34d";
        qBox.style.fontSize = "0.85rem";
        qBox.style.margin = "0.4rem 0";
        card.appendChild(qBox);
      }

      card.appendChild(actionRow);
      container.appendChild(card);
    });
  } catch (err) {
    console.warn("Could not load review queue:", err.message);
  }
}

async function loadReviewQueueCount() {
  try {
    // Stats are aggregated across all records; a limited history response is
    // only a page of results and cannot provide an accurate queue count.
    const data = await api("/api/stats");
    const count = data.pending_review || 0;
    const badge = document.getElementById("nav-review-badge");
    if (badge) badge.textContent = String(count);
  } catch (e) {
    // ignore
  }
}

// Load and Render Analytics Dashboard
async function loadDashboard() {
  try {
    const statsData = await api("/api/stats");
    const historyData = await api("/api/history?limit=50");

    // KPI Updates
    document.getElementById("kpi-total").textContent = String(statsData.total || 0);
    document.getElementById("kpi-pending").textContent = String(statsData.pending_review || 0);
    document.getElementById("kpi-urgent").textContent = String(statsData.high_urgency || 0);

    const agreement = statsData.reviewer_agreement;
    document.getElementById("kpi-agreement").textContent =
      agreement !== null && agreement !== undefined ? `${Math.round(agreement * 100)}%` : "--";

    // Chart.js Visualizations (destroy old instances first)
    if (window.Chart) {
      renderIntentChart(statsData.by_intent || {});
      renderStatusChart(statsData.by_status || {});
      renderLangChart(statsData.by_language || {});
    }

    // Render Recent History Table
    renderHistoryTable(historyData.items || []);
  } catch (err) {
    showBanner(`Could not load dashboard stats: ${err.message}`);
  }
}

function renderIntentChart(intentMap) {
  const canvas = document.getElementById("intentChart");
  if (!canvas) return;
  if (intentChartInstance) intentChartInstance.destroy();

  const labels = Object.keys(intentMap).map((k) => k.replace("_", " "));
  const values = Object.values(intentMap);

  intentChartInstance = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Messages",
          data: values,
          backgroundColor: "#3b82f6",
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8", font: { size: 10 } }, grid: { display: false } },
        y: { ticks: { color: "#94a3b8", stepSize: 1 }, grid: { color: "#1e293b" } },
      },
    },
  });
}

function renderStatusChart(statusMap) {
  const canvas = document.getElementById("statusChart");
  if (!canvas) return;
  if (statusChartInstance) statusChartInstance.destroy();

  const labels = Object.keys(statusMap).map((k) => k.replace("_", " "));
  const values = Object.values(statusMap);

  statusChartInstance = new Chart(canvas, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data: values,
          backgroundColor: ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#64748b"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { color: "#cbd5e1", font: { size: 11 } } },
      },
    },
  });
}

function renderLangChart(langMap) {
  const canvas = document.getElementById("langChart");
  if (!canvas) return;
  if (langChartInstance) langChartInstance.destroy();

  const labels = Object.keys(langMap);
  const values = Object.values(langMap);

  langChartInstance = new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Volume",
          data: values,
          backgroundColor: ["#8b5cf6", "#ec4899", "#06b6d4", "#f97316"],
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
        y: { ticks: { color: "#94a3b8", stepSize: 1 }, grid: { color: "#1e293b" } },
      },
    },
  });
}

function renderHistoryTable(items) {
  const tbody = document.getElementById("history-table-body");
  if (!tbody) return;
  tbody.replaceChildren();

  if (items.length === 0) {
    const tr = el("tr");
    const td = el("td", "No messages in history yet.", "text-center");
    td.colSpan = 7;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  items.forEach((row) => {
    const tr = el("tr");
    tr.appendChild(el("td", `#${row.id}`));
    tr.appendChild(el("td", (row.created_at || "").substring(11, 19) || "--"));

    const textTd = el("td", (row.message_masked || "").substring(0, 35) + "...");
    tr.appendChild(textTd);

    tr.appendChild(el("td", row.top_intent || "--"));
    tr.appendChild(el("td", `${Math.round((row.confidence || 0) * 100)}%`));

    const statusTd = el("td");
    statusTd.appendChild(el("span", row.status || "--", `badge badge-${row.status}`));
    tr.appendChild(statusTd);

    const reviewTd = el("td");
    const rStatus = row.review_status || "not_required";
    reviewTd.appendChild(el("span", rStatus, rStatus === "confirmed" ? "badge badge-confident" : "badge badge-outline"));
    tr.appendChild(reviewTd);

    tbody.appendChild(tr);
  });
}

// Global initialization
document.addEventListener("DOMContentLoaded", () => {
  initRouter();
  loadSystemMetadata();
  initAnalyzeForm();

  const bannerClose = document.getElementById("banner-close");
  if (bannerClose) {
    bannerClose.addEventListener("click", hideBanner);
  }

  const refreshQueueBtn = document.getElementById("btn-refresh-queue");
  if (refreshQueueBtn) {
    refreshQueueBtn.addEventListener("click", loadReviewQueue);
  }

  const refreshDashBtn = document.getElementById("btn-refresh-dashboard");
  if (refreshDashBtn) {
    refreshDashBtn.addEventListener("click", loadDashboard);
  }
});
