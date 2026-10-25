"""Tests for the browser-facing CORS boundary."""

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.main import create_app


def test_frontend_origin_can_preflight_credentialed_api_route(monkeypatch: MonkeyPatch) -> None:
    """The configured frontend may use every supported CRUD method."""

    origin = "http://localhost:5173"
    monkeypatch.setenv("MONITOR_CORS_ORIGIN", origin)
    response = TestClient(create_app()).options(
        "/api/auth/request-otp",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["access-control-allow-methods"] == "GET, POST, PATCH, DELETE"


def test_other_origins_are_not_allowed() -> None:
    """An origin outside the configured frontend boundary is rejected."""

    response = TestClient(create_app()).options(
        "/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
