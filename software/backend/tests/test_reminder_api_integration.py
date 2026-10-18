"""Live PostgreSQL authorization tests for reminder settings APIs."""

from typing import Literal
from uuid import uuid4

from app.endpoints.auth import COOKIE_NAME
from app.database import connect_database
from app.main import create_app
from app.modules.meters import create_meter
from app.modules.sessions import create_session
from app.settings import Settings
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


def test_reminder_settings_defaults_updates_validation_and_access() -> None:
    """Owners and admins manage preferences while foreign users receive 404."""

    suffix = uuid4().hex
    owner_email = f"reminder-api-owner-{suffix}@example.test"
    other_email = f"reminder-api-other-{suffix}@example.test"
    admin_email = f"reminder-api-admin-{suffix}@example.test"
    settings = Settings(environment="test")
    owner, owner_id = _client_for(settings, owner_email)
    other, _ = _client_for(settings, other_email)
    admin, _ = _client_for(settings, admin_email, "admin")
    with connect_database(settings) as connection:
        meter = create_meter(connection, owner_id, "Home")
    url = f"/api/meters/{meter.id}/reminders"
    payload = {
        "monthly_enabled": True,
        "monthly_day": 15,
        "low_balance_enabled": True,
        "low_balance_days": "2.50",
        "timezone": "Africa/Johannesburg",
    }

    try:
        assert TestClient(create_app(settings)).get(url).status_code == 401
        defaults = owner.get(url)
        assert defaults.status_code == 200
        assert defaults.json()["monthly_enabled"] is False
        assert defaults.json()["low_balance_enabled"] is False
        assert defaults.json()["created_at"] is None

        saved = owner.patch(url, json=payload)
        assert saved.status_code == 200
        assert saved.json()["monthly_day"] == 15
        assert saved.json()["low_balance_days"] == "2.50"
        assert saved.json()["timezone"] == "Africa/Johannesburg"
        assert saved.json()["created_at"] is not None

        assert other.get(url).status_code == 404
        assert other.patch(url, json=payload).status_code == 404
        assert admin.get(url).json()["monthly_enabled"] is True
        admin_update = admin.patch(
            url,
            json={**payload, "monthly_day": 20, "low_balance_enabled": False},
        )
        assert admin_update.status_code == 200
        assert admin_update.json()["monthly_day"] == 20
        assert admin_update.json()["low_balance_enabled"] is False

        invalid_payloads = (
            {**payload, "monthly_day": 29},
            {**payload, "low_balance_days": "0"},
            {**payload, "low_balance_days": "1.001"},
            {**payload, "timezone": "Not/A_Timezone"},
        )
        for invalid in invalid_payloads:
            assert owner.patch(url, json=invalid).status_code == 422
    finally:
        with connect_database(settings) as connection:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s, %s)",
                (owner_email, other_email, admin_email),
            )
