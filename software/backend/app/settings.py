"""Typed configuration for the Monitor API."""

from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_OTP_HMAC_SECRET = "monitor_dev_otp_secret_change_me"


class Settings(BaseSettings):
    """Load application settings from defaults and ``MONITOR_`` variables."""

    model_config = SettingsConfigDict(env_prefix="MONITOR_", case_sensitive=False)

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: str = "postgresql://monitor:monitor_dev_only@database:5432/monitor"
    cors_origin: str = "http://localhost:5173"
    otp_hmac_secret: SecretStr = SecretStr(DEFAULT_OTP_HMAC_SECRET)

    @model_validator(mode="after")
    def reject_development_secret_in_production(self) -> "Settings":
        """Prevent production from using the committed development OTP secret."""

        if (
            self.environment == "production"
            and self.otp_hmac_secret.get_secret_value() == DEFAULT_OTP_HMAC_SECRET
        ):
            raise ValueError("Production requires a unique MONITOR_OTP_HMAC_SECRET")
        return self
