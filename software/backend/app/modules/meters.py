"""Raw-SQL persistence and member-scoped access for software meters."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.errors import UniqueViolation

MAX_METER_NAME_LENGTH = 80
METER_COLUMNS = """meters.id, meters.user_id, users.email, meters.name,
                   meters.created_at, meters.updated_at"""
MEMBER_SCOPE = """EXISTS (SELECT 1 FROM monitor.user_meters AS access
                         WHERE access.meter_id = meters.id AND access.user_id = %s)"""


class MeterNotFoundError(Exception):
    """Raised when a meter is missing from the requested access scope."""


class MeterNameConflictError(Exception):
    """Raised when a creator already has a meter with the requested name."""


@dataclass(frozen=True)
class Meter:
    """A nickname-only meter with creator metadata, not ownership authority."""

    id: UUID
    user_id: int
    owner_email: str
    name: str
    created_at: datetime
    updated_at: datetime


def create_meter(connection: Connection[Any], user_id: int, name: str) -> Meter:
    """Create a meter and its creator membership in one transaction."""

    meter_id = uuid4()
    try:
        with connection.transaction():
            connection.execute(
                "INSERT INTO monitor.meters (id, user_id, name) VALUES (%s, %s, %s)",
                (meter_id, user_id, normalize_meter_name(name)),
            )
            connection.execute(
                "INSERT INTO monitor.user_meters (user_id, meter_id) VALUES (%s, %s)",
                (user_id, meter_id),
            )
            return get_meter(connection, meter_id, user_id)
    except UniqueViolation as error:
        raise MeterNameConflictError("Meter name is already in use") from error


def list_meters(
    connection: Connection[Any],
    access_user_id: int | None,
    query: str | None = None,
) -> list[Meter]:
    """List accessible meters, optionally matching a name or member email."""

    clauses: list[str] = []
    parameters: list[object] = []
    if access_user_id is not None:
        clauses.append(MEMBER_SCOPE)
        parameters.append(access_user_id)
    keyword = query.strip() if query else ""
    if keyword:
        clauses.append(
            "(STRPOS(LOWER(meters.name), LOWER(%s)) > 0 "
            "OR EXISTS (SELECT 1 FROM monitor.user_meters AS members "
            "JOIN monitor.users AS member ON member.id = members.user_id "
            "WHERE members.meter_id = meters.id "
            "AND STRPOS(LOWER(member.email), LOWER(%s)) > 0))"
        )
        parameters.extend((keyword, keyword))
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = connection.execute(
        f"""SELECT {METER_COLUMNS}
            FROM monitor.meters AS meters
            JOIN monitor.users AS users ON users.id = meters.user_id
            {where}
            ORDER BY LOWER(meters.name), meters.created_at, meters.id""",
        tuple(parameters),
    ).fetchall()
    return [Meter(*row) for row in rows]


def get_meter(
    connection: Connection[Any], meter_id: UUID, access_user_id: int | None
) -> Meter:
    """Retrieve a meter for a member, or unrestricted for an admin."""

    access_clause = "" if access_user_id is None else f"AND {MEMBER_SCOPE}"
    parameters = (meter_id,) if access_user_id is None else (meter_id, access_user_id)
    row = connection.execute(
        f"""SELECT {METER_COLUMNS}
            FROM monitor.meters AS meters
            JOIN monitor.users AS users ON users.id = meters.user_id
            WHERE meters.id = %s {access_clause}""",
        parameters,
    ).fetchone()
    if not row:
        raise MeterNotFoundError("Meter is unavailable")
    return Meter(*row)


def lock_meter_access(
    connection: Connection[Any], meter_id: UUID, access_user_id: int | None
) -> Meter:
    """Lock the parent, then recheck current access in the caller's transaction."""

    row = connection.execute(
        "SELECT id FROM monitor.meters WHERE id = %s FOR UPDATE", (meter_id,)
    ).fetchone()
    if not row:
        raise MeterNotFoundError("Meter is unavailable")
    # A separate statement sees membership changes committed while awaiting the lock.
    return get_meter(connection, meter_id, access_user_id)


def rename_meter(
    connection: Connection[Any],
    meter_id: UUID,
    access_user_id: int | None,
    name: str,
) -> Meter:
    """Rename an accessible meter without treating creator metadata as access."""

    try:
        with connection.transaction():
            lock_meter_access(connection, meter_id, access_user_id)
            connection.execute(
                """UPDATE monitor.meters
                    SET name = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s""",
                (normalize_meter_name(name), meter_id),
            )
            return get_meter(connection, meter_id, access_user_id)
    except UniqueViolation as error:
        raise MeterNameConflictError("Meter name is already in use") from error


def delete_meter(
    connection: Connection[Any], meter_id: UUID, access_user_id: int | None
) -> None:
    """Permanently delete a meter and its history for any member or admin."""

    with connection.transaction():
        lock_meter_access(connection, meter_id, access_user_id)
        connection.execute("DELETE FROM monitor.meters WHERE id = %s", (meter_id,))


def normalize_meter_name(name: str) -> str:
    """Trim a display name and enforce its small V1 storage contract."""

    normalized = name.strip()
    if not normalized or len(normalized) > MAX_METER_NAME_LENGTH:
        raise ValueError("Meter name must contain between 1 and 80 characters")
    return normalized
