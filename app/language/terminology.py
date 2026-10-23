"""Medical-term detection from a data-driven glossary.

Matching is case-insensitive for Latin and allows Marathi/Hindi suffixes after
Devanagari terms (मधुमेहाबद्दल -> मधुमेह). The glossary will later be loaded from
campaign configuration; today it covers the two initial campaigns.
"""

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class GlossaryEntry:
    term_id: str
    variants: tuple[str, ...]


@dataclass(frozen=True)
class TermMatch:
    term_id: str
    surface: str
    start: int
    end: int


GLOSSARY: tuple[GlossaryEntry, ...] = (
    GlossaryEntry(
        "world_cancer_day",
        ("World Cancer Day", "Cancer Day", "cancer diwas", "कैंसर दिवस", "कर्करोग दिन", "कर्करोग दिवस"),
    ),
    GlossaryEntry(
        "world_diabetes_day",
        ("World Diabetes Day", "Diabetes Day", "diabetes diwas", "मधुमेह दिवस"),
    ),
    GlossaryEntry("cancer", ("cancer", "कैंसर", "कर्करोग", "कर्क रोग")),
    GlossaryEntry("diabetes", ("diabetes", "madhumeh", "मधुमेह", "डायबिटीज़", "डायबिटीज")),
)


def _is_devanagari(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def _pattern(variant: str) -> str:
    body = r"\s+".join(re.escape(part) for part in variant.split())
    if _is_devanagari(variant):
        return rf"(?<![\u0900-\u097F]){body}"
    return rf"(?<![A-Za-z]){body}(?![A-Za-z])"


def _key(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).lower().split())


_VARIANT_TO_ID = {
    _key(v): entry.term_id for entry in GLOSSARY for v in entry.variants
}
# Longest variants first so "World Cancer Day" wins over "Cancer Day" over "cancer".
_REGEX = re.compile(
    "|".join(
        f"(?:{_pattern(unicodedata.normalize('NFC', v))})"
        for v in sorted(
            (v for entry in GLOSSARY for v in entry.variants), key=len, reverse=True
        )
    ),
    re.IGNORECASE,
)


def find_medical_terms(text: str) -> list[TermMatch]:
    """Glossary matches in order of appearance, using the surface form from the text."""
    text = unicodedata.normalize("NFC", text)
    return [
        TermMatch(_VARIANT_TO_ID[_key(m.group())], m.group(), m.start(), m.end())
        for m in _REGEX.finditer(text)
    ]