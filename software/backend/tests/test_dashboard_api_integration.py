"""Live PostgreSQL tests for the authorised meter dashboard API."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from app.endpoints.auth import COOKIE_NAME
from app.database import connect_database
from app.main import create_app
from app.modules.meters import create_meter
from app.modules.sessions import create_session
from fastapi.testclient import TestClient
from tests.support import cleanup_users


def _client_for(
    email: str, user_type: Literal["user", "admin"] = "user"
) -> tuple[TestClient, int]:
    with connect_database() as connection:
        row = connection.execute(
            "INSERT INTO monitor.users (email, type) VALUES (%s, %s) RETURNING id",
            (email, user_type),
        ).fetchone()
        assert row
        session = create_session(connection, row[0])
    client = TestClient(create_app())
    client.cookies.set(COOKIE_NAME, session.token)
    return client, row[0]


def test_dashboard_states_history_corrections_and_access() -> None:
    """Dashboard derives fresh forecasts within established meter scope."""

    suffix = uuid4().hex
    owner_email = f"dashboard-owner-{suffix}@example.test"
    other_email = f"dashboard-other-{suffix}@example.test"
    admin_email = f"dashboard-admin-{suffix}@example.test"
    owner, owner_id = _client_for(owner_email)
    other, _ = _client_for(other_email)
    admin, _ = _client_for(admin_email, "admin")
    with connect_database() as connection:
        meter = create_meter(connection, owner_id, "Home")
        separate_meter = create_meter(connection, owner_id, "Separate home")
    url = f"/api/meters/{meter.id}/dashboard"
    ledger_url = f"/api/meters/{meter.id}"
    separate_url = f"/api/meters/{separate_meter.id}"
    start = datetime.now(UTC) - timedelta(days=4)

    try:
        assert TestClient(create_app()).get(url).status_code == 401
        empty = owner.get(url)
        assert empty.status_code == 200
        assert empty.json()["forecast"]["status"] == "not_enough_data"
        assert empty.json()["history"] == []

        first_response = owner.post(f"{ledger_url}/balances", json={
            "balance_kwh": "50", "occurred_at": start.isoformat(),
        })
        assert first_response.status_code == 201
        first = first_response.json()
        initial = owner.get(url).json()["forecast"]
        assert initial["status"] == "available"
        assert initial["daily_usage_kwh"] == "10.000000"
        assert initial["intervals_used"] == 0
        assert Decimal(initial["monthly_requirement_kwh"]) == Decimal(10 * initial["planning_days"])
        assert Decimal("9") < Decimal(initial["estimated_balance_kwh"]) <= Decimal("10")

        assert owner.post(f"{separate_url}/balances", json={
            "balance_kwh": "80", "occurred_at": start.isoformat(),
        }).status_code == 201
        top_up_response = owner.post(f"{ledger_url}/top-ups", json={
            "top_up_kwh": "10", "occurred_at": (start + timedelta(days=1)).isoformat(),
        })
        assert top_up_response.status_code == 201
        top_up = top_up_response.json()
        after_purchase = owner.get(url).json()["forecast"]
        assert after_purchase["daily_usage_kwh"] == "10.000000"
        assert Decimal(after_purchase["estimated_balance_kwh"]) > Decimal(initial["estimated_balance_kwh"])
        assert after_purchase["monthly_requirement_kwh"] == initial["monthly_requirement_kwh"]
        second_response = owner.post(f"{ledger_url}/balances", json={
            "balance_kwh": "50", "occurred_at": (start + timedelta(days=2)).isoformat(),
        })
        assert second_response.status_code == 201
        second = second_response.json()

        available = owner.get(url).json()
        assert available["forecast"]["status"] == "available"
        assert available["forecast"]["daily_usage_kwh"] == "5.000000"
        assert available["forecast"]["intervals_used"] == 1
        separate = owner.get(f"{separate_url}/dashboard").json()["forecast"]
        assert separate["daily_usage_kwh"] == "10.000000"
        assert separate["intervals_used"] == 0
        forecast = available["forecast"]
        planning_at = datetime.fromisoformat(forecast["planning_at"])
        assert planning_at.day == 1 and planning_at.hour == planning_at.minute == planning_at.second == 0
        assert forecast["planning_days"] in (28, 29, 30, 31)
        assert "recommended_top_up_30_days_kwh" not in forecast
        expected_extra = max(Decimal("0"), Decimal(forecast["daily_usage_kwh"]) * forecast["planning_days"]
            - Decimal(forecast["estimated_balance_kwh"])).quantize(Decimal("0.001"))
        assert Decimal(forecast["recommended_monthly_top_up_kwh"]) == expected_extra
        assert Decimal(forecast["monthly_requirement_kwh"]) == Decimal(5 * forecast["planning_days"])
        assert available["latest_actual_balance"]["id"] == second["id"]
        assert [item["kind"] for item in available["history"]] == [
            "balance",
            "top_up",
            "balance",
        ]
        assert other.get(url).status_code == 404
        assert admin.get(url).status_code == 200

        assert owner.patch(f"{ledger_url}/balances/{second['id']}", json={
            "balance_kwh": "70", "occurred_at": second["occurred_at"],
        }).status_code == 200
        assert owner.get(url).json()["forecast"]["status"] == "inconsistent_history"

        assert owner.patch(f"{ledger_url}/balances/{second['id']}", json={
            "balance_kwh": "50", "occurred_at": second["occurred_at"],
        }).status_code == 200
        corrected = owner.get(url).json()
        assert corrected["forecast"]["status"] == "available"
        assert corrected["top_ups"][0]["id"] == top_up["id"]
        assert corrected["balances"][-1]["id"] == first["id"]

        assert owner.delete(f"{ledger_url}/balances/{second['id']}").status_code == 204
        reverted = owner.get(url).json()["forecast"]
        assert reverted["daily_usage_kwh"] == "10.000000"
        assert reverted["intervals_used"] == 0
        assert owner.delete(f"{ledger_url}/top-ups/{top_up['id']}").status_code == 204
        without_purchase = owner.get(url).json()["forecast"]
        assert Decimal(without_purchase["estimated_balance_kwh"]) < Decimal(reverted["estimated_balance_kwh"])
        assert owner.patch(f"{ledger_url}/balances/{first['id']}", json={
            "balance_kwh": "60", "occurred_at": (start + timedelta(days=1)).isoformat(),
        }).status_code == 200
        edited = owner.get(url).json()["forecast"]
        assert edited["latest_actual_balance_kwh"] == "60.000"
        assert Decimal(edited["estimated_balance_kwh"]) > Decimal(without_purchase["estimated_balance_kwh"])
        assert owner.delete(f"{ledger_url}/balances/{first['id']}").status_code == 204
        emptied = owner.get(url).json()["forecast"]
        assert emptied["status"] == "not_enough_data"
        assert emptied["daily_usage_kwh"] is None
        assert emptied["estimated_balance_kwh"] is None
        assert emptied["monthly_requirement_kwh"] is None
        assert owner.get(f"{separate_url}/dashboard").json()["forecast"]["daily_usage_kwh"] == "10.000000"
    finally:
        with connect_database() as connection:
            cleanup_users(connection, (owner_email, other_email, admin_email))
