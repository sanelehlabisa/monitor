"""Live PostgreSQL authorization tests for manual ledger APIs."""

from datetime import UTC, datetime, timedelta
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


def test_manual_ledger_crud_validation_and_access() -> None:
    """Owners manage their ledger while admins manage every accessible meter."""

    owner_email = f"ledger-owner-{uuid4().hex}@example.test"
    other_email = f"ledger-other-{uuid4().hex}@example.test"
    admin_email = f"ledger-admin-{uuid4().hex}@example.test"
    owner, owner_id = _client_for(owner_email)
    other, _ = _client_for(other_email)
    admin, _ = _client_for(admin_email, "admin")
    with connect_database() as connection:
        home = create_meter(connection, owner_id, "Home")
        garage = create_meter(connection, owner_id, "Garage")

    first_time = datetime.now(UTC) - timedelta(days=2)
    second_time = datetime.now(UTC) - timedelta(days=1)
    future_time = datetime.now(UTC) + timedelta(days=1)
    balances_url = f"/api/meters/{home.id}/balances"
    top_ups_url = f"/api/meters/{home.id}/top-ups"
    try:
        assert TestClient(create_app()).get(balances_url).status_code == 401
        first_balance = owner.post(
            balances_url,
            json={"balance_kwh": "42.125", "occurred_at": first_time.isoformat()},
        )
        second_balance = owner.post(
            balances_url,
            json={"balance_kwh": "40.000", "occurred_at": second_time.isoformat()},
        )
        duplicate = owner.post(
            balances_url,
            json={"balance_kwh": "39", "occurred_at": first_time.isoformat()},
        )
        assert first_balance.status_code == second_balance.status_code == 201
        assert duplicate.status_code == 409
        assert [item["id"] for item in owner.get(balances_url).json()] == [
            second_balance.json()["id"],
            first_balance.json()["id"],
        ]

        first_top_up = owner.post(
            top_ups_url,
            json={"top_up_kwh": "20.500", "occurred_at": first_time.isoformat()},
        )
        second_top_up = owner.post(
            top_ups_url,
            json={"top_up_kwh": "5", "occurred_at": first_time.isoformat()},
        )
        assert first_top_up.status_code == second_top_up.status_code == 201
        assert len(owner.get(top_ups_url).json()) == 2

        assert other.get(balances_url).status_code == 404
        assert other.patch(
            f"{balances_url}/{first_balance.json()['id']}",
            json={"balance_kwh": "1", "occurred_at": second_time.isoformat()},
        ).status_code == 404
        assert owner.get(
            f"/api/meters/{garage.id}/balances/{first_balance.json()['id']}"
        ).status_code == 404

        admin_balances = admin.get(balances_url)
        assert admin_balances.status_code == 200
        corrected = admin.patch(
            f"{balances_url}/{first_balance.json()['id']}",
            json={
                "balance_kwh": "41.250",
                "occurred_at": (first_time + timedelta(hours=1)).isoformat(),
            },
        )
        assert corrected.status_code == 200
        assert corrected.json()["balance_kwh"] == "41.250"
        assert admin.delete(
            f"{top_ups_url}/{first_top_up.json()['id']}"
        ).status_code == 204

        invalid_payloads = (
            (balances_url, {"balance_kwh": "-1", "occurred_at": first_time.isoformat()}),
            (top_ups_url, {"top_up_kwh": "0", "occurred_at": first_time.isoformat()}),
            (balances_url, {"balance_kwh": "1.0001", "occurred_at": first_time.isoformat()}),
            (balances_url, {"balance_kwh": "1", "occurred_at": future_time.isoformat()}),
            (balances_url, {"balance_kwh": "1", "occurred_at": "2026-10-01T08:00:00"}),
        )
        for url, payload in invalid_payloads:
            assert owner.post(url, json=payload).status_code == 422
    finally:
        with connect_database() as connection:
            cleanup_users(connection, (owner_email, other_email, admin_email))
