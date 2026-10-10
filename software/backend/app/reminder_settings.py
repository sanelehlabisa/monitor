"""Raw-SQL persistence for optional per-meter reminder preferences."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from psycopg import Connection

from app.meters import get_meter

DEFAULT_MONTHLY_DAY = 1
DEFAULT_LOW_BALANCE_DAYS = Decimal("3.00")
LOW_BALANCE_DAYS_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class ReminderSettings:
    """One meter's opt-in email reminder configuration."""

    meter_id: UUID
    monthly_enabled: bool
    monthly_day: int
    low_balance_enabled: bool
    low_balance_days: Decimal
    timezone: str
    created_at: datetime | None
    updated_at: datetime | None


def normalize_timezone(value: str) -> str:
    """Require one available IANA timezone name suitable for storage."""

    normalized = value.strip()
    if not normalized or len(normalized) > 64:
        raise ValueError("Timezone must contain between 1 and 64 characters")
    try:
        ZoneInfo(normalized)
    except ZoneInfoNotFoundError as error:
        raise ValueError("Timezone must be a valid IANA name") from error
    return normalized


def normalize_monthly_day(value: int) -> int:
    """Restrict monthly reminders to dates present in every month."""

    if isinstance(value, bool) or not 1 <= value <= 28:
        raise ValueError("Monthly reminder day must be between 1 and 28")
    return value


def normalize_low_balance_days(value: Decimal) -> Decimal:
    """Validate a positive warning horizon without silent rounding."""

    try:
        normalized = value.quantize(LOW_BALANCE_DAYS_QUANTUM)
    except InvalidOperation as error:
        raise ValueError("Low-balance days are outside the supported range") from error
    if not value.is_finite() or value != normalized or not 0 < value <= 30:
        raise ValueError("Low-balance days must be from 0.01 through 30")
    return normalized


def get_reminder_settings(
    connection: Connection[Any],
    meter_id: UUID,
    owner_user_id: int | None,
    default_timezone: str = "UTC",
) -> ReminderSettings:
    """Return saved settings or safe disabled defaults for an accessible meter."""

    get_meter(connection, meter_id, owner_user_id)
    row = connection.execute(
        """SELECT meter_id, monthly_enabled, monthly_day,
                  low_balance_enabled, low_balance_days, timezone,
                  created_at, updated_at
           FROM monitor.reminder_settings WHERE meter_id = %s""",
        (meter_id,),
    ).fetchone()
    if row:
        return ReminderSettings(*row)
    return ReminderSettings(
        meter_id=meter_id,
        monthly_enabled=False,
        monthly_day=DEFAULT_MONTHLY_DAY,
        low_balance_enabled=False,
        low_balance_days=DEFAULT_LOW_BALANCE_DAYS,
        timezone=normalize_timezone(default_timezone),
        created_at=None,
        updated_at=None,
    )


def upsert_reminder_settings(
    connection: Connection[Any],
    meter_id: UUID,
    owner_user_id: int | None,
    *,
    monthly_enabled: bool,
    monthly_day: int,
    low_balance_enabled: bool,
    low_balance_days: Decimal,
    timezone: str,
) -> ReminderSettings:
    """Create or replace an accessible meter's reminder preferences."""

    if not isinstance(monthly_enabled, bool) or not isinstance(
        low_balance_enabled, bool
    ):
        raise ValueError("Reminder enabled values must be true or false")
    with connection.transaction():
        get_meter(connection, meter_id, owner_user_id)
        connection.execute(
            """INSERT INTO monitor.reminder_settings
               (meter_id, monthly_enabled, monthly_day, low_balance_enabled,
                low_balance_days, timezone)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (meter_id) DO UPDATE SET
                   monthly_enabled = EXCLUDED.monthly_enabled,
                   monthly_day = EXCLUDED.monthly_day,
                   low_balance_enabled = EXCLUDED.low_balance_enabled,
                   low_balance_days = EXCLUDED.low_balance_days,
                   timezone = EXCLUDED.timezone,
                   updated_at = CURRENT_TIMESTAMP""",
            (
                meter_id,
                monthly_enabled,
                normalize_monthly_day(monthly_day),
                low_balance_enabled,
                normalize_low_balance_days(low_balance_days),
                normalize_timezone(timezone),
            ),
        )
    return get_reminder_settings(connection, meter_id, owner_user_id)
