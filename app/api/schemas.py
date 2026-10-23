"""Shared API response schemas."""

from typing import Any

from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None
    details: list[dict[str, Any]] = []


class ErrorResponse(BaseModel):
    error: ErrorBody
