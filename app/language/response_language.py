"""Decide the response language independently of raw input detection."""

from collections.abc import Sequence

from app.language.models import LanguageCode, ResponseLanguage, Style

MIN_CONFIDENT_TOKENS = 3


def language_from_input(primary: str | None, style: Style) -> ResponseLanguage | None:
    if primary is None:
        return None
    if primary == "hi":
        return "hinglish" if style == "hinglish" else "hi"
    if primary == "mr":
        return "mr_latn" if style == "roman_marathi" else "mr"
    return "en"


def choose_response_language(
    primary: str | None,
    style: Style,
    token_count: int,
    *,
    selected_language: LanguageCode | None = None,
    history: Sequence[ResponseLanguage] = (),
) -> ResponseLanguage:
    """Input wins when long enough to trust; otherwise previous turn, then UI selection."""
    from_input = language_from_input(primary, style)
    if from_input is not None and token_count >= MIN_CONFIDENT_TOKENS:
        return from_input
    if history:
        return history[-1]
    if selected_language:
        return selected_language
    return from_input or "en"