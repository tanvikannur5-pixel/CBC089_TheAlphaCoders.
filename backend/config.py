import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent

# Load .env from project root
load_dotenv(ROOT_DIR / ".env")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
MAX_MESSAGE_CHARS = int(os.getenv("MAX_MESSAGE_CHARS", "1000"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-admin-secret-token-2026")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT_DIR / 'intent.db').as_posix()}")

FRONTEND_TEMPLATES = ROOT_DIR / "frontend" / "templates"
FRONTEND_STATIC = ROOT_DIR / "frontend" / "static"
