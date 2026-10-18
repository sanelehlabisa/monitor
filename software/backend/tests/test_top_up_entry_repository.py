"""PostgreSQL integration tests for purchased-kWh top-up entries."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from app.database import connect_database
from app.meters import MeterNotFoundError, create_meter
from app.settings import Settings
from app.top_up_entries import (
    TopUpEntryNotFoundError,
    create_top_up_entry,
    delete_top_up_entry,
    get_top_up_entry,
    list_top_up_entries,
    update_top_up_entry,
)
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


def test_top_up_crud_allows_repeated_times_and_enforces_owner_scope() -> None:
    """Purchases can share a time while foreign users cannot reach the meter."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, owner_email = _create_user(connection, "top-up-owner")
        other_id, other_email = _create_user(connection, "top-up-other")
        meter = create_meter(connection, owner_id, "Home")
        occurred_at = datetime(2026, 10, 3, 8, tzinfo=UTC)
        try:
            first = create_top_up_entry(
                connection, meter.id, owner_id, Decimal("20.125"), occurred_at
            )
            second = create_top_up_entry(
                connection, meter.id, owner_id, Decimal("5.0000"), occurred_at
            )
            listed = list_top_up_entries(connection, meter.id, owner_id)
            assert {item.id for item in listed} == {first.id, second.id}
            with raises(MeterNotFoundError):
                list_top_up_entries(connection, meter.id, other_id)

            corrected = update_top_up_entry(
                connection,
                meter.id,
                first.id,
                owner_id,
                Decimal("21.500"),
                occurred_at + timedelta(hours=1),
            )
            assert corrected.top_up_kwh == Decimal("21.500")
            assert get_top_up_entry(connection, meter.id, corrected.id, None) == corrected
            delete_top_up_entry(connection, meter.id, corrected.id, owner_id)
            with raises(TopUpEntryNotFoundError):
                get_top_up_entry(connection, meter.id, corrected.id, owner_id)
        finally:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s)",
                (owner_email, other_email),
            )


def test_top_up_values_and_database_constraints_are_strict() -> None:
    """Repository and schema reject zero, negative and over-precise purchases."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, email = _create_user(connection, "top-up-values")
        meter = create_meter(connection, owner_id, "Home")
        occurred_at = datetime(2026, 10, 4, 8, tzinfo=UTC)
        try:
            for value in (Decimal("0"), Decimal("-1"), Decimal("1.0001")):
                with raises(ValueError):
                    create_top_up_entry(
                        connection, meter.id, owner_id, value, occurred_at
                    )
            with raises(ValueError, match="timezone"):
                create_top_up_entry(
                    connection,
                    meter.id,
                    owner_id,
                    Decimal("1"),
                    datetime(2026, 10, 4, 8),
                )
            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        """INSERT INTO monitor.top_up_entries
                           (id, meter_id, top_up_kwh, occurred_at)
                           VALUES (%s, %s, %s, %s)""",
                        (uuid4(), meter.id, Decimal("0"), occurred_at),
                    )
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))
