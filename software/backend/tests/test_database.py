"""Integration checks against an isolated, freshly bootstrapped database."""

from uuid import uuid4

from app.database import connect_database, database_is_available
from app.settings import Settings
from psycopg.errors import (
    CheckViolation,
    ForeignKeyViolation,
    NotNullViolation,
    UniqueViolation,
)
from pytest import raises

SEED_OWNER = "monitor-seed@example.test"


def test_database_connectivity() -> None:
    """The backend can execute SQL against its explicit isolated test target."""

    assert database_is_available(Settings())


def test_fresh_schema_has_domain_tables_without_fake_migration_history() -> None:
    """Empty-volume initialization supplies nine tables, not applied markers."""

    with connect_database(Settings()) as connection:
        tables = connection.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'monitor'"
        ).fetchall()
        history = connection.execute(
            "SELECT to_regclass('monitor.schema_migrations'), "
            "to_regclass('public.schema_migrations')"
        ).fetchone()

    assert {row[0] for row in tables} == {
        "users", "otp_challenges", "user_sessions", "meters", "user_meters",
        "balance_entries", "top_up_entries", "reminder_settings", "reminder_deliveries",
    }
    assert history == (None, None)


def test_fresh_seeds_have_stored_types_and_owner_memberships() -> None:
    """Seeded DB types prepare later work; they do not change runtime authority."""

    with connect_database(Settings()) as connection:
        users = connection.execute(
            "SELECT email, type FROM monitor.users WHERE email IN (%s, %s) ORDER BY email",
            ("hlabisasanele730@gmail.com", SEED_OWNER),
        ).fetchall()
        meters = connection.execute(
            """SELECT meters.name, members.user_id = meters.user_id
               FROM monitor.meters AS meters
               JOIN monitor.users AS users ON users.id = meters.user_id
               LEFT JOIN monitor.user_meters AS members
                 ON members.meter_id = meters.id AND members.user_id = meters.user_id
               WHERE users.email = %s ORDER BY meters.name""",
            (SEED_OWNER,),
        ).fetchall()

    assert users == [("hlabisasanele730@gmail.com", "admin"), (SEED_OWNER, "user")]
    assert meters == [("Seed home", True), ("Seed shop", True)]


def test_user_type_defaults_and_constraints() -> None:
    """New users default to user, and invalid or absent stored types fail."""

    with connect_database(Settings()) as connection:
        try:
            user = connection.execute(
                "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id, type",
                (f"bootstrap-type-{uuid4().hex}@example.test",),
            ).fetchone()
            assert user is not None and user[1] == "user"
            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        "UPDATE monitor.users SET type = 'owner' WHERE id = %s", (user[0],)
                    )
            with raises(NotNullViolation):
                with connection.transaction():
                    connection.execute(
                        "UPDATE monitor.users SET type = NULL WHERE id = %s", (user[0],)
                    )
        finally:
            connection.rollback()


def test_membership_keys_and_cascading_foreign_keys() -> None:
    """Membership rejects duplicates/missing meters and follows both FK deletes."""

    with connect_database(Settings()) as connection:
        try:
            user = connection.execute(
                "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id",
                (f"bootstrap-member-{uuid4().hex}@example.test",),
            ).fetchone()
            assert user is not None
            meter_id = uuid4()
            connection.execute(
                "INSERT INTO monitor.meters (id, user_id, name) VALUES (%s, %s, %s)",
                (meter_id, user[0], "Membership fixture"),
            )
            insert = "INSERT INTO monitor.user_meters (user_id, meter_id) VALUES (%s, %s)"
            connection.execute(insert, (user[0], meter_id))
            with raises(UniqueViolation):
                with connection.transaction():
                    connection.execute(insert, (user[0], meter_id))
            with raises(ForeignKeyViolation):
                with connection.transaction():
                    connection.execute(insert, (user[0], uuid4()))
            connection.execute("DELETE FROM monitor.meters WHERE id = %s", (meter_id,))
            assert connection.execute(
                "SELECT 1 FROM monitor.user_meters WHERE meter_id = %s", (meter_id,)
            ).fetchone() is None
            seed_meter = connection.execute(
                """SELECT meters.id FROM monitor.meters AS meters
                   JOIN monitor.users AS users ON users.id = meters.user_id
                   WHERE users.email = %s ORDER BY meters.name LIMIT 1""", (SEED_OWNER,)
            ).fetchone()
            assert seed_meter is not None
            connection.execute(insert, (user[0], seed_meter[0]))
            connection.execute("DELETE FROM monitor.users WHERE id = %s", (user[0],))
            assert connection.execute(
                "SELECT 1 FROM monitor.user_meters WHERE user_id = %s", (user[0],)
            ).fetchone() is None
        finally:
            connection.rollback()
