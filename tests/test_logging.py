import json
import logging

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
