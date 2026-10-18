"""PostgreSQL integration tests for nickname-only meter profiles."""

from typing import Any
from uuid import uuid4

from app.database import connect_database
from app.modules.meters import (
    MeterNameConflictError,
    MeterNotFoundError,
    create_meter,
    delete_meter,
    get_meter,
    list_meters,
    rename_meter,
)
from app.settings import Settings
from psycopg import Connection
from psycopg.errors import CheckViolation
from pytest import raises
from tests.support import cleanup_users


def _create_user(connection: Connection[Any], prefix: str) -> tuple[int, str]:
    email = f"{prefix}-{uuid4().hex}@example.test"
    row = connection.execute(
        "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id", (email,)
    ).fetchone()
    assert row
    return row[0], email


def test_meter_crud_is_ordered_and_owner_scoped() -> None:
    """Owners see their meters while unrestricted lookups see all."""

    settings = Settings()
    with connect_database(settings) as connection:
        first_user, first_email = _create_user(connection, "meters-first")
        second_user, second_email = _create_user(connection, "meters-second")
        try:
            shop = create_meter(connection, first_user, " Shop ")
            home = create_meter(connection, first_user, "Home")
            other_home = create_meter(connection, second_user, "Home")

            assert [meter.name for meter in list_meters(connection, first_user)] == [
                "Home",
                "Shop",
            ]
            assert {meter.id for meter in list_meters(connection, None)} >= {
                shop.id,
                home.id,
                other_home.id,
            }
            assert [
                meter.id for meter in list_meters(connection, first_user, "HOME")
            ] == [home.id]
            assert [
                meter.id
                for meter in list_meters(connection, None, second_email[:18].upper())
            ] == [other_home.id]
            assert list_meters(connection, first_user, "%") == []
            assert get_meter(connection, other_home.id, None).owner_email == second_email
            with raises(MeterNotFoundError):
                get_meter(connection, other_home.id, first_user)

            renamed = rename_meter(connection, shop.id, first_user, "Workshop")
            assert renamed.name == "Workshop"
            with raises(MeterNotFoundError):
                rename_meter(connection, renamed.id, second_user, "Hidden")

            delete_meter(connection, home.id, first_user)
            with raises(MeterNotFoundError):
                get_meter(connection, home.id, first_user)
        finally:
            cleanup_users(connection, (first_email, second_email))


def test_meter_names_are_valid_and_unique_per_owner() -> None:
    """Names are trimmed, bounded, and case-insensitively unique per owner."""

    settings = Settings()
    with connect_database(settings) as connection:
        user_id, email = _create_user(connection, "meter-constraints")
        try:
            create_meter(connection, user_id, "Home")
            shop = create_meter(connection, user_id, "Shop")
            with raises(MeterNameConflictError):
                create_meter(connection, user_id, " home ")
            with raises(MeterNameConflictError):
                rename_meter(connection, shop.id, user_id, "HOME")
            with raises(ValueError):
                create_meter(connection, user_id, "  ")
            with raises(ValueError):
                create_meter(connection, user_id, "x" * 81)
            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        """INSERT INTO monitor.meters (id, user_id, name)
                           VALUES (%s, %s, %s)""",
                        (uuid4(), user_id, " invalid "),
                    )
        finally:
            cleanup_users(connection, (email,))
