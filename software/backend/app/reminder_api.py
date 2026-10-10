"""Authenticated routes for per-meter email reminder preferences."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from app.auth_api import AuthenticatedUser, require_authenticated_user
from app.database import connect_database
from app.meter_api import meter_owner_scope
from app.meters import MeterNotFoundError
from app.reminder_settings import (
    ReminderSettings,
    get_reminder_settings,
    normalize_timezone,
    upsert_reminder_settings,
)

router = APIRouter(prefix="/api/meters/{meter_id}/reminders", tags=["reminders"])


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


@router.get("", response_model=ReminderSettingsResponse)
def reminders_show(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> ReminderSettingsResponse:
    """Return reminder preferences for an accessible meter."""

    try:
        with connect_database(request.app.state.settings) as connection:
            settings = get_reminder_settings(
                connection, meter_id, meter_owner_scope(authenticated)
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    return _response(settings)


@router.patch("", response_model=ReminderSettingsResponse)
def reminders_update(
    meter_id: UUID,
    payload: ReminderSettingsRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> ReminderSettingsResponse:
    """Create or replace reminder preferences for an accessible meter."""

    try:
        with connect_database(request.app.state.settings) as connection:
            settings = upsert_reminder_settings(
                connection,
                meter_id,
                meter_owner_scope(authenticated),
                **payload.model_dump(),
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    return _response(settings)


def _response(settings: ReminderSettings) -> ReminderSettingsResponse:
    return ReminderSettingsResponse(**settings.__dict__)


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Reminder settings not found")
