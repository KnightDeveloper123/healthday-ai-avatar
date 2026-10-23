import logging
import re

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

HEALTH = "/api/v1/health"


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_generates_request_id(client: TestClient) -> None:
    response = client.get(HEALTH)
    assert re.fullmatch(r"[0-9a-f]{32}", response.headers["X-Request-ID"])


def test_echoes_valid_client_request_id(client: TestClient) -> None:
    response = client.get(HEALTH, headers={"X-Request-ID": "client-req-12345"})
    assert response.headers["X-Request-ID"] == "client-req-12345"


def test_replaces_unsafe_request_id(client: TestClient) -> None:
    response = client.get(HEALTH, headers={"X-Request-ID": "bad id!"})
    assert response.headers["X-Request-ID"] != "bad id!"
    assert re.fullmatch(r"[0-9a-f]{32}", response.headers["X-Request-ID"])


def test_access_log_has_fields_and_no_query_string(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="app.core.middleware"):
        client.get(HEALTH, params={"name": "private"})
    record = next(r for r in caplog.records if r.getMessage() == "request completed")
    assert record.method == "GET"
    assert record.path == HEALTH
    assert record.status_code == 200
    assert record.latency_ms >= 0
    assert "private" not in str(record.__dict__)
