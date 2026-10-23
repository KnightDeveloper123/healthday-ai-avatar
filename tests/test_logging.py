import json
import logging

from app.core.context import request_id_var, session_id_var
from app.core.logging import JsonFormatter


def _record(message: str, **extra: object) -> logging.LogRecord:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, message, (), None)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_outputs_valid_json_with_extras() -> None:
    line = JsonFormatter().format(_record("hello", request_id="abc-123"))
    data = json.loads(line)
    assert data["message"] == "hello"
    assert data["level"] == "INFO"
    assert data["request_id"] == "abc-123"
    assert "timestamp" in data


def test_json_formatter_preserves_devanagari() -> None:
    line = JsonFormatter().format(_record("मुझे Cancer Day के बारे में बताएं"))
    assert "मुझे" in line


def test_json_formatter_includes_request_context() -> None:
    request_token = request_id_var.set("req-12345678")
    session_token = session_id_var.set("sess-12345678")
    try:
        data = json.loads(JsonFormatter().format(_record("hello")))
    finally:
        request_id_var.reset(request_token)
        session_id_var.reset(session_token)
    assert data["request_id"] == "req-12345678"
    assert data["session_id"] == "sess-12345678"
