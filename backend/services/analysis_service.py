import logging
from backend import config
from ml_model.analyzer import Analyzer
from database import database as db

log = logging.getLogger("intent-app.service")

# Global singleton analyzer instance
analyzer = Analyzer()


def validate_message(value):
    """Validate customer message. Returns (clean_text, None) or (None, (status_code, code, message))."""
    if not isinstance(value, str):
        return None, (400, "invalid_message", "message must be a string.")
    text = value.strip()
    if not text:
        return None, (400, "empty_message", "Please enter a message.")
    if len(text) > config.MAX_MESSAGE_CHARS:
        return None, (
            400,
            "message_too_long",
            f"Message must be at most {config.MAX_MESSAGE_CHARS} characters.",
        )
    if not any(c.isalpha() for c in text):
        return None, (
            422,
            "no_text_content",
            "Message must contain letters, not only numbers or symbols.",
        )
    return text, None


def analyze_customer_message(text: str, save: bool = True) -> dict:
    """Analyze text with ML model and persist masked output in the database."""
    result = analyzer.analyze(text)
    result["id"] = None
    if save:
        try:
            result["id"] = db.save_prediction(result)
        except Exception:
            log.exception("Database unavailable: proceeding with analysis result (id=null).")
    return result
