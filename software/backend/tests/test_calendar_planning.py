"""Pure calendar planning and coherent API/message contract checks."""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from pytest import mark

from app.endpoints.ledger import _forecast_response
from app.modules.forecasting import run_forecast_model
from app.modules.reminder_deliveries import ReminderCandidate
from app.modules.reminder_runner import build_monthly_reminder_message
from tests.test_forecasting import _balance, _top_up


@mark.parametrize("year,month,planning_year,planning_month,days,extra", [
    (2027, 1, 2027, 2, 28, "120.000"),
    (2028, 1, 2028, 2, 29, "135.000"),
    (2026, 3, 2026, 4, 30, "150.000"),
    (2026, 4, 2026, 5, 31, "165.000"),
    (2026, 12, 2027, 1, 31, "165.000"),
])
def test_calendar_length_uses_current_balance_without_future_depletion(
    year: int, month: int, planning_year: int, planning_month: int, days: int, extra: str,
) -> None:
    """All month lengths subtract today's 300 kWh, not balance at the future 1st."""
    as_of = datetime(year, month, 15, 9, 17, 23, 123456, tzinfo=UTC)
    result = run_forecast_model(
        [_balance("450", as_of - timedelta(days=10)), _balance("300", as_of)], [], as_of,
    )
    assert result.planning_at == datetime(planning_year, planning_month, 1, tzinfo=UTC)
    assert result.planning_days == days
    assert result.recommended_monthly_top_up_kwh == Decimal(extra)
    assert result.daily_usage_kwh == Decimal("15.000000")
    assert result.estimated_balance_kwh == Decimal("300.000")
    assert result.remaining_days == Decimal("20.00")
    assert result.run_out_at == as_of + timedelta(days=20)
    assert result.as_of == as_of


@mark.parametrize("as_of,target,days", [
    (datetime(2026, 10, 1, tzinfo=UTC), datetime(2026, 11, 1, tzinfo=UTC), 30),
    (datetime(2026, 10, 31, 23, 59, 59, 999999, tzinfo=UTC), datetime(2026, 11, 1, tzinfo=UTC), 30),
    (datetime(2026, 11, 1, tzinfo=UTC), datetime(2026, 12, 1, tzinfo=UTC), 31),
    (datetime(2026, 11, 1, 23, 59, tzinfo=UTC), datetime(2026, 12, 1, tzinfo=UTC), 31),
])
def test_calendar_always_advances_on_the_first(as_of: datetime, target: datetime, days: int) -> None:
    """A date's exact UTC month determines planning, even without observations."""
    result = run_forecast_model([], [], as_of)
    assert result.planning_at == target
    assert result.planning_days == days
    assert result.status == "not_enough_data"
    assert result.recommended_monthly_top_up_kwh is None


@mark.parametrize("history,status", [
    ("empty", "not_enough_data"), ("one", "not_enough_data"),
    ("increase", "inconsistent_history"), ("duplicate", "inconsistent_history"),
    ("future", "inconsistent_history"),
])
def test_unavailable_estimates_keep_calendar_metadata(history: str, status: str) -> None:
    """Knowing a calendar date never invents a usage or kWh recommendation."""
    as_of = datetime(2027, 1, 20, 9, tzinfo=UTC)
    balances = {
        "empty": [], "one": [_balance("10", as_of)],
        "increase": [_balance("10", as_of - timedelta(days=1)), _balance("11", as_of)],
        "duplicate": [_balance("10", as_of), _balance("10", as_of)],
        "future": [_balance("10", as_of), _balance("9", as_of + timedelta(days=1))],
    }[history]
    result = run_forecast_model(balances, [], as_of)
    assert result.status == status
    assert result.planning_at == datetime(2027, 2, 1, tzinfo=UTC)
    assert result.planning_days == 28
    assert result.daily_usage_kwh is None
    assert result.recommended_monthly_top_up_kwh is None


def test_exact_instants_and_timezone_equivalence_preserve_current_estimates() -> None:
    """Local November 1 is still October in UTC; elapsed microseconds stay exact."""
    as_of = datetime(2026, 10, 31, 23, 30, 0, 123456, tzinfo=UTC)
    latest = as_of - timedelta(hours=6)
    balances = [_balance("450", latest - timedelta(days=10)), _balance("300", latest)]
    top_ups = [_top_up("5", latest + timedelta(hours=1))]
    result = run_forecast_model(balances, top_ups, as_of)
    equivalent = run_forecast_model(balances, top_ups, as_of.astimezone(timezone(timedelta(hours=2))))
    assert result == equivalent
    assert result.planning_at == datetime(2026, 11, 1, tzinfo=UTC)
    assert result.planning_days == 30
    assert result.estimated_balance_kwh == Decimal("301.250")
    assert result.recommended_monthly_top_up_kwh == Decimal("148.750")
    assert result.run_out_at == as_of + timedelta(seconds=float(Decimal("301.250") / 15 * 86400))


def test_monthly_rounding_zero_usage_and_sufficient_balance() -> None:
    """Existing rate/energy precision, genuine zero use and zero-extra clamps remain."""
    as_of = datetime(2027, 1, 20, 9, tzinfo=UTC)
    rounded = run_forecast_model(
        [_balance("2.111", as_of - timedelta(days=1.5)), _balance("1.111", as_of)], [], as_of,
    )
    assert rounded.daily_usage_kwh == Decimal("0.666667")
    assert rounded.recommended_monthly_top_up_kwh == Decimal("17.556")
    for previous in ("1000", "1015"):
        result = run_forecast_model(
            [_balance(previous, as_of - timedelta(days=1)), _balance("1000", as_of)], [], as_of,
        )
        assert result.recommended_monthly_top_up_kwh == Decimal("0.000")
        if previous == "1000":
            assert result.remaining_days is result.run_out_at is None
        assert result.planning_days == 28


def test_api_and_monthly_message_share_target_and_amount() -> None:
    """The renamed response and unsent message use one result, not parallel math."""
    as_of = datetime(2027, 1, 31, 9, tzinfo=UTC)
    forecast = run_forecast_model(
        [_balance("450", as_of - timedelta(days=10)), _balance("300", as_of)], [], as_of,
    )
    response = _forecast_response(forecast)
    assert response.model_dump() == forecast.__dict__
    assert "recommended_top_up_30_days_kwh" not in response.model_dump()
    candidate = ReminderCandidate(uuid4(), "Synthetic home", 1, "calendar@example.test", True, 1, False, Decimal("3"), "UTC")
    body = build_monthly_reminder_message(candidate, forecast, "no-reply@example.test").get_content()
    assert f"{response.recommended_monthly_top_up_kwh} additional kWh" in body
    assert "28-day calendar month" in body
    assert "Planning date: 2027-02-01 UTC." in body
    assert "current estimated balance" in body
    assert "next 30 days" not in body
