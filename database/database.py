import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Float, Boolean,
    DateTime, select, func, delete
)
from sqlalchemy.orm import declarative_base, sessionmaker

# Locate root directory and load .env
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT_DIR / 'intent.db').as_posix()}")
STORE_MASKED_TEXT = os.getenv("STORE_MASKED_TEXT", "true").lower() == "true"
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "7"))

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=utcnow, index=True)
    masked_text = Column(Text, nullable=True)
    language = Column(String(16))
    top_intent = Column(String(40), index=True)
    confidence = Column(Float)
    status = Column(String(24), index=True)
    multi_intent = Column(Boolean, default=False)
    urgency = Column(String(8))
    needs_review = Column(Boolean, default=False, index=True)
    result_json = Column(Text)
    review_status = Column(String(16), default="not_required")
    corrected_intent = Column(String(40), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(engine)


def to_dict(row: Prediction) -> dict:
    detail = json.loads(row.result_json or "{}")
    return {
        "id": row.id,
        "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        "message_masked": row.masked_text,
        "language": row.language,
        "top_intent": row.top_intent,
        "confidence": row.confidence,
        "status": row.status,
        "multi_intent": row.multi_intent,
        "urgency": row.urgency,
        "needs_review": row.needs_review,
        "review_status": row.review_status,
        "corrected_intent": row.corrected_intent,
        "intents": detail.get("intents", []),
        "entities": detail.get("entities", []),
        "clarification_question": detail.get("clarification_question"),
        "route_to": detail.get("route_to"),
    }


def save_prediction(result: dict) -> int:
    top = result["intents"][0] if result.get("intents") else {"label": "unknown", "confidence": 0.0}
    detail = {k: result[k] for k in ("intents", "entities", "clarification_question", "route_to") if k in result}
    row = Prediction(
        masked_text=result.get("message_masked") if STORE_MASKED_TEXT else None,
        language=result.get("language"),
        top_intent=top["label"],
        confidence=top["confidence"],
        status=result.get("status"),
        multi_intent=result.get("multi_intent", False),
        urgency=result.get("urgency", "normal"),
        needs_review=result.get("needs_review", False),
        result_json=json.dumps(detail, ensure_ascii=False),
        review_status="pending" if result.get("needs_review") else "not_required",
    )
    with SessionLocal() as s:
        s.add(row)
        s.commit()
        return row.id


def list_predictions(limit: int = 50, status: str = None, review: str = None) -> list[dict]:
    q = select(Prediction).order_by(Prediction.id.desc()).limit(limit)
    if status:
        q = q.where(Prediction.status == status)
    if review:
        q = q.where(Prediction.review_status == review)
    with SessionLocal() as s:
        return [to_dict(r) for r in s.scalars(q)]


def apply_feedback(pid: int, action: str, corrected_intent: str = None) -> dict | None:
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
        confirmed = reviewed.get("confirmed", 0)
        corrected = reviewed.get("corrected", 0)
        total_rev = confirmed + corrected

        return {
            "total": s.scalar(select(func.count(Prediction.id))) or 0,
            "by_intent": grouped(Prediction.top_intent),
            "by_status": grouped(Prediction.status),
            "by_language": grouped(Prediction.language),
            "pending_review": reviewed.get("pending", 0),
            "high_urgency": s.scalar(select(func.count(Prediction.id)).where(Prediction.urgency == "high")) or 0,
            "avg_score": round(float(s.scalar(select(func.avg(Prediction.confidence))) or 0.0), 3),
            "reviewer_agreement": round(confirmed / total_rev, 3) if total_rev > 0 else None,
        }


def get_feedback_rows() -> list[tuple[str, str]]:
    """Fetch reviewed predictions (confirmed or corrected) to export for model retraining."""
    with SessionLocal() as s:
        rows = s.scalars(
            select(Prediction).where(
                Prediction.masked_text.is_not(None),
                Prediction.review_status.in_(["confirmed", "corrected"]),
            )
        )
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "purge"])
    cmd = parser.parse_args().command
    if cmd == "init":
        init_db()
        print(f"Database initialized at: {DATABASE_URL}")
    else:
        deleted = purge_older_than(RETENTION_DAYS)
        print(f"Purged {deleted} records older than {RETENTION_DAYS} days.")
