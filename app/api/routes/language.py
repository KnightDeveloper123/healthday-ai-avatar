"""Language analysis endpoint (also useful for frontend and QA)."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.language.analyzer import analyze_text
from app.language.models import LanguageAnalysis, LanguageCode, ResponseLanguage
from app.language.router import RoutePlan, plan_tts_route

logger = logging.getLogger(__name__)
router = APIRouter(tags=["language"])


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    selected_language: LanguageCode | None = None
    history: list[ResponseLanguage] = Field(default_factory=list, max_length=10)


class AnalyzeResponse(BaseModel):
    analysis: LanguageAnalysis
    route: RoutePlan


@router.post("/language/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    analysis = analyze_text(
        payload.text, selected_language=payload.selected_language, history=payload.history
    )
    # Metadata only: the user's text must never be logged.
    logger.info(
        "language analyzed",
        extra={
            "primary_language": analysis.primary_language,
            "script": analysis.script.value,
            "style": analysis.style,
            "token_count": analysis.token_count,
            "response_language": analysis.response_language,
        },
    )
    return AnalyzeResponse(analysis=analysis, route=plan_tts_route(analysis.response_language))