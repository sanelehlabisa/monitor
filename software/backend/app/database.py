"""Direct PostgreSQL connection helpers for the Monitor API."""

import os
from typing import Any

from psycopg import Connection, connect


def connect_database(*, connect_timeout: int | None = None) -> Connection[Any]:
    """Open a PostgreSQL connection using the configured URL."""

    options = {} if connect_timeout is None else {"connect_timeout": connect_timeout}
    return connect(os.environ["MONITOR_DATABASE_URL"], **options)


def database_is_available() -> bool:
    """Check connectivity with a minimal SQL query."""

    with connect_database() as connection:
        return connection.execute("SELECT 1").fetchone() == (1,)
