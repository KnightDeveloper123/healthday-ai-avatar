import pytest

from app.language.analyzer import analyze_text


@pytest.mark.parametrize(
    ("text", "primary", "script", "switched", "style", "response", "terms"),
    [
        ("Tell me about cancer prevention.", "en", "latin", False, "standard", "en", ["cancer"]),
        ("मुझे Cancer Day के बारे में बताएं।", "hi", "mixed", True, "standard", "hi", ["Cancer Day"]),
        ("मला मधुमेहाबद्दल माहिती द्या.", "mr", "devanagari", False, "standard", "mr", ["मधुमेह"]),
        (
            "Mujhe Cancer Day ke baare mein batao.",
            "hi",
            "latin",
            True,
            "hinglish",
            "hinglish",
            ["Cancer Day"],
        ),
        (
            "मुझे Cancer Day के बारे में information चाहिए.",
            "hi",
            "mixed",
            True,
            "standard",
            "hi",
            ["Cancer Day"],
        ),
        (
            "Mala diabetes baddal mahiti dya",
            "mr",
            "latin",
            True,
            "roman_marathi",
            "mr_latn",
            ["diabetes"],
        ),
        (
            "मला Cancer Day बद्दल information हवी आहे",
            "mr",
            "mixed",
            True,
            "standard",
            "mr",
            ["Cancer Day"],
        ),
        ("डायबिटीज क्या है", "hi", "devanagari", False, "standard", "hi", ["डायबिटीज"]),
        ("Diabetes kya hai", "hi", "latin", True, "hinglish", "hinglish", ["Diabetes"]),
    ],
)
def test_analysis(
    text: str,
    primary: str,
    script: str,
    switched: bool,
    style: str,
    response: str,
    terms: list[str],
) -> None:
    result = analyze_text(text)
    assert result.primary_language == primary
    assert result.script.value == script
    assert result.code_switched is switched
    assert result.style == style
    assert result.response_language == response
    assert result.medical_terms == terms
    assert result.original_text == text


def test_secondary_languages_for_code_switched_hindi() -> None:
    result = analyze_text("मुझे Cancer Day के बारे में बताएं।")
    assert result.detected_languages == ["hi", "en"]
    assert result.secondary_languages == ["en"]


def test_segments_split_by_language() -> None:
    result = analyze_text("मुझे Cancer Day के बारे में बताएं।")
    assert [(s.text, s.language) for s in result.segments] == [
        ("मुझे", "hi"),
        ("Cancer Day", "en"),
        ("के बारे में बताएं", "hi"),
    ]


def test_empty_punctuation_only_text() -> None:
    result = analyze_text("...")
    assert result.primary_language is None
    assert result.detected_languages == []
    assert result.token_count == 0
    assert result.response_language == "en"


def test_unmarked_devanagari_uses_selected_language_hint() -> None:
    assert analyze_text("मधुमेह").primary_language == "hi"
    assert analyze_text("मधुमेह", selected_language="mr").primary_language == "mr"
