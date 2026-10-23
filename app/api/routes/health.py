"""Health endpoints: liveness and readiness."""

import logging
from collections.abc import Callable
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

ReadinessCheck = Callable[[], bool]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    checks: dict[str, Literal["ok", "fail"]]


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Is the process up? Does not touch any dependency."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
    summary="Readiness check",
)
def readiness(request: Request) -> JSONResponse:
    """Are dependencies reachable? Checks are registered on `app.state.readiness_checks`."""
    checks: dict[str, ReadinessCheck] = getattr(request.app.state, "readiness_checks", {})
    results: dict[str, bool] = {}
    for name, check in checks.items():
        try:
            results[name] = bool(check())
        except Exception:
            logger.exception("readiness check raised", extra={"check": name})
            results[name] = False

    ready = all(results.values())
    body = ReadinessResponse(
        status="ready" if ready else "not_ready",
        checks={name: ("ok" if ok else "fail") for name, ok in results.items()},
    )
    return JSONResponse(status_code=200 if ready else 503, content=body.model_dump())
