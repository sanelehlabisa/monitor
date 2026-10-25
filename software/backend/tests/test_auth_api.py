"""Focused API tests for passwordless authentication behavior."""

from contextlib import nullcontext
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from app.endpoints.auth import REQUEST_ACCEPTED_MESSAGE
from app.modules.email_delivery import EmailDeliveryError
from app.main import create_app
from app.modules.otp import OtpRateLimitError, OtpVerificationError, User
from app.modules.sessions import CreatedSession
from fastapi.testclient import TestClient
from pytest import MonkeyPatch, mark


@mark.parametrize(
    "expected_error",
    [None, OtpRateLimitError("limited"), EmailDeliveryError("failed")],
)
def test_request_response_hides_expected_outcomes(
    monkeypatch: MonkeyPatch, expected_error: Exception | None
) -> None:
    """Delivery success, policy rejection and SMTP failure look identical."""

    def fake_delivery(*args: object, **kwargs: object) -> None:
        if expected_error:
            raise expected_error

    monkeypatch.setattr(
        "app.endpoints.auth.connect_database", lambda: nullcontext(object())
    )
    monkeypatch.setattr("app.endpoints.auth.deliver_login_code", fake_delivery)
    client = TestClient(create_app())

    response = client.post(
        "/api/auth/request-otp", json={"email": " USER@Example.test "}
    )

    assert response.status_code == 202
    assert response.json() == {"message": REQUEST_ACCEPTED_MESSAGE}


def test_request_does_not_hide_unexpected_server_failures(
    monkeypatch: MonkeyPatch,
) -> None:
    """Programming and infrastructure failures remain observable as HTTP 500."""

    def fail_unexpectedly(*args: object, **kwargs: object) -> None:
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(
        "app.endpoints.auth.connect_database", lambda: nullcontext(object())
    )
    monkeypatch.setattr("app.endpoints.auth.deliver_login_code", fail_unexpectedly)
    client = TestClient(
        create_app(), raise_server_exceptions=False
    )

    response = client.post(
        "/api/auth/request-otp", json={"email": "user@example.test"}
    )

    assert response.status_code == 500


@mark.parametrize(
    "email,user_type,expected_admin",
    [
        ("user@example.test", "user", False),
        ("user@example.test", "admin", True),
        ("hlabisasanele730@gmail.com", "user", False),
    ],
)
def test_verification_sets_approved_secure_cookie(
    monkeypatch: MonkeyPatch,
    email: str,
    user_type: Literal["user", "admin"],
    expected_admin: bool,
) -> None:
    """Stored types alone control access, despite seed email or stale admin env."""

    monkeypatch.setenv("MONITOR_ADMIN_EMAILS", email)  # Negative legacy-env regression.
    user = User(7, email, datetime(2026, 10, 9, tzinfo=UTC), user_type)
    session = CreatedSession(
        UUID("00000000-0000-0000-0000-000000000001"),
        "opaque-cookie-token",
        datetime(2026, 11, 8, tzinfo=UTC),
    )
    monkeypatch.setattr(
        "app.endpoints.auth.connect_database", lambda: nullcontext(object())
    )
    monkeypatch.setattr("app.endpoints.auth.verify_otp", lambda *args: user)
    monkeypatch.setattr("app.endpoints.auth.create_session", lambda *args: session)
    client = TestClient(
        create_app(), base_url="https://testserver"
    )

    response = client.post(
        "/api/auth/verify-otp",
        json={"email": email, "code": "123456"},
    )

    cookie = response.headers["set-cookie"]
    assert response.json() == {
        "id": 7,
        "email": email,
        "is_admin": expected_admin,
    }
    assert "monitor_session=opaque-cookie-token" in cookie
    assert "Max-Age=2592000" in cookie
    assert "Path=/" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" in cookie
    assert "123456" not in response.text
    assert "opaque-cookie-token" not in response.text


def test_verification_failure_is_generic(monkeypatch: MonkeyPatch) -> None:
    """OTP policy details do not cross the HTTP boundary."""

    def reject_code(*args: object) -> None:
        raise OtpVerificationError("specific internal reason")

    monkeypatch.setattr(
        "app.endpoints.auth.connect_database", lambda: nullcontext(object())
    )
    monkeypatch.setattr("app.endpoints.auth.verify_otp", reject_code)
    client = TestClient(create_app())

    response = client.post(
        "/api/auth/verify-otp",
        json={"email": "user@example.test", "code": "123456"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired code"}


def test_invalid_email_and_code_shapes_are_rejected() -> None:
    """Malformed inputs fail before database or SMTP work starts."""

    client = TestClient(create_app())

    invalid_email = client.post(
        "/api/auth/request-otp", json={"email": "not-an-email"}
    )
    assert invalid_email.status_code == 422
    assert client.post(
        "/api/auth/verify-otp",
        json={"email": "user@example.test", "code": "12345"},
    ).status_code == 422


def test_logout_without_cookie_is_idempotent() -> None:
    """A missing session still receives the same successful logout response."""

    response = TestClient(create_app()).post(
        "/api/auth/logout"
    )

    assert response.status_code == 204
    assert "monitor_session=" in response.headers["set-cookie"]
