import pytest

from app.language.models import Script
from app.language.script_detector import detect_script


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello world", Script.LATIN),
        ("नमस्ते दुनिया", Script.DEVANAGARI),
        ("मुझे Cancer Day", Script.MIXED),
        ("12345 !!!", Script.UNKNOWN),
        ("।", Script.UNKNOWN),
        ("१२३", Script.UNKNOWN),
        ("", Script.UNKNOWN),
        ("日本語", Script.OTHER),
    ],
)
def test_detect_script(text: str, expected: Script) -> None:
    assert detect_script(text) is expected