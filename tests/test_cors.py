from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

ORIGIN = "http://localhost:3000"


def _client() -> TestClient:
    return TestClient(create_app(Settings(_env_file=None, cors_origins=[ORIGIN])))


def test_allowed_origin_gets_cors_headers() -> None:
    response = _client().options(
        "/api/v1/health",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ORIGIN
    assert "X-Request-ID" in response.headers


def test_unlisted_origin_gets_no_cors_headers() -> None:
    response = _client().get("/api/v1/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers
