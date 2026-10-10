# Frontend Component - Intelligent Customer Intent Detector

> **Assigned Team Member:** Frontend Developer (Member 1)  
> **Technologies:** HTML5, Modern CSS3 (custom CSS variables & flex/grid), Vanilla JavaScript (ES6+), Chart.js 4 (offline vendored).

---

## 1. Directory Structure

```
frontend/
├── templates/
│   └── index.html             # Single-page application containing all 4 views (#home, #analyze, #review, #dashboard)
├── static/
│   ├── style.css              # Custom design system with CSS tokens, responsive grid & animations
│   ├── script.js              # Client state, hash routing, API fetch client & Chart.js instances
│   └── vendor/
│       └── chart.umd.min.js   # Local vendored Chart.js library for offline presentation
└── README.md                  # This component guide
```

---

## 2. Run with the Backend

The frontend calls the same-origin `/api/*` endpoints and does not include a mock data implementation. Run the integrated Flask app from the repository root (see the root README), then open `http://127.0.0.1:5000`. Serving this folder with a separate static server displays the page but API features will not work unless that server is configured to proxy `/api/*` to Flask.

---

## 3. UI Views & Component Responsibilities

1. **Home (`#home`):**
   - Brand identity, problem statement tagline, "Launch Intent Detector" CTA.
   - 3-step workflow pipeline and 6 capability highlight cards.

2. **Analyze (`#analyze`):**
   - Multi-line textarea for customer queries with a live character counter (`0 / 1000`).
   - 11 benchmark sample message chips (M1–M14) for fast demo loading.
   - Dynamic Result Card displaying status badges, model score bar, sub-intent clause breakdowns, entity chips, clarification questions, routing destination, and masked PII text.
   - Human feedback action buttons (`Confirm` and `Correct` with dropdown).

3. **Review Queue (`#review`):**
   - Review list of queries flagged with `needs_review = true` and `review_status = pending`.
   - Allows support supervisors to confirm or correct low-confidence predictions.

4. **Operations Dashboard (`#dashboard`):**
   - 4 KPI summary cards (Total messages, Pending review, High urgency, Reviewer agreement).
   - 3 dynamic Chart.js charts (Intent Distribution, Status Breakdown, Language Modality Mix).
   - Recent message log table.
