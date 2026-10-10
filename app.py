"""Intelligent Customer Intent Detector - Root Application Entry Point"""
from backend.app import app
from backend import config

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=False)
