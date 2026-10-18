"""Request and response validation for meter ledgers and forecasts."""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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
