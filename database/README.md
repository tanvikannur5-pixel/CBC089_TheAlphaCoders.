# Database Component - Intelligent Customer Intent Detector

> **Assigned Team Member:** Database / Backend Support  
> **Technologies:** SQLAlchemy 2.x, SQLite (development default) / MySQL 8 (production option).

---

## 1. Directory Structure

```
database/
├── database.py       # SQLAlchemy ORM models, session maker, migrations & query functions
└── README.md         # This database component guide
```

---

## 2. Configuration & Connections

Connection URL is controlled via `DATABASE_URL` in `.env`:

### Option A: SQLite (Zero Configuration - Default)
```ini
DATABASE_URL=sqlite:///intent.db
```

### Option B: MySQL 8 (As Promised in Submitted Deck)
```ini
DATABASE_URL=mysql+pymysql://intent_user:your_password@localhost:3306/intent_db?charset=utf8mb4
```
*(Note: `charset=utf8mb4` is mandatory to store Kannada script correctly).*

---

## 3. Database Schema: `predictions` Table

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incrementing prediction ID |
| `created_at` | DateTime | UTC timestamp of the query |
| `masked_text` | Text (Nullable) | PII-masked query (`[CARD]`, `[PHONE]`, etc.). NULL if storage disabled. |
| `language` | String(16) | Detected language: `en`, `kn`, `kn-latn`, `mixed` |
| `top_intent` | String(40) | Highest ranked intent label |
| `confidence` | Float | Model output score for top intent |
| `status` | String(24) | `confident`, `multi_intent`, `needs_clarification`, `unknown`, `unsupported` |
| `multi_intent` | Boolean | True if multiple distinct clause requests found |
| `urgency` | String(8) | `normal` or `high` |
| `needs_review` | Boolean | Flagged true if ambiguous or low score |
| `result_json` | Text | Serialized entities, routing, and clarification questions |
| `review_status`| String(16) | `not_required`, `pending`, `confirmed`, `corrected` |
| `corrected_intent` | String(40) | Replacement label submitted by reviewer |
| `reviewed_at` | DateTime | UTC timestamp when reviewer acted |

---

## 4. Independent CLI Commands

Initialize the database tables:
```powershell
python -m database.database init
```

Purge records older than the retention period (`RETENTION_DAYS`, default 7 days):
```powershell
python -m database.database purge
```
