"""Shared types for the language layer."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

LanguageCode = Literal["en", "hi", "mr"]
# hinglish = Hindi in Latin script; mr_latn = Marathi in Latin script
ResponseLanguage = Literal["en", "hi", "mr", "hinglish", "mr_latn"]
Style = Literal["standard", "hinglish", "roman_marathi"]


class Script(StrEnum):
    DEVANAGARI = "devanagari"
    LATIN = "latin"
    MIXED = "mixed"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TokenInfo:
    """One word with its script, language and character span in the analyzed text."""

    text: str
    script: Script
    language: LanguageCode
    start: int
    end: int


class Segment(BaseModel):
    """A run of consecutive tokens sharing script and language."""

    text: str
    script: Script
    language: LanguageCode


class LanguageAnalysis(BaseModel):
    original_text: str
    normalized_text: str
    script: Script
    detected_languages: list[LanguageCode]
    primary_language: LanguageCode | None
    secondary_languages: list[LanguageCode]
    code_switched: bool
    style: Style
    confidence: float = Field(
        ge=0.0, le=1.0, description="Heuristic share of tokens, not a probability"
    )
    token_count: int
    medical_terms: list[str]
    segments: list[Segment]
    response_language: ResponseLanguage
