"""Direct PostgreSQL connection helpers for the Monitor API."""

from typing import Any

from psycopg import Connection, connect

from app.settings import Settings


def connect_database(settings: Settings) -> Connection[Any]:
    """Open a PostgreSQL connection using the configured URL."""

    return connect(settings.database_url)


def database_is_available(settings: Settings) -> bool:
    """Check connectivity with a minimal SQL query."""

    with connect_database(settings) as connection:
        return connection.execute("SELECT 1").fetchone() == (1,)
