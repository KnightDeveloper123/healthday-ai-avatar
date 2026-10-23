from app.language.normalizer import normalize_text
from app.language.terminology import find_medical_terms


def _surfaces(text: str) -> list[str]:
    return [m.surface for m in find_medical_terms(text)]


def test_longest_phrase_wins() -> None:
    assert _surfaces("Tell me about World Cancer Day") == ["World Cancer Day"]


def test_case_insensitive_and_keeps_original_surface() -> None:
    assert _surfaces("what is cancer day") == ["cancer day"]


def test_devanagari_term_inside_inflected_word() -> None:
    assert _surfaces("मला मधुमेहाबद्दल माहिती द्या") == ["मधुमेह"]


def test_no_partial_match_inside_latin_word() -> None:
    assert _surfaces("cancerous growth") == []


def test_multiple_terms_in_order() -> None:
    assert _surfaces("Diabetes Day and cancer") == ["Diabetes Day", "cancer"]


def test_normalization_preserves_terms_and_cleans_whitespace() -> None:
    assert normalize_text("  Cancer   Day\u200b ") == "Cancer Day"
    assert normalize_text("मुझे Cancer Day के बारे में बताएं।") == "मुझे Cancer Day के बारे में बताएं।"