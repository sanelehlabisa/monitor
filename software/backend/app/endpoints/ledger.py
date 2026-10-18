"""Authenticated CRUD routes for manual balance and top-up entries."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.endpoints.auth import AuthenticatedUser, require_authenticated_user
from app.modules.balance_entries import (
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
from app.modules.forecasting import ForecastResult, run_forecast_model
from app.endpoints.meters import meter_access_scope
from app.modules.meters import MeterNotFoundError
from app.modules.top_up_entries import (
    TopUpEntry,
    TopUpEntryNotFoundError,
    create_top_up_entry,
    delete_top_up_entry,
    get_top_up_entry,
    list_top_up_entries,
    update_top_up_entry,
)

from app.schemas.ledger import (
    BalanceEntryRequest,
    BalanceEntryResponse,
    DashboardResponse,
    ForecastResponse,
    HistoryEntryResponse,
    TopUpEntryRequest,
    TopUpEntryResponse,
)

router = APIRouter(prefix="/api/meters/{meter_id}", tags=["manual ledger"])
T = TypeVar("T")


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard_show(
    meter_id: UUID,
    request: Request,
    authenticated: AuthenticatedUser = Depends(require_authenticated_user),
) -> DashboardResponse:
    """Return current factual history and a newly calculated forecast."""

    access_scope = meter_access_scope(authenticated)
    with connect_database(request.app.state.settings) as connection:
        balances = _available(
            lambda: list_balance_entries(connection, meter_id, access_scope)
        )
        top_ups = _available(
            lambda: list_top_up_entries(connection, meter_id, access_scope)
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
                connection, meter_id, meter_access_scope(authenticated)
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
                    meter_access_scope(authenticated),
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
                connection, meter_id, entry_id, meter_access_scope(authenticated)
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
                    meter_access_scope(authenticated),
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
                connection, meter_id, entry_id, meter_access_scope(authenticated)
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
                connection, meter_id, meter_access_scope(authenticated)
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
                meter_access_scope(authenticated),
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
                connection, meter_id, entry_id, meter_access_scope(authenticated)
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
                meter_access_scope(authenticated),
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
                connection, meter_id, entry_id, meter_access_scope(authenticated)
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
