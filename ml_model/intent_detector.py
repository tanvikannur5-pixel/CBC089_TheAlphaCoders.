from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

TOKEN_PATTERN = r"[^\s.,!?;:()\[\]\"']+"

KEYWORDS = {
    "order_tracking": ["where is my order", "track", "tracking", "order status", "yelli ide", "ಎಲ್ಲಿದೆ", "status heli", "parcel"],
    "order_cancellation": ["cancel", "ಕ್ಯಾನ್ಸಲ್", "ರದ್ದು", "beda", "stop shipment"],
    "refund_request": ["refund", "money back", "ಹಣ ವಾಪಸ್", "hana vapas", "duddu", "ರಿಫಂಡ್"],
    "product_information": ["does it", "price of", "specification", "available in", "ಬೆಲೆ", "features", "warranty", "color"],
    "complaint": ["terrible", "worst", "unacceptable", "disappointed", "complaint", "ಚೆನ್ನಾಗಿಲ್ಲ", "frustrated", "pathetic", "rude"],
    "return_exchange": ["return", "exchange", "replace", "ಬದಲಾಯಿಸಿ", "wrong size", "damaged item", "broken"],
    "payment_issue": ["payment", "deducted", "charged", "upi", "ಪೇಮೆಂಟ್", "debit", "failed", "double charge", "cut aagide"],
    "delivery_problem": ["delivery", "delayed", "not received", "late", "ಡೆಲಿವರಿ", "courier", "wrong address", "innu bandilla"],
    "general_inquiry": ["working hours", "contact", "customer care", "store", "office", "helpline", "talk to human", "ಸಹಾಯವಾಣಿ"],
    "out_of_scope": ["weather", "cricket", "joke", "capital", "flight", "poem", "movie", "song", "ಹವಾಮಾನ"]
}


def build_pipeline() -> Pipeline:
    """Build the production scikit-learn classification pipeline.
    Combines word n-grams and char_wb n-grams with class-balanced Logistic Regression.
    """
    features = FeatureUnion([
        (
            "word",
            TfidfVectorizer(
                ngram_range=(1, 2),
                token_pattern=TOKEN_PATTERN,
                sublinear_tf=True,
                lowercase=True,
            ),
        ),
        (
            "char",
            TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                sublinear_tf=True,
                lowercase=True,
            ),
        ),
    ])
    clf = LogisticRegression(C=10.0, max_iter=2000, class_weight="balanced")
    return Pipeline([("features", features), ("clf", clf)])


class IntentDetector:
    def __init__(self, model_path, labels):
        self.labels = labels
        self.model_path = Path(model_path)
        self.pipeline = joblib.load(self.model_path) if self.model_path.exists() else None
        self.mode = "trained" if self.pipeline is not None else "keyword_fallback"

    def predict(self, text: str, top_k: int = 3) -> list[dict]:
        """Classify text, returning top_k intents with confidence scores."""
        if self.pipeline is None:
            return self._keyword_predict(text, top_k)
        try:
            probs = self.pipeline.predict_proba([text])[0]
            classes = self.pipeline.classes_
            order = probs.argsort()[::-1][:top_k]
            return [
                {"label": str(classes[i]), "confidence": round(float(probs[i]), 3)}
                for i in order
            ]
        except Exception:
            return self._keyword_predict(text, top_k)

    def _keyword_predict(self, text: str, top_k: int) -> list[dict]:
        t = text.lower()
        hits = {label: sum(kw in t for kw in kws) for label, kws in KEYWORDS.items()}
        total_hits = sum(hits.values())
        if total_hits == 0:
            return [
                {"label": "general_inquiry", "confidence": 0.20},
                {"label": "out_of_scope", "confidence": 0.10},
            ][:top_k]

        ranked = sorted(hits.items(), key=lambda kv: -kv[1])[:top_k]
        return [
            {
                "label": label,
                "confidence": round(min(0.75, 0.35 + 0.15 * count) if count else 0.05, 3),
            }
            for label, count in ranked
        ]
