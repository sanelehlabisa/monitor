"""Raw-SQL persistence for manually purchased top-up energy."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection

from app.modules.ledger_values import normalize_kwh, normalize_occurred_at
from app.modules.meters import get_meter, lock_meter_access


class TopUpEntryNotFoundError(Exception):
    """Raised when a top-up is missing from its requested meter."""


@dataclass(frozen=True)
class TopUpEntry:
    """One factual purchased-kWh event for a software meter."""

    id: UUID
    meter_id: UUID
    top_up_kwh: Decimal
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


def create_top_up_entry(
    connection: Connection[Any],
    meter_id: UUID,
    owner_user_id: int | None,
    top_up_kwh: Decimal,
    occurred_at: datetime,
) -> TopUpEntry:
    """Create a purchased-energy event after enforcing meter access."""

    entry_id = uuid4()
    with connection.transaction():
        lock_meter_access(connection, meter_id, owner_user_id)
        connection.execute(
            """INSERT INTO monitor.top_up_entries
               (id, meter_id, top_up_kwh, occurred_at)
               VALUES (%s, %s, %s, %s)""",
            (
                entry_id,
                meter_id,
                normalize_kwh(top_up_kwh, allow_zero=False),
                normalize_occurred_at(occurred_at),
            ),
        )
    return get_top_up_entry(connection, meter_id, entry_id, owner_user_id)


def list_top_up_entries(
    connection: Connection[Any], meter_id: UUID, owner_user_id: int | None
) -> list[TopUpEntry]:
    """List an accessible meter's purchased-energy events newest-first."""

    get_meter(connection, meter_id, owner_user_id)
    rows = connection.execute(
        """SELECT id, meter_id, top_up_kwh, occurred_at, created_at, updated_at
           FROM monitor.top_up_entries WHERE meter_id = %s
           ORDER BY occurred_at DESC, id DESC""",
        (meter_id,),
    ).fetchall()
    return [TopUpEntry(*row) for row in rows]


def get_top_up_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
) -> TopUpEntry:
    """Retrieve one top-up inside an accessible meter."""

    get_meter(connection, meter_id, owner_user_id)
    row = connection.execute(
        """SELECT id, meter_id, top_up_kwh, occurred_at, created_at, updated_at
           FROM monitor.top_up_entries WHERE id = %s AND meter_id = %s""",
        (entry_id, meter_id),
    ).fetchone()
    if not row:
        raise TopUpEntryNotFoundError("Top-up entry is unavailable")
    return TopUpEntry(*row)


def update_top_up_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
    top_up_kwh: Decimal,
    occurred_at: datetime,
) -> TopUpEntry:
    """Correct both the value and occurrence time of an accessible top-up."""

    with connection.transaction():
        lock_meter_access(connection, meter_id, owner_user_id)
        result = connection.execute(
            """UPDATE monitor.top_up_entries
               SET top_up_kwh = %s, occurred_at = %s,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = %s AND meter_id = %s""",
            (
                normalize_kwh(top_up_kwh, allow_zero=False),
                normalize_occurred_at(occurred_at),
                entry_id,
                meter_id,
            ),
        )
        if result.rowcount != 1:
            raise TopUpEntryNotFoundError("Top-up entry is unavailable")
    return get_top_up_entry(connection, meter_id, entry_id, owner_user_id)


def delete_top_up_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
) -> None:
    """Delete one top-up inside an accessible meter."""

    with connection.transaction():
        lock_meter_access(connection, meter_id, owner_user_id)
        result = connection.execute(
            "DELETE FROM monitor.top_up_entries WHERE id = %s AND meter_id = %s",
            (entry_id, meter_id),
        )
        if result.rowcount != 1:
            raise TopUpEntryNotFoundError("Top-up entry is unavailable")
