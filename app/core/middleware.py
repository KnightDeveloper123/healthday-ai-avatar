"""Request context + access logging middleware."""

import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import request_id_var, session_id_var
from app.core.exceptions import error_response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
SESSION_ID_HEADER = "X-Session-ID"
_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{8,64}")


def _clean_id(value: str | None) -> str | None:
    """Accept a client-supplied ID only if it is safe to log."""
    if value and _ID_PATTERN.fullmatch(value):
        return value
    return None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign request/session IDs, log each request, and convert crashes to a clean 500."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _clean_id(request.headers.get(REQUEST_ID_HEADER)) or uuid.uuid4().hex
        session_id = _clean_id(request.headers.get(SESSION_ID_HEADER))
        request.state.request_id = request_id

        request_token = request_id_var.set(request_id)
        session_token = session_id_var.set(session_id)
        started = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("unhandled error", extra={"path": request.url.path})
                response = error_response(
                    500, "internal_error", "An unexpected error occurred.", request_id
                )

            response.headers[REQUEST_ID_HEADER] = request_id
            logger.info(
                "request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,  # path only: query strings may hold personal data
                    "status_code": response.status_code,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            return response
        finally:
            request_id_var.reset(request_token)
            session_id_var.reset(session_token)
