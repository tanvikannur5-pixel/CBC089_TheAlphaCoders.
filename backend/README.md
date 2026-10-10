# Backend Component - Intelligent Customer Intent Detector

> **Assigned Team Member:** Backend Developer (Member 2)  
> **Technologies:** Python 3.10+, Flask 3.x, REST API, JSON.

---

## 1. Directory Structure

```
backend/
├── app.py                 # Flask application factory, blueprint registration & error handling
├── config.py              # Central environment variables, thresholds & static/template paths
├── routes/                # Modular Flask route Blueprints
│   ├── meta_routes.py     # Root view (/), /api/health, /api/intents, /api/history, /api/stats
│   ├── analyze_routes.py  # /api/analyze, /api/analyze/batch
│   └── feedback_routes.py # /api/feedback (human review confirm/correct actions)
├── services/              # Business logic & component integration
│   └── analysis_service.py# Message validation, ML model bridge & database persistence
└── README.md              # This backend component guide
```

---

## 2. Independent Development & Commands

Member 2 can run and develop the backend API from their laptop:

### Start the Backend Server:
```powershell
python -m backend.app
```
or run from project root:
```powershell
python run.py
```
The server binds to `0.0.0.0` by default and uses the `PORT` environment
variable (default `5000`); open `http://127.0.0.1:5000` for local development.

### Production WSGI Server

From the project root on a Linux hosting platform, start the exported root
application with:

```sh
gunicorn --bind "0.0.0.0:${PORT:-5000}" app:app
```

### Health Check:
```powershell
curl http://127.0.0.1:5000/api/health
```
Returns: `{"status": "ok", "detector_mode": "trained"}`.

---

## 3. API Contract Specifications

All API responses are formatted in standardized JSON.

### `POST /api/analyze`
**Request:**
```json
{
  "message": "Where is my order #48213? It was supposed to arrive yesterday.",
  "save": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "confident",
  "language": "en",
  "intents": [
    { "label": "order_tracking", "display": "Order Tracking", "confidence": 0.64, "clause": null }
  ],
  "entities": [
    { "type": "order_id", "value": "48213" },
    { "type": "date", "value": "yesterday" }
  ],
  "urgency": "normal",
  "clarification_question": null,
  "route_to": { "teams": ["Order Support"], "priority": "normal" },
  "message_masked": "Where is my order #48213? It was supposed to arrive yesterday."
}
```

### Error Responses
All 4xx and 5xx errors return uniform schema:
```json
{
  "error": {
    "code": "empty_message",
    "message": "Please enter a message."
  }
}
```
Standard codes: `invalid_json`, `invalid_message`, `empty_message`, `message_too_long`, `no_text_content`, `invalid_id`, `invalid_action`, `invalid_intent`, `not_found`, `forbidden`, `internal_error`.
