import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from backend import config
from backend.routes import meta_bp, analyze_bp, feedback_bp
from database import database as db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("intent-app")

def create_app():
    """Application factory for the backend Flask service."""
    app = Flask(
        __name__,
        template_folder=str(config.FRONTEND_TEMPLATES),
        static_folder=str(config.FRONTEND_STATIC),
        static_url_path="/static"
    )
    app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

    # Initialize database tables
    db.init_db()

    # Register modular route blueprints
    app.register_blueprint(meta_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(feedback_bp)

    @app.errorhandler(Exception)
    def handle_error(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": {"code": e.name.lower().replace(" ", "_"), "message": e.description}}), e.code
        log.exception("Unhandled error in backend: %s", e)
        return jsonify({"error": {"code": "internal_error", "message": "Something went wrong. Please try again."}}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=False)
