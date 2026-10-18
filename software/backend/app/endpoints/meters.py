"""Authenticated CRUD routes for nickname-only meter profiles."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from psycopg import Connection

from app.endpoints.auth import AuthenticatedUser, require_authenticated_user
from app.database import connect_database
from app.modules.memberships import (
    LastMemberError,
    MemberNotFoundError,
    list_members,
    remove_member,
    share_member,
)
from app.modules.meters import (
    Meter,
    MeterNameConflictError,
    MeterNotFoundError,
    create_meter,
    delete_meter,
    get_meter,
    list_meters,
    rename_meter,
)

from app.schemas.auth import EmailRequest
from app.schemas.meters import MemberResponse, MeterNameRequest, MeterResponse

router = APIRouter(prefix="/api/meters", tags=["meters"])


@router.get("", response_model=list[MeterResponse])
def meters_index(
    request: Request,
    q: Annotated[str | None, Query(max_length=254)] = None,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> list[MeterResponse]:
    """List accessible meters, optionally filtered by one keyword."""

    with connect_database(request.app.state.settings) as connection:
        meters = list_meters(connection, meter_access_scope(authenticated), q)
    return [_response(meter) for meter in meters]


@router.post("", response_model=MeterResponse, status_code=status.HTTP_201_CREATED)
def meters_create(
    payload: MeterNameRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> MeterResponse:
    """Create a meter with the signed-in user as its first member."""

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
        meter = _find(connection, meter_id, meter_access_scope(authenticated))
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
                connection, meter_id, meter_access_scope(authenticated), payload.name
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
    """Permanently delete a meter and history as a current member or admin."""

    try:
        with connect_database(request.app.state.settings) as connection:
            delete_meter(connection, meter_id, meter_access_scope(authenticated))
    except MeterNotFoundError as error:
        raise _not_found() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{meter_id}/members", response_model=list[MemberResponse])
def members_index(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> list[MemberResponse]:
    """List an accessible meter's members without exposing a global directory."""

    try:
        with connect_database(request.app.state.settings) as connection:
            members = list_members(
                connection, meter_id, meter_access_scope(authenticated)
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    return [MemberResponse(**member.__dict__) for member in members]


@router.post("/{meter_id}/members", response_model=MemberResponse)
def members_share(
    meter_id: UUID,
    payload: EmailRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> MemberResponse:
    """Share by normalized email, provisioning only a regular account if absent."""

    try:
        with connect_database(request.app.state.settings) as connection:
            member = share_member(
                connection, meter_id, meter_access_scope(authenticated), payload.email
            )
    except MeterNotFoundError as error:
        raise _not_found() from error
    return MemberResponse(**member.__dict__)


@router.delete("/{meter_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def members_remove(
    meter_id: UUID,
    user_id: int,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> Response:
    """Remove one member, including oneself, unless they are the last member."""

    try:
        with connect_database(request.app.state.settings) as connection:
            remove_member(
                connection, meter_id, meter_access_scope(authenticated), user_id
            )
    except (MeterNotFoundError, MemberNotFoundError) as error:
        raise _not_found() from error
    except LastMemberError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def meter_access_scope(authenticated: AuthenticatedUser) -> int | None:
    """Return the repository member scope, or unrestricted access for an admin."""

    return None if authenticated.is_admin else authenticated.user.id


def _find(
    connection: Connection[Any], meter_id: UUID, access_user_id: int | None
) -> Meter:
    try:
        return get_meter(connection, meter_id, access_user_id)
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
