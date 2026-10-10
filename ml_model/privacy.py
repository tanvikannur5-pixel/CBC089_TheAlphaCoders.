import re


def _luhn(candidate: str) -> bool:
    """Validate payment card numbers using Luhn checksum."""
    digits = [int(c) for c in re.sub(r"\D", "", candidate)]
    if not (13 <= len(digits) <= 19):
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d = d * 2 - 9 if d * 2 > 9 else d * 2
        total += d
    return total % 10 == 0


PII_PATTERNS = [
    ("UPI", re.compile(r"\b[\w.\-]{2,}@(?:upi|ybl|oksbi|okaxis|okhdfcbank|okicici|paytm|ibl|axl)\b", re.I), None),
    ("EMAIL", re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b"), None),
    ("CARD", re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"), _luhn),
    ("AADHAAR", re.compile(r"(?<!\d)\d{4}\s\d{4}\s\d{4}(?!\d)"), None),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), None),
    ("PHONE", re.compile(r"(?<!\d)(?:\+91[\s-]?|0)?[6-9]\d{9}(?!\d)"), None),
    ("OTP", re.compile(r"\b(?:otp|cvv|pin)\b\D{0,12}\d{3,8}\b", re.I), None),
]


def mask_pii(text: str, protected_spans=()):
    """Replace sensitive PII tokens with [TYPE].
    protected_spans (e.g. order IDs) are excluded from masking.
    Returns (masked_text, counts_by_type).
    """
    found = []
    for kind, pattern, validator in PII_PATTERNS:
        for m in pattern.finditer(text):
            if validator and not validator(m.group()):
                continue
            s, e = m.span()
            if any(s < pe and e > ps for ps, pe in protected_spans):
                continue
            found.append((s, e, kind))

    # Sort spans in ascending order, longest first for ties
    found.sort(key=lambda x: (x[0], -(x[1] - x[0])))

    out, pos, counts = [], 0, {}
    for s, e, kind in found:
        if s < pos:
            continue
        out.append(text[pos:s])
        out.append(f"[{kind}]")
        counts[kind] = counts.get(kind, 0) + 1
        pos = e
    out.append(text[pos:])
    return "".join(out), counts
