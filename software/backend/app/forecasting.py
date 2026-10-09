"""Replaceable deterministic forecasting boundary for meter ledger history."""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal, Sequence

from app.balance_entries import BalanceEntry
from app.top_up_entries import TopUpEntry

ForecastStatus = Literal[
    "available",
    "not_enough_data",
    "inconsistent_history",
]
RATE_QUANTUM = Decimal("0.000001")
SECONDS_PER_DAY = Decimal("86400")


@dataclass(frozen=True)
class ForecastResult:
    """Current output contract of the replaceable forecast model."""

    status: ForecastStatus
    daily_usage_kwh: Decimal | None
    intervals_used: int


def _elapsed_days(duration: timedelta) -> Decimal:
    """Convert a timedelta to exact decimal days without float arithmetic."""

    microseconds = (
        (duration.days * 86_400 + duration.seconds) * 1_000_000
        + duration.microseconds
    )
    return Decimal(microseconds) / Decimal("86400000000")


def run_forecast_model(
    balances: Sequence[BalanceEntry],
    top_ups: Sequence[TopUpEntry],
) -> ForecastResult:
    """Calculate a time-weighted daily-use rate from factual ledger entries."""

    ordered_balances = sorted(balances, key=lambda item: (item.occurred_at, item.id))
    if len(ordered_balances) < 2:
        return ForecastResult("not_enough_data", None, 0)

    total_consumption = Decimal("0")
    total_days = Decimal("0")
    for previous, current in zip(ordered_balances, ordered_balances[1:]):
        elapsed_days = _elapsed_days(current.occurred_at - previous.occurred_at)
        if elapsed_days <= 0:
            return ForecastResult("inconsistent_history", None, 0)
        interval_top_ups = sum(
            (
                item.top_up_kwh
                for item in top_ups
                if previous.occurred_at < item.occurred_at <= current.occurred_at
            ),
            start=Decimal("0"),
        )
        consumption = previous.balance_kwh + interval_top_ups - current.balance_kwh
        if consumption < 0:
            return ForecastResult("inconsistent_history", None, 0)
        total_consumption += consumption
        total_days += elapsed_days

    daily_usage = (total_consumption / total_days).quantize(
        RATE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    return ForecastResult("available", daily_usage, len(ordered_balances) - 1)
