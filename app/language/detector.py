"""Token- and segment-level language identification."""

import re
import unicodedata
from collections import Counter
from collections.abc import Sequence

from app.language.hinglish_detector import roman_indic_language
from app.language.models import LanguageCode, Script, Segment, TokenInfo
from app.language.script_detector import detect_script

# Latin letters/digits and Devanagari, excluding danda (U+0964/0965). \w is NOT used because
# it splits Devanagari words at vowel signs (matras).
_TOKEN_RE = re.compile(r"[A-Za-z0-9\u00C0-\u024F\u0900-\u0963\u0966-\u097F]+")


def _nfc(words: str) -> frozenset[str]:
    return frozenset(unicodedata.normalize("NFC", w) for w in words.split())


# Unambiguous markers only. Hindi "का/की" and Marathi "का/की" overlap, so they are left out.
DEVANAGARI_HINDI = _nfc(
    """
    है हैं के को में से मुझे हमें आपको क्या नहीं और लिए कैसे क्यों बारे बताएं बताएँ बताइए
    बताइये बताओ चाहिए चाहिये जानकारी यह वह था थी सकता सकती करें कीजिए
    """
)
DEVANAGARI_MARATHI = _nfc(
    """
    आहे आहेत मला आम्ही तुम्ही तुम्हाला आपण काय नाही आणि साठी मध्ये बद्दल कसे कसा कशी
    सांगा सांगू माहिती द्या हवी हवे पाहिजे झाले झाला आता कुठे केव्हा मी माझा माझी माझे
    """
)
MARATHI_SUFFIXES = ("बद्दल", "मध्ये", "साठी")


def _devanagari_language(token: str) -> LanguageCode | None:
    if token in DEVANAGARI_MARATHI or token.endswith(MARATHI_SUFFIXES):
        return "mr"
    if token in DEVANAGARI_HINDI:
        return "hi"
    return None


def _devanagari_default(
    pending: Sequence[tuple[re.Match[str], Script, LanguageCode | None]],
    hint: str | None,
) -> LanguageCode:
    """Language for Devanagari words without markers: majority, else hint, else Hindi."""
    votes = Counter(lang for _, script, lang in pending if script is Script.DEVANAGARI and lang)
    if votes["mr"] > votes["hi"]:
        return "mr"
    if votes["hi"] > votes["mr"]:
        return "hi"
    return "mr" if hint == "mr" else "hi"


def identify_tokens(text: str, hint: str | None = None) -> list[TokenInfo]:
    """Tag each word with script and language. Numbers/punctuation are skipped."""
    pending: list[tuple[re.Match[str], Script, LanguageCode | None]] = []
    for match in _TOKEN_RE.finditer(text):
        token = match.group()
        script = detect_script(token)
        if script is Script.LATIN:
            pending.append((match, script, roman_indic_language(token.lower()) or "en"))
        elif script is Script.DEVANAGARI:
            pending.append((match, script, _devanagari_language(token)))
    default = _devanagari_default(pending, hint)
    return [
        TokenInfo(m.group(), script, lang or default, m.start(), m.end())
        for m, script, lang in pending
    ]


def build_segments(tokens: Sequence[TokenInfo], text: str) -> list[Segment]:
    """Group consecutive tokens with the same script+language into segments."""
    segments: list[Segment] = []
    group: list[TokenInfo] = []

    def flush() -> None:
        if group:
            segments.append(
                Segment(
                    text=text[group[0].start : group[-1].end],
                    script=group[0].script,
                    language=group[0].language,
                )
            )

    for token in tokens:
        if group and (group[-1].script, group[-1].language) != (token.script, token.language):
            flush()
            group = []
        group.append(token)
    flush()
    return segments