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

    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.endswith("@database:5432/monitor")
    assert settings.cors_origin == "http://localhost:5173"
    assert settings.otp_hmac_secret.get_secret_value().endswith("change_me")


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
