"""Root Application Runner - Intelligent Customer Intent Detector"""
from backend.app import app
from backend import config

if __name__ == "__main__":
    print(f"Starting Intelligent Customer Intent Detector on http://127.0.0.1:{config.PORT} ...")
    app.run(host=config.HOST, port=config.PORT, debug=False)
