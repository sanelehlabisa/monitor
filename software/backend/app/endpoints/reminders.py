"""Authenticated routes for per-meter email reminder preferences."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.endpoints.auth import AuthenticatedUser, require_authenticated_user
from app.database import connect_database
from app.endpoints.meters import meter_access_scope
from app.modules.meters import MeterNotFoundError
from app.modules.reminder_settings import (
    ReminderSettings,
    get_reminder_settings,
    upsert_reminder_settings,
)

from app.schemas.reminders import ReminderSettingsRequest, ReminderSettingsResponse

router = APIRouter(prefix="/api/meters/{meter_id}/reminders", tags=["reminders"])


@router.get("", response_model=ReminderSettingsResponse)
def reminders_show(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> ReminderSettingsResponse:
    """Return reminder preferences for an accessible meter."""

    try:
        with connect_database() as connection:
            settings = get_reminder_settings(
                connection, meter_id, meter_access_scope(authenticated)
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
        with connect_database() as connection:
            settings = upsert_reminder_settings(
                connection,
                meter_id,
                meter_access_scope(authenticated),
                **payload.model_dump(),
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    return _response(settings)


def _response(settings: ReminderSettings) -> ReminderSettingsResponse:
    return ReminderSettingsResponse(**settings.__dict__)


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Reminder settings not found")
