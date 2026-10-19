"""Replaceable deterministic forecasting boundary for meter ledger history."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal, Sequence

from app.modules.balance_entries import BalanceEntry
from app.modules.top_up_entries import TopUpEntry

ForecastStatus = Literal[
    "available",
    "not_enough_data",
    "inconsistent_history",
]
RATE_QUANTUM = Decimal("0.000001")
ENERGY_QUANTUM = Decimal("0.001")
DAYS_QUANTUM = Decimal("0.01")
SECONDS_PER_DAY = Decimal("86400")


@dataclass(frozen=True)
class ForecastResult:
    """Current output contract of the replaceable forecast model."""

    status: ForecastStatus
    as_of: datetime
    planning_at: datetime
    planning_days: int
    latest_actual_balance_kwh: Decimal | None
    latest_actual_at: datetime | None
    daily_usage_kwh: Decimal | None
    estimated_balance_kwh: Decimal | None
    remaining_days: Decimal | None
    run_out_at: datetime | None
    recommended_monthly_top_up_kwh: Decimal | None
    intervals_used: int


def _elapsed_days(duration: timedelta) -> Decimal:
    """Convert a timedelta to exact decimal days without float arithmetic."""

    microseconds = (
        (duration.days * 86_400 + duration.seconds) * 1_000_000
        + duration.microseconds
    )
    return Decimal(microseconds) / Decimal("86400000000")


def _unavailable_result(
    status: ForecastStatus,
    as_of: datetime,
    latest: BalanceEntry | None,
) -> ForecastResult:
    """Build a forecast state that intentionally contains no estimates."""

    planning_at, planning_days = _planning_period(as_of)
    return ForecastResult(
        status=status,
        as_of=as_of,
        planning_at=planning_at,
        planning_days=planning_days,
        latest_actual_balance_kwh=latest.balance_kwh if latest else None,
        latest_actual_at=latest.occurred_at if latest else None,
        daily_usage_kwh=None,
        estimated_balance_kwh=None,
        remaining_days=None,
        run_out_at=None,
        recommended_monthly_top_up_kwh=None,
        intervals_used=0,
    )


def _planning_period(as_of: datetime) -> tuple[datetime, int]:
    """Return the strictly-next UTC month start and its full datetime duration."""

    month_start = as_of.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    planning_at = (month_start + timedelta(days=32)).replace(day=1)
    following_start = (planning_at + timedelta(days=32)).replace(day=1)
    return planning_at, (following_start - planning_at).days


def run_forecast_model(
    balances: Sequence[BalanceEntry],
    top_ups: Sequence[TopUpEntry],
    as_of: datetime,
) -> ForecastResult:
    """Calculate V1 planning estimates from factual ledger entries."""

    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("Forecast time must include a timezone")
    as_of = as_of.astimezone(UTC)

    ordered_balances = sorted(balances, key=lambda item: (item.occurred_at, item.id))
    latest = ordered_balances[-1] if ordered_balances else None
    if len(ordered_balances) < 2:
        return _unavailable_result("not_enough_data", as_of, latest)
    if latest and latest.occurred_at > as_of:
        return _unavailable_result("inconsistent_history", as_of, latest)

    total_consumption = Decimal("0")
    total_days = Decimal("0")
    for previous, current in zip(ordered_balances, ordered_balances[1:]):
        elapsed_days = _elapsed_days(current.occurred_at - previous.occurred_at)
        if elapsed_days <= 0:
            return _unavailable_result("inconsistent_history", as_of, latest)
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
            return _unavailable_result("inconsistent_history", as_of, latest)
        total_consumption += consumption
        total_days += elapsed_days

    daily_usage = (total_consumption / total_days).quantize(
        RATE_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    assert latest
    later_top_ups = sum(
        (
            item.top_up_kwh
            for item in top_ups
            if latest.occurred_at < item.occurred_at <= as_of
        ),
        start=Decimal("0"),
    )
    elapsed_since_latest = _elapsed_days(as_of - latest.occurred_at)
    raw_balance = (
        latest.balance_kwh + later_top_ups - daily_usage * elapsed_since_latest
    )
    estimated_balance = max(Decimal("0"), raw_balance).quantize(
        ENERGY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )
    planning_at, planning_days = _planning_period(as_of)
    if daily_usage == 0:
        remaining_days = None
        run_out_at = None
        recommendation = Decimal("0.000")
    else:
        exact_remaining_days = estimated_balance / daily_usage
        remaining_days = exact_remaining_days.quantize(
            DAYS_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
        run_out_at = as_of + timedelta(
            seconds=float(exact_remaining_days * SECONDS_PER_DAY)
        )
        recommendation = max(
            Decimal("0"),
            daily_usage * planning_days - estimated_balance,
        ).quantize(ENERGY_QUANTUM, rounding=ROUND_HALF_UP)

    return ForecastResult(
        status="available",
        as_of=as_of,
        planning_at=planning_at,
        planning_days=planning_days,
        latest_actual_balance_kwh=latest.balance_kwh,
        latest_actual_at=latest.occurred_at,
        daily_usage_kwh=daily_usage,
        estimated_balance_kwh=estimated_balance,
        remaining_days=remaining_days,
        run_out_at=run_out_at,
        recommended_monthly_top_up_kwh=recommendation,
        intervals_used=len(ordered_balances) - 1,
    )
