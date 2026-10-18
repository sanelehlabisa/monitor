"""PostgreSQL integration tests for actual remaining-balance entries."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import uuid4

from app.balance_entries import (
    BalanceEntryNotFoundError,
    BalanceTimeConflictError,
    create_balance_entry,
    delete_balance_entry,
    get_balance_entry,
    list_balance_entries,
    update_balance_entry,
)
from app.database import connect_database
from app.meters import MeterNotFoundError, create_meter
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


def test_balance_crud_ordering_conflicts_and_owner_scope() -> None:
    """Balances support correction while foreign users cannot reach the meter."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, owner_email = _create_user(connection, "balance-owner")
        other_id, other_email = _create_user(connection, "balance-other")
        meter = create_meter(connection, owner_id, "Home")
        first_time = datetime(2026, 10, 1, 8, tzinfo=UTC)
        try:
            first = create_balance_entry(
                connection, meter.id, owner_id, Decimal("42.125"), first_time
            )
            second = create_balance_entry(
                connection,
                meter.id,
                owner_id,
                Decimal("39.5000"),
                first_time + timedelta(days=1),
            )
            assert [item.id for item in list_balance_entries(connection, meter.id, owner_id)] == [
                second.id,
                first.id,
            ]
            with raises(BalanceTimeConflictError):
                create_balance_entry(
                    connection, meter.id, owner_id, Decimal("40"), first_time
                )
            with raises(MeterNotFoundError):
                list_balance_entries(connection, meter.id, other_id)

            corrected = update_balance_entry(
                connection,
                meter.id,
                first.id,
                owner_id,
                Decimal("41.250"),
                first_time + timedelta(hours=1),
            )
            assert corrected.balance_kwh == Decimal("41.250")
            assert get_balance_entry(connection, meter.id, corrected.id, None) == corrected
            delete_balance_entry(connection, meter.id, corrected.id, owner_id)
            with raises(BalanceEntryNotFoundError):
                get_balance_entry(connection, meter.id, corrected.id, owner_id)
        finally:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s)",
                (owner_email, other_email),
            )


def test_balance_values_and_database_constraints_are_strict() -> None:
    """Repository and schema reject negative, over-precise and invalid values."""

    settings = Settings()
    with connect_database(settings) as connection:
        owner_id, email = _create_user(connection, "balance-values")
        meter = create_meter(connection, owner_id, "Home")
        occurred_at = datetime(2026, 10, 2, 8, tzinfo=UTC)
        try:
            for value in (Decimal("-0.001"), Decimal("1.0001"), Decimal("1000000000")):
                with raises(ValueError):
                    create_balance_entry(
                        connection, meter.id, owner_id, value, occurred_at
                    )
            with raises(ValueError, match="timezone"):
                create_balance_entry(
                    connection,
                    meter.id,
                    owner_id,
                    Decimal("1"),
                    datetime(2026, 10, 2, 8),
                )
            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        """INSERT INTO monitor.balance_entries
                           (id, meter_id, balance_kwh, occurred_at)
                           VALUES (%s, %s, %s, %s)""",
                        (uuid4(), meter.id, Decimal("-1"), occurred_at),
                    )
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))
