"""PostgreSQL integration tests for per-meter reminder settings."""

from decimal import Decimal
from typing import Any
from uuid import uuid4

from app.database import connect_database
from app.modules.meters import MeterNotFoundError, create_meter, delete_meter
from app.modules.reminder_settings import get_reminder_settings, upsert_reminder_settings
from app.settings import Settings
from psycopg import Connection
from psycopg.errors import CheckViolation
from pytest import raises


def _create_user(connection: Connection[Any], prefix: str) -> tuple[int, str]:
    email = f"{prefix}-{uuid4().hex}@example.test"
    row = connection.execute(
        "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id", (email,)
    ).fetchone()
    assert row
    return row[0], email


def test_reminder_settings_defaults_upsert_scope_and_cascade() -> None:
    """Settings are opt-in, owner-scoped, admin-readable and meter-owned."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, owner_email = _create_user(connection, "reminder-owner")
        other_id, other_email = _create_user(connection, "reminder-other")
        meter = create_meter(connection, owner_id, "Home")
        try:
            defaults = get_reminder_settings(
                connection, meter.id, owner_id, "Africa/Johannesburg"
            )
            assert defaults.monthly_enabled is False
            assert defaults.monthly_day == 1
            assert defaults.low_balance_enabled is False
            assert defaults.low_balance_days == Decimal("3.00")
            assert defaults.timezone == "Africa/Johannesburg"
            assert defaults.created_at is None

            saved = upsert_reminder_settings(
                connection,
                meter.id,
                owner_id,
                monthly_enabled=True,
                monthly_day=15,
                low_balance_enabled=True,
                low_balance_days=Decimal("2.50"),
                timezone="Africa/Johannesburg",
            )
            assert saved.monthly_day == 15
            assert saved.low_balance_days == Decimal("2.50")
            assert get_reminder_settings(connection, meter.id, None) == saved
            with raises(MeterNotFoundError):
                get_reminder_settings(connection, meter.id, other_id)

            delete_meter(connection, meter.id, owner_id)
            count = connection.execute(
                "SELECT COUNT(*) FROM monitor.reminder_settings WHERE meter_id = %s",
                (meter.id,),
            ).fetchone()
            assert count == (0,)
        finally:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s)",
                (owner_email, other_email),
            )


def test_reminder_settings_validation_and_constraints() -> None:
    """Repository and schema reject unsafe days and timezone values."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, email = _create_user(connection, "reminder-values")
        meter = create_meter(connection, owner_id, "Home")
        values = {
            "monthly_enabled": True,
            "monthly_day": 1,
            "low_balance_enabled": True,
            "low_balance_days": Decimal("3"),
            "timezone": "UTC",
        }
        try:
            for field, invalid in (
                ("monthly_enabled", 1),
                ("monthly_day", 29),
                ("low_balance_days", Decimal("0")),
                ("low_balance_days", Decimal("1.001")),
                ("timezone", "Not/A_Timezone"),
            ):
                with raises(ValueError):
                    upsert_reminder_settings(
                        connection,
                        meter.id,
                        owner_id,
                        **{**values, field: invalid},
                    )
            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        """INSERT INTO monitor.reminder_settings
                           (meter_id, monthly_day, timezone)
                           VALUES (%s, 29, 'UTC')""",
                        (meter.id,),
                    )
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))
