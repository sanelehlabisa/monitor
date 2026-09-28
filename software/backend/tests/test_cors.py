"""Tests for the browser-facing CORS boundary."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def test_frontend_origin_can_preflight_api_route() -> None:
    """The configured frontend may make browser API requests."""

    settings = Settings(environment="test", cors_origin="http://localhost:5173")
    response = TestClient(create_app(settings)).options(
        "/health",
        headers={
            "Origin": settings.cors_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == settings.cors_origin


def test_other_origins_are_not_allowed() -> None:
    """An origin outside the configured frontend boundary is rejected."""

    response = TestClient(create_app(Settings(environment="test"))).options(
        "/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
