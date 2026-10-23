"""Aggregate token languages into primary/secondary languages and a code-switch flag."""

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from app.language.models import TokenInfo

_ORDER = {"hi": 0, "mr": 1, "en": 2}
_MIN_INDIC_RATIO = 0.3


@dataclass(frozen=True)
class CodeSwitchSummary:
    languages: list[str]
    primary: str | None
    secondary: list[str]
    code_switched: bool
    confidence: float


def summarize(tokens: Sequence[TokenInfo]) -> CodeSwitchSummary:
    if not tokens:
        return CodeSwitchSummary([], None, [], False, 0.0)

    counts = Counter(t.language for t in tokens)
    total = len(tokens)
    languages = sorted(counts, key=lambda lang: (-counts[lang], _ORDER[lang]))
    primary = languages[0]

    # Hinglish often has more English words than Hindi ones. Let the Indic language win
    # when it is a meaningful share (>=30%) and has >=2 words (or the text is tiny).
    indic_total = counts["hi"] + counts["mr"]
    if (
        primary == "en"
        and indic_total >= 1
        and indic_total / total >= _MIN_INDIC_RATIO
        and (indic_total >= 2 or total <= 2)
    ):
        primary = max(("hi", "mr"), key=lambda lang: (counts[lang], -_ORDER[lang]))

    languages = [primary] + [lang for lang in languages if lang != primary]
    return CodeSwitchSummary(
        languages=languages,
        primary=primary,
        secondary=languages[1:],
        code_switched=len(languages) > 1,
        confidence=round(counts[primary] / total, 2),
    )