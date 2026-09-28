"""Tests for Monitor API settings."""

from app.settings import Settings
from pytest import MonkeyPatch


def test_settings_have_development_defaults(monkeypatch: MonkeyPatch) -> None:
    """Local development works without environment overrides."""

    monkeypatch.delenv("MONITOR_ENVIRONMENT", raising=False)
    monkeypatch.delenv("MONITOR_LOG_LEVEL", raising=False)
    monkeypatch.delenv("MONITOR_DATABASE_URL", raising=False)

    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.endswith("@database:5432/monitor")


def test_settings_read_monitor_environment_variables(monkeypatch: MonkeyPatch) -> None:
    """MONITOR-prefixed variables override the local defaults."""

    monkeypatch.setenv("MONITOR_ENVIRONMENT", "test")
    monkeypatch.setenv("MONITOR_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MONITOR_DATABASE_URL", "postgresql://test:test@database/test")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "postgresql://test:test@database/test"
