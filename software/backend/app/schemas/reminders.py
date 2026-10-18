"""Request and response validation for email reminder preferences."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.modules.reminder_settings import normalize_timezone


class ReminderSettingsRequest(BaseModel):
    """Complete user-controlled reminder preference values."""

    monthly_enabled: bool
    monthly_day: int = Field(ge=1, le=28)
    low_balance_enabled: bool
    low_balance_days: Decimal = Field(
        gt=0,
        le=30,
        max_digits=4,
        decimal_places=2,
    )
    timezone: str = Field(min_length=1, max_length=64)

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        """Normalize and validate the submitted IANA timezone."""

        return normalize_timezone(value)


class ReminderSettingsResponse(BaseModel):
    """Stored settings or safe disabled defaults for one meter."""

    meter_id: UUID
    monthly_enabled: bool
    monthly_day: int
    low_balance_enabled: bool
    low_balance_days: Decimal
    timezone: str
    created_at: datetime | None
    updated_at: datetime | None
