"""Authenticated CRUD routes for nickname-only meter profiles."""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from psycopg import Connection

from app.auth_api import AuthenticatedUser, require_authenticated_user
from app.database import connect_database
from app.meters import (
    Meter,
    MeterNameConflictError,
    MeterNotFoundError,
    create_meter,
    delete_meter,
    get_meter,
    list_meters,
    normalize_meter_name,
    rename_meter,
)

router = APIRouter(prefix="/api/meters", tags=["meters"])


class MeterNameRequest(BaseModel):
    """The only user-entered value required by a V1 meter profile."""

    name: str = Field(min_length=1, max_length=80)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return normalize_meter_name(value)


class MeterResponse(BaseModel):
    """Safe meter representation including owner identity for admin displays."""

    id: UUID
    name: str
    owner_email: str
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[MeterResponse])
def meters_index(
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> list[MeterResponse]:
    """List owned meters, or every meter for a configured administrator."""

    with connect_database(request.app.state.settings) as connection:
        meters = list_meters(connection, meter_owner_scope(authenticated))
    return [_response(meter) for meter in meters]


@router.post("", response_model=MeterResponse, status_code=status.HTTP_201_CREATED)
def meters_create(
    payload: MeterNameRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> MeterResponse:
    """Create a meter owned by the signed-in user."""

    try:
        with connect_database(request.app.state.settings) as connection:
            meter = create_meter(connection, authenticated.user.id, payload.name)
    except MeterNameConflictError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    return _response(meter)


@router.get("/{meter_id}", response_model=MeterResponse)
def meters_show(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> MeterResponse:
    """Return an accessible meter without revealing inaccessible IDs."""

    with connect_database(request.app.state.settings) as connection:
        meter = _find(connection, meter_id, meter_owner_scope(authenticated))
    return _response(meter)


@router.patch("/{meter_id}", response_model=MeterResponse)
def meters_rename(
    meter_id: UUID,
    payload: MeterNameRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> MeterResponse:
    """Rename an accessible meter."""

    try:
        with connect_database(request.app.state.settings) as connection:
            meter = rename_meter(
                connection, meter_id, meter_owner_scope(authenticated), payload.name
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    except MeterNameConflictError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    return _response(meter)


@router.delete("/{meter_id}", status_code=status.HTTP_204_NO_CONTENT)
def meters_delete(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> Response:
    """Delete an accessible meter."""

    try:
        with connect_database(request.app.state.settings) as connection:
            delete_meter(connection, meter_id, meter_owner_scope(authenticated))
    except MeterNotFoundError as error:
        raise _not_found() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def meter_owner_scope(authenticated: AuthenticatedUser) -> int | None:
    """Return the repository owner scope for a regular user or administrator."""

    return None if authenticated.is_admin else authenticated.user.id


def _find(
    connection: Connection[Any], meter_id: UUID, owner_user_id: int | None
) -> Meter:
    try:
        return get_meter(connection, meter_id, owner_user_id)
    except MeterNotFoundError as error:
        raise _not_found() from error


def _not_found() -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, "Meter not found")


def _response(meter: Meter) -> MeterResponse:
    return MeterResponse(
        id=meter.id,
        name=meter.name,
        owner_email=meter.owner_email,
        created_at=meter.created_at,
        updated_at=meter.updated_at,
    )
