import re
import unicodedata

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SPLIT = re.compile(
    r"(?<=[.!?])\s+|;\s*|,\s+|\s+(?:and also|and|but|also|plus|mattu|ಮತ್ತು|aadre|ಆದರೆ)\s+",
    re.IGNORECASE,
)
_ABBREV = re.compile(r"\b(rs|no|inr)\.\s*", re.IGNORECASE)  # "Rs. 2,499" must not split

_KN_ROMAN_HINTS = {
    "nanna", "nange", "nanage", "beku", "illa", "aagide", "aagilla", "yelli", "yaake",
    "madi", "maadi", "bandilla", "banilla", "hana", "duddu", "tumba", "mattu", "ide",
    "helidru", "heli", "kodi", "madbeku", "beda", "sari", "badalisi"
}


def normalize(text: str) -> str:
    """Normalize whitespace and unicode representations, remove control characters."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_language(text: str) -> str:
    """Heuristic language detector.
    Returns: 'kn' (Kannada script), 'mixed' (script mix), 'kn-latn' (romanized Kannada),
    'en' (English), or 'unknown'.
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "unknown"
    kn_count = sum("\u0c80" <= c <= "\u0cff" for c in letters)
    ratio = kn_count / len(letters)
    if ratio > 0.7:
        return "kn"
    if ratio > 0.1:
        return "mixed"
    words = set(re.findall(r"[a-z]+", text.lower()))
    if len(words & _KN_ROMAN_HINTS) >= 1:
        return "kn-latn"
    return "en"


def split_clauses(text: str) -> list[str]:
    """Split message into clauses for multi-intent detection.
    Guards abbreviations and requires at least 2 words per clause.
    """
    text = _ABBREV.sub(r"\1 ", text)
    parts = [p.strip() for p in _SPLIT.split(text) if p and p.strip()]
    return [p for p in parts if len(p.split()) >= 2]
