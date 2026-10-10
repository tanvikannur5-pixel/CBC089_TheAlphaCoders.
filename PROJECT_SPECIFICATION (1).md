# PROJECT_SPECIFICATION.md

# Intelligent Customer Intent Detector

> *"Catch the Intent. Clarify the Need. Trigger the Action."*

| | |
|---|---|
| **Hackathon** | CBC 2.0, Design Round |
| **Team** | The Alpha Coders (Team ID CBC089) |
| **Domain** | Artificial Intelligence and Machine Learning |
| **Problem ID** | PS-030 |
| **Submitted deck names** | "Decode The Unsaid" (title slide) and "SmartIntent AI" (slide 7). This document uses **Intelligent Customer Intent Detector**. Pick one public name before the demo. |

**How to read this document**

- Tags used throughout: **[PPT]** = promised or implied in the submitted deck, **[ADD]** = our own additional suggestion.
- Priority tags: **MVP** (must work in the demo), **SHOULD** (build if time allows), **OPTIONAL** (only after everything else works).
- Nothing in this document claims achieved accuracy or completed functionality. All scores and numbers are illustrative until you measure them (Sections 9 and 11).

---

## Table of Contents

0. [Analysis of the Submitted PPT](#0-analysis-of-the-submitted-ppt)
1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Recommended Technology Stack](#3-recommended-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Website Pages and UI](#5-website-pages-and-ui)
6. [Project Structure and File Requirements](#6-project-structure-and-file-requirements)
7. [AI/NLP Implementation](#7-ainlp-implementation)
8. [Backend API Design](#8-backend-api-design)
9. [Sample Data and Expected Output](#9-sample-data-and-expected-output)
10. [Privacy and Security](#10-privacy-and-security)
11. [Testing and Evaluation](#11-testing-and-evaluation)
12. [Team Division](#12-team-division)
13. [Setup and Execution](#13-setup-and-execution)
14. [Development Roadmap](#14-development-roadmap)
15. [Final Deliverables and Demo Checklist](#15-final-deliverables-and-demo-checklist)

---

## 0. Analysis of the Submitted PPT

### 0.1 What the deck actually commits to

| ID | Commitment | Slide | Where it is implemented here |
|---|---|---|---|
| P-01 | Intelligent intent classification (NLP, ML, text classification) | 5 | §2 F1, §7 |
| P-02 | Context-aware entity extraction: order IDs, products, dates, amounts (NER + information extraction) | 5 | §2 F2, §7.6 |
| P-03 | Multilingual intent detection: Kannada, English, mixed-language text; language detection | 4, 5 | §2 F3, §7.7 |
| P-04 | Multi-intent detection (multi-label classification, intent ranking) | 5 | §2 F4, §7.9 |
| P-05 | Confidence and ambiguity analysis; clarification for unclear messages | 4, 5 | §2 F5, §7.8 |
| P-06 | Privacy-aware processing: PII detection, anonymization, data minimization, controlled retention | 4, 5 | §2 F6, §10 |
| P-07 | Web interface: message input, intent review, human correction | 6 | §2 F7-F8, §5 |
| P-08 | Human feedback and correction; "Feedback Learning" in the Data & AI layer | 4, 6 | §2 F8-F9 |
| P-09 | Intent routing and confidence thresholds in the application layer | 6 | §2 F10, §7.8 |
| P-10 | Python API, request processing, REST API | 6 | §8 |
| P-11 | MySQL database | 6 | §3, §6 |
| P-12 | Scikit-learn for ML | 6 | §7 |
| P-13 | Workflow: Message → Intent Detection → Entity Extraction → Confidence Scoring → Human Review | 6 | §4 |
| P-14 | Configurable intents; batch/API processing; modular architecture; lightweight open-source stack | 7 | §2 F11-F12 |
| P-15 | Example: "payment failure + deduction" implies refund intent with high urgency | 3 | §2 F13, sample M3 |
| P-16 | Risks mitigated by confidence thresholds, encryption, human-in-the-loop | 8 | §10 |
| P-17 | Design in Figma; Frontend HTML/CSS/JavaScript; Backend Python/Flask | 6 | §3, §5 |

### 0.2 What the deck leaves open (we decide here)

| Open item | Our decision |
|---|---|
| Which classifier exactly | TF-IDF (word + character n-grams) + Logistic Regression in scikit-learn |
| How Kannada is supported | Character n-grams, Kannada and romanized-Kannada training examples, script-based language detection |
| How entities are extracted | Regex rules plus a product gazetteer (spaCy optional) |
| How "encryption" (slide 8) is applied | TLS in transit when deployed, encrypted database connection/disk where available; we do **not** build custom encryption |
| Charts library | Chart.js |
| Where the frontend runs | Served by Flask itself (no CORS setup needed) |

### 0.3 Note on the deck's typo

The tech-stack slide says "PHYTON". It means **Python**.

---

## 1. Project Overview

### 1.1 The problem

Customers rarely write "I want to raise a refund request for order 48213." They write *"Money got cut but order not showing"* or *"nanna order yelli ide"* (Kannada written in English letters). Support teams then triage messages by hand, which causes:

- **Intent ambiguity**: one sentence can mean several things.
- **Contextual blindness**: keyword rules ignore what surrounds the words.
- **Manual triage and misrouting**: tickets reach the wrong team and get transferred.
- **Business cost**: slower replies, higher support cost, SLA breaches, lower CSAT.

### 1.2 Target users

| User | What they do in the system |
|---|---|
| **Support agent / reviewer** | Reads the predicted intent, confirms or corrects uncertain predictions |
| **Support team lead** | Watches the dashboard: intent mix, review queue size, urgency |
| **Business (e-commerce, banking, telecom)** | Integrates through the REST API |
| **Customer (indirect)** | Receives clarification questions and faster routing |

### 1.3 Main objective

Build a working prototype that takes a raw customer message (English, Kannada or mixed) and returns:
1. the intent(s) with a model score,
2. extracted entities (order ID, product, date, amount),
3. a routing suggestion and urgency,
4. a clarification question when unsure,
5. a human-review path whose corrections feed back into training,

while masking personal data before anything is stored.

### 1.4 How it works (summary)

```
Message → validate → normalize → detect language → extract entities
        → mask PII → classify intent (scores for all intents)
        → split clauses for multi-intent → apply thresholds
        → route OR ask clarification OR send to human review
        → store masked result in MySQL → show on dashboard
        → human corrections become new training data
```

### 1.5 Why this beats manual or keyword-only approaches

| Aspect | Manual / keyword rules | This system |
|---|---|---|
| Implicit intent | Misses it ("money got cut") | Learns phrasing patterns from examples |
| Typos, code-mixing | Needs a rule for every variant | Character n-grams tolerate spelling variants |
| Multiple requests | One label per ticket | Splits and labels each request |
| Uncertainty | Silent wrong guess | Flags it and asks a targeted question |
| Maintenance | Rule lists grow forever | Add examples and retrain |
| Privacy | Raw text everywhere | PII masked before storage |

**Honest caveat:** a small hand-made dataset gives a *prototype*, not a production-grade model. Section 7 explains how to be truthful about this in the demo.

---

## 2. Features

### 2.1 Feature summary

| ID | Feature | Source | Priority |
|---|---|---|---|
| F1 | Intelligent intent classification | [PPT] Feature 1 | **MVP** |
| F2 | Context-aware entity extraction | [PPT] Feature 2 | **MVP** |
| F3 | Multilingual intent detection (Kannada, English, mixed) | [PPT] Feature 3 | **MVP** (basic) |
| F4 | Multi-intent detection | [PPT] Feature 4 | **MVP-lite** (clause-based) |
| F5 | Confidence and ambiguity analysis + clarification questions | [PPT] Feature 5 | **MVP** |
| F6 | Privacy-aware processing | [PPT] Feature 6 | **MVP** |
| F7 | Web interface: message input, intent review | [PPT] User layer | **MVP** |
| F8 | Human correction (human-in-the-loop) | [PPT] | **MVP** |
| F9 | Feedback learning (retrain from corrections) | [PPT] Data & AI layer | **SHOULD** |
| F10 | Intent routing to teams | [PPT] Application layer | **MVP** (simple mapping) |
| F11 | Configurable intents (JSON-driven) | [PPT] slide 7 | **SHOULD** |
| F12 | REST API incl. batch processing | [PPT] slides 6-7 | single: **MVP**, batch: **SHOULD** |
| F13 | Urgency indication | [PPT] implied by slide 3 example | **SHOULD** |
| F14 | MySQL storage of masked results and feedback | [PPT] slide 6 | **MVP** |
| A1 | Analytics dashboard with charts | [ADD] | **SHOULD** |
| A2 | Explainability: top words behind a prediction | [ADD] | OPTIONAL |
| A3 | Suggested reply templates per intent | [ADD] | OPTIONAL |
| A4 | CSV import/export of messages and results | [ADD] | OPTIONAL |
| A5 | Rule-based sentiment indicator | [ADD] | OPTIONAL |
| A6 | Multilingual embedding model upgrade | [ADD] | OPTIONAL |
| A7 | Reviewer login | [ADD] | OPTIONAL |
| A8 | Dark mode and Kannada UI labels | [ADD] | OPTIONAL |

### 2.2 Promised features, detailed

#### F1 Intelligent Intent Classification **[PPT] MVP**
1. **What it does:** maps a message to one of the supported intents (§7.1) and returns a ranked list with scores.
2. **Why useful:** replaces manual reading and keyword rules; enables routing.
3. **How:** TF-IDF features → Logistic Regression → `predict_proba` for every class; top-k returned. Trained from `data/training_data.csv`.
4. **Tech:** scikit-learn, pandas, joblib.
5. **Priority:** MVP. Without it nothing else works.

#### F2 Context-Aware Entity Extraction **[PPT] MVP**
1. **What:** finds order IDs, products, dates, amounts, plus issue terms (e.g. "deducted", "damaged").
2. **Why:** agents do not have to re-ask for details; routing and clarification use missing-entity checks.
3. **How:** regular expressions for IDs/amounts/dates with context words ("order", "#", "Rs."), a product gazetteer file (`data/products.txt`), and a small issue-term lexicon. "Context-aware" here means an ID is accepted only next to order context (e.g. `order 48213`, `#48213`, `ORD-48213`), not any random number.
4. **Tech:** Python `re`; spaCy `EntityRuler` is an optional upgrade.
5. **Priority:** MVP.

#### F3 Multilingual Intent Detection **[PPT] MVP (basic)**
1. **What:** handles English, Kannada script, romanized Kannada ("Kanglish") and mixed text; reports detected language.
2. **Why:** a large share of real customers write code-mixed text; keyword systems fail on it.
3. **How:** (a) language detection by Unicode script ratio plus a small list of romanized-Kannada hint words; (b) character n-gram TF-IDF so one model learns from all scripts; (c) include Kannada and romanized examples for every intent in the training data.
4. **Tech:** Python `re`/`unicodedata`; scikit-learn char n-grams. Optional: multilingual embeddings (A6).
5. **Priority:** MVP in basic form. **Limitation:** quality in Kannada depends entirely on how many Kannada examples you write. A native speaker on the team must review them.

#### F4 Multi-Intent Detection **[PPT] MVP-lite**
1. **What:** finds several requests in one message ("cancel my order and refund the money").
2. **Why:** customers combine requests; single-label systems drop one.
3. **How:** split the message into clauses (sentence ends, "and", "but", commas, Kannada connectors), classify each clause, keep distinct intents above a clause threshold, rank by score. (A true multi-label model needs multi-label training data, which a student team rarely has. Clause-based detection reuses the single-label classifier.)
4. **Tech:** Python `re`, the same scikit-learn model.
5. **Priority:** MVP-lite. **Limitation:** two intents in one clause without a connector ("late delivery, terrible service") may be missed; see sample M7.

#### F5 Confidence & Ambiguity Analysis **[PPT] MVP**
1. **What:** decides per message: `confident`, `multi_intent`, `needs_clarification`, `unknown`, or `unsupported`; asks a targeted question when unsure.
2. **Why:** a wrong silent guess is worse than a question.
3. **How:** use top score, the gap ("margin") between the top two intents, and tunable thresholds; map common confusable pairs to specific questions (§7.8).
4. **Tech:** plain Python logic over model scores.
5. **Priority:** MVP.

#### F6 Privacy-Aware Processing **[PPT] MVP**
1. **What:** detects PII (email, phone, card numbers, UPI IDs, PAN, Aadhaar-format numbers, OTP phrases), masks it, stores only masked text, supports retention limits and purge.
2. **Why:** support messages often contain sensitive data; storing it raw is a liability.
3. **How:** regex plus Luhn check for cards; extract entities *before* masking so order IDs survive; classify and store the masked text only; `STORE_MASKED_TEXT` switch; `RETENTION_DAYS` + purge command (§10).
4. **Tech:** Python `re`.
5. **Priority:** MVP. Regex PII detection misses unusual formats; do not claim full compliance.

#### F7 Web Interface **[PPT] MVP**
Message input, results view (intent, score, entities, routing), review screen. See §5. Tech: HTML, CSS, JavaScript (Figma for design, per the deck).

#### F8 Human Correction **[PPT] MVP**
1. **What:** a reviewer confirms or corrects a prediction; uncertain predictions are queued.
2. **Why:** keeps humans in control of low-confidence decisions and creates labelled data.
3. **How:** `POST /api/feedback` updates the stored row; the review queue lists `needs_review = true` rows.
4. **Tech:** Flask + SQLAlchemy + MySQL; vanilla JS.
5. **Priority:** MVP.

#### F9 Feedback Learning **[PPT] SHOULD**
Corrected predictions (masked text + correct label) are exported by `python -m training.train --include-feedback` into the next training run. This is **batch retraining**, not live learning. Say so in the demo.

#### F10 Intent Routing **[PPT] MVP (simple)**
Each intent maps to a team in `data/intents.json`. Confident results show "Route to: Refunds & Billing"; uncertain ones go to "Human Review Queue". Priority comes from urgency.

#### F11 Configurable Intents **[PPT] SHOULD**
Intent names, display names, teams and required entities live in `data/intents.json`. To add an intent: edit the JSON, add training examples, retrain.

#### F12 REST API and Batch Processing **[PPT] MVP / SHOULD**
`POST /api/analyze` (MVP). `POST /api/analyze/batch` up to 50 messages (SHOULD).

#### F13 Urgency Indication **[PPT] SHOULD**
Rule-based: terms like "urgent", "deducted", "charged twice", "fraud", "ASAP" → `high`. Matches the deck's "refund intent + high urgency" example.

#### F14 MySQL Storage **[PPT] MVP**
Stores masked text, predicted intent, status, review outcome. SQLite fallback for developers who have not installed MySQL (§13).

### 2.3 Additional features [ADD]

| ID | What | Why | How | Tech | Priority |
|---|---|---|---|---|---|
| A1 | Charts: intent distribution, status split, language mix, review queue size | Shows value to team leads in the demo | `GET /api/stats` → Chart.js | Chart.js | SHOULD |
| A2 | Show the words that pushed the prediction | Builds trust; helps debugging | Multiply TF-IDF vector by the class's coefficients; show top 3 terms | scikit-learn `coef_` | OPTIONAL |
| A3 | Suggested reply per intent | Faster agent responses | Dictionary of templates in JSON; shown with result | JSON | OPTIONAL |
| A4 | Upload CSV, download results | Batch demo with realistic volumes | Frontend reads file, calls batch endpoint; export via Blob | JS | OPTIONAL |
| A5 | Negative/neutral flag | Prioritizes angry customers | Small lexicon of negative words | Python | OPTIONAL |
| A6 | Better Kannada understanding | Stronger cross-language generalization | Sentence embeddings + Logistic Regression. **Verify the chosen model's card lists Kannada**; not every "multilingual" model does. Large download. | sentence-transformers | OPTIONAL |
| A7 | Reviewer login | Review screen should not be public | Simple token or Flask-Login | Flask | OPTIONAL |
| A8 | Dark mode, Kannada labels | Polish | CSS variables, translation dict | CSS/JS | OPTIONAL |

---

## 3. Recommended Technology Stack

**Principle:** keep to what the deck committed to, add only what is needed, and make everything runnable on a student laptop without paid services.

| Layer | Choice | Why | Alternative |
|---|---|---|---|
| Design | **Figma** [PPT] | Already chosen in the deck | Any wireframe tool |
| Frontend | **HTML5 + CSS3 + vanilla JavaScript** [PPT] | No build tooling, easy for 4 students | React (not needed) |
| Charts | **Chart.js 4** | Small, no build step | Plain HTML/CSS bars |
| Backend | **Python 3.10+ with Flask** [PPT] | Simplest REST API; deck specifies Flask | FastAPI |
| ML | **scikit-learn** [PPT] (TF-IDF + Logistic Regression) | Trains in seconds, no GPU, gives per-class scores | Embeddings (A6) |
| NER / extraction | **Python `re` + gazetteer file** | Deterministic, explainable, no model download | spaCy EntityRuler |
| Language detection | **Unicode-script ratio + romanized hint words** | `langdetect`-style tools are unreliable for romanized Kannada and short text | `langdetect` for English/Kannada script only |
| Database | **MySQL 8** [PPT] via **SQLAlchemy + PyMySQL** | Deck commits to MySQL; SQLAlchemy lets one code path also run on SQLite | SQLite only |
| Data files | **CSV** (training/test), **JSON** (intents, API) | Human-editable | Spreadsheet |
| API format | **JSON over REST** [PPT] | Standard | |
| Config/secrets | **`.env` file + python-dotenv** | Keeps credentials out of code | OS env vars |
| Tests | **pytest** | Standard | |

**Deliberately not included:** React, Docker, paid LLM APIs, Redis, Celery. They add setup risk without helping the demo. If you later want an external LLM for fallback classification, make it optional, read its key from an environment variable, and keep the local classifier as the default.

**Compatibility check:** Flask serves `frontend/` as static files and the `/api/*` routes from the same origin, so the browser needs no CORS configuration. SQLAlchemy 2.x works with both `mysql+pymysql://` and `sqlite:///` URLs. scikit-learn models are saved with `joblib` and loaded once at server start.

---

## 4. System Architecture

### 4.1 Layers (from the deck)

| Layer | Contents in this implementation |
|---|---|
| **User layer** | `frontend/` HTML/CSS/JS: message input, results, review, dashboard |
| **Application layer** | `app.py` Flask routes, `backend/analyzer.py` (request processing, thresholds, routing) |
| **Data & AI layer** | `backend/intent_detector.py`, `entity_extractor.py`, `privacy.py`, `database.py` (MySQL), `training/` (feedback learning) |

### 4.2 Flowchart

```mermaid
flowchart TD
    A["Customer message from web form or API"] --> B["Input validation"]
    B -->|invalid| E1["Error JSON with code and message"]
    B -->|valid| C["Normalize text and detect language"]
    C --> D["Entity extraction: order ID, product, date, amount"]
    D --> F["PII masking, order IDs protected"]
    F --> G["Intent model scores every intent"]
    G --> H["Clause split for multi-intent check"]
    H --> I{"Thresholds: score and margin"}
    I -->|confident or multi intent| J["Route to team and set priority"]
    I -->|ambiguous| K["Clarification question and review queue"]
    I -->|unknown| K
    I -->|unsupported| L["Polite decline, no routing"]
    J --> M["Save masked result to MySQL"]
    K --> M
    L --> M
    M --> N["JSON response shown on dashboard"]
    N --> O["Human review: confirm or correct"]
    O --> P["Feedback stored in MySQL"]
    P --> Q["Retrain script adds corrections to dataset"]
    Q --> G
```

### 4.3 Request and feedback sequence

```mermaid
sequenceDiagram
    participant U as Browser UI
    participant F as Flask API
    participant A as Analyzer
    participant D as MySQL
    U->>F: POST /api/analyze with message
    F->>F: validate input
    F->>A: analyze(text)
    A-->>F: result dictionary
    F->>D: save masked result
    F-->>U: JSON result
    U->>F: POST /api/feedback with id and action
    F->>D: update review status
    F-->>U: updated record
```

### 4.4 How components communicate

| From → To | Mechanism | Data |
|---|---|---|
| Browser → Flask | `fetch()` HTTP, JSON body | message text, feedback |
| Flask → Analyzer | Python function call | `analyze(text) -> dict` |
| Analyzer → model/extractor | Python calls (model loaded once at startup) | masked text, entities |
| Flask → MySQL | SQLAlchemy sessions | masked text, result, review status |
| Training script → model file | `joblib.dump` to `models/intent_model.joblib` | Server restart loads the new model |

---

## 5. Website Pages and UI

A single `index.html` with four views switched by URL hash (`#home`, `#analyze`, `#review`, `#dashboard`). No framework needed.

### 5.1 Design guidance (create in Figma first, per the deck)

- **Look:** clean, light background, one accent color, system font stack (no external fonts, so the demo works offline).
- **Tokens (CSS variables):** `--bg`, `--surface`, `--text`, `--muted`, `--accent`, `--ok` (green), `--warn` (amber), `--bad` (red), `--radius: 12px`.
- **Layout:** mobile-first. One column under 768 px; two columns (input left, results right) from 900 px. Sticky top navigation collapses to a menu button on mobile.
- **Touch targets:** at least 44 × 44 px. Body text at least 16 px.
- **Accessibility:** every input has a `<label>`; results area has `aria-live="polite"`; status never shown by color alone (also text and an icon).

### 5.2 Screens

#### Home (`#home`)
- Title, one-line tagline, "Try it now" button.
- Three-step explainer cards (Input → Process → Outcome, from slide 4).
- Six feature cards (from slide 5).
- Footer with team name and Team ID.

#### Analyze (`#analyze`) **MVP**
```
┌────────────────────────────────────────────────────┐
│ Customer message                                   │
│ ┌────────────────────────────────────────────────┐ │
│ │ textarea (4 rows)                              │ │
│ └────────────────────────────────────────────────┘ │
│ 0 / 1000        [Example messages ▼]  [Analyze]    │
├────────────────────────────────────────────────────┤
│ RESULT CARD                                        │
│ Status badge · Language · Urgency                  │
│ Intent: Refund Request   Model score: 71%  ▮▮▮▮▯   │
│ Other intents (ranked) …                           │
│ Entities: [order_id 48213] [amount INR 2499]       │
│ Route to: Refunds & Billing · Priority: High       │
│ Clarification: "Did a payment fail or …?"          │
│ PII masked: 1 phone, 1 email                       │
│ Masked message (plain text)                        │
│ [Confirm ✓]  [Correct ▾ intent dropdown] [Save]    │
└────────────────────────────────────────────────────┘
```
Interactions:
- Button disabled while the textarea is empty or a request is running.
- Live character counter; turns red above the limit.
- Example chips fill the textarea (use the samples in §9).
- Multi-intent: render one row per intent with its clause text.
- Score shown as a whole percent labelled **"Model score"** with an info tooltip: *"A model output used for thresholds. Not a guaranteed probability."* Bar color: green ≥ accept threshold, amber between thresholds, red below.

#### Review Queue (`#review`) **MVP**
- List of predictions with `needs_review = true` and `review_status = pending`.
- Each row: masked message, predicted intent + score, entities, clarification question.
- Buttons: **Confirm** or **Correct** (dropdown of intents from `GET /api/intents`) then **Save**.
- Empty state: "Nothing waiting for review."

#### Dashboard (`#dashboard`) **SHOULD**
- KPI tiles: total analyzed, awaiting review, reviewer agreement rate (confirmed ÷ reviewed), high-urgency count.
- Charts: bar (intent distribution), doughnut (status split), bar (language mix).
- History table (latest 50): time, masked text (truncated), intent, score, status, review. On mobile, table scrolls horizontally inside its own container.
- "Clear all data" button (needs admin token; see §10).

### 5.3 States every screen must handle

| State | Behavior |
|---|---|
| Loading | Spinner on the button, results area shows a skeleton card |
| Validation error | Inline message under the textarea ("Please enter a message") |
| API/network error | Red banner with message and **Retry** button; never a blank screen |
| Empty data | Friendly empty-state text |
| Server returns `needs_clarification` | Amber card showing the clarification question prominently |
| Server returns `unsupported` | Neutral card: "This looks outside what we support" |

### 5.4 Key frontend code (`frontend/script.js`)

```javascript
const USE_MOCK = false;               // set true while the backend is not ready
const API = "";                       // same origin

async function api(path, options = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetch(API + path, { ...options, signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error?.message || `Request failed (${res.status})`);
    return data;
  } catch (err) {
    if (err.name === "AbortError") throw new Error("The server took too long to respond.");
    throw err;
  } finally { clearTimeout(timer); }
}

// Safe rendering: ALWAYS textContent, never innerHTML, for anything from users or the API.
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

async function onAnalyze() {
  const box = document.getElementById("message");
  const message = box.value.trim();
  if (!message) return showFieldError("Please enter a message.");
  setLoading(true);
  try {
    const result = USE_MOCK ? MOCK_RESULT : await api("/api/analyze",
      { method: "POST", body: JSON.stringify({ message }) });
    renderResult(result);
  } catch (err) { showBanner(err.message, onAnalyze); }
  finally { setLoading(false); }
}

function renderResult(r) {
  const root = document.getElementById("result");
  root.replaceChildren();
  root.append(el("span", r.status.replace("_", " "), `badge badge-${r.status}`));
  r.intents.forEach(i => root.append(el("p", `${i.label}: ${Math.round(i.confidence * 100)}% model score`)));
  r.entities.forEach(e => root.append(el("span", `${e.type}: ${e.value}`, "chip")));
  if (r.clarification_question) root.append(el("p", r.clarification_question, "clarify"));
  root.append(el("pre", r.message_masked, "masked"));   // pre + textContent is safe
}

async function sendFeedback(id, action, correctedIntent) {
  return api("/api/feedback", { method: "POST",
    body: JSON.stringify({ prediction_id: id, action, corrected_intent: correctedIntent }) });
}
```

Dashboard chart (destroy the old chart before redrawing):

```javascript
let intentChart;
async function loadDashboard() {
  const s = await api("/api/stats");
  intentChart?.destroy();
  intentChart = new Chart(document.getElementById("intentChart"), {
    type: "bar",
    data: { labels: Object.keys(s.by_intent),
            datasets: [{ label: "Messages", data: Object.values(s.by_intent) }] },
    options: { responsive: true, plugins: { legend: { display: false } } }
  });
}
```

Load Chart.js in `index.html` with a **pinned version**, and for demo day also copy the file into `frontend/vendor/` so the demo works without internet:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
```

### 5.5 Responsive CSS skeleton (`frontend/style.css`)

```css
:root { --bg:#f6f8fb; --surface:#fff; --text:#16202c; --muted:#5b6b7c;
        --accent:#2563eb; --ok:#15803d; --warn:#b45309; --bad:#b91c1c; --radius:12px; }
* { box-sizing: border-box; }
body { margin:0; font:16px/1.5 system-ui, "Segoe UI", Roboto, sans-serif; background:var(--bg); color:var(--text); }
.container { width:min(1100px, 100% - 2rem); margin-inline:auto; }
.card { background:var(--surface); border-radius:var(--radius); padding:1rem; box-shadow:0 1px 4px rgba(0,0,0,.08); }
.grid-2 { display:grid; gap:1rem; }
@media (min-width: 900px) { .grid-2 { grid-template-columns: 1fr 1fr; } }
button { min-height:44px; padding:0 1rem; border-radius:8px; border:0; background:var(--accent); color:#fff; font-size:1rem; }
button:disabled { opacity:.5; cursor:not-allowed; }
.table-wrap { overflow-x:auto; }
.badge { padding:.15rem .6rem; border-radius:999px; font-size:.85rem; }
.badge-confident,.badge-multi_intent { background:#dcfce7; color:var(--ok); }
.badge-needs_clarification,.badge-unknown { background:#fef3c7; color:var(--warn); }
.badge-unsupported { background:#e5e7eb; color:#374151; }
```

---

## 6. Project Structure and File Requirements

```
intelligent-intent-detector/
├── app.py                      # Flask app: routes, validation, error handling
├── requirements.txt
├── .env.example                # template (committed). Real .env is NOT committed
├── .gitignore
├── README.md                   # short run instructions (copy of §13)
├── backend/
│   ├── __init__.py
│   ├── config.py               # settings, thresholds, paths (reads .env)
│   ├── preprocess.py           # normalize, language detection, clause splitting
│   ├── privacy.py              # PII detection and masking
│   ├── entity_extractor.py     # order ID, product, date, amount, issue terms
│   ├── intent_detector.py      # model build/load/predict + keyword fallback
│   ├── analyzer.py             # pipeline orchestration, thresholds, routing, clarification
│   └── database.py             # SQLAlchemy models and queries
├── training/
│   ├── train.py                # train, report holdout metrics, save model
│   └── evaluate.py             # evaluate on separate test CSV, threshold table
├── data/
│   ├── intents.json            # intent labels, display names, teams, required entities
│   ├── training_data.csv       # text,intent,language
│   ├── test_messages.csv       # held-out test set, never used for training
│   └── products.txt            # product gazetteer (one name per line)
├── models/                     # generated: intent_model.joblib, model_info.json
├── frontend/
│   ├── index.html              # all views
│   ├── style.css
│   ├── script.js
│   └── vendor/                 # optional local copy of chart.umd.min.js
└── tests/
    ├── conftest.py
    ├── test_entities.py
    ├── test_privacy.py
    └── test_api.py
```

### 6.1 How files connect

| File | Purpose | Depends on |
|---|---|---|
| `app.py` | HTTP layer only; validates input, calls `Analyzer`, `database` | `analyzer`, `database`, `config` |
| `analyzer.py` | The single entry point `analyze(text) -> dict` (the contract the API relies on) | `preprocess`, `privacy`, `entity_extractor`, `intent_detector`, `config` |
| `intent_detector.py` | Loads `models/intent_model.joblib`; falls back to keywords if missing | scikit-learn, joblib |
| `database.py` | Tables, save, history, feedback, stats, purge | SQLAlchemy, `config` |
| `training/train.py` | Builds the model from CSV (+ optional feedback) | `intent_detector.build_pipeline`, `database` |
| `frontend/script.js` | Calls `/api/*`, renders results | the API contract in §8 |

### 6.2 Configuration files

**`.env.example`**
```ini
# Copy to .env and edit. Never commit .env.
DATABASE_URL=mysql+pymysql://intent_user:change_me@localhost:3306/intent_db?charset=utf8mb4
# For a quick start without MySQL, use:  DATABASE_URL=sqlite:///intent.db
ACCEPT_THRESHOLD=0.55
REVIEW_THRESHOLD=0.35
MARGIN_THRESHOLD=0.15
CLAUSE_MIN_CONF=0.40
MAX_MESSAGE_CHARS=1000
STORE_MASKED_TEXT=true
RETENTION_DAYS=7
ADMIN_TOKEN=replace-with-a-long-random-string
```

**`.gitignore`**
```
venv/
__pycache__/
.env
*.db
models/
```

**`requirements.txt`**
```
Flask>=3.0
scikit-learn>=1.4
pandas>=2.1
joblib>=1.3
SQLAlchemy>=2.0
PyMySQL>=1.1
cryptography>=42.0
python-dotenv>=1.0
pytest>=8.0
```
(`cryptography` is needed by PyMySQL for MySQL 8's default authentication.)

### 6.3 `backend/config.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'intent.db').as_posix()}")
MODEL_PATH = BASE_DIR / "models" / "intent_model.joblib"
MODEL_INFO_PATH = BASE_DIR / "models" / "model_info.json"
INTENTS_PATH = BASE_DIR / "data" / "intents.json"
PRODUCTS_PATH = BASE_DIR / "data" / "products.txt"
TRAIN_CSV = BASE_DIR / "data" / "training_data.csv"
TEST_CSV = BASE_DIR / "data" / "test_messages.csv"

MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "1000"))
ACCEPT_THRESHOLD = float(os.getenv("ACCEPT_THRESHOLD", "0.55"))
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", "0.35"))
MARGIN_THRESHOLD = float(os.getenv("MARGIN_THRESHOLD", "0.15"))
CLAUSE_MIN_CONF = float(os.getenv("CLAUSE_MIN_CONF", "0.40"))
STORE_MASKED_TEXT = os.getenv("STORE_MASKED_TEXT", "true").lower() == "true"
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "7"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
```

### 6.4 `data/intents.json`

```json
{
  "order_tracking":      {"display": "Order Tracking",       "team": "Order Support",           "required_entities": ["order_id"]},
  "order_cancellation":  {"display": "Order Cancellation",   "team": "Order Support",           "required_entities": ["order_id"]},
  "refund_request":      {"display": "Refund Request",       "team": "Refunds & Billing",       "required_entities": ["order_id"]},
  "product_information": {"display": "Product Information",  "team": "Sales & Product Help",    "required_entities": []},
  "complaint":           {"display": "Complaint",            "team": "Customer Care (Senior)",  "required_entities": []},
  "return_exchange":     {"display": "Return / Exchange",    "team": "Returns Desk",            "required_entities": ["order_id"]},
  "payment_issue":       {"display": "Payment Issue",        "team": "Payments & Billing",      "required_entities": []},
  "delivery_problem":    {"display": "Delivery Problem",     "team": "Logistics Support",       "required_entities": ["order_id"]},
  "general_inquiry":     {"display": "General Inquiry",      "team": "General Help Desk",       "required_entities": []},
  "out_of_scope":        {"display": "Unsupported",          "team": null,                      "required_entities": []}
}
```

### 6.5 `backend/preprocess.py`

```python
import re
import unicodedata

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SPLIT = re.compile(
    r"(?<=[.!?])\s+|;\s*|,\s+|\s+(?:and also|and|but|also|plus|mattu|ಮತ್ತು|aadre|ಆದರೆ)\s+",
    re.IGNORECASE,
)
_ABBREV = re.compile(r"\b(rs|no|inr)\.\s*", re.IGNORECASE)   # "Rs. 2,499" must not split
_KN_ROMAN_HINTS = {
    "nanna", "nange", "nanage", "beku", "illa", "aagide", "aagilla", "yelli", "yaake",
    "madi", "maadi", "bandilla", "banilla", "hana", "duddu", "tumba", "mattu", "ide", "helidru",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_language(text: str) -> str:
    """Heuristic. Returns 'en', 'kn' (Kannada script), 'mixed' (script mix),
    'kn-latn' (romanized Kannada) or 'unknown'."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "unknown"
    ratio = sum("\u0c80" <= c <= "\u0cff" for c in letters) / len(letters)
    if ratio > 0.7:
        return "kn"
    if ratio > 0.1:
        return "mixed"
    words = set(re.findall(r"[a-z]+", text.lower()))
    return "kn-latn" if len(words & _KN_ROMAN_HINTS) >= 2 else "en"


def split_clauses(text: str) -> list[str]:
    text = _ABBREV.sub(r"\1 ", text)
    parts = [p.strip() for p in _SPLIT.split(text) if p and p.strip()]
    return [p for p in parts if len(p.split()) >= 2]
```

### 6.6 `backend/privacy.py`

```python
import re


def _luhn(candidate: str) -> bool:
    digits = [int(c) for c in re.sub(r"\D", "", candidate)]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
    return total % 10 == 0


PII_PATTERNS = [
    ("UPI", re.compile(r"\b[\w.\-]{2,}@(?:upi|ybl|oksbi|okaxis|okhdfcbank|okicici|paytm|ibl|axl)\b", re.I), None),
    ("EMAIL", re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b"), None),
    ("CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), _luhn),
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}\s\d{4}\s\d{4}(?!\d)"), None),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), None),
    ("PHONE", re.compile(r"(?<!\d)(?:\+91[\s-]?|0)?[6-9]\d{9}(?!\d)"), None),
    ("OTP", re.compile(r"\b(?:otp|cvv|pin)\b\D{0,12}\d{3,8}\b", re.I), None),
]


def mask_pii(text: str, protected_spans=()):
    """Replace PII with [TYPE]. protected_spans (e.g. order IDs) are never masked.
    Returns (masked_text, counts_by_type)."""
    found = []
    for kind, pattern, validator in PII_PATTERNS:
        for m in pattern.finditer(text):
            if validator and not validator(m.group()):
                continue
            s, e = m.span()
            if any(s < pe and e > ps for ps, pe in protected_spans):
                continue
            found.append((s, e, kind))
    found.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    out, pos, counts = [], 0, {}
    for s, e, kind in found:
        if s < pos:
            continue                      # overlaps an earlier match
        out.append(text[pos:s])
        out.append(f"[{kind}]")
        counts[kind] = counts.get(kind, 0) + 1
        pos = e
    out.append(text[pos:])
    return "".join(out), counts
```

### 6.7 `backend/entity_extractor.py`

```python
import re
from pathlib import Path

_MONTH = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
          r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)")

ORDER_PREFIXED = re.compile(r"\b[A-Z]{2,4}-\d{4,10}\b", re.I)                     # ORD-48213
ORDER_LABELLED = re.compile(
    r"(?:\border(?:\s*(?:no|number|id))?\.?\s*[:#]?\s*|\bordar\s*|ಆರ್ಡರ್\s*|#)(\d{4,12})\b", re.I)
AMOUNT_PREFIX = re.compile(r"(₹|\brs\.?|\binr|\brupees?|\$|\busd)\s*(\d[\d,]*(?:\.\d{1,2})?)", re.I)
AMOUNT_SUFFIX = re.compile(r"(\d[\d,]*(?:\.\d{1,2})?)\s*(?:₹|\brs\b|\brupees\b|/-)", re.I)
DATES = [
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTH}\b(?:\s+\d{{4}})?", re.I),
    re.compile(rf"\b{_MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?\b(?:,?\s+\d{{4}})?", re.I),
    re.compile(r"\b(?:today|tomorrow|yesterday|last (?:week|month)|\d+\s+days?\s+ago)\b", re.I),
]
ISSUE_TERMS = ["charged twice", "double charged", "deducted", "not received", "damaged", "broken",
               "defective", "wrong item", "wrong size", "missing", "delayed", "late", "expired", "failed"]


class EntityExtractor:
    def __init__(self, products_path):
        names, p = [], Path(products_path)
        if p.exists():
            names = [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.startswith("#")]
        names.sort(key=len, reverse=True)           # longest match first
        self.product_re = (re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b", re.I)
                           if names else None)

    def extract(self, text: str) -> list[dict]:
        found = []

        def add(kind, value, span):
            found.append({"type": kind, "value": value, "span": span})

        for m in ORDER_PREFIXED.finditer(text):
            add("order_id", m.group(0).upper(), m.span())
        for m in ORDER_LABELLED.finditer(text):
            add("order_id", m.group(1), m.span(1))
        for m in AMOUNT_PREFIX.finditer(text):
            cur = "USD" if m.group(1).lower().rstrip(".") in ("$", "usd") else "INR"
            add("amount", f"{cur} {m.group(2).replace(',', '')}", m.span())
        for m in AMOUNT_SUFFIX.finditer(text):
            add("amount", f"INR {m.group(1).replace(',', '')}", m.span())
        for rx in DATES:
            for m in rx.finditer(text):
                add("date", m.group(0), m.span())
        if self.product_re:
            for m in self.product_re.finditer(text):
                add("product", m.group(0), m.span())
        low = text.lower()
        for term in ISSUE_TERMS:
            i = low.find(term)
            if i != -1:
                add("issue", term, (i, i + len(term)))
        return self._dedupe(found)

    @staticmethod
    def _dedupe(items):
        seen, out = set(), []
        for it in sorted(items, key=lambda x: x["span"][0]):
            key = (it["type"], it["value"].lower())
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out
```

`data/products.txt` (replace with your demo catalogue):
```
# one product name per line
Galaxy M14
iPhone 14
wireless earbuds
headphones
smart watch
laptop
running shoes
mixer grinder
```

### 6.8 `backend/intent_detector.py`

```python
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

# \w misses Kannada vowel signs, so split on whitespace/punctuation instead.
TOKEN_PATTERN = r"[^\s.,!?;:()\[\]\"']+"

KEYWORDS = {   # used ONLY when no trained model exists (fallback mode)
    "order_tracking": ["where is my order", "track", "tracking", "order status", "yelli ide", "ಎಲ್ಲಿದೆ"],
    "order_cancellation": ["cancel", "ಕ್ಯಾನ್ಸಲ್"],
    "refund_request": ["refund", "money back", "ಹಣ ವಾಪಸ್", "hana vapas"],
    "product_information": ["does it", "price of", "specification", "available in", "ಬೆಲೆ"],
    "complaint": ["terrible", "worst", "unacceptable", "disappointed", "complaint", "ಚೆನ್ನಾಗಿಲ್ಲ"],
    "return_exchange": ["return", "exchange", "replace", "ಬದಲಾಯಿಸಿ"],
    "payment_issue": ["payment", "deducted", "charged", "upi", "ಪೇಮೆಂಟ್"],
    "delivery_problem": ["delivery", "delayed", "not received", "late", "ಡೆಲಿವರಿ"],
    "general_inquiry": ["working hours", "contact", "customer care", "store"],
}


def build_pipeline() -> Pipeline:
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), token_pattern=TOKEN_PATTERN,
                                 sublinear_tf=True, lowercase=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                                 sublinear_tf=True, lowercase=True)),
    ])
    clf = LogisticRegression(C=10.0, max_iter=2000, class_weight="balanced")
    return Pipeline([("features", features), ("clf", clf)])


class IntentDetector:
    def __init__(self, model_path, labels):
        self.labels = labels
        self.pipeline = joblib.load(model_path) if Path(model_path).exists() else None
        self.mode = "trained" if self.pipeline is not None else "keyword_fallback"

    def predict(self, text: str, top_k: int = 3) -> list[dict]:
        if self.pipeline is None:
            return self._keyword_predict(text, top_k)
        probs = self.pipeline.predict_proba([text])[0]
        classes = self.pipeline.classes_
        order = probs.argsort()[::-1][:top_k]
        return [{"label": str(classes[i]), "confidence": round(float(probs[i]), 3)} for i in order]

    def _keyword_predict(self, text: str, top_k: int) -> list[dict]:
        t = text.lower()
        hits = {label: sum(kw in t for kw in kws) for label, kws in KEYWORDS.items()}
        if sum(hits.values()) == 0:
            return [{"label": "general_inquiry", "confidence": 0.10},
                    {"label": "out_of_scope", "confidence": 0.05}][:top_k]
        ranked = sorted(hits.items(), key=lambda kv: -kv[1])[:top_k]
        return [{"label": l, "confidence": round(min(0.65, 0.25 + 0.2 * h) if h else 0.02, 3)}
                for l, h in ranked]
```

### 6.9 `backend/analyzer.py`

```python
import json
from . import config
from .preprocess import normalize, detect_language, split_clauses
from .privacy import mask_pii
from .entity_extractor import EntityExtractor
from .intent_detector import IntentDetector

URGENT_TERMS = ["urgent", "asap", "immediately", "right now", "deducted", "charged twice",
                "double charged", "fraud", "unauthorized", "emergency", "ಬೇಗ", "jaldi"]
SKIP_FOR_MULTI = {"general_inquiry", "out_of_scope"}
ENTITY_PROMPTS = {"order_id": "your Order ID"}
GENERIC_QUESTION = ("Could you tell us a bit more? For example, is this about an order, "
                    "a payment, a delivery, or a product?")
PAIR_QUESTIONS = {
    frozenset({"payment_issue", "refund_request"}):
        "Did a payment fail or get deducted wrongly, or are you asking for a refund on a completed order?",
    frozenset({"order_tracking", "delivery_problem"}):
        "Do you want to know where your order is, or is there a problem with the delivery (late, not received, wrong address)?",
    frozenset({"order_cancellation", "return_exchange"}):
        "Has the order already been delivered? (Cancellation applies before delivery; return or exchange after.)",
    frozenset({"return_exchange", "refund_request"}):
        "Would you like to return or exchange the item, or only get your money back?",
    frozenset({"payment_issue", "order_tracking"}):
        "Is your payment not going through, or is the payment done and you cannot see your order?",
}


class Analyzer:
    def __init__(self):
        self.intents = json.loads(config.INTENTS_PATH.read_text(encoding="utf-8"))
        self.labels = list(self.intents)
        self.detector = IntentDetector(config.MODEL_PATH, self.labels)
        self.extractor = EntityExtractor(config.PRODUCTS_PATH)

    # ---- public contract: the API only ever calls this ----
    def analyze(self, raw_text: str) -> dict:
        text = normalize(raw_text)
        language = detect_language(text)
        entities = self.extractor.extract(text)                    # on original text
        protected = [e["span"] for e in entities if e["type"] == "order_id"]
        masked, pii_counts = mask_pii(text, protected)             # classify masked text only

        ranked = self.detector.predict(masked, top_k=3)
        intents, multi = self._multi_intent(masked, ranked)
        status = self._decide(ranked, multi)
        needs_review = status in ("needs_clarification", "unknown") or (
            multi and min(i["confidence"] for i in intents) < config.ACCEPT_THRESHOLD)

        public_entities = [{"type": e["type"], "value": e["value"]} for e in entities]
        found_types = {e["type"] for e in entities}
        missing = []
        if status in ("confident", "multi_intent"):
            for i in intents:
                for req in self.intents[i["label"]]["required_entities"]:
                    if req not in found_types and req not in missing:
                        missing.append(req)

        return {
            "message_masked": masked,
            "language": language,
            "status": status,
            "multi_intent": multi,
            "intents": [dict(i, display=self.intents[i["label"]]["display"]) for i in intents],
            "alternatives": ranked[1:] if not multi else [],
            "entities": public_entities,
            "missing_entities": missing,
            "urgency": "high" if any(t in text.lower() for t in URGENT_TERMS) else "normal",
            "clarification_question": self._clarify(status, ranked, missing),
            "needs_review": needs_review,
            "route_to": self._route(status, intents, needs_review, text),
            "pii_masked": pii_counts,
            "model": {"mode": self.detector.mode,
                      "note": "Scores are model outputs, not calibrated probabilities."},
        }

    # ---- internals ----
    def _multi_intent(self, masked, ranked):
        clauses = split_clauses(masked)
        single = [dict(ranked[0], clause=None)]
        if len(clauses) < 2:
            return single, False
        found = {}
        for clause in clauses:
            top = self.detector.predict(clause, top_k=1)[0]
            if top["label"] in SKIP_FOR_MULTI or top["confidence"] < config.CLAUSE_MIN_CONF:
                continue
            if top["label"] not in found or top["confidence"] > found[top["label"]]["confidence"]:
                found[top["label"]] = dict(top, clause=clause)
        if len(found) >= 2:
            return sorted(found.values(), key=lambda x: -x["confidence"]), True
        return single, False

    def _decide(self, ranked, multi):
        if multi:
            return "multi_intent"
        top = ranked[0]
        margin = top["confidence"] - (ranked[1]["confidence"] if len(ranked) > 1 else 0.0)
        if top["label"] == "out_of_scope" and top["confidence"] >= config.REVIEW_THRESHOLD:
            return "unsupported"
        if top["confidence"] < config.REVIEW_THRESHOLD:
            return "unknown"
        if top["confidence"] < config.ACCEPT_THRESHOLD or margin < config.MARGIN_THRESHOLD:
            return "needs_clarification"
        return "confident"

    def _clarify(self, status, ranked, missing):
        if status == "unknown":
            return GENERIC_QUESTION
        if status == "needs_clarification":
            a, b = ranked[0]["label"], ranked[1]["label"]
            return PAIR_QUESTIONS.get(frozenset({a, b}),
                f"Just to be sure, is this about {self.intents[a]['display']} or {self.intents[b]['display']}?")
        if missing:
            names = " and ".join(ENTITY_PROMPTS.get(m, m) for m in missing)
            return f"Could you share {names} so we can look into this?"
        return None

    def _route(self, status, intents, needs_review, text):
        priority = "high" if any(t in text.lower() for t in URGENT_TERMS) else "normal"
        if status == "unsupported":
            return {"teams": [], "priority": "none"}
        if needs_review:
            return {"teams": ["Human Review Queue"], "priority": priority}
        teams = []
        for i in intents:
            t = self.intents[i["label"]]["team"]
            if t and t not in teams:
                teams.append(t)
        return {"teams": teams, "priority": priority}
```

### 6.10 `backend/database.py`

```python
import json
import argparse
from datetime import datetime, timedelta, timezone
from sqlalchemy import (create_engine, Column, Integer, String, Text, Float, Boolean,
                        DateTime, select, func, delete)
from sqlalchemy.orm import declarative_base, sessionmaker
from . import config

engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=utcnow, index=True)
    masked_text = Column(Text, nullable=True)          # NULL when STORE_MASKED_TEXT=false
    language = Column(String(16))
    top_intent = Column(String(40), index=True)
    confidence = Column(Float)
    status = Column(String(24), index=True)
    multi_intent = Column(Boolean, default=False)
    urgency = Column(String(8))
    needs_review = Column(Boolean, default=False, index=True)
    result_json = Column(Text)                         # intents, entities, routing (no raw text)
    review_status = Column(String(16), default="not_required")   # not_required|pending|confirmed|corrected
    corrected_intent = Column(String(40), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(engine)


def to_dict(row: Prediction) -> dict:
    detail = json.loads(row.result_json or "{}")
    return {"id": row.id, "created_at": row.created_at.isoformat() + "Z",
            "message_masked": row.masked_text, "language": row.language,
            "top_intent": row.top_intent, "confidence": row.confidence, "status": row.status,
            "multi_intent": row.multi_intent, "urgency": row.urgency,
            "needs_review": row.needs_review, "review_status": row.review_status,
            "corrected_intent": row.corrected_intent,
            "intents": detail.get("intents", []), "entities": detail.get("entities", []),
            "clarification_question": detail.get("clarification_question"),
            "route_to": detail.get("route_to")}


def save_prediction(result: dict) -> int:
    top = result["intents"][0]
    detail = {k: result[k] for k in ("intents", "entities", "clarification_question", "route_to")}
    row = Prediction(
        masked_text=result["message_masked"] if config.STORE_MASKED_TEXT else None,
        language=result["language"], top_intent=top["label"], confidence=top["confidence"],
        status=result["status"], multi_intent=result["multi_intent"], urgency=result["urgency"],
        needs_review=result["needs_review"], result_json=json.dumps(detail, ensure_ascii=False),
        review_status="pending" if result["needs_review"] else "not_required")
    with SessionLocal() as s:
        s.add(row)
        s.commit()
        return row.id


def list_predictions(limit=50, status=None, review=None):
    q = select(Prediction).order_by(Prediction.id.desc()).limit(limit)
    if status:
        q = q.where(Prediction.status == status)
    if review:
        q = q.where(Prediction.review_status == review)
    with SessionLocal() as s:
        return [to_dict(r) for r in s.scalars(q)]


def apply_feedback(pid: int, action: str, corrected_intent=None):
    with SessionLocal() as s:
        row = s.get(Prediction, pid)
        if row is None:
            return None
        row.review_status = "confirmed" if action == "confirm" else "corrected"
        row.corrected_intent = corrected_intent if action == "correct" else None
        row.reviewed_at = utcnow()
        s.commit()
        return to_dict(row)


def stats() -> dict:
    with SessionLocal() as s:
        def grouped(col):
            return {k: v for k, v in s.execute(select(col, func.count()).group_by(col)).all() if k}
        reviewed = grouped(Prediction.review_status)
        confirmed, corrected = reviewed.get("confirmed", 0), reviewed.get("corrected", 0)
        return {
            "total": s.scalar(select(func.count(Prediction.id))) or 0,
            "by_intent": grouped(Prediction.top_intent),
            "by_status": grouped(Prediction.status),
            "by_language": grouped(Prediction.language),
            "pending_review": reviewed.get("pending", 0),
            "high_urgency": s.scalar(select(func.count(Prediction.id)).where(Prediction.urgency == "high")) or 0,
            "avg_score": round(s.scalar(select(func.avg(Prediction.confidence))) or 0, 3),
            "reviewer_agreement": (round(confirmed / (confirmed + corrected), 3)
                                   if confirmed + corrected else None),
        }


def get_feedback_rows():
    """(masked_text, intent) pairs from human review, for retraining."""
    with SessionLocal() as s:
        rows = s.scalars(select(Prediction).where(Prediction.masked_text.is_not(None),
                         Prediction.review_status.in_(["confirmed", "corrected"])))
        return [(r.masked_text, r.corrected_intent or r.top_intent) for r in rows]


def purge_older_than(days: int) -> int:
    cutoff = utcnow() - timedelta(days=days)
    with SessionLocal() as s:
        n = s.execute(delete(Prediction).where(Prediction.created_at < cutoff)).rowcount
        s.commit()
        return n


def purge_all() -> int:
    with SessionLocal() as s:
        n = s.execute(delete(Prediction)).rowcount
        s.commit()
        return n


if __name__ == "__main__":      # python -m backend.database init | purge
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["init", "purge"])
    cmd = ap.parse_args().command
    if cmd == "init":
        init_db(); print("Tables created.")
    else:
        print(f"Deleted {purge_older_than(config.RETENTION_DAYS)} rows older than {config.RETENTION_DAYS} days.")
```

**Table summary**

| Column | Type | Note |
|---|---|---|
| id | INT PK | |
| created_at | DATETIME | UTC |
| masked_text | TEXT NULL | PII already masked; NULL if storage disabled |
| language, top_intent, status, urgency | VARCHAR | |
| confidence | FLOAT | model score of the top intent |
| needs_review | BOOL | queue flag |
| review_status | VARCHAR | not_required, pending, confirmed, corrected |
| corrected_intent | VARCHAR NULL | reviewer's label |
| result_json | TEXT | intents, entities, routing |

### 6.11 `app.py`

```python
import hmac
import logging
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from backend import config, database as db
from backend.analyzer import Analyzer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("intent-app")

app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
db.init_db()
analyzer = Analyzer()
log.info("Detector mode: %s", analyzer.detector.mode)


def err(status, code, message):
    return jsonify({"error": {"code": code, "message": message}}), status


def validate_message(value):
    """Returns (clean_text, None) or (None, (status, code, message))."""
    if not isinstance(value, str):
        return None, (400, "invalid_message", "message must be a string.")
    text = value.strip()
    if not text:
        return None, (400, "empty_message", "Please enter a message.")
    if len(text) > config.MAX_MESSAGE_CHARS:
        return None, (400, "message_too_long",
                      f"Message must be at most {config.MAX_MESSAGE_CHARS} characters.")
    if not any(c.isalpha() for c in text):
        return None, (422, "no_text_content", "Message must contain letters, not only numbers or symbols.")
    return text, None


def analyze_and_save(text, save=True):
    result = analyzer.analyze(text)
    result["id"] = None
    if save:
        try:
            result["id"] = db.save_prediction(result)
        except Exception:                      # DB down must not break analysis
            log.exception("Could not save prediction")
    return result


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "detector_mode": analyzer.detector.mode})


@app.get("/api/intents")
def intents():
    return jsonify({"intents": [{"label": k, "display": v["display"]} for k, v in analyzer.intents.items()]})


@app.post("/api/analyze")
def analyze_route():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return err(400, "invalid_json", "Request body must be a JSON object.")
    text, problem = validate_message(data.get("message"))
    if problem:
        return err(*problem)
    return jsonify(analyze_and_save(text, save=bool(data.get("save", True))))


@app.post("/api/analyze/batch")
def analyze_batch():
    data = request.get_json(silent=True)
    msgs = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(msgs, list) or not msgs:
        return err(400, "invalid_messages", "messages must be a non-empty list.")
    if len(msgs) > 50:
        return err(400, "too_many_messages", "At most 50 messages per batch.")
    results = []
    for i, m in enumerate(msgs):
        text, problem = validate_message(m)
        results.append({"index": i, "error": {"code": problem[1], "message": problem[2]}} if problem
                       else {"index": i, "result": analyze_and_save(text, save=bool(data.get("save", True)))})
    return jsonify({"results": results})


@app.post("/api/feedback")
def feedback():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return err(400, "invalid_json", "Request body must be a JSON object.")
    pid, action, corrected = data.get("prediction_id"), data.get("action"), data.get("corrected_intent")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return err(400, "invalid_id", "prediction_id must be an integer.")
    if action not in ("confirm", "correct"):
        return err(400, "invalid_action", "action must be 'confirm' or 'correct'.")
    if action == "correct" and corrected not in analyzer.labels:
        return err(400, "invalid_intent", "corrected_intent is not a supported intent.")
    row = db.apply_feedback(pid, action, corrected)
    return jsonify(row) if row else err(404, "not_found", "Prediction not found.")


@app.get("/api/history")
def history():
    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
    except ValueError:
        return err(400, "invalid_limit", "limit must be an integer.")
    return jsonify({"items": db.list_predictions(limit, request.args.get("status"),
                                                 request.args.get("review"))})


@app.get("/api/stats")
def stats():
    return jsonify(db.stats())


@app.delete("/api/history")
def clear_history():
    token = request.headers.get("X-Admin-Token", "")
    if not config.ADMIN_TOKEN or not hmac.compare_digest(token, config.ADMIN_TOKEN):
        return err(403, "forbidden", "Admin token required.")
    return jsonify({"deleted": db.purge_all()})


@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, HTTPException):
        return err(e.code, e.name.lower().replace(" ", "_"), e.description)
    log.exception("Unhandled error")
    return err(500, "internal_error", "Something went wrong. Please try again.")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
```

---

## 7. AI/NLP Implementation

### 7.1 Intents

| Label | Example |
|---|---|
| `order_tracking` | "Where is my order?" |
| `order_cancellation` | "Cancel my order" |
| `refund_request` | "I want my money back" |
| `product_information` | "Does this phone support fast charging?" |
| `complaint` | "Your service is terrible" |
| `return_exchange` | "The shoes are the wrong size, can I exchange them?" |
| `payment_issue` | "Payment failed but money was deducted" |
| `delivery_problem` | "Delivery is very late" |
| `general_inquiry` | "What are your working hours?" |
| `out_of_scope` | "What's the weather today?" (unsupported) |

`unknown` is **not** a trained class. It is a *decision outcome* when the model is not sure (§7.8). `out_of_scope` **is** a trained class so the model can learn what we do not support.

### 7.2 Recommended approach: hybrid, classical ML first

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Keyword rules only | No data needed, transparent | Brittle, fails on implicit/code-mixed text (the exact problem we solve) | Fallback only |
| **TF-IDF + Logistic Regression** | Trains in seconds on a laptop; per-class scores; works with small data; character n-grams handle spelling variants and Kannada | No deep context understanding; needs examples for every phrasing | **Use for MVP** |
| Pretrained multilingual embeddings + classifier | Better generalization with little data | Large download, slower, must verify Kannada support | Optional upgrade (A6) |
| Fine-tuned transformer | Highest ceiling | Needs GPU and far more labelled data | Out of scope |
| External LLM API | Strong zero-shot | Cost, privacy, network dependency | Not default |

**Hybrid:** the model does classification; rules do entity extraction, PII masking, urgency, language detection and the final thresholded decision; humans decide uncertain cases.

### 7.3 Preparing the dataset

**Format** (`data/training_data.csv`, UTF-8, quote text that contains commas):

```csv
text,intent,language
"Where is my order?",order_tracking,en
"nanna order yelli ide",order_tracking,kn-latn
"ನನ್ನ ಆರ್ಡರ್ ಎಲ್ಲಿದೆ",order_tracking,kn
```

**Labeling rules (write these on one page and share them):**
1. One label per row = the customer's **main request**.
2. Label by what the customer wants done, not by emotion. "Where is my refund?" is `refund_request`.
3. If a message has two requests, **split it into two rows** (one per clause) for training; multi-intent is handled at inference time by clause splitting.
4. Delivered-and-damaged item with replacement request → `return_exchange`. Not-yet-arrived → `delivery_problem`. Money taken but order not placed → `payment_issue`.
5. Anything that is not customer support for orders/payments/products → `out_of_scope`.
6. Put **masked** text in the dataset (use `[PHONE]`, `[EMAIL]`) and never real personal data.
7. Two people should label a sample of 50 rows independently; discuss disagreements and fix the rules.

**Size targets (realistic for students):** at least **30-40 examples per intent** for English and **10-15 per intent** in Kannada and romanized Kannada. Vary length, politeness, typos, and word order. More is better; data quality matters more than count. Keep a **separate** `data/test_messages.csv` (at least 5-10 per intent) written *after* the training set and never copied into it.

**Starter seed (extend this; a native Kannada speaker must verify all Kannada rows):**

```csv
text,intent,language
"Where is my order?",order_tracking,en
"Can you tell me the status of my order #48213",order_tracking,en
"track my package please",order_tracking,en
"nanna order yelli ide",order_tracking,kn-latn
"ನನ್ನ ಆರ್ಡರ್ ಎಲ್ಲಿದೆ",order_tracking,kn
"Please cancel my order",order_cancellation,en
"I ordered by mistake, cancel it",order_cancellation,en
"I want to cancel ORD-55120 before it ships",order_cancellation,en
"order cancel madi",order_cancellation,kn-latn
"ನನ್ನ ಆರ್ಡರ್ ಕ್ಯಾನ್ಸಲ್ ಮಾಡಿ",order_cancellation,kn
"I want my money back",refund_request,en
"Please refund the amount for my order",refund_request,en
"When will my refund be credited?",refund_request,en
"nange hana vapas beku",refund_request,kn-latn
"ನನಗೆ ಹಣ ವಾಪಸ್ ಬೇಕು",refund_request,kn
"Does this phone support fast charging?",product_information,en
"What colours does the smart watch come in?",product_information,en
"Is the laptop available with 16 GB RAM?",product_information,en
"ಈ ಫೋನ್ ಬೆಲೆ ಎಷ್ಟು",product_information,kn
"Your service is terrible",complaint,en
"I am very disappointed with how I was treated",complaint,en
"Worst experience, nobody replies to my emails",complaint,en
"ನಿಮ್ಮ ಸೇವೆ ಚೆನ್ನಾಗಿಲ್ಲ",complaint,kn
"I want to return these shoes",return_exchange,en
"The size is wrong, can I exchange it?",return_exchange,en
"The item arrived damaged, please replace it",return_exchange,en
"ವಸ್ತು ಹಾಳಾಗಿದೆ ಬದಲಾಯಿಸಿ ಕೊಡಿ",return_exchange,kn
"My payment failed",payment_issue,en
"Money was deducted but the order was not placed",payment_issue,en
"I was charged twice for the same order",payment_issue,en
"payment aagilla but hana kat aagide",payment_issue,kn-latn
"ಪೇಮೆಂಟ್ ಆಗಿಲ್ಲ ಆದರೆ ಹಣ ಕಟ್ ಆಗಿದೆ",payment_issue,kn
"My delivery is very late",delivery_problem,en
"The courier says delivered but I did not receive anything",delivery_problem,en
"Package was left at the wrong address",delivery_problem,en
"delivery tumba late aagide",delivery_problem,kn-latn
"ಡೆಲಿವರಿ ತುಂಬಾ ತಡವಾಗಿದೆ",delivery_problem,kn
"What are your working hours?",general_inquiry,en
"How can I contact customer care?",general_inquiry,en
"Do you have a store in Bengaluru?",general_inquiry,en
"What is the weather like today?",out_of_scope,en
"Tell me a joke",out_of_scope,en
"Who won the cricket match yesterday?",out_of_scope,en
"Can you book me a flight to Delhi?",out_of_scope,en
```

(This seed is about 4 rows per intent; it is enough to run the pipeline end to end but **not** enough for trustworthy accuracy. Expect to expand it.)

### 7.4 Train

`training/train.py`:

```python
import argparse
import json
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import cross_val_score, train_test_split, StratifiedKFold
from backend import config
from backend.intent_detector import build_pipeline


def load_data(include_feedback: bool) -> pd.DataFrame:
    df = pd.read_csv(config.TRAIN_CSV).dropna(subset=["text", "intent"])
    labels = set(json.loads(config.INTENTS_PATH.read_text(encoding="utf-8")))
    bad = set(df.intent) - labels
    if bad:
        raise SystemExit(f"Unknown labels in CSV (not in intents.json): {bad}")
    if include_feedback:
        from backend.database import get_feedback_rows
        extra = pd.DataFrame(get_feedback_rows(), columns=["text", "intent"])
        print(f"Adding {len(extra)} reviewed rows from the database")
        df = pd.concat([df[["text", "intent"]], extra], ignore_index=True)
    return df.drop_duplicates(subset=["text"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-feedback", action="store_true")
    args = ap.parse_args()

    df = load_data(args.include_feedback)
    counts = df.intent.value_counts()
    print(counts.to_string())
    if counts.min() < 5:
        raise SystemExit("Need at least 5 examples per intent. Add more data first.")
    if counts.min() < 20:
        print("WARNING: fewer than 20 examples for some intents. Metrics will be unreliable.")

    X_tr, X_te, y_tr, y_te = train_test_split(
        df.text, df.intent, test_size=0.2, stratify=df.intent, random_state=42)
    model = build_pipeline().fit(X_tr, y_tr)
    pred = model.predict(X_te)
    print("\nHoldout report (20% of the training CSV):")
    print(classification_report(y_te, pred, zero_division=0))
    macro_f1 = f1_score(y_te, pred, average="macro", zero_division=0)

    folds = min(5, int(counts.min()))
    cv = cross_val_score(build_pipeline(), df.text, df.intent,
                         cv=StratifiedKFold(folds, shuffle=True, random_state=42), scoring="f1_macro")
    print(f"{folds}-fold CV macro-F1: {cv.mean():.3f} (+/- {cv.std():.3f})")

    final = build_pipeline().fit(df.text, df.intent)          # refit on everything
    config.MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(final, config.MODEL_PATH)
    config.MODEL_INFO_PATH.write_text(json.dumps({
        "trained_at": datetime.now(timezone.utc).isoformat(), "n_examples": int(len(df)),
        "holdout_macro_f1": round(float(macro_f1), 3), "cv_macro_f1": round(float(cv.mean()), 3),
        "note": "Computed on our own small dataset; not a real-world accuracy claim."}, indent=2))
    print(f"Saved {config.MODEL_PATH}")


if __name__ == "__main__":
    main()
```

Run: `python -m training.train` (always from the project root so `backend` is importable).

### 7.5 Predict

`IntentDetector.predict()` (§6.8) calls `predict_proba`, sorts all classes, and returns the top-k. The `Analyzer` always classifies the **masked** text.

### 7.6 Entity extraction

Implemented in §6.7. Summary of rules and limits:

| Entity | Rule | Known limit |
|---|---|---|
| `order_id` | `ORD-48213` style, or digits (4-12) after "order", "order no/id", "#", Kannada "ಆರ್ಡರ್" | Unlabelled numbers are ignored on purpose |
| `amount` | ₹ / Rs. / INR / rupees / $ / USD before the number, or "rs", "rupees", "/-" after | Amounts written in words are missed |
| `date` | `12/03/2025`, `12 March`, `March 12`, today/yesterday/tomorrow, `3 days ago` | Does not resolve relative dates to calendar dates |
| `product` | Gazetteer match from `data/products.txt` | Only products in the file are found; spaCy EntityRuler or a trained NER is the upgrade path |
| `issue` | Small lexicon ("deducted", "damaged", "late", ...) | Lexicon is English-only; extend for Kannada |

**Ordering rule:** entities are extracted *before* masking, and order-ID spans are protected from the PII masker so a 10-digit order number is not mistaken for a phone number.

### 7.7 Multilingual handling (honest scope)

- Language label is a heuristic (script ratio plus hint words) and is shown for transparency; it does **not** gate classification.
- One shared model trained on English + Kannada + romanized rows. Character n-grams let it learn from partial overlaps such as "cancel", "refund", "payment" appearing in Kanglish.
- Quality in Kannada is bounded by your Kannada examples. Report per-language metrics (§11.3) instead of one blended number.
- Romanized Kannada has no standard spelling ("hana", "hanna", "duddu"); add spelling variants to the data.

### 7.8 Confidence, thresholds and uncertainty

**What the score is.** Logistic Regression's `predict_proba` is a softmax-style value that sums to 1 across intents. It is useful for *ranking* and for *thresholding*, but it is **not guaranteed to be a calibrated probability**. A "0.70" does not mean "70% of such predictions are right". With small data and ten classes the scores are often low and compressed. Therefore:

1. Display it as **"Model score"**, never "accuracy" or "probability of being correct".
2. Choose thresholds from **measured data** (§11.2 coverage-vs-accuracy table), not by feel.
3. If you have 100+ examples per class, you may try `CalibratedClassifierCV` and check a reliability curve; do not assume it helped.

**Decision rules (`Analyzer._decide`):**

| Condition (evaluated in order) | Status | Action |
|---|---|---|
| multiple distinct clause intents ≥ `CLAUSE_MIN_CONF` | `multi_intent` | Route each; review if any score < `ACCEPT_THRESHOLD` |
| top is `out_of_scope` and score ≥ `REVIEW_THRESHOLD` | `unsupported` | Polite decline, no routing |
| top score < `REVIEW_THRESHOLD` (default 0.35) | `unknown` | Generic clarification + human review |
| top score < `ACCEPT_THRESHOLD` (0.55) **or** gap to 2nd < `MARGIN_THRESHOLD` (0.15) | `needs_clarification` | Pair-specific question + human review |
| otherwise | `confident` | Route to team |

Default thresholds (0.35 / 0.55 / 0.15 / 0.40) are **starting guesses**. Tune them: raise `ACCEPT_THRESHOLD` if too many wrong auto-routes appear; lower it if too many correct predictions go to review.

**Clarification questions.** (a) Confusable pairs map to targeted questions (`PAIR_QUESTIONS`), (b) otherwise a generic "is it A or B?" question using the top two intents, (c) a missing required entity (e.g. Order ID) produces "Could you share your Order ID...?" even when the intent is confident.

### 7.9 Multi-intent detection

1. `split_clauses()` splits on sentence ends, semicolons, commas followed by a space, and connectors (`and`, `but`, `also`, `plus`, `mattu`, `ಮತ್ತು`, ...). `Rs.` is protected so "Rs. 2,499" is not cut.
2. Each clause (≥ 2 words) is classified separately.
3. Clause labels with score ≥ `CLAUSE_MIN_CONF` are kept, excluding `general_inquiry` and `out_of_scope`.
4. If ≥ 2 distinct labels remain → `multi_intent`, ranked by score ("intent ranking", per the deck).

**Limits:** two intents in one clause without a connector are missed; a connector inside a single intent ("exchange and return policy") can over-split. Clause scores come from short text and are noisier. Reviewers should be able to see which clause produced which intent (the response includes `clause`).

### 7.10 If data is insufficient (fallback plan)

| Situation | What to do |
|---|---|
| No trained model file yet | App starts in `keyword_fallback` mode (shown by `/api/health` and in each response). Scores are capped and the UI should show a "Demo fallback mode" badge. |
| Very small dataset (under ~20 per intent) | Still train, but say plainly: "prototype trained on N hand-written examples". Lean on the clarification/human-review path, and raise `ACCEPT_THRESHOLD`. |
| Poor Kannada results | Add more Kannada/Kanglish rows; show per-language metrics; label Kannada support as "experimental" in the demo. |
| Time left | Try A6 (multilingual embeddings) only if the model card confirms Kannada. |

**Never** present the holdout F1 from the seed data as real-world accuracy.

### 7.11 Testing predictions against examples

Quick manual check from a Python shell (project root):

```python
from backend.analyzer import Analyzer
a = Analyzer()
r = a.analyze("My payment failed but Rs. 2,499 was deducted. Please refund it urgently.")
print(r["status"], [(i["label"], i["confidence"]) for i in r["intents"]], r["entities"])
```

Then run the full test set with `python -m training.evaluate`:

```python
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from backend import config
from backend.intent_detector import IntentDetector
import json

labels = list(json.loads(config.INTENTS_PATH.read_text(encoding="utf-8")))
det = IntentDetector(config.MODEL_PATH, labels)
df = pd.read_csv(config.TEST_CSV)           # columns: text,intent,language
rows = []
for text, true in zip(df.text, df.intent):
    top = det.predict(text, top_k=1)[0]
    rows.append((true, top["label"], top["confidence"]))
res = pd.DataFrame(rows, columns=["true", "pred", "score"])
res["language"] = df.language.values

print(f"Mode: {det.mode} | test rows: {len(res)}")
print("Accuracy:", round(accuracy_score(res.true, res.pred), 3))
print(classification_report(res.true, res.pred, zero_division=0))
print(confusion_matrix(res.true, res.pred, labels=sorted(set(res.true) | set(res.pred))))

print("\nPer-language accuracy:")
print(res.assign(ok=res.true == res.pred).groupby("language").ok.agg(["mean", "count"]))

print("\nThreshold table (use it to choose ACCEPT_THRESHOLD):")
for t in (0.30, 0.40, 0.50, 0.55, 0.60, 0.70):
    kept = res[res.score >= t]
    acc = (kept.true == kept.pred).mean() if len(kept) else float("nan")
    print(f"threshold {t:.2f}: coverage {len(kept)/len(res):.0%}, accuracy on covered {acc:.0%}")
```

---

## 8. Backend API Design

Base URL (local): `http://127.0.0.1:5000`. All bodies are JSON (`Content-Type: application/json`). Errors always use:

```json
{ "error": { "code": "empty_message", "message": "Please enter a message." } }
```

### 8.1 Endpoint summary

| Method | Path | Purpose | Priority |
|---|---|---|---|
| GET | `/api/health` | Server and model status | MVP |
| GET | `/api/intents` | Intent list for correction dropdown | MVP |
| POST | `/api/analyze` | Analyze one message | MVP |
| POST | `/api/analyze/batch` | Analyze up to 50 messages | SHOULD |
| POST | `/api/feedback` | Confirm or correct a prediction | MVP |
| GET | `/api/history` | Recent predictions / review queue | MVP |
| GET | `/api/stats` | Dashboard numbers | SHOULD |
| DELETE | `/api/history` | Delete all stored predictions (admin) | SHOULD |

### 8.2 `POST /api/analyze`

**Request**
```json
{ "message": "My payment failed but Rs. 2,499 was deducted. Please refund it urgently.", "save": true }
```

**Response 200 (illustrative values)**
```json
{
  "id": 42,
  "message_masked": "My payment failed but Rs. 2,499 was deducted. Please refund it urgently.",
  "language": "en",
  "status": "multi_intent",
  "multi_intent": true,
  "intents": [
    {"label": "payment_issue", "display": "Payment Issue", "confidence": 0.62, "clause": "My payment failed"},
    {"label": "refund_request", "display": "Refund Request", "confidence": 0.58, "clause": "Please refund it urgently"}
  ],
  "alternatives": [],
  "entities": [
    {"type": "amount", "value": "INR 2499"},
    {"type": "issue", "value": "deducted"}
  ],
  "missing_entities": ["order_id"],
  "urgency": "high",
  "clarification_question": "Could you share your Order ID so we can look into this?",
  "needs_review": false,
  "route_to": {"teams": ["Payments & Billing", "Refunds & Billing"], "priority": "high"},
  "pii_masked": {},
  "model": {"mode": "trained", "note": "Scores are model outputs, not calibrated probabilities."}
}
```

| Field | Meaning |
|---|---|
| `status` | `confident`, `multi_intent`, `needs_clarification`, `unknown`, `unsupported` |
| `intents` | Final intents, ranked. `clause` is set only for multi-intent |
| `alternatives` | Runner-up intents (single-intent case) |
| `id` | Database ID, or `null` if saving failed or `save` was false |
| `missing_entities` | Required entities not found (e.g. `order_id`) |

**Validation and errors**

| Condition | HTTP | `error.code` |
|---|---|---|
| Body is not a JSON object | 400 | `invalid_json` |
| `message` missing or not a string | 400 | `invalid_message` |
| Empty or whitespace only | 400 | `empty_message` |
| Longer than `MAX_MESSAGE_CHARS` | 400 | `message_too_long` |
| No letters (e.g. `"12345 !!!"`) | 422 | `no_text_content` |
| Body larger than 256 KB | 413 | `request_entity_too_large` |
| Unexpected server error | 500 | `internal_error` |

If the database is unavailable, analysis still succeeds with `"id": null`.

### 8.3 `POST /api/analyze/batch`

**Request**
```json
{ "messages": ["Where is my order #48213?", "", "Cancel ORD-77120"], "save": true }
```
**Response 200**
```json
{
  "results": [
    {"index": 0, "result": { "...same shape as /api/analyze..." }},
    {"index": 1, "error": {"code": "empty_message", "message": "Please enter a message."}},
    {"index": 2, "result": { "...": "..." }}
  ]
}
```
Errors: `invalid_messages` (not a non-empty list), `too_many_messages` (> 50). One bad item does not fail the batch.

### 8.4 `POST /api/feedback`

**Request: confirm**
```json
{ "prediction_id": 42, "action": "confirm" }
```
**Request: correct**
```json
{ "prediction_id": 42, "action": "correct", "corrected_intent": "refund_request" }
```
**Response 200**
```json
{ "id": 42, "review_status": "corrected", "corrected_intent": "refund_request", "top_intent": "payment_issue", "...": "..." }
```
| Condition | HTTP | `error.code` |
|---|---|---|
| `prediction_id` not an integer | 400 | `invalid_id` |
| `action` not `confirm`/`correct` | 400 | `invalid_action` |
| Unknown `corrected_intent` | 400 | `invalid_intent` |
| ID not found | 404 | `not_found` |

### 8.5 `GET /api/history?limit=50&status=needs_clarification&review=pending`

All query parameters optional. `limit` 1-200 (default 50). Review queue = `?review=pending`.

**Response 200**
```json
{ "items": [ { "id": 41, "created_at": "2025-01-15T10:22:04Z", "message_masked": "It's not working.",
               "top_intent": "general_inquiry", "confidence": 0.21, "status": "unknown",
               "needs_review": true, "review_status": "pending", "urgency": "normal",
               "clarification_question": "Could you tell us a bit more? ...", "entities": [], "intents": [ ] } ] }
```
Error: `invalid_limit` (400).

### 8.6 `GET /api/stats`

```json
{ "total": 120, "by_intent": {"refund_request": 22}, "by_status": {"confident": 80},
  "by_language": {"en": 95, "kn-latn": 14}, "pending_review": 9, "high_urgency": 17,
  "avg_score": 0.612, "reviewer_agreement": 0.84 }
```
`reviewer_agreement` is `confirmed ÷ (confirmed + corrected)` among reviewed rows, or `null` if none reviewed. It describes reviewer behavior on the sampled queue, not overall model accuracy. (All numbers above are illustrative.)

### 8.7 `GET /api/health`, `GET /api/intents`, `DELETE /api/history`

```json
{ "status": "ok", "detector_mode": "trained" }
```
```json
{ "intents": [ {"label": "order_tracking", "display": "Order Tracking"}, "..." ] }
```
`DELETE /api/history` requires header `X-Admin-Token: <ADMIN_TOKEN>`; returns `{"deleted": 57}` or 403 `forbidden`. Disabled when `ADMIN_TOKEN` is empty.

### 8.8 Manual API tests

macOS/Linux:
```bash
curl -s -X POST http://127.0.0.1:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"Where is my order #48213?"}'
```
Windows PowerShell (the `curl` alias behaves differently, use this instead):
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/analyze `
  -ContentType "application/json" `
  -Body '{"message":"Where is my order #48213?"}' | ConvertTo-Json -Depth 6
```

---

## 9. Sample Data and Expected Output

> **Important:** the confidence ranges below are **illustrative targets for demo planning**, not measured model performance. Your real numbers depend on your dataset and will differ. Record real outputs after training and compare.

| ID | Type | Input message | Expected intent(s) | Expected entities | Clarification needed? | Illustrative score range |
|---|---|---|---|---|---|---|
| M1 | Clear | "Where is my order #48213? It was supposed to arrive yesterday." | `order_tracking` (alt: `delivery_problem`) | order_id `48213`; date `yesterday` | No | 0.50 – 0.80 |
| M2 | Clear | "I want to cancel order ORD-77120, I ordered it by mistake." | `order_cancellation` | order_id `ORD-77120` | No | 0.55 – 0.85 |
| M3 | Multi-intent (the deck's example) | "My payment failed but Rs. 2,499 was deducted. Please refund it urgently." | `payment_issue` + `refund_request`; urgency **high** | amount `INR 2499`; issue `deducted` | Asks for Order ID (missing) | each 0.40 – 0.70 |
| M4 | Multi-intent | "The wireless earbuds I got yesterday have a broken left speaker and I want to exchange them." | `return_exchange` (+ possibly `complaint`) | product `wireless earbuds`; date `yesterday`; issue `broken` | Asks for Order ID | 0.45 – 0.75 |
| M5 | Clear | "Does the Galaxy M14 come in blue and does it support fast charging?" | `product_information` | product `Galaxy M14` | No | 0.50 – 0.80 |
| M6 | Ambiguous | "I was charged but I can't see my order." | `payment_issue` vs `order_tracking` | none | **Yes**: "Is your payment not going through, or is the payment done and you cannot see your order?" | top 0.30 – 0.50, small gap |
| M7 | Hard multi-intent (known limitation) | "This is the third time my delivery is late and nobody is answering. Terrible service!" | Ideal: `delivery_problem` + `complaint`. The clause splitter may return just one | issue `late` | Possibly | 0.40 – 0.65 |
| M8 | Very vague | "It's not working." | None clear → `unknown` | none | **Yes**: generic question | below 0.35 |
| M9 | Unsupported | "What's the weather like in Bengaluru today?" | `out_of_scope` → `unsupported` | none | No (polite decline) | 0.40 – 0.80 |
| M10 | Kannada script | "ನನ್ನ ಆರ್ಡರ್ ಎಲ್ಲಿದೆ? ಇನ್ನೂ ಬಂದಿಲ್ಲ" | `order_tracking` (alt: `delivery_problem`); language `kn` | none | Likely asks for Order ID | 0.30 – 0.65 (depends on Kannada data) |
| M11 | Romanized Kannada, multi-intent | "Nanna order cancel madi, hana refund beku" | `order_cancellation` + `refund_request`; language `kn-latn` | none | Asks for Order ID | each 0.30 – 0.60 (depends on data) |
| M12 | General | "Hi, what are your customer care working hours?" | `general_inquiry` | none | No | 0.45 – 0.80 |
| M13 | PII | "My card 4111 1111 1111 1111 was charged twice, call me on 9876543210 or mail asha@example.com" | `payment_issue`; urgency **high** | issue `charged twice` | No | 0.45 – 0.75 |
| M14 | Clear with ID | "Order 51234 arrived with the wrong size, how do I exchange it?" | `return_exchange` | order_id `51234`; issue `wrong size` | No | 0.50 – 0.80 |

**Expected masked output for M13:**
`My card [CARD] was charged twice, call me on [PHONE] or mail [EMAIL]` with `"pii_masked": {"CARD": 1, "PHONE": 1, "EMAIL": 1}` (4111 1111 1111 1111 is a standard test card number that passes the Luhn check; no real card is involved).

Add these 14 messages to the "Example messages" dropdown in the UI for the demo.

---

## 10. Privacy and Security

> We do **not** claim this prototype is compliant with GDPR, India's DPDP Act, PCI-DSS or any other regulation. Compliance requires legal review, a security assessment and proper operations, none of which a hackathon prototype has.

### 10.1 Input validation
- Server side (never trust the browser): type check, trim, non-empty, max length (`MAX_MESSAGE_CHARS`), must contain letters, request body size cap (`MAX_CONTENT_LENGTH`).
- Strip control characters during `normalize()`.
- Validate `corrected_intent` against the list in `intents.json`; validate IDs as integers.
- SQL is always parameterized through SQLAlchemy; never build SQL with string formatting.

### 10.2 Secrets and configuration
- All credentials live in `.env` (listed in `.gitignore`); `.env.example` has placeholders only.
- No API keys exist in the default stack. If you add an external API later, read the key with `os.getenv(...)`, never place it in JavaScript or in the repository, and call the API from the backend only.
- Use a dedicated MySQL user with rights only on `intent_db`, not `root`.
- Keep `debug=False`; Flask's debugger exposes code execution.

### 10.3 Personal data handling (maps to deck Feature 6)

| Principle | Implementation |
|---|---|
| **PII detection** | `privacy.py` patterns: email, phone, card (Luhn-checked), UPI, PAN, Aadhaar-format, OTP phrases |
| **Anonymization** | Replaced by `[EMAIL]`, `[PHONE]`, ... before classification and before storage |
| **Data minimization** | Only masked text and derived fields are stored; raw text is never written to DB or logs |
| **Controlled retention** | `RETENTION_DAYS` + `python -m backend.database purge`; `DELETE /api/history`; `STORE_MASKED_TEXT=false` stores no text at all |
| **Encryption (deck slide 8)** | Use HTTPS when deployed, MySQL TLS/disk encryption where available. We rely on platform features; no homemade crypto |
| **Logging** | Do not log message bodies. Log only IDs, statuses and errors |

Limits to state openly: regex detection misses names, addresses and unusual formats; order IDs are intentionally kept (they are business identifiers, but treat them as sensitive in real deployments).

### 10.4 Preventing unsafe rendering (XSS)
- In JavaScript render user-provided or API text **only** with `textContent` (the `el()` helper in §5.4) or inside `<pre>`; never use `innerHTML` with such text.
- Add a Content-Security-Policy meta tag in `index.html`:
  `<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self'">`
  (remove the CDN host if you vendor Chart.js locally).
- JSON responses are produced with `jsonify`, which escapes properly.

### 10.5 Other protections
- The review and delete actions are unauthenticated in the MVP except the admin token on `DELETE`. State this in the demo; A7 adds login.
- Optional rate limiting (e.g. Flask-Limiter) if the demo is exposed publicly.
- Bind to `127.0.0.1` for local demos; put a proper reverse proxy and HTTPS in front if deploying.
- Prompt-injection note: the default stack uses no LLM, so message text cannot instruct the system. If you add an LLM later, treat messages strictly as data and constrain outputs to the label list.

---

## 11. Testing and Evaluation

### 11.1 Functional test cases

| ID | Area | Input / action | Expected result |
|---|---|---|---|
| T1 | Correct intent | M2 "cancel order ORD-77120" | `order_cancellation`, status not `unknown` |
| T2 | Correct intent | M5 product question | `product_information` |
| T3 | Entities | M1 | order_id `48213`, date `yesterday` |
| T4 | Entities | "Rs. 2,499 deducted" | amount `INR 2499` |
| T5 | Entities | "order 9876543210" | recognized as order_id, **not** masked as phone |
| T6 | Ambiguous | M6 | status `needs_clarification`, non-empty question |
| T7 | Multiple intents | M3, M11 | `multi_intent`, ≥ 2 intents, ranked |
| T8 | Low confidence | M8 "It's not working." | status `unknown`, generic question, `needs_review = true`, queued |
| T9 | Unsupported | M9 | status `unsupported`, no teams |
| T10 | Privacy | M13 | no `4111`, `9876543210` or email in `message_masked`; DB row also masked |
| T11 | Empty input | `{"message": "   "}` | 400 `empty_message`; UI shows inline error without a request |
| T12 | Invalid input | `{"message": 123}`; `{"message": "12345 !!!"}`; non-JSON body | 400 `invalid_message`; 422 `no_text_content`; 400 `invalid_json` |
| T13 | Too long | 1001 characters | 400 `message_too_long` |
| T14 | API errors | Stop MySQL / point to a bad DB | `/api/analyze` still returns 200 with `id: null`; UI disables review buttons |
| T15 | API errors | Backend stopped | UI shows banner with Retry, no blank page |
| T16 | Feedback | Confirm, correct, bad intent, bad id | Row updated; 400 `invalid_intent`; 404 `not_found` |
| T17 | Review flow | Correct a prediction, run `python -m training.train --include-feedback` | Output says it added N reviewed rows |
| T18 | XSS | Message `<script>alert(1)</script>` | Text appears literally; no alert |
| T19 | Fallback mode | Delete `models/intent_model.joblib`, restart | `/api/health` shows `keyword_fallback`; UI badge visible |
| T20 | Batch | 51 messages; list with one empty item | 400 `too_many_messages`; partial results with per-item error |
| T21 | Mobile | Chrome DevTools at 360×640 and 768×1024, plus a real phone | No horizontal page scroll; buttons ≥ 44 px; table scrolls inside its container; text readable |

### 11.2 Automated tests

`tests/conftest.py`
```python
import os
os.environ["DATABASE_URL"] = "sqlite:///test_intent.db"     # never touch the real DB
```

`tests/test_entities.py`
```python
from backend import config
from backend.entity_extractor import EntityExtractor

ex = EntityExtractor(config.PRODUCTS_PATH)

def found(text):
    return {(e["type"], e["value"]) for e in ex.extract(text)}

def test_order_hash():     assert ("order_id", "48213") in found("Where is my order #48213?")
def test_order_prefixed(): assert ("order_id", "ORD-77120") in found("cancel ORD-77120 please")
def test_amount():         assert ("amount", "INR 2499") in found("Rs. 2,499 was deducted")
def test_relative_date():  assert ("date", "yesterday") in found("it arrived yesterday")
def test_random_number_ignored():
    assert not [e for e in ex.extract("I waited 45678 minutes") if e["type"] == "order_id"]
```

`tests/test_privacy.py`
```python
from backend.privacy import mask_pii

def test_masks_card_phone_email():
    out, counts = mask_pii("card 4111 1111 1111 1111 call 9876543210 mail a@b.com")
    assert "4111" not in out and "9876543210" not in out and "a@b.com" not in out
    assert counts == {"CARD": 1, "PHONE": 1, "EMAIL": 1}

def test_protected_span_kept():
    text = "order 9876543210 please"
    start = text.index("9876543210")
    out, counts = mask_pii(text, protected_spans=[(start, start + 10)])
    assert "9876543210" in out and counts == {}
```

`tests/test_api.py`
```python
from app import app

client = app.test_client()
post = lambda body: client.post("/api/analyze", json=body)

def test_empty():
    r = post({"message": "   "})
    assert r.status_code == 400 and r.get_json()["error"]["code"] == "empty_message"

def test_wrong_type():      assert post({"message": 123}).status_code == 400
def test_no_letters():      assert post({"message": "12345 !!!"}).status_code == 422
def test_too_long():        assert post({"message": "a" * 1001}).status_code == 400

def test_invalid_json():
    r = client.post("/api/analyze", data="nope", content_type="application/json")
    assert r.status_code == 400

def test_valid_shape():
    r = post({"message": "Where is my order #48213?", "save": False})
    body = r.get_json()
    assert r.status_code == 200
    assert {"intents", "entities", "status", "route_to"} <= body.keys()
    assert any(e["type"] == "order_id" and e["value"] == "48213" for e in body["entities"])

def test_feedback_unknown_id():
    r = client.post("/api/feedback", json={"prediction_id": 999999, "action": "confirm"})
    assert r.status_code == 404
```

Run: `python -m pytest -v`. These tests check **behavior and contracts**, not model accuracy.

### 11.3 Evaluating the model

Use `data/test_messages.csv` (hand-labelled, **never** in training). Metrics, via `python -m training.evaluate`:

| Metric | What it tells you |
|---|---|
| **Accuracy** | Share correct overall; misleading if classes are unbalanced |
| **Precision (per intent)** | Of messages predicted as X, how many truly are X; high precision avoids wrong auto-routing |
| **Recall (per intent)** | Of true X messages, how many we found; low recall means missed requests |
| **F1 / macro-F1** | Balance of precision and recall; macro-F1 treats all intents equally |
| **Confusion matrix** | Which intents get mixed up; use it to write better clarification questions |
| **Per-language accuracy** | Reports English, Kannada, Kanglish separately |
| **Coverage vs accuracy (threshold table)** | The honest way to set `ACCEPT_THRESHOLD`: higher threshold = fewer auto-routes, higher accuracy on those |
| **Review rate** | Fraction of messages sent to humans; shows the workload tradeoff |
| **Entity precision/recall** | Annotate entities for ~30 test messages; count correct, missed and spurious extractions per entity type |
| **Multi-intent exact match** | On a small set of multi-intent test messages, share where the predicted *set* of intents equals the true set |

**Reporting rules:** always quote the number of test messages, say the data are hand-written by the team, and do not generalize ("93% on our 80 test messages", not "93% accurate"). With a few dozen test rows, differences of a few points are noise.

---

## 12. Team Division

| Role | Owner | Main responsibilities | Files |
|---|---|---|---|
| **A. Frontend and UI/UX** | ____ | Figma designs, all screens, states, responsive CSS, charts, calls to the API, mock data | `frontend/*` |
| **B. Backend and API** | ____ | Flask routes, validation, error handling, MySQL schema and queries, retention/purge, security settings | `app.py`, `backend/database.py`, `backend/config.py`, `.env.example` |
| **C. AI/NLP and data** | ____ | Dataset and labeling guide, training/evaluation scripts, intent detector, entity extractor, PII masking, language detection, thresholds, Kannada data | `backend/{intent_detector,entity_extractor,privacy,preprocess,analyzer}.py`, `training/*`, `data/*` |
| **D. Integration, testing, docs, presentation** | ____ | Integration branch, automated and manual tests, README, sample messages, demo script, slides, bug triage | `tests/*`, `README.md`, demo assets |

(Fill in names. Ask a Kannada speaker, whichever role, to own Kannada data verification.)

### 12.1 Contracts that remove blocking

1. **API contract (frozen on day 1):** the JSON in §8. Changes need a team decision and an update to this file.
2. **Analyzer contract:** `Analyzer.analyze(text: str) -> dict` returning the shape in §8.2. Member B depends only on this function.
3. **Intent list contract:** `data/intents.json`. Everyone reads it; only C edits it (with team notice).
4. **Mock-first workflow:**
   - A builds against `MOCK_RESULT` (`USE_MOCK = true`) with three mock results: confident, ambiguous, multi-intent.
   - B starts with a stub analyzer returning the same mock shape, so the API and DB work before the model exists.
   - C develops in a Python shell/notebook and delivers `analyze()` into `analyzer.py`.
   - D writes tests against the contract from day 1; they pass against the stub and the real analyzer.

### 12.2 Integration plan

| Checkpoint | What happens | Gate |
|---|---|---|
| **CP0** (start) | Repo created, structure from §6, API contract agreed, branches per member | Everyone can run `python app.py` on an empty skeleton |
| **CP1** | B's API returns stub results; A's UI renders mocks | UI shows a stub result from the real `/api/analyze` |
| **CP2** | C's seed model + extractor + masker merged into `analyzer.py` | M1-M14 return sensible output; unit tests green |
| **CP3** | Review queue, feedback and dashboard connected | Full loop: analyze → review → stats update |
| **CP4** | Freeze features; test, tune thresholds, rehearse | Test table in §11.1 completed; demo script run twice |

Git rules: short-lived feature branches, merge to `main` through D's integration check, commit small and often, never commit `.env`, `models/`, or `*.db`. Daily 10-minute sync, one shared issue list.

---

## 13. Setup and Execution

### 13.1 Install prerequisites

| Software | Version | Notes |
|---|---|---|
| Python | 3.10 or newer | Windows: tick "Add Python to PATH" in the installer |
| Git | any recent | |
| MySQL Server | 8.x | Optional for a first run; SQLite fallback exists |
| Browser | Chrome, Edge or Firefox | |

### 13.2 Get the project and create a virtual environment

macOS / Linux:
```bash
cd intelligent-intent-detector
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):
```powershell
cd intelligent-intent-detector
py -m venv venv
venv\Scripts\Activate.ps1
# If activation is blocked:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Windows (Command Prompt): `venv\Scripts\activate.bat`

### 13.3 Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 13.4 Configure the database

**Option A: SQLite (fastest, for first runs).** Create `.env` containing:
```ini
DATABASE_URL=sqlite:///intent.db
```

**Option B: MySQL (the deck's database).** In the MySQL shell (`mysql -u root -p`):
```sql
CREATE DATABASE intent_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'intent_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON intent_db.* TO 'intent_user'@'localhost';
FLUSH PRIVILEGES;
```
Copy `.env.example` to `.env` (`cp .env.example .env` on macOS/Linux, `copy .env.example .env` on Windows) and set:
```ini
DATABASE_URL=mysql+pymysql://intent_user:choose-a-strong-password@localhost:3306/intent_db?charset=utf8mb4
```
`utf8mb4` is required so Kannada text is stored correctly. Tables are created automatically on first start (or run `python -m backend.database init`). If the password contains special characters, URL-encode them.

### 13.5 Prepare data and train

1. Fill `data/training_data.csv` (start with the seed in §7.3) and `data/test_messages.csv`.
2. Edit `data/products.txt` for your demo catalogue.
3. Train from the project root:
```bash
python -m training.train
python -m training.evaluate
```
Check that `models/intent_model.joblib` now exists.

### 13.6 Start the backend and open the frontend

```bash
python app.py
```
Open **http://127.0.0.1:5000** in a browser. Flask serves the frontend and the API on the same address. Health check: http://127.0.0.1:5000/api/health (should show `"detector_mode": "trained"`).

### 13.7 Test locally

```bash
python -m pytest -v
```
Then run the manual checks T1-T21 (§11.1) and the 14 sample messages (§9) in the UI. Use browser DevTools device mode for mobile checks.

### 13.8 Common problems

| Symptom | Likely fix |
|---|---|
| `ModuleNotFoundError: backend` | Run commands from the project root; use `python -m training.train`, not `python training/train.py` |
| Health shows `keyword_fallback` | Model not trained yet; run `python -m training.train` and restart `app.py` |
| MySQL "Authentication plugin" error | Ensure `cryptography` is installed (it is in `requirements.txt`) |
| Kannada shows as `???` in DB | Database/tables not `utf8mb4`; recreate with the SQL above |
| Windows PowerShell: script blocked | Use the `Set-ExecutionPolicy -Scope Process` line from §13.2 |
| Port 5000 already in use | Change the port in the last line of `app.py` |
| Charts empty offline | Copy Chart.js into `frontend/vendor/` and point the `<script>` tag to it |

### 13.9 Retraining with human feedback

After reviewers have confirmed or corrected some predictions:
```bash
python -m training.train --include-feedback
```
Restart `app.py` to load the new model. Re-run `python -m training.evaluate` on the untouched test set and compare with the previous run before claiming any improvement.

---

## 14. Development Roadmap

Time shares are relative; scale them to your deadline.

### Phase 1: Minimum viable prototype (~25%)
- [ ] Repo, structure, `.env.example`, `requirements.txt` (§6)
- [ ] Freeze the API contract; mock results for the UI
- [ ] Flask app with `/api/health` and `/api/analyze` returning stub data
- [ ] SQLite (or MySQL) connected; `predictions` table
- [ ] UI: Analyze screen with textarea, button, result card, error/loading states
- [ ] Figma frames for the four screens
- [ ] First 40 training rows and `intents.json`

**Exit:** type a message in the browser, get a (stub) result saved in the DB.

### Phase 2: Core AI/NLP (~30%)
- [ ] Normalization, language detection, PII masking, entity extractor with unit tests (F2, F3, F6)
- [ ] Training CSV expanded (≥ 30 per intent English, ≥ 10 Kannada/Kanglish) and test CSV written
- [ ] Train TF-IDF + Logistic Regression; `evaluate.py` (F1)
- [ ] Threshold decision logic, clarification questions, routing (F5, F10)
- [ ] Clause-based multi-intent detection (F4)
- [ ] Urgency rules (F13)
- [ ] Replace the stub with the real `Analyzer`

**Exit:** samples M1-M14 behave as in §9 (or differences are understood and documented).

### Phase 3: Integration and UI improvements (~25%)
- [ ] Review Queue screen and `/api/feedback` (F8)
- [ ] `/api/history`, `/api/stats`, Dashboard with Chart.js (A1)
- [ ] Mobile layout polish; accessibility pass
- [ ] Retention purge command, `DELETE /api/history` (F6)
- [ ] `--include-feedback` retraining (F9)
- [ ] SHOULD: batch endpoint (F12), configurable intents demo (F11)
- [ ] OPTIONAL (only if everything above is stable): A2 explainability, A3 reply templates, A4 CSV, A5 sentiment, A6 embeddings, A7 login, A8 dark mode

**Exit:** the full loop works: analyze → clarify/review → feedback → stats → retrain.

### Phase 4: Testing and final demonstration (~20%)
- [ ] Automated tests green; manual test table §11.1 completed
- [ ] Tune thresholds from the coverage-vs-accuracy table
- [ ] Record real metrics with test-set size and caveats
- [ ] Vendor Chart.js locally; prepare an offline-capable demo and a screen recording as backup
- [ ] README, final slides, rehearse the demo twice
- [ ] Feature freeze 3-4 hours before the deadline (hackathon rule of thumb)

---

## 15. Final Deliverables and Demo Checklist

### 15.1 Deliverables
- [ ] Source repository with the structure in §6
- [ ] Working local app (`python app.py`)
- [ ] `data/` with the training and test CSVs and `intents.json`
- [ ] `models/intent_model.joblib` generated (not committed)
- [ ] README with the setup steps from §13
- [ ] This `PROJECT_SPECIFICATION.md` updated to match what was actually built
- [ ] Final presentation and (if required) PDF named `TeamID_Domain` per the organizers' rules

### 15.2 Suggested 3-minute demo script
1. **Problem (20 s):** "Customers don't say what they want." Show M3 (deck's payment + deduction example).
2. **Analyze (60 s):** run M3: two intents, entities, urgency high, routing; run M11 (Kanglish, multi-intent) to show multilingual handling.
3. **Uncertainty (40 s):** run M6 or M8: system asks a targeted question instead of guessing; it lands in the review queue.
4. **Privacy (20 s):** run M13: card, phone and email masked; show the DB row.
5. **Human loop (30 s):** correct a prediction in the Review Queue; show the dashboard update and mention retraining.
6. **Honest close (10 s):** "Trained on N hand-written examples; metrics on M test messages; Kannada is experimental; next steps: more data, embeddings, auth."

### 15.3 Claims you may and may not make

| You may say | You may not say |
|---|---|
| "Detects intent, entities and multiple intents using a model trained on our dataset of N examples" | "99% accurate" or any accuracy not measured on a held-out set |
| "Scores are used for thresholds and review routing" | "The score is the probability the answer is correct" |
| "Masks common PII patterns before storage" | "Fully GDPR/DPDP compliant" |
| "Supports Kannada, English and mixed text (experimental for Kannada)" | "Understands all Indian languages" |
| "Corrections are collected and used when we retrain" | "Learns in real time" |

---

*End of PROJECT_SPECIFICATION.md. Keep this file in the repository root and update it whenever the design changes.*
