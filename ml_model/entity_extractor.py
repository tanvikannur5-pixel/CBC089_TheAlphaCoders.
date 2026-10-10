import re
from pathlib import Path

_MONTH = (
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
    r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
)

ORDER_PREFIXED = re.compile(r"\b[A-Z]{2,4}-\d{4,10}\b", re.I)
ORDER_LABELLED = re.compile(
    r"(?:\border(?:\s*(?:no|number|id))?\.?\s*[:#]?\s*|\bordar\s*|ಆರ್ಡರ್\s*|#)(\d{4,12})\b",
    re.I,
)
AMOUNT_PREFIX = re.compile(
    r"(₹|\brs\.?|\binr|\brupees?|\$|\busd)\s*(\d[\d,]*(?:\.\d{1,2})?)", re.I
)
AMOUNT_SUFFIX = re.compile(
    r"(\d[\d,]*(?:\.\d{1,2})?)\s*(?:₹|\brs\b|\brupees\b|/-)", re.I
)
DATES = [
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTH}\b(?:\s+\d{{4}})?", re.I),
    re.compile(rf"\b{_MONTH}\s+\d{{1,2}}(?:st|nd|rd|th)?\b(?:,?\s+\d{{4}})?", re.I),
    re.compile(r"\b(?:today|tomorrow|yesterday|last (?:week|month)|\d+\s+days?\s+ago)\b", re.I),
]
ISSUE_TERMS = [
    "charged twice", "double charged", "deducted", "not received", "damaged", "broken",
    "defective", "wrong item", "wrong size", "missing", "delayed", "late", "expired",
    "failed", "not working", "cancelled"
]


class EntityExtractor:
    def __init__(self, products_path):
        names, p = [], Path(products_path)
        if p.exists():
            names = [
                line.strip()
                for line in p.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
        names.sort(key=len, reverse=True)  # longest match first
        self.product_re = (
            re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b", re.I)
            if names
            else None
        )

    def extract(self, text: str) -> list[dict]:
        found = []

        def add(kind, value, span):
            found.append({"type": kind, "value": value, "span": span})

        for m in ORDER_PREFIXED.finditer(text):
            add("order_id", m.group(0).upper(), m.span())
        for m in ORDER_LABELLED.finditer(text):
            add("order_id", m.group(1), m.span(1))
        for m in AMOUNT_PREFIX.finditer(text):
            cur = "USD" if m.group(1).lower().rstrip(".") in ("$", "usd") else "INR"
            clean_num = m.group(2).replace(",", "")
            add("amount", f"{cur} {clean_num}", m.span())
        for m in AMOUNT_SUFFIX.finditer(text):
            clean_num = m.group(1).replace(",", "")
            add("amount", f"INR {clean_num}", m.span())
        for rx in DATES:
            for m in rx.finditer(text):
                add("date", m.group(0), m.span())
        if self.product_re:
            for m in self.product_re.finditer(text):
                add("product", m.group(0), m.span())

        low = text.lower()
        for term in ISSUE_TERMS:
            i = low.find(term)
            if i != -1:
                add("issue", term, (i, i + len(term)))

        return self._dedupe(found)

    @staticmethod
    def _dedupe(items):
        seen, out = set(), []
        for it in sorted(items, key=lambda x: x["span"][0]):
            key = (it["type"], it["value"].lower())
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out
