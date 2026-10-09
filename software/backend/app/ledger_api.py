"""Authenticated CRUD routes for manual balance and top-up entries."""

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator

from app.auth_api import AuthenticatedUser, require_authenticated_user
from app.balance_entries import (
    BalanceEntry,
    BalanceEntryNotFoundError,
    BalanceTimeConflictError,
    create_balance_entry,
    delete_balance_entry,
    get_balance_entry,
    list_balance_entries,
    update_balance_entry,
)
from app.database import connect_database
from app.forecasting import ForecastResult, run_forecast_model
from app.meter_api import meter_owner_scope
from app.meters import MeterNotFoundError
from app.top_up_entries import (
    TopUpEntry,
    TopUpEntryNotFoundError,
    create_top_up_entry,
    delete_top_up_entry,
    get_top_up_entry,
    list_top_up_entries,
    update_top_up_entry,
)

router = APIRouter(prefix="/api/meters/{meter_id}", tags=["manual ledger"])
T = TypeVar("T")


def _past_aware_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Occurrence time must include a timezone")
    normalized = value.astimezone(UTC)
    if normalized > datetime.now(UTC):
        raise ValueError("Occurrence time cannot be in the future")
    return normalized


class BalanceEntryRequest(BaseModel):
    """Validated actual remaining-balance input."""

    balance_kwh: Decimal = Field(ge=0, max_digits=12, decimal_places=3)
    occurred_at: datetime

    _validate_time = field_validator("occurred_at")(_past_aware_time)


class TopUpEntryRequest(BaseModel):
    """Validated purchased-energy input."""

    top_up_kwh: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    occurred_at: datetime

    _validate_time = field_validator("occurred_at")(_past_aware_time)


class BalanceEntryResponse(BaseModel):
    """One factual actual-balance record."""

    id: UUID
    meter_id: UUID
    balance_kwh: Decimal
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


class TopUpEntryResponse(BaseModel):
    """One factual purchased-energy record."""

    id: UUID
    meter_id: UUID
    top_up_kwh: Decimal
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


class HistoryEntryResponse(BaseModel):
    """One clearly labelled factual event in combined ledger history."""

    kind: Literal["balance", "top_up"]
    id: UUID
    kwh: Decimal
    occurred_at: datetime


class ForecastResponse(BaseModel):
    """Derived planning output from the replaceable forecast model."""

    status: Literal["available", "not_enough_data", "inconsistent_history"]
    as_of: datetime
    latest_actual_balance_kwh: Decimal | None
    latest_actual_at: datetime | None
    daily_usage_kwh: Decimal | None
    estimated_balance_kwh: Decimal | None
    remaining_days: Decimal | None
    run_out_at: datetime | None
    recommended_top_up_30_days_kwh: Decimal | None
    intervals_used: int


class DashboardResponse(BaseModel):
    """Factual ledger data and derived forecast for one accessible meter."""

    latest_actual_balance: BalanceEntryResponse | None
    balances: list[BalanceEntryResponse]
    top_ups: list[TopUpEntryResponse]
    history: list[HistoryEntryResponse]
    forecast: ForecastResponse


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard_show(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> DashboardResponse:
    """Return current factual history and a newly calculated forecast."""

    owner_scope = meter_owner_scope(authenticated)
    with connect_database(request.app.state.settings) as connection:
        balances = _available(
            lambda: list_balance_entries(connection, meter_id, owner_scope)
        )
        top_ups = _available(
            lambda: list_top_up_entries(connection, meter_id, owner_scope)
        )
    history = sorted(
        [
            *(
                HistoryEntryResponse(
                    kind="balance",
                    id=entry.id,
                    kwh=entry.balance_kwh,
                    occurred_at=entry.occurred_at,
                )
                for entry in balances
            ),
            *(
                HistoryEntryResponse(
                    kind="top_up",
                    id=entry.id,
                    kwh=entry.top_up_kwh,
                    occurred_at=entry.occurred_at,
                )
                for entry in top_ups
            ),
        ],
        key=lambda item: (item.occurred_at, str(item.id)),
        reverse=True,
    )
    forecast = run_forecast_model(balances, top_ups, datetime.now(UTC))
    return DashboardResponse(
        latest_actual_balance=_balance_response(balances[0]) if balances else None,
        balances=[_balance_response(entry) for entry in balances],
        top_ups=[_top_up_response(entry) for entry in top_ups],
        history=history,
        forecast=_forecast_response(forecast),
    )


@router.get("/balances", response_model=list[BalanceEntryResponse])
def balances_index(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> list[BalanceEntryResponse]:
    """List an accessible meter's actual balances newest-first."""

    with connect_database(request.app.state.settings) as connection:
        entries = _available(
            lambda: list_balance_entries(
                connection, meter_id, meter_owner_scope(authenticated)
            )
        )
    return [_balance_response(entry) for entry in entries]


@router.post(
    "/balances",
    response_model=BalanceEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def balances_create(
    meter_id: UUID,
    payload: BalanceEntryRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> BalanceEntryResponse:
    """Record one actual remaining balance."""

    try:
        with connect_database(request.app.state.settings) as connection:
            entry = _available(
                lambda: create_balance_entry(
                    connection,
                    meter_id,
                    meter_owner_scope(authenticated),
                    payload.balance_kwh,
                    payload.occurred_at,
                )
            )
    except BalanceTimeConflictError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    return _balance_response(entry)


@router.get("/balances/{entry_id}", response_model=BalanceEntryResponse)
def balances_show(
    meter_id: UUID,
    entry_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> BalanceEntryResponse:
    """Retrieve one accessible actual balance."""

    with connect_database(request.app.state.settings) as connection:
        entry = _available(
            lambda: get_balance_entry(
                connection, meter_id, entry_id, meter_owner_scope(authenticated)
            )
        )
    return _balance_response(entry)


@router.patch("/balances/{entry_id}", response_model=BalanceEntryResponse)
def balances_update(
    meter_id: UUID,
    entry_id: UUID,
    payload: BalanceEntryRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> BalanceEntryResponse:
    """Correct an accessible actual balance."""

    try:
        with connect_database(request.app.state.settings) as connection:
            entry = _available(
                lambda: update_balance_entry(
                    connection,
                    meter_id,
                    entry_id,
                    meter_owner_scope(authenticated),
                    payload.balance_kwh,
                    payload.occurred_at,
                )
            )
    except BalanceTimeConflictError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
    return _balance_response(entry)


@router.delete("/balances/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def balances_delete(
    meter_id: UUID,
    entry_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> Response:
    """Delete one accessible actual balance."""

    with connect_database(request.app.state.settings) as connection:
        _available(
            lambda: delete_balance_entry(
                connection, meter_id, entry_id, meter_owner_scope(authenticated)
            )
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/top-ups", response_model=list[TopUpEntryResponse])
def top_ups_index(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> list[TopUpEntryResponse]:
    """List an accessible meter's purchased-energy events newest-first."""

    with connect_database(request.app.state.settings) as connection:
        entries = _available(
            lambda: list_top_up_entries(
                connection, meter_id, meter_owner_scope(authenticated)
            )
        )
    return [_top_up_response(entry) for entry in entries]


@router.post(
    "/top-ups", response_model=TopUpEntryResponse, status_code=status.HTTP_201_CREATED
)
def top_ups_create(
    meter_id: UUID,
    payload: TopUpEntryRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> TopUpEntryResponse:
    """Record one purchased-energy event."""

    with connect_database(request.app.state.settings) as connection:
        entry = _available(
            lambda: create_top_up_entry(
                connection,
                meter_id,
                meter_owner_scope(authenticated),
                payload.top_up_kwh,
                payload.occurred_at,
            )
        )
    return _top_up_response(entry)


@router.get("/top-ups/{entry_id}", response_model=TopUpEntryResponse)
def top_ups_show(
    meter_id: UUID,
    entry_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> TopUpEntryResponse:
    """Retrieve one accessible purchased-energy event."""

    with connect_database(request.app.state.settings) as connection:
        entry = _available(
            lambda: get_top_up_entry(
                connection, meter_id, entry_id, meter_owner_scope(authenticated)
            )
        )
    return _top_up_response(entry)


@router.patch("/top-ups/{entry_id}", response_model=TopUpEntryResponse)
def top_ups_update(
    meter_id: UUID,
    entry_id: UUID,
    payload: TopUpEntryRequest,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> TopUpEntryResponse:
    """Correct an accessible purchased-energy event."""

    with connect_database(request.app.state.settings) as connection:
        entry = _available(
            lambda: update_top_up_entry(
                connection,
                meter_id,
                entry_id,
                meter_owner_scope(authenticated),
                payload.top_up_kwh,
                payload.occurred_at,
            )
        )
    return _top_up_response(entry)


@router.delete("/top-ups/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def top_ups_delete(
    meter_id: UUID,
    entry_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> Response:
    """Delete one accessible purchased-energy event."""

    with connect_database(request.app.state.settings) as connection:
        _available(
            lambda: delete_top_up_entry(
                connection, meter_id, entry_id, meter_owner_scope(authenticated)
            )
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _available(operation: Callable[[], T]) -> T:
    try:
        return operation()
    except (
        MeterNotFoundError,
        BalanceEntryNotFoundError,
        TopUpEntryNotFoundError,
    ) as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entry not found") from error


def _balance_response(entry: BalanceEntry) -> BalanceEntryResponse:
    return BalanceEntryResponse(**entry.__dict__)


def _top_up_response(entry: TopUpEntry) -> TopUpEntryResponse:
    return TopUpEntryResponse(**entry.__dict__)


def _forecast_response(result: ForecastResult) -> ForecastResponse:
    return ForecastResponse(**result.__dict__)
