"""Pure tests for the replaceable deterministic forecast model."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from app.modules.balance_entries import BalanceEntry
from app.modules.forecasting import run_forecast_model
from app.modules.top_up_entries import TopUpEntry

START = datetime(2026, 10, 1, 8, tzinfo=UTC)


def _balance(kwh: str, occurred_at: datetime) -> BalanceEntry:
    return BalanceEntry(
        uuid4(), uuid4(), Decimal(kwh), occurred_at, occurred_at, occurred_at
    )


def _top_up(kwh: str, occurred_at: datetime) -> TopUpEntry:
    return TopUpEntry(
        uuid4(), uuid4(), Decimal(kwh), occurred_at, occurred_at, occurred_at
    )


def test_forecast_requires_two_actual_balances() -> None:
    """No rate is invented without a complete observation interval."""

    result = run_forecast_model([_balance("20", START)], [], START)

    assert result.status == "not_enough_data"
    assert result.daily_usage_kwh is None
    assert result.intervals_used == 0


def test_forecast_uses_top_ups_and_time_weighted_intervals() -> None:
    """Unordered facts produce one rate weighted by each interval duration."""

    balances = [
        _balance("38", START + timedelta(days=3)),
        _balance("50", START),
        _balance("42", START + timedelta(days=1)),
    ]
    top_ups = [
        _top_up("10", START + timedelta(days=2)),
        _top_up("99", START - timedelta(minutes=1)),
        _top_up("99", START + timedelta(days=4)),
    ]

    result = run_forecast_model(balances, top_ups, START + timedelta(days=3))

    assert result.status == "available"
    assert result.daily_usage_kwh == Decimal("7.333333")
    assert result.intervals_used == 2


def test_forecast_accepts_zero_usage() -> None:
    """An unchanged balance is valid evidence of a zero daily-use rate."""

    result = run_forecast_model(
        [_balance("10", START), _balance("10", START + timedelta(days=2))],
        [],
        START + timedelta(days=3),
    )

    assert result.status == "available"
    assert result.daily_usage_kwh == Decimal("0.000000")
    assert result.estimated_balance_kwh == Decimal("10.000")
    assert result.remaining_days is None
    assert result.run_out_at is None
    assert result.recommended_top_up_30_days_kwh == Decimal("0.000")


def test_forecast_surfaces_negative_consumption() -> None:
    """An unexplained balance increase invalidates the complete forecast."""

    result = run_forecast_model(
        [_balance("10", START), _balance("11", START + timedelta(days=1))],
        [],
        START + timedelta(days=1),
    )

    assert result.status == "inconsistent_history"
    assert result.daily_usage_kwh is None


def test_forecast_projects_balance_run_out_and_recommendation() -> None:
    """Later top-ups affect current balance without changing observed usage."""

    balances = [
        _balance("50", START),
        _balance("40", START + timedelta(days=2)),
    ]
    top_ups = [
        _top_up("5", START + timedelta(days=3)),
        _top_up("99", START + timedelta(days=5)),
    ]

    result = run_forecast_model(
        balances,
        top_ups,
        START + timedelta(days=4),
    )

    assert result.daily_usage_kwh == Decimal("5.000000")
    assert result.estimated_balance_kwh == Decimal("35.000")
    assert result.remaining_days == Decimal("7.00")
    assert result.run_out_at == START + timedelta(days=11)
    assert result.recommended_top_up_30_days_kwh == Decimal("115.000")


def test_forecast_clamps_an_exhausted_balance() -> None:
    """A projected exhausted meter never reports negative energy or days."""

    result = run_forecast_model(
        [_balance("10", START), _balance("5", START + timedelta(days=1))],
        [],
        START + timedelta(days=3),
    )

    assert result.estimated_balance_kwh == Decimal("0.000")
    assert result.remaining_days == Decimal("0.00")
    assert result.run_out_at == START + timedelta(days=3)
    assert result.recommended_top_up_30_days_kwh == Decimal("150.000")


def test_forecast_requires_an_aware_as_of_after_latest_actual() -> None:
    """The model rejects ambiguous or backward projection times."""

    balances = [_balance("10", START), _balance("9", START + timedelta(days=1))]

    try:
        run_forecast_model(balances, [], datetime(2026, 10, 2, 8))
    except ValueError as error:
        assert "timezone" in str(error)
    else:
        raise AssertionError("Naive as_of should fail")

    result = run_forecast_model(balances, [], START)
    assert result.status == "inconsistent_history"


def test_forecast_normalizes_equivalent_time_zones() -> None:
    """Equivalent aware calculation times produce the same UTC projection."""

    balances = [_balance("10", START), _balance("8", START + timedelta(days=1))]
    local_as_of = datetime(
        2026,
        10,
        3,
        10,
        tzinfo=timezone(timedelta(hours=2)),
    )

    result = run_forecast_model(balances, [], local_as_of)

    assert result.as_of == START + timedelta(days=2)
    assert result.estimated_balance_kwh == Decimal("6.000")
