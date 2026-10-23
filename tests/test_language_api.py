import logging

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

URL = "/api/v1/language/analyze"


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_analyze_spec_example(client: TestClient) -> None:
    response = client.post(URL, json={"text": "मुझे Cancer Day के बारे में बताएं।"})
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    body = response.json()
    assert body["analysis"]["primary_language"] == "hi"
    assert body["analysis"]["detected_languages"] == ["hi", "en"]
    assert body["analysis"]["code_switched"] is True
    assert body["analysis"]["medical_terms"] == ["Cancer Day"]
    assert body["route"]["tts_language"] == "hi"


def test_hinglish_route_uses_latin_script(client: TestClient) -> None:
    body = client.post(URL, json={"text": "Mujhe diabetes ke baare mein batao"}).json()
    assert body["analysis"]["response_language"] == "hinglish"
    assert body["route"]["tts_script"] == "latin"


@pytest.mark.parametrize(
    "payload",
    [
        {"text": ""},
        {"text": "x" * 2001},
        {"text": "hello", "selected_language": "fr"},
        {"text": "hello", "history": ["klingon"]},
        {},
    ],
)
def test_invalid_requests_use_error_envelope(client: TestClient, payload: dict) -> None:
    response = client.post(URL, json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_user_text_is_never_logged(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO):
        client.post(URL, json={"text": "Secret symptom words about cancer"})
    logged = " ".join(f"{r.getMessage()} {r.__dict__}" for r in caplog.records)
    assert "language analyzed" in logged
    assert "Secret symptom" not in logged