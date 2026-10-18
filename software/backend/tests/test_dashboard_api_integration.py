"""Live PostgreSQL tests for the authorised meter dashboard API."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from app.endpoints.auth import COOKIE_NAME
from app.modules.balance_entries import create_balance_entry, update_balance_entry
from app.database import connect_database
from app.main import create_app
from app.modules.meters import create_meter
from app.modules.sessions import create_session
from app.settings import Settings
from app.modules.top_up_entries import create_top_up_entry
from fastapi.testclient import TestClient


def _client_for(
    settings: Settings, email: str, user_type: Literal["user", "admin"] = "user"
) -> tuple[TestClient, int]:
    with connect_database(settings) as connection:
        row = connection.execute(
            "INSERT INTO monitor.users (email, type) VALUES (%s, %s) RETURNING id",
            (email, user_type),
        ).fetchone()
        assert row
        session = create_session(connection, row[0])
    client = TestClient(create_app(settings))
    client.cookies.set(COOKIE_NAME, session.token)
    return client, row[0]


def test_dashboard_states_history_corrections_and_access() -> None:
    """Dashboard derives fresh forecasts within established meter scope."""

    suffix = uuid4().hex
    owner_email = f"dashboard-owner-{suffix}@example.test"
    other_email = f"dashboard-other-{suffix}@example.test"
    admin_email = f"dashboard-admin-{suffix}@example.test"
    settings = Settings(environment="test")
    owner, owner_id = _client_for(settings, owner_email)
    other, _ = _client_for(settings, other_email)
    admin, _ = _client_for(settings, admin_email, "admin")
    with connect_database(settings) as connection:
        meter = create_meter(connection, owner_id, "Home")
    url = f"/api/meters/{meter.id}/dashboard"
    start = datetime.now(UTC) - timedelta(days=4)

    try:
        assert TestClient(create_app(settings)).get(url).status_code == 401
        empty = owner.get(url)
        assert empty.status_code == 200
        assert empty.json()["forecast"]["status"] == "not_enough_data"
        assert empty.json()["history"] == []

        with connect_database(settings) as connection:
            first = create_balance_entry(
                connection, meter.id, owner_id, Decimal("50"), start
            )
            top_up = create_top_up_entry(
                connection,
                meter.id,
                owner_id,
                Decimal("10"),
                start + timedelta(days=1),
            )
            second = create_balance_entry(
                connection,
                meter.id,
                owner_id,
                Decimal("50"),
                start + timedelta(days=2),
            )

        available = owner.get(url).json()
        assert available["forecast"]["status"] == "available"
        assert available["forecast"]["daily_usage_kwh"] == "5.000000"
        assert available["latest_actual_balance"]["id"] == str(second.id)
        assert [item["kind"] for item in available["history"]] == [
            "balance",
            "top_up",
            "balance",
        ]
        assert other.get(url).status_code == 404
        assert admin.get(url).status_code == 200

        with connect_database(settings) as connection:
            update_balance_entry(
                connection,
                meter.id,
                second.id,
                owner_id,
                Decimal("70"),
                second.occurred_at,
            )
        assert owner.get(url).json()["forecast"]["status"] == "inconsistent_history"

        with connect_database(settings) as connection:
            update_balance_entry(
                connection,
                meter.id,
                second.id,
                owner_id,
                Decimal("50"),
                second.occurred_at,
            )
        corrected = owner.get(url).json()
        assert corrected["forecast"]["status"] == "available"
        assert corrected["top_ups"][0]["id"] == str(top_up.id)
        assert corrected["balances"][-1]["id"] == str(first.id)
    finally:
        with connect_database(settings) as connection:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s, %s)",
                (owner_email, other_email, admin_email),
            )
