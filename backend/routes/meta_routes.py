import hmac
from flask import Blueprint, jsonify, render_template, request, send_from_directory
from backend import config
from backend.services.analysis_service import analyzer
from database import database as db

meta_bp = Blueprint("meta", __name__)


def err(status_code: int, code: str, message: str):
    return jsonify({"error": {"code": code, "message": message}}), status_code


@meta_bp.get("/")
def index():
    return render_template("index.html")


@meta_bp.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "detector_mode": analyzer.detector.mode,
    })


@meta_bp.get("/api/intents")
def intents():
    return jsonify({
        "intents": [
            {"label": k, "display": v.get("display", k)}
            for k, v in analyzer.intents.items()
        ]
    })


@meta_bp.get("/api/history")
def history():
    limit_arg = request.args.get("limit", "50")
    try:
        limit = max(1, min(int(limit_arg), 200))
    except ValueError:
        return err(400, "invalid_limit", "limit must be an integer.")

    items = db.list_predictions(
        limit=limit,
        status=request.args.get("status"),
        review=request.args.get("review")
    )
    return jsonify({"items": items})


@meta_bp.get("/api/stats")
def stats():
    return jsonify(db.stats())


@meta_bp.delete("/api/history")
def clear_history():
    token = request.headers.get("X-Admin-Token", "")
    if not config.ADMIN_TOKEN or not hmac.compare_digest(token, config.ADMIN_TOKEN):
        return err(403, "forbidden", "Admin token required.")
    deleted = db.purge_all()
    return jsonify({"deleted": deleted})
