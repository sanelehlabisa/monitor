"""Typed configuration for the Monitor API."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load application settings from defaults and ``MONITOR_`` variables."""

    model_config = SettingsConfigDict(env_prefix="MONITOR_", case_sensitive=False)

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = "postgresql://monitor:monitor_dev_only@database:5432/monitor"
    keycloak_issuer: str = "http://localhost:8080/realms/monitor"
    keycloak_audience: str = "monitor-api"
    keycloak_jwks_url: str = (
        "http://keycloak:8080/realms/monitor/protocol/openid-connect/certs"
    )
    cors_origin: str = "http://localhost:5173"
