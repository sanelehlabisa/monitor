"""Tests for Monitor API settings."""

from app.settings import Settings
from pytest import MonkeyPatch


def test_settings_have_development_defaults(monkeypatch: MonkeyPatch) -> None:
    """Local development works without environment overrides."""

    monkeypatch.delenv("MONITOR_ENVIRONMENT", raising=False)
    monkeypatch.delenv("MONITOR_LOG_LEVEL", raising=False)

    settings = Settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_settings_read_monitor_environment_variables(monkeypatch: MonkeyPatch) -> None:
    """MONITOR-prefixed variables override the local defaults."""

    monkeypatch.setenv("MONITOR_ENVIRONMENT", "test")
    monkeypatch.setenv("MONITOR_LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
