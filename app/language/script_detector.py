"""Unicode-based script detection."""

import unicodedata
from collections import Counter

from app.language.models import Script

_DANDA = (0x0964, 0x0965)
_DEVANAGARI_DIGITS = range(0x0966, 0x0970)


def char_script(ch: str) -> Script:
    """Script of one character. Punctuation, digits and danda are UNKNOWN."""
    cp = ord(ch)
    if 0x0900 <= cp <= 0x097F and cp not in _DANDA and cp not in _DEVANAGARI_DIGITS:
        return Script.DEVANAGARI
    if not ch.isalpha():
        return Script.UNKNOWN
    if unicodedata.name(ch, "").startswith("LATIN"):
        return Script.LATIN
    return Script.OTHER


def detect_script(text: str) -> Script:
    """Dominant script of a text; MIXED when Devanagari and Latin both appear."""
    counts = Counter(char_script(c) for c in text)
    dev, lat, other = counts[Script.DEVANAGARI], counts[Script.LATIN], counts[Script.OTHER]
    if dev + lat + other == 0:
        return Script.UNKNOWN
    if other > dev + lat:
        return Script.OTHER
    if dev and lat:
        return Script.MIXED
    if dev:
        return Script.DEVANAGARI
    if lat:
        return Script.LATIN
    return Script.OTHER