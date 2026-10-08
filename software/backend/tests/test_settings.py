"""Tests for Monitor API settings."""

from app.settings import Settings
from pydantic import ValidationError
from pytest import MonkeyPatch, raises


def test_settings_have_development_defaults(monkeypatch: MonkeyPatch) -> None:
    """Local development works without environment overrides."""

    monkeypatch.delenv("MONITOR_ENVIRONMENT", raising=False)
    monkeypatch.delenv("MONITOR_LOG_LEVEL", raising=False)
    monkeypatch.delenv("MONITOR_DATABASE_URL", raising=False)
    monkeypatch.delenv("MONITOR_CORS_ORIGIN", raising=False)
    monkeypatch.delenv("MONITOR_OTP_HMAC_SECRET", raising=False)
    for name in (
        "SMTP_HOST",
        "SMTP_PORT",
        "SMTP_SECURE",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "EMAIL_FROM",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.endswith("@database:5432/monitor")
    assert settings.cors_origin == "http://localhost:5173"
    assert settings.otp_hmac_secret.get_secret_value().endswith("change_me")
    assert settings.smtp_host == "mailpit"
    assert settings.smtp_port == 1025
    assert settings.smtp_secure is False
    assert settings.smtp_password.get_secret_value() == ""
    assert settings.email_from == "no-reply@monitor.local"


def test_settings_read_monitor_environment_variables(monkeypatch: MonkeyPatch) -> None:
    """MONITOR-prefixed variables override the local defaults."""

    monkeypatch.setenv("MONITOR_ENVIRONMENT", "test")
    monkeypatch.setenv("MONITOR_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MONITOR_DATABASE_URL", "postgresql://test:test@database/test")
    monkeypatch.setenv("MONITOR_CORS_ORIGIN", "http://frontend.test")
    monkeypatch.setenv("MONITOR_OTP_HMAC_SECRET", "test-otp-secret")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://test:test@database/test"
    assert settings.cors_origin == "http://frontend.test"
    assert settings.otp_hmac_secret.get_secret_value() == "test-otp-secret"


def test_production_rejects_the_development_otp_secret(monkeypatch: MonkeyPatch) -> None:
    """Production startup requires an explicit secret without extra policy envs."""

    monkeypatch.setenv("MONITOR_ENVIRONMENT", "production")
    monkeypatch.delenv("MONITOR_OTP_HMAC_SECRET", raising=False)

    with raises(ValidationError, match="requires a unique"):
        Settings()


def test_settings_read_job_talk_style_smtp_variables(monkeypatch: MonkeyPatch) -> None:
    """Mail settings use the approved unprefixed deployment convention."""

    monkeypatch.setenv("SMTP_HOST", "smtp.example.test")
    monkeypatch.setenv("SMTP_PORT", "465")
    monkeypatch.setenv("SMTP_SECURE", "true")
    monkeypatch.setenv("SMTP_USER", "monitor")
    monkeypatch.setenv("SMTP_PASSWORD", "not-a-real-secret")
    monkeypatch.setenv("EMAIL_FROM", "login@example.test")

    settings = Settings()

    assert settings.smtp_host == "smtp.example.test"
    assert settings.smtp_port == 465
    assert settings.smtp_secure is True
    assert settings.smtp_user == "monitor"
    assert settings.smtp_password.get_secret_value() == "not-a-real-secret"
    assert "not-a-real-secret" not in repr(settings)
    assert settings.email_from == "login@example.test"
