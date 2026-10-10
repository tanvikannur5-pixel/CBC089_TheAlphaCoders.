import json
from . import config
from .preprocess import normalize, detect_language, split_clauses
from .privacy import mask_pii
from .entity_extractor import EntityExtractor
from .intent_detector import IntentDetector

URGENT_TERMS = [
    "urgent", "asap", "immediately", "right now", "deducted", "charged twice",
    "double charged", "fraud", "unauthorized", "emergency", "ಬೇಗ", "jaldi", "fast"
]
SKIP_FOR_MULTI = {"general_inquiry", "out_of_scope"}
ENTITY_PROMPTS = {"order_id": "your Order ID"}
GENERIC_QUESTION = (
    "Could you tell us a bit more? For example, is this about an order, a payment, a delivery, or a product?"
)
PAIR_QUESTIONS = {
    frozenset({"payment_issue", "refund_request"}):
        "Did a payment fail or get deducted wrongly, or are you asking for a refund on a completed order?",
    frozenset({"order_tracking", "delivery_problem"}):
        "Do you want to know where your order is, or is there a problem with the delivery (late, not received, wrong address)?",
    frozenset({"order_cancellation", "return_exchange"}):
        "Has the order already been delivered? (Cancellation applies before delivery; return or exchange after.)",
    frozenset({"return_exchange", "refund_request"}):
        "Would you like to return or exchange the item, or only get your money back?",
    frozenset({"payment_issue", "order_tracking"}):
        "Is your payment not going through, or is the payment done and you cannot see your order?",
}


class Analyzer:
    def __init__(self):
        self.intents = json.loads(config.INTENTS_PATH.read_text(encoding="utf-8"))
        self.labels = list(self.intents.keys())
        self.detector = IntentDetector(config.MODEL_PATH, self.labels)
        self.extractor = EntityExtractor(config.PRODUCTS_PATH)

    def analyze(self, raw_text: str) -> dict:
        """Process customer text and return the complete intent analysis result."""
        text = normalize(raw_text)
        language = detect_language(text)

        # 1. Extract entities on original text before masking
        entities = self.extractor.extract(text)

        # 2. Protect extracted order IDs from PII masking
        protected = [e["span"] for e in entities if e["type"] == "order_id"]

        # 3. Mask PII in text
        masked, pii_counts = mask_pii(text, protected)

        # 4. Predict primary intent on masked text
        ranked = self.detector.predict(masked, top_k=3)

        # 5. Check multi-intent via clause splitting
        intents, multi = self._multi_intent(masked, ranked)

        # 6. Evaluate decision thresholds
        status = self._decide(ranked, multi)

        # 7. Check if human review is needed
        needs_review = status in ("needs_clarification", "unknown") or (
            multi and min(i["confidence"] for i in intents) < config.ACCEPT_THRESHOLD
        )

        # 8. Check for missing required entities
        public_entities = [{"type": e["type"], "value": e["value"]} for e in entities]
        found_types = {e["type"] for e in entities}
        missing = []
        if status in ("confident", "multi_intent"):
            for i in intents:
                for req in self.intents.get(i["label"], {}).get("required_entities", []):
                    if req not in found_types and req not in missing:
                        missing.append(req)

        # 9. Format response
        urgency = "high" if any(t in text.lower() for t in URGENT_TERMS) else "normal"
        clarification = self._clarify(status, ranked, missing)
        routing = self._route(status, intents, needs_review, urgency)

        return {
            "message_masked": masked,
            "language": language,
            "status": status,
            "multi_intent": multi,
            "intents": [
                dict(i, display=self.intents.get(i["label"], {}).get("display", i["label"]))
                for i in intents
            ],
            "alternatives": (
                [
                    dict(a, display=self.intents.get(a["label"], {}).get("display", a["label"]))
                    for a in ranked[1:]
                ]
                if not multi
                else []
            ),
            "entities": public_entities,
            "missing_entities": missing,
            "urgency": urgency,
            "clarification_question": clarification,
            "needs_review": needs_review,
            "route_to": routing,
            "pii_masked": pii_counts,
            "model": {
                "mode": self.detector.mode,
                "note": "Scores are model outputs, not calibrated probabilities.",
            },
        }

    def _multi_intent(self, masked: str, ranked: list[dict]):
        clauses = split_clauses(masked)
        single = [dict(ranked[0], clause=None)]
        if len(clauses) < 2:
            return single, False

        found = {}
        for clause in clauses:
            top = self.detector.predict(clause, top_k=1)[0]
            if top["label"] in SKIP_FOR_MULTI or top["confidence"] < config.CLAUSE_MIN_CONF:
                continue
            if top["label"] not in found or top["confidence"] > found[top["label"]]["confidence"]:
                found[top["label"]] = dict(top, clause=clause)

        if len(found) >= 2:
            return sorted(found.values(), key=lambda x: -x["confidence"]), True
        return single, False

    def _decide(self, ranked: list[dict], multi: bool) -> str:
        if multi:
            return "multi_intent"
        top = ranked[0]
        margin = top["confidence"] - (ranked[1]["confidence"] if len(ranked) > 1 else 0.0)

        if top["label"] == "out_of_scope" and top["confidence"] >= config.REVIEW_THRESHOLD:
            return "unsupported"
        if top["confidence"] < config.REVIEW_THRESHOLD:
            return "unknown"
        if top["confidence"] < config.ACCEPT_THRESHOLD or margin < config.MARGIN_THRESHOLD:
            return "needs_clarification"
        return "confident"

    def _clarify(self, status: str, ranked: list[dict], missing: list[str]) -> str | None:
        if status == "unknown":
            return GENERIC_QUESTION
        if status == "needs_clarification":
            if len(ranked) >= 2:
                a, b = ranked[0]["label"], ranked[1]["label"]
                pair_q = PAIR_QUESTIONS.get(frozenset({a, b}))
                if pair_q:
                    return pair_q
                disp_a = self.intents.get(a, {}).get("display", a)
                disp_b = self.intents.get(b, {}).get("display", b)
                return f"Just to be sure, is this about {disp_a} or {disp_b}?"
            return GENERIC_QUESTION
        if missing:
            names = " and ".join(ENTITY_PROMPTS.get(m, m) for m in missing)
            return f"Could you share {names} so we can look into this?"
        return None

    def _route(self, status: str, intents: list[dict], needs_review: bool, urgency: str) -> dict:
        if status == "unsupported":
            return {"teams": [], "priority": "none"}
        if needs_review:
            return {"teams": ["Human Review Queue"], "priority": urgency}
        teams = []
        for i in intents:
            t = self.intents.get(i["label"], {}).get("team")
            if t and t not in teams:
                teams.append(t)
        return {"teams": teams, "priority": urgency}
