"""Tests for Keycloak bearer-token validation and protected routes."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from jwt import encode
from pytest import MonkeyPatch

from app.auth import TokenValidator
from app.main import create_app
from app.settings import Settings


def _authenticated_client(
    monkeypatch: MonkeyPatch,
    token_audience: str = "monitor-api",
) -> tuple[TestClient, str]:
    settings = Settings(environment="test")
    validator = TokenValidator(settings)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def signing_key(_: str) -> SimpleNamespace:
        return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setattr(validator.jwks_client, "get_signing_key_from_jwt", signing_key)
    token = encode(
        {
            "iss": settings.keycloak_issuer,
            "aud": token_audience,
            "sub": "development-user-id",
            "preferred_username": "monitor.developer",
            "email": "developer@example.test",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )
    application = create_app(settings)
    application.state.token_validator = validator
    return TestClient(application), token


def test_auth_me_rejects_missing_token() -> None:
    """Protected routes require bearer authentication."""

    response = TestClient(create_app(Settings(environment="test"))).get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_auth_me_returns_validated_identity(monkeypatch: MonkeyPatch) -> None:
    """A valid Keycloak-style token returns the selected identity claims."""

    client, token = _authenticated_client(monkeypatch)
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "sub": "development-user-id",
        "username": "monitor.developer",
        "email": "developer@example.test",
    }


def test_auth_me_rejects_wrong_audience(monkeypatch: MonkeyPatch) -> None:
    """A correctly signed token for another audience is rejected."""

    client, token = _authenticated_client(monkeypatch, token_audience="other-api")
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
