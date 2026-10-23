import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api.schemas import ErrorResponse
from app.core.exceptions import NotFoundError
from app.main import create_app


class EchoPayload(BaseModel):
    text: str


@pytest.fixture
def client() -> TestClient:
    app = create_app()

    @app.post("/api/v1/_test/echo")
    def echo(payload: EchoPayload) -> dict[str, str]:
        return {"text": payload.text}

    @app.get("/api/v1/_test/app-error")
    def app_error() -> None:
        raise NotFoundError("campaign not found")

    @app.get("/api/v1/_test/boom")
    def boom() -> None:
        raise RuntimeError("secret internal detail")

    return TestClient(app, raise_server_exceptions=False)


def test_validation_error_uses_envelope_and_hides_input(client: TestClient) -> None:
    response = client.post("/api/v1/_test/echo", json={"text": ["secret-value"]})
    assert response.status_code == 422
    body = ErrorResponse.model_validate(response.json())
    assert body.error.code == "validation_error"
    assert body.error.request_id == response.headers["X-Request-ID"]
    assert body.error.details[0]["loc"] == ["body", "text"]
    assert "secret-value" not in response.text


def test_malformed_json_is_422(client: TestClient) -> None:
    response = client.post(
        "/api/v1/_test/echo", content="{bad", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_app_error_maps_to_status_and_code(client: TestClient) -> None:
    response = client.get("/api/v1/_test/app-error")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert error["message"] == "campaign not found"


def test_unhandled_exception_returns_generic_500(client: TestClient) -> None:
    response = client.get("/api/v1/_test/boom")
    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "internal_error"
    assert error["request_id"] == response.headers["X-Request-ID"]
    assert "secret internal detail" not in response.text
    assert "RuntimeError" not in response.text


def test_unknown_route_uses_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_wrong_method_uses_envelope(client: TestClient) -> None:
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"