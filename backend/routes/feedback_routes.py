from flask import Blueprint, jsonify, request
from backend.services.analysis_service import analyzer
from database import database as db

feedback_bp = Blueprint("feedback", __name__)


def err(status_code: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status_code


@feedback_bp.post("/api/feedback")
def feedback():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return err(400, "invalid_json", "Request body must be a JSON object.")

    pid = data.get("prediction_id")
    action = data.get("action")
    corrected = data.get("corrected_intent")

    if not isinstance(pid, int) or isinstance(pid, bool):
        return err(400, "invalid_id", "prediction_id must be an integer.")
    if action not in ("confirm", "correct"):
        return err(400, "invalid_action", "action must be 'confirm' or 'correct'.")
    if action == "correct" and corrected not in analyzer.labels:
        return err(400, "invalid_intent", "corrected_intent is not a supported intent.")

    row = db.apply_feedback(pid, action, corrected)
    if row is None:
        return err(404, "not_found", "Prediction record not found.")
    return jsonify(row)
