from flask import Blueprint, jsonify, request
from backend.services.analysis_service import analyze_customer_message, validate_message

analyze_bp = Blueprint("analyze", __name__)


def err(status_code: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status_code


@analyze_bp.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return err(400, "invalid_json", "Request body must be a JSON object.")

    text, problem = validate_message(data.get("message"))
    if problem:
        return err(*problem)

    save_flag = bool(data.get("save", True))
    result = analyze_customer_message(text, save=save_flag)
    return jsonify(result)


@analyze_bp.post("/api/analyze/batch")
def analyze_batch():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return err(400, "invalid_json", "Request body must be a JSON object.")

    msgs = data.get("messages")
    if not isinstance(msgs, list) or len(msgs) == 0:
        return err(400, "invalid_messages", "messages must be a non-empty list.")
    if len(msgs) > 50:
        return err(400, "too_many_messages", "At most 50 messages per batch.")

    save_flag = bool(data.get("save", True))
    results = []
    for i, m in enumerate(msgs):
        text, problem = validate_message(m)
        if problem:
            results.append({"index": i, "error": {"code": problem[1], "message": problem[2]}})
        else:
            results.append({"index": i, "result": analyze_customer_message(text, save=save_flag)})
    return jsonify({"results": results})
