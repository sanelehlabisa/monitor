"""Typed configuration for the Monitor API."""

from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_OTP_HMAC_SECRET = "monitor_dev_otp_secret_change_me"


class Settings(BaseSettings):
    """Load application settings from defaults and ``MONITOR_`` variables."""

    model_config = SettingsConfigDict(
        env_prefix="MONITOR_", case_sensitive=False, populate_by_name=True
    )

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = "postgresql://monitor:monitor_dev_only@database:5432/monitor"
    cors_origin: str = "http://localhost:5173"
    otp_hmac_secret: SecretStr = SecretStr(DEFAULT_OTP_HMAC_SECRET)
    smtp_host: str = Field(default="mailpit", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, ge=1, le=65535, validation_alias="SMTP_PORT")
    smtp_secure: bool = Field(default=False, validation_alias="SMTP_SECURE")
    smtp_user: str = Field(default="", validation_alias="SMTP_USER")
    smtp_password: SecretStr = Field(
        default=SecretStr(""), validation_alias="SMTP_PASSWORD"
    )
    email_from: str = Field(
        default="no-reply@monitor.local", validation_alias="EMAIL_FROM"
    )

    @model_validator(mode="after")
    def reject_development_secret_in_production(self) -> "Settings":
        """Prevent production from using the committed development OTP secret."""

        if (
            self.environment == "production"
            and self.otp_hmac_secret.get_secret_value() == DEFAULT_OTP_HMAC_SECRET
        ):
            raise ValueError("Production requires a unique MONITOR_OTP_HMAC_SECRET")
        return self
