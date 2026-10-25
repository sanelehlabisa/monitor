"""Runtime environment boundaries with synthetic values and no service calls."""

from fastapi.testclient import TestClient
from pytest import MonkeyPatch, fixture, mark, raises

from app.main import create_app, validate_origin
from app.modules.email_delivery import SmtpEmailSender
from app.modules.otp import get_otp_secret
from app.modules.reminder_scheduler import read_activation_cutoff


@fixture(autouse=True)
def configured_environment(monkeypatch: MonkeyPatch) -> None:
    """Supply complete synthetic input without a replacement settings object."""
    values = {
        "MONITOR_ENVIRONMENT": "test",
        "MONITOR_DATABASE_URL": "postgresql://runtime:synthetic@database:5432/runtime_test",
        "MONITOR_CORS_ORIGIN": "https://frontend.example.test",
        "MONITOR_OTP_HMAC_SECRET": "synthetic-runtime-otp-secret",
        "SMTP_HOST": "mailpit",
        "SMTP_PORT": "1025",
        "SMTP_SECURE": "false",
        "SMTP_USER": "",
        "SMTP_PASSWORD": "",
        "EMAIL_FROM": "no-reply@example.test",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT", raising=False)


@mark.parametrize("name", [
    "MONITOR_ENVIRONMENT", "MONITOR_DATABASE_URL", "MONITOR_CORS_ORIGIN",
    "MONITOR_OTP_HMAC_SECRET", "SMTP_HOST", "SMTP_PORT", "SMTP_SECURE",
    "SMTP_USER", "SMTP_PASSWORD", "EMAIL_FROM",
])
def test_missing_runtime_value_fails_at_startup(monkeypatch: MonkeyPatch, name: str) -> None:
    """Missing inputs name the key without exposing credentials."""
    monkeypatch.delenv(name)
    with raises(KeyError) as captured:
        create_app()
    assert captured.value.args == (name,)
    assert "synthetic-runtime-otp-secret" not in repr(captured.value)


@mark.parametrize("name,value", [
    ("MONITOR_ENVIRONMENT", "private-invalid-environment"),
    ("SMTP_PORT", "private-invalid-port"),
    ("SMTP_PORT", "0"),
    ("SMTP_PORT", "65536"),
    ("SMTP_SECURE", "private-invalid-bool"),
])
def test_malformed_input_fails_without_reflecting_value(
    monkeypatch: MonkeyPatch, name: str, value: str,
) -> None:
    monkeypatch.setenv(name, value)
    with raises(ValueError) as captured:
        create_app()
    assert name in str(captured.value)
    if value.startswith("private-"):
        assert value not in str(captured.value)
        assert value not in repr(captured.value)


def test_invalid_reminder_cutoff_does_not_expose_input(monkeypatch: MonkeyPatch) -> None:
    value = "private-invalid-reminder-cutoff"
    monkeypatch.setenv("MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT", value)
    with raises(ValueError) as captured:
        create_app()
    assert value not in str(captured.value)
    assert value not in repr(captured.value)


def test_otp_key_is_read_unchanged_across_app_creation(monkeypatch: MonkeyPatch) -> None:
    """Restart-style construction does not generate or replace a login-code key."""
    monkeypatch.setenv("MONITOR_OTP_HMAC_SECRET", "test-persistent-otp-key")
    create_app()
    first = get_otp_secret()
    create_app()
    assert first == get_otp_secret() == "test-persistent-otp-key"


def test_explicit_blank_capture_credentials_and_disabled_cutoff_are_allowed() -> None:
    sender = SmtpEmailSender()
    assert sender.smtp_host == "mailpit"
    assert sender.smtp_port == 1025
    assert sender.smtp_secure is False
    assert sender.smtp_user == sender.smtp_password == ""
    assert read_activation_cutoff() is None


@mark.parametrize("name", ["MONITOR_ADMIN_EMAILS", "MONITOR_LOG_LEVEL"])
def test_removed_environment_settings_cannot_restore_runtime_fields(
    monkeypatch: MonkeyPatch, name: str,
) -> None:
    monkeypatch.setenv(name, "not-a-valid-setting")
    app = create_app()
    assert not hasattr(app.state, "settings")
    assert TestClient(app).get("/health").json()["environment"] == "test"


@mark.parametrize("secret", [
    "monitor_dev_otp_secret_change_me", "", "   ", " monitor_dev_otp_secret_change_me ",
])
def test_production_rejects_example_or_blank_keys(monkeypatch: MonkeyPatch, secret: str) -> None:
    monkeypatch.setenv("MONITOR_ENVIRONMENT", "production")
    monkeypatch.setenv("MONITOR_OTP_HMAC_SECRET", secret)
    with raises(ValueError, match="requires a unique"):
        create_app()


@mark.parametrize("origin", ["https://localhost:5173", "https://monitor.roventics.com"])
def test_production_accepts_https_and_supplied_secret(monkeypatch: MonkeyPatch, origin: str) -> None:
    monkeypatch.setenv("MONITOR_ENVIRONMENT", "production")
    monkeypatch.setenv("MONITOR_CORS_ORIGIN", origin)
    assert TestClient(create_app()).get("/health").json()["environment"] == "production"


@mark.parametrize("origin", [
    "http://localhost:5173", "http://localhost", "https://localhost",
    "https://localhost:8443", "https://monitor.roventics.com",
    "https://127.0.0.1:5173", "http://192.0.2.1:8080",
])
def test_canonical_public_origin_is_preserved(origin: str) -> None:
    assert validate_origin(origin, "test") == origin


@mark.parametrize("origin", [
    "", "ftp://localhost", "HTTPS://localhost", "https://Monitor.roventics.com",
    "https://localhost/", "https://user:private-origin-marker@localhost",
    "https://localhost?private-origin-marker", "https://localhost#private-origin-marker",
    " https://localhost", "https://localhost\n", "https://local\thost",
    "https://localhost\r\nprivate-origin-marker", 'https://localhost";private-origin-marker',
    "https://monitor..roventics.com", "https://-monitor.roventics.com",
    "https://monitor-.roventics.com", "https://monitor_roventics.com",
    "https://localhost.", "https://localhost:", "https://localhost:0",
    "https://localhost:65536", "https://localhost:443", "http://localhost:80",
    "https://localhost:08443", "https://127.000.0.1", "https://999.0.0.1",
    "https://2130706433", "https://[::1]", "https://localhost\\private-origin-marker",
    "https://" + "a" * 64 + ".test", "https://" + ".".join(["a" * 63] * 4),
])
def test_noncanonical_public_origin_is_rejected_without_value(origin: str) -> None:
    with raises(ValueError, match="canonical HTTP\\(S\\) origin") as captured:
        validate_origin(origin, "test")
    if origin:
        assert origin not in str(captured.value)
        assert origin not in repr(captured.value)


def test_production_rejects_http_even_for_localhost(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("MONITOR_ENVIRONMENT", "production")
    monkeypatch.setenv("MONITOR_CORS_ORIGIN", "http://localhost:5173")
    with raises(ValueError, match="Production APP_URL must use HTTPS"):
        create_app()


def test_smtp_reads_provider_variables_without_exposing_password(monkeypatch: MonkeyPatch) -> None:
    for name, value in {
        "SMTP_HOST": "smtp.example.test", "SMTP_PORT": "465", "SMTP_SECURE": "true",
        "SMTP_USER": "monitor", "SMTP_PASSWORD": "not-a-real-secret",
    }.items():
        monkeypatch.setenv(name, value)
    sender = SmtpEmailSender()
    assert sender.smtp_host == "smtp.example.test"
    assert sender.smtp_port == 465 and sender.smtp_secure is True
    assert sender.smtp_user == "monitor" and sender.smtp_password == "not-a-real-secret"
    assert "not-a-real-secret" not in repr(sender)
