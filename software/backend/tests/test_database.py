"""Integration tests for direct SQL connectivity and migrations."""

from pathlib import Path

from app.database import connect_database, database_is_available
from app.migrations import run_migrations
from app.settings import Settings

MIGRATIONS_DIRECTORY = Path("/migrations")


def test_database_connectivity() -> None:
    """The backend can execute SQL against the development database."""

    assert database_is_available(Settings())


def test_migrations_are_recorded_once() -> None:
    """Running migrations repeatedly does not reapply committed SQL files."""

    settings = Settings()
    run_migrations(settings, MIGRATIONS_DIRECTORY)
    assert run_migrations(settings, MIGRATIONS_DIRECTORY) == 0

    with connect_database(settings) as connection:
        result = connection.execute(
            """SELECT version FROM schema_migrations
               WHERE version IN (%s, %s) ORDER BY version""",
            ("001_baseline.sql", "002_users_and_otp_challenges.sql"),
        ).fetchall()

    assert result == [
        ("001_baseline.sql",),
        ("002_users_and_otp_challenges.sql",),
    ]
