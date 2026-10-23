from app.language.detector import DEVANAGARI_HINDI, DEVANAGARI_MARATHI
from app.language.hinglish_detector import ROMAN_HINDI, ROMAN_MARATHI

ENGLISH_COLLISIONS = {
    "is",
    "me",
    "to",
    "the",
    "he",
    "have",
    "us",
    "bare",
    "sang",
    "hum",
    "pan",
    "ho",
    "hi",
}


def test_hindi_and_marathi_lexicons_do_not_overlap() -> None:
    assert not ROMAN_HINDI & ROMAN_MARATHI
    assert not DEVANAGARI_HINDI & DEVANAGARI_MARATHI


def test_roman_lexicons_exclude_common_english_words() -> None:
    assert not (ROMAN_HINDI | ROMAN_MARATHI) & ENGLISH_COLLISIONS
