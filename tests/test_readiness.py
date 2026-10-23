from fastapi.testclient import TestClient

from app.main import create_app

READY = "/api/v1/health/ready"


def test_ready_with_no_checks() -> None:
    response = TestClient(create_app()).get(READY)
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {}}


def test_not_ready_when_a_check_fails() -> None:
    app = create_app()
    app.state.readiness_checks = {"db": lambda: True, "qdrant": lambda: False}
    response = TestClient(app).get(READY)
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "checks": {"db": "ok", "qdrant": "fail"}}


def test_raising_check_is_failure_without_leaking_details() -> None:
    def broken() -> bool:
        raise ConnectionError("password=hunter2")

    app = create_app()
    app.state.readiness_checks = {"redis": broken}
    response = TestClient(app).get(READY)
    assert response.status_code == 503
    assert response.json()["checks"] == {"redis": "fail"}
    assert "hunter2" not in response.text
