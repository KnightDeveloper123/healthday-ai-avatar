"""Single entry point for the language layer."""

from collections.abc import Sequence

from app.language.code_switch_detector import summarize
from app.language.detector import build_segments, identify_tokens
from app.language.hinglish_detector import determine_style
from app.language.models import LanguageAnalysis, LanguageCode, ResponseLanguage
from app.language.normalizer import normalize_text
from app.language.response_language import choose_response_language
from app.language.script_detector import detect_script
from app.language.terminology import find_medical_terms


def analyze_text(
    text: str,
    *,
    selected_language: LanguageCode | None = None,
    history: Sequence[ResponseLanguage] = (),
) -> LanguageAnalysis:
    normalized = normalize_text(text)
    tokens = identify_tokens(normalized, hint=selected_language)
    summary = summarize(tokens)
    style = determine_style(tokens, summary.primary)
    terms = list(dict.fromkeys(m.surface for m in find_medical_terms(normalized)))
    return LanguageAnalysis(
        original_text=text,
        normalized_text=normalized,
        script=detect_script(normalized),
        detected_languages=summary.languages,
        primary_language=summary.primary,
        secondary_languages=summary.secondary,
        code_switched=summary.code_switched,
        style=style,
        confidence=summary.confidence,
        token_count=len(tokens),
        medical_terms=terms,
        segments=build_segments(tokens, normalized),
        response_language=choose_response_language(
            summary.primary,
            style,
            len(tokens),
            selected_language=selected_language,
            history=history,
        ),
    )