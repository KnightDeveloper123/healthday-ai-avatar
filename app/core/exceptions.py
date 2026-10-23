"""Application exceptions and the single error-response format."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    429: "rate_limited",
}


class AppError(Exception):
    """Base class for expected, client-facing errors."""

    status_code = 500
    code = "internal_error"
    default_message = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or []
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = 400
    code = "bad_request"
    default_message = "The request could not be processed."


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"
    default_message = "The requested resource was not found."


class ServiceUnavailableError(AppError):
    status_code = 503
    code = "service_unavailable"
    default_message = "A required service is temporarily unavailable."


def error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str | None,
    details: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """Build the standard error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id,
                "details": details or [],
            }
        },
    )


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    if exc.status_code >= 500:
        logger.error("application error", extra={"code": exc.code, "error_message": exc.message})
    return error_response(exc.status_code, exc.code, exc.message, _request_id(request), exc.details)


async def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = _HTTP_CODES.get(exc.status_code, "http_error")
    response = error_response(exc.status_code, code, str(exc.detail), _request_id(request))
    if exc.headers:
        response.headers.update(exc.headers)
    return response


async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Deliberately omit "input": it may contain personal or health data.
    details = [
        {"loc": list(err.get("loc", ())), "msg": err.get("msg", ""), "type": err.get("type", "")}
        for err in exc.errors()
    ]
    return error_response(
        422, "validation_error", "Request validation failed.", _request_id(request), details
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _handle_app_error)
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
