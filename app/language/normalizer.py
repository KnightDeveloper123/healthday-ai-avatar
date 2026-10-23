"""Conservative text normalization. Never translates; never rewrites words."""

import re
import unicodedata

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\ufeff"))


def normalize_text(text: str) -> str:
    """Unicode NFC, drop zero-width space/BOM, collapse whitespace."""
    text = unicodedata.normalize("NFC", text).translate(_ZERO_WIDTH)
    return re.sub(r"\s+", " ", text).strip()