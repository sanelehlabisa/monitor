"""Tests for the Monitor API application."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def test_health_returns_service_metadata() -> None:
    """The health endpoint exposes its stable process-level contract."""

    client = TestClient(create_app(Settings(environment="test")))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "monitor-api",
        "version": "0.1.0",
        "environment": "test",
    }
