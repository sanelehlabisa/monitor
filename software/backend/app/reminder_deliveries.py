"""Raw-SQL delivery claims and reminder-runner candidate queries."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

from psycopg import Connection

ReminderType = Literal["monthly", "low_balance"]
CLAIM_TIMEOUT = timedelta(minutes=30)


@dataclass(frozen=True)
class ReminderCandidate:
    """Enabled meter settings plus their delivery recipient."""

    meter_id: UUID
    meter_name: str
    owner_user_id: int
    owner_email: str
    monthly_enabled: bool
    monthly_day: int
    low_balance_enabled: bool
    low_balance_days: Decimal
    timezone: str


def list_reminder_candidates(
    connection: Connection[Any],
) -> list[ReminderCandidate]:
    """List meters with at least one explicitly enabled email reminder."""

    rows = connection.execute(
        """SELECT meters.id, meters.name, users.id, users.email,
                  reminders.monthly_enabled, reminders.monthly_day,
                  reminders.low_balance_enabled, reminders.low_balance_days,
                  reminders.timezone
           FROM monitor.reminder_settings AS reminders
           JOIN monitor.meters AS meters ON meters.id = reminders.meter_id
           JOIN monitor.users AS users ON users.id = meters.user_id
           WHERE reminders.monthly_enabled OR reminders.low_balance_enabled
           ORDER BY meters.id"""
    ).fetchall()
    return [ReminderCandidate(*row) for row in rows]


def claim_reminder_delivery(
    connection: Connection[Any],
    meter_id: UUID,
    reminder_type: ReminderType,
    dedupe_key: str,
    now: datetime,
) -> UUID | None:
    """Claim a new delivery or safely recover one abandoned before completion."""

    claim_id = uuid4()
    with connection.transaction():
        row = connection.execute(
            """INSERT INTO monitor.reminder_deliveries
               (id, meter_id, reminder_type, dedupe_key, claimed_at)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (meter_id, reminder_type, dedupe_key) DO NOTHING
               RETURNING id""",
            (claim_id, meter_id, reminder_type, dedupe_key, now),
        ).fetchone()
        if row:
            return row[0]
        stale = connection.execute(
            """UPDATE monitor.reminder_deliveries
               SET claimed_at = %s
               WHERE meter_id = %s AND reminder_type = %s AND dedupe_key = %s
                 AND status = 'pending' AND claimed_at <= %s
               RETURNING id""",
            (
                now,
                meter_id,
                reminder_type,
                dedupe_key,
                now - CLAIM_TIMEOUT,
            ),
        ).fetchone()
        return stale[0] if stale else None


def complete_reminder_delivery(
    connection: Connection[Any], claim_id: UUID, sent_at: datetime
) -> None:
    """Mark a successfully delivered claim as sent."""

    with connection.transaction():
        connection.execute(
            """UPDATE monitor.reminder_deliveries
               SET status = 'sent', sent_at = %s
               WHERE id = %s AND status = 'pending'""",
            (sent_at, claim_id),
        )


def release_reminder_delivery(
    connection: Connection[Any], claim_id: UUID
) -> None:
    """Release a failed pending delivery so the next run may retry it."""

    with connection.transaction():
        connection.execute(
            "DELETE FROM monitor.reminder_deliveries WHERE id = %s AND status = 'pending'",
            (claim_id,),
        )
