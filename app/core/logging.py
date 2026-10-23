"""Structured JSON logging (stdlib only).

Extra fields passed via `logger.info("msg", extra={"intent": "..."})` are included.
`request_id` and `session_id` are added automatically from the request context.
"""

import json
import logging
import sys
from datetime import timezone, datetime
from typing import Any

from app.core.context import request_id_var, session_id_var

# Attributes every LogRecord has; anything else came from `extra=`.
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}
_HANDLER_FLAG = "_healthday_handler"
_UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


class JsonFormatter(logging.Formatter):
    """Render each log record as one JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        session_id = session_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        if session_id:
            payload["session_id"] = session_id
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once. Safe to call repeatedly."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, _HANDLER_FLAG, False):
            root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    setattr(handler, _HANDLER_FLAG, True)
    root.addHandler(handler)
    root.setLevel(level)

    # Route uvicorn's logs through our JSON handler; our middleware logs requests itself,
    # so silence uvicorn's duplicate access log.
    for name in _UVICORN_LOGGERS:
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
