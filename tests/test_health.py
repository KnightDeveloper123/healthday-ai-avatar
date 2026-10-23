from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "HealthDay AI"
    assert set(body) == {"status", "app", "version", "environment"}


def test_openapi_lists_health_route() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]


def test_unknown_route_returns_404() -> None:
    assert client.get("/api/v1/does-not-exist").status_code == 404


def test_health_rejects_wrong_method() -> None:
    assert client.post("/api/v1/health").status_code == 405