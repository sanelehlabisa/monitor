"""Raw-SQL persistence for user-owned software meter profiles."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.errors import UniqueViolation

MAX_METER_NAME_LENGTH = 80
METER_COLUMNS = """meters.id, meters.user_id, users.email, meters.name,
                   meters.created_at, meters.updated_at"""


class MeterNotFoundError(Exception):
    """Raised when a meter is missing from the requested ownership scope."""


class MeterNameConflictError(Exception):
    """Raised when an owner already has a meter with the requested name."""


@dataclass(frozen=True)
class Meter:
    """A nickname-only meter profile and its owner identity."""

    id: UUID
    user_id: int
    owner_email: str
    name: str
    created_at: datetime
    updated_at: datetime


def create_meter(connection: Connection[Any], user_id: int, name: str) -> Meter:
    """Create a meter owned by one verified user."""

    meter_id = uuid4()
    try:
        with connection.transaction():
            connection.execute(
                "INSERT INTO monitor.meters (id, user_id, name) VALUES (%s, %s, %s)",
                (meter_id, user_id, normalize_meter_name(name)),
            )
    except UniqueViolation as error:
        raise MeterNameConflictError("Meter name is already in use") from error
    return get_meter(connection, meter_id, user_id)


def list_meters(
    connection: Connection[Any], owner_user_id: int | None
) -> list[Meter]:
    """List one owner's meters, or every meter when the scope is unrestricted."""

    where = "" if owner_user_id is None else "WHERE meters.user_id = %s"
    parameters = () if owner_user_id is None else (owner_user_id,)
    rows = connection.execute(
        f"""SELECT {METER_COLUMNS}
            FROM monitor.meters AS meters
            JOIN monitor.users AS users ON users.id = meters.user_id
            {where}
            ORDER BY LOWER(meters.name), meters.created_at, meters.id""",
        parameters,
    ).fetchall()
    return [Meter(*row) for row in rows]


def get_meter(
    connection: Connection[Any], meter_id: UUID, owner_user_id: int | None
) -> Meter:
    """Retrieve a meter inside an owner scope, or unrestricted for an admin."""

    owner_clause = "" if owner_user_id is None else "AND meters.user_id = %s"
    parameters = (meter_id,) if owner_user_id is None else (meter_id, owner_user_id)
    row = connection.execute(
        f"""SELECT {METER_COLUMNS}
            FROM monitor.meters AS meters
            JOIN monitor.users AS users ON users.id = meters.user_id
            WHERE meters.id = %s {owner_clause}""",
        parameters,
    ).fetchone()
    if not row:
        raise MeterNotFoundError("Meter is unavailable")
    return Meter(*row)


def rename_meter(
    connection: Connection[Any],
    meter_id: UUID,
    owner_user_id: int | None,
    name: str,
) -> Meter:
    """Rename a meter inside the supplied ownership scope."""

    owner_clause = "" if owner_user_id is None else "AND user_id = %s"
    parameters = (
        (normalize_meter_name(name), meter_id)
        if owner_user_id is None
        else (normalize_meter_name(name), meter_id, owner_user_id)
    )
    try:
        with connection.transaction():
            result = connection.execute(
                f"""UPDATE monitor.meters
                    SET name = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s {owner_clause}""",
                parameters,
            )
            if result.rowcount != 1:
                raise MeterNotFoundError("Meter is unavailable")
    except UniqueViolation as error:
        raise MeterNameConflictError("Meter name is already in use") from error
    return get_meter(connection, meter_id, owner_user_id)


def delete_meter(
    connection: Connection[Any], meter_id: UUID, owner_user_id: int | None
) -> None:
    """Delete a meter inside the supplied ownership scope."""

    owner_clause = "" if owner_user_id is None else "AND user_id = %s"
    parameters = (meter_id,) if owner_user_id is None else (meter_id, owner_user_id)
    with connection.transaction():
        result = connection.execute(
            f"DELETE FROM monitor.meters WHERE id = %s {owner_clause}", parameters
        )
        if result.rowcount != 1:
            raise MeterNotFoundError("Meter is unavailable")


def normalize_meter_name(name: str) -> str:
    """Trim a display name and enforce its small V1 storage contract."""

    normalized = name.strip()
    if not normalized or len(normalized) > MAX_METER_NAME_LENGTH:
        raise ValueError("Meter name must contain between 1 and 80 characters")
    return normalized
