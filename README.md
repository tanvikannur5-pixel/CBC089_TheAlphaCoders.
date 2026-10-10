# Intelligent Customer Intent Detector

> *"Catch the Intent. Clarify the Need. Trigger the Action."*

| Key Metric | Value |
|---|---|
| **Hackathon** | CBC 2.0, Design Round |
| **Team Name** | The Alpha Coders |
| **Team ID** | CBC089 |
| **Domain** | Artificial Intelligence and Machine Learning |
| **Problem ID** | PS-030 |

---

## 1. Project Overview & Multi-Member Architecture

This repository is organized into **four self-contained components** so different team members can develop, test, and run them independently on different laptops:

```
intelligent-customer-intent-detector/
├── frontend/                      # [Member 1: Frontend Developer]
│   ├── templates/                 # HTML5 single-page application (index.html)
│   ├── static/                    # Custom CSS, client JavaScript & vendored Chart.js
│   └── README.md                  # Frontend development & mock mode instructions
│
├── backend/                       # [Member 2: Backend Developer]
│   ├── app.py                     # Flask application factory & error handling
│   ├── routes/                    # Modular Blueprints (meta, analyze, feedback)
│   ├── services/                  # Validation & integration bridge to ML & DB
│   ├── config.py                  # Environment config & path resolution
│   └── README.md                  # Backend API documentation & run guide
│
├── ml_model/                      # [Member 3: AI / ML Developer]
│   ├── intent_detector.py         # TF-IDF + Logistic Regression NLP pipeline
│   ├── analyzer.py                # Pipeline orchestrator (Analyzer.analyze)
│   ├── preprocess.py              # Text normalizer, language detector & clause splitter
│   ├── privacy.py                 # PII masking (Luhn cards, phones, emails, UPI, OTP)
│   ├── entity_extractor.py        # Context-aware regex & product gazetteer extractor
│   ├── train.py                   # Model trainer with CV and feedback retraining loop
│   ├── evaluate.py                # Offline test evaluation & threshold curve
│   ├── data/                      # Intents JSON, product catalog, training & test CSVs
│   ├── models/                    # Serialized joblib pipeline & model metadata
│   └── README.md                  # AI/ML developer guide & training commands
│
├── database/                      # [Database Layer]
│   ├── database.py                # SQLAlchemy ORM (Prediction model, history, stats, purge)
│   └── README.md                  # Database setup (SQLite vs MySQL 8)
│
├── tests/                         # [Member 4: QA / Integration Lead]
│   ├── conftest.py                # Pytest setup & isolated test database fixture
│   ├── test_api.py                # REST API contract & validation tests
│   ├── test_entities.py           # Entity extraction unit tests
│   └── test_privacy.py            # PII masking unit tests
│
├── requirements.txt               # Python package dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules protecting models, db, and venv
├── app.py                         # WSGI entry point for production hosting
├── run.py                         # Single command to launch the full application
└── README.md                      # This root documentation
```

---

## 2. Quick Start: Running the Complete Application

### 1. Prerequisites & Virtual Environment
Open Windows PowerShell:
```powershell
# Clone or navigate to the repository
cd C:\HACKATHON

# Create and activate Python 3.10+ virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
copy .env.example .env
```
*(By default, `.env` uses zero-config SQLite: `DATABASE_URL=sqlite:///intent.db`).*

### 3. Launch the Application
```powershell
python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

## Production Deployment

The root `app.py` exports the Flask application as `app` for WSGI servers. On a
Linux hosting platform, install `requirements.txt` and use this start command:

```sh
gunicorn --bind "0.0.0.0:${PORT:-5000}" app:app
```

Gunicorn listens on all interfaces and uses the hosting platform's `PORT`
environment variable (or port 5000 when it is not set). The built-in Flask
launchers (`python app.py`, `python run.py`, and `python -m backend.app`) use
`HOST` and `PORT` from the environment; `HOST` defaults to `0.0.0.0`.

The frontend is served at `/` and its assets at `/static/`. It calls the API
through same-origin `/api/...` paths, so no frontend API host setting or
localhost URL needs to be changed for deployment.

Before deploying, set a strong unique `ADMIN_TOKEN` and configure `DATABASE_URL`
for a persistent production database. The default SQLite database is stored in
the application directory and may not persist across host restarts or releases.

---

## 3. How Teammates Develop Independently on Different Laptops

Each teammate has their own component directory with a dedicated `README.md` and zero cross-blocking dependencies:

### A. Member 1: Frontend Developer (`frontend/`)
- **Laptop Requirements:** Just a browser and optionally VS Code Live Server or Python.
- **Independent Testing:** Open `frontend/static/script.js` and set:
  ```javascript
  const USE_MOCK = true;
  ```
- **Run command:**
  ```powershell
  python -m http.server 8000 --directory frontend
  ```
  Open `http://localhost:8000/templates/index.html`. Member 1 can style, animate, test sample chips, review queues, and Chart.js charts completely isolated with mock fixtures without needing the backend or ML model!

### B. Member 2: Backend Developer (`backend/`)
- **Laptop Requirements:** Python 3.10+ and Flask.
- **Independent Testing:**
  ```powershell
  python -m backend.app
  ```
- Server starts on `http://127.0.0.1:5000` with full REST API endpoints (`/api/health`, `/api/intents`, `/api/analyze`, `/api/analyze/batch`, `/api/feedback`, `/api/history`, `/api/stats`).
- Connects to SQLite or MySQL automatically via SQLAlchemy.

### C. Member 3: AI / ML Developer (`ml_model/`)
- **Laptop Requirements:** Python 3.10+, scikit-learn, pandas, joblib.
- **Independent Commands:**
  ```powershell
  # Train model from CSV and export to ml_model/models/intent_model.joblib:
  python -m ml_model.train

  # Evaluate model accuracy on held-out benchmark test set:
  python -m ml_model.evaluate
  ```
- Member 3 works directly with training datasets (`ml_model/data/`), fine-tunes decision thresholds (`ml_model/config.py`), and tests NLP predictions in a Python shell without needing Flask or HTML.

### D. Member 4: Integration, QA & Database (`database/` & `tests/`)
- **Run Automated Tests:**
  ```powershell
  python -m pytest -v
  ```
- **Database Management:**
  ```powershell
  # Initialize or inspect database tables:
  python -m database.database init

  # Purge old records based on retention policy:
  python -m database.database purge
  ```

---

## 4. How the Components Communicate

```
+-------------------------------------------------------------+
|                     1. FRONTEND                             |
|  frontend/templates/index.html + frontend/static/*          |
+-------------------------------------------------------------+
                              │
                              │ HTTP REST JSON API
                              │ (fetch: /api/analyze, /api/feedback)
                              ▼
+-------------------------------------------------------------+
|                     2. BACKEND                              |
|  backend/app.py -> routes/ -> services/analysis_service.py   |
+-------------------------------------------------------------+
           │                                      │
           │ Python Class Contract                │ SQLAlchemy ORM
           │ Analyzer.analyze(raw_text: str)      │ save_prediction(), stats()
           ▼                                      ▼
+-----------------------+              +-----------------------+
|     3. ML MODEL       |              |     4. DATABASE       |
|  ml_model/analyzer.py |              |  database/database.py |
+-----------------------+              +-----------------------+
```

1. **Frontend $\leftrightarrow$ Backend:** Standard JSON over REST. Endpoints return status, ranked intents, confidence scores, extracted entities, clarification questions, and routing targets.
2. **Backend $\leftrightarrow$ ML Model:** One clean Python interface: `Analyzer.analyze(text: str) -> dict`. The backend passes the raw message and receives the complete structured result.
3. **Backend $\leftrightarrow$ Database:** Persistence is decoupled in `database/database.py`. If the database ever goes offline, the backend continues to serve predictions gracefully with `id: null`.
4. **ML Model $\leftrightarrow$ Database (Retraining Loop):** `python -m ml_model.train --include-feedback` queries reviewed records from the database and incorporates them into the next model training run.

---

## 5. Automated Test Verification Results

Automated tests are run via pytest:
```powershell
python -m pytest -v
```
- API routing, request validation, error formatting, and batch analysis: **Passed**.
- Entity extraction (`order_id`, amounts, dates, products, defect terms): **Passed**.
- PII masking with Luhn card checksum and order ID span protection: **Passed**.
- Reviewer confirmation and feedback logging: **Passed**.
- Held-out model accuracy on `ml_model/data/test_messages.csv`: **93.3%**.
