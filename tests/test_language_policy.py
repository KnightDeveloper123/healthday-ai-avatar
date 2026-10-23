from app.language.analyzer import analyze_text
from app.language.response_language import choose_response_language
from app.language.router import asr_language_hint, plan_tts_route


def test_long_english_input_beats_selected_hindi() -> None:
    result = analyze_text("Tell me about cancer prevention.", selected_language="hi")
    assert result.response_language == "en"


def test_short_input_falls_back_to_selected_language() -> None:
    assert analyze_text("Namaste", selected_language="hi").response_language == "hi"


def test_short_input_prefers_previous_response_language() -> None:
    result = analyze_text("Thank you", selected_language="en", history=["hinglish"])
    assert result.response_language == "hinglish"


def test_no_signal_defaults_to_english() -> None:
    assert choose_response_language(None, "standard", 0) == "en"


def test_route_plans() -> None:
    assert plan_tts_route("en").tts_language == "en"
    hinglish = plan_tts_route("hinglish")
    assert (hinglish.tts_language, hinglish.tts_script) == ("hi", "latin")
    assert hinglish.note is not None
    assert plan_tts_route("mr").tts_script == "native"


def test_asr_hint_is_selected_language() -> None:
    assert asr_language_hint("mr") == "mr"
    assert asr_language_hint(None) is None