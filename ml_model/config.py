import os
from pathlib import Path
from dotenv import load_dotenv

ML_DIR = Path(__file__).resolve().parent
ROOT_DIR = ML_DIR.parent

# Load .env if present
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ML_DIR / "data"
MODELS_DIR = ML_DIR / "models"

INTENTS_PATH = DATA_DIR / "intents.json"
PRODUCTS_PATH = DATA_DIR / "products.txt"
TRAIN_CSV = DATA_DIR / "training_data.csv"
TEST_CSV = DATA_DIR / "test_messages.csv"

MODEL_PATH = MODELS_DIR / "intent_model.joblib"
MODEL_INFO_PATH = MODELS_DIR / "model_info.json"

# Thresholds
ACCEPT_THRESHOLD = float(os.getenv("ACCEPT_THRESHOLD", "0.55"))
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", "0.35"))
MARGIN_THRESHOLD = float(os.getenv("MARGIN_THRESHOLD", "0.15"))
CLAUSE_MIN_CONF = float(os.getenv("CLAUSE_MIN_CONF", "0.40"))
