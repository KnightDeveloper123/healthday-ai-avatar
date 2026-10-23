"""Provider-neutral routing hints. Real providers are wired in Phase 4."""

from typing import Literal

from pydantic import BaseModel

from app.language.models import LanguageCode, ResponseLanguage


class RoutePlan(BaseModel):
    response_language: ResponseLanguage
    tts_language: LanguageCode
    tts_script: Literal["native", "latin"]
    translation_required: bool = False
    note: str | None = None


_PLANS: dict[ResponseLanguage, RoutePlan] = {
    "en": RoutePlan(response_language="en", tts_language="en", tts_script="native"),
    "hi": RoutePlan(response_language="hi", tts_language="hi", tts_script="native"),
    "mr": RoutePlan(response_language="mr", tts_language="mr", tts_script="native"),
    "hinglish": RoutePlan(
        response_language="hinglish",
        tts_language="hi",
        tts_script="latin",
        note="Roman-script input support in TTS is unverified; may need transliteration.",
    ),
    "mr_latn": RoutePlan(
        response_language="mr_latn",
        tts_language="mr",
        tts_script="latin",
        note="Roman-script input support in TTS is unverified; may need transliteration.",
    ),
}


def plan_tts_route(response_language: ResponseLanguage) -> RoutePlan:
    return _PLANS[response_language]


def asr_language_hint(selected_language: LanguageCode | None) -> LanguageCode | None:
    """STT runs before language analysis, so the UI-selected language is the only hint."""
    return selected_language