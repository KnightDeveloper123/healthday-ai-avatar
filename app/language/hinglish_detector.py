"""Roman-script Hindi/Marathi detection and style classification.

The lexicons are small, hand-curated and conservative. Words that are also common
English words (me, is, to, have, bare, sang, hum, pan) are excluded on purpose.
Extend them using misses found by the evaluation set.
"""

from collections.abc import Sequence

from app.language.models import LanguageCode, Script, Style, TokenInfo

ROMAN_HINDI = frozenset(
    [
        "mujhe",
        "mujhko",
        "mere",
        "meri",
        "mera",
        "hamein",
        "humein",
        "aap",
        "aapko",
        "aapke",
        "hai",
        "hain",
        "hoga",
        "hogi",
        "nahin",
        "kya",
        "kaise",
        "kyun",
        "kyu",
        "kab",
        "kaun",
        "batao",
        "bataiye",
        "bataye",
        "batayen",
        "bataiyen",
        "chahiye",
        "chahie",
        "aur",
        "liye",
        "ke",
        "ki",
        "ka",
        "ko",
        "se",
        "mein",
        "baare",
        "baray",
        "bimari",
        "bimaari",
        "jankari",
        "jaankari",
        "sakta",
        "sakti",
        "karna",
        "kijiye",
        "karein",
        "kare",
        "ye",
        "yeh",
        "woh",
        "wo",
        "bhi",
        "toh",
        "abhi",
        "phir",
        "lekin",
        "magar",
        "agar",
        "kuch",
        "koi",
        "sab",
        "bahut",
        "accha",
        "acha",
        "theek",
        "dhanyavaad",
        "dhanyavad",
        "shukriya",
        "swasthya",
        "kitna",
        "kitne",
        "kaisa",
        "hota",
        "hoti",
        "tha",
        "thi",
    ]
)

ROMAN_MARATHI = frozenset(
    [
        "mala",
        "majha",
        "majhi",
        "majhe",
        "tumhi",
        "tumhala",
        "amhi",
        "aapan",
        "aahe",
        "ahe",
        "aahet",
        "ahet",
        "kay",
        "kasa",
        "kashi",
        "kase",
        "kuthe",
        "kadhi",
        "sanga",
        "saanga",
        "dya",
        "dyaa",
        "mahiti",
        "babat",
        "baddal",
        "sathi",
        "madhe",
        "ani",
        "aani",
        "ata",
        "aata",
        "pahije",
        "pahijet",
        "havi",
        "mhanje",
        "zala",
        "jhala",
        "naahi",
    ]
)


def roman_indic_language(token_lower: str) -> LanguageCode | None:
    """'hi' or 'mr' if a lowercase Latin token is a known Roman Hindi/Marathi word."""
    if token_lower in ROMAN_HINDI:
        return "hi"
    if token_lower in ROMAN_MARATHI:
        return "mr"
    return None


def determine_style(tokens: Sequence[TokenInfo], primary: str | None) -> Style:
    """'hinglish' / 'roman_marathi' when the Indic words are mostly written in Latin script."""
    roman = sum(1 for t in tokens if t.script is Script.LATIN and t.language in ("hi", "mr"))
    devanagari = sum(1 for t in tokens if t.script is Script.DEVANAGARI)
    if roman and roman >= devanagari:
        if primary == "hi":
            return "hinglish"
        if primary == "mr":
            return "roman_marathi"
    return "standard"
