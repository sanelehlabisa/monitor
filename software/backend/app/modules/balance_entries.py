"""Raw-SQL persistence for actual remaining-balance observations."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.modules.ledger_values import normalize_kwh, normalize_occurred_at
from app.modules.meters import get_meter


class BalanceEntryNotFoundError(Exception):
    """Raised when an entry is missing from its requested meter."""


class BalanceTimeConflictError(Exception):
    """Raised when a meter already has a balance at an occurrence time."""


@dataclass(frozen=True)
class BalanceEntry:
    """One factual remaining-kWh observation for a software meter."""

    id: UUID
    meter_id: UUID
    balance_kwh: Decimal
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


def create_balance_entry(
    connection: Connection[Any],
    meter_id: UUID,
    owner_user_id: int | None,
    balance_kwh: Decimal,
    occurred_at: datetime,
) -> BalanceEntry:
    """Create an observation after enforcing meter access and value rules."""

    entry_id = uuid4()
    try:
        with connection.transaction():
            get_meter(connection, meter_id, owner_user_id)
            connection.execute(
                """INSERT INTO monitor.balance_entries
                   (id, meter_id, balance_kwh, occurred_at)
                   VALUES (%s, %s, %s, %s)""",
                (
                    entry_id,
                    meter_id,
                    normalize_kwh(balance_kwh, allow_zero=True),
                    normalize_occurred_at(occurred_at),
                ),
            )
    except UniqueViolation as error:
        raise BalanceTimeConflictError(
            "A balance already exists at that time"
        ) from error
    return get_balance_entry(connection, meter_id, entry_id, owner_user_id)


def list_balance_entries(
    connection: Connection[Any], meter_id: UUID, owner_user_id: int | None
) -> list[BalanceEntry]:
    """List an accessible meter's observations newest-first."""

    get_meter(connection, meter_id, owner_user_id)
    rows = connection.execute(
        """SELECT id, meter_id, balance_kwh, occurred_at, created_at, updated_at
           FROM monitor.balance_entries WHERE meter_id = %s
           ORDER BY occurred_at DESC, id DESC""",
        (meter_id,),
    ).fetchall()
    return [BalanceEntry(*row) for row in rows]


def get_balance_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
) -> BalanceEntry:
    """Retrieve one entry inside an accessible meter."""

    get_meter(connection, meter_id, owner_user_id)
    row = connection.execute(
        """SELECT id, meter_id, balance_kwh, occurred_at, created_at, updated_at
           FROM monitor.balance_entries WHERE id = %s AND meter_id = %s""",
        (entry_id, meter_id),
    ).fetchone()
    if not row:
        raise BalanceEntryNotFoundError("Balance entry is unavailable")
    return BalanceEntry(*row)


def update_balance_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
    balance_kwh: Decimal,
    occurred_at: datetime,
) -> BalanceEntry:
    """Correct both the value and occurrence time of an accessible entry."""

    try:
        with connection.transaction():
            get_meter(connection, meter_id, owner_user_id)
            result = connection.execute(
                """UPDATE monitor.balance_entries
                   SET balance_kwh = %s, occurred_at = %s,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = %s AND meter_id = %s""",
                (
                    normalize_kwh(balance_kwh, allow_zero=True),
                    normalize_occurred_at(occurred_at),
                    entry_id,
                    meter_id,
                ),
            )
            if result.rowcount != 1:
                raise BalanceEntryNotFoundError("Balance entry is unavailable")
    except UniqueViolation as error:
        raise BalanceTimeConflictError(
            "A balance already exists at that time"
        ) from error
    return get_balance_entry(connection, meter_id, entry_id, owner_user_id)


def delete_balance_entry(
    connection: Connection[Any],
    meter_id: UUID,
    entry_id: UUID,
    owner_user_id: int | None,
) -> None:
    """Delete one entry inside an accessible meter."""

    with connection.transaction():
        get_meter(connection, meter_id, owner_user_id)
        result = connection.execute(
            "DELETE FROM monitor.balance_entries WHERE id = %s AND meter_id = %s",
            (entry_id, meter_id),
        )
        if result.rowcount != 1:
            raise BalanceEntryNotFoundError("Balance entry is unavailable")
