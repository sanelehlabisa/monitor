"""Typed configuration for the Monitor API."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load application settings from defaults and ``MONITOR_`` variables."""

    model_config = SettingsConfigDict(env_prefix="MONITOR_", case_sensitive=False)

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
