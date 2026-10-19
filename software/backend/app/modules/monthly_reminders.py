"""Finite member-based monthly delivery; deliberately not wired to a scheduler."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
import re
from typing import Any, Literal
from uuid import UUID

from psycopg import Connection

from app.database import connect_database
from app.modules.balance_entries import list_balance_entries
from app.modules.email_delivery import EmailDeliveryError, EmailSender, SmtpEmailSender
from app.modules.forecasting import run_forecast_model
from app.modules.meters import MeterNotFoundError, get_meter, lock_meter_access
from app.modules.reminder_deliveries import (
    CLAIM_TIMEOUT,
    ReminderCandidate,
    claim_reminder_delivery,
    complete_reminder_delivery,
)
from app.modules.reminder_runner import ReminderRunResult, build_monthly_reminder_message
from app.modules.top_up_entries import list_top_up_entries
from app.settings import Settings

MONTHLY_KEY = re.compile(r"([0-9]{4}-(?:0[1-9]|1[0-2])):([1-9][0-9]{0,18})")
MONTH_END_LEAD = timedelta(hours=15)  # 09:00 UTC on the day before the target 1st.


def _latest_cycle(now: datetime) -> datetime:
    """Choose only the latest cycle whose month-end 09:00 UTC has passed."""
    current = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    following = (current + timedelta(days=32)).replace(day=1)
    return following if now >= following - MONTH_END_LEAD else current


def _parse_key(key: str) -> tuple[datetime, int] | None:
    """Recognize only valid new recipient keys, never legacy or malformed jobs."""
    match = MONTHLY_KEY.fullmatch(key)
    if match is None:
        return None
    try:
        cycle = datetime.strptime(match[1], "%Y-%m").replace(tzinfo=UTC)
        cycle - MONTH_END_LEAD  # Reject dates whose scheduled instant overflows.
    except (ValueError, OverflowError):
        return None
    user_id = int(match[2])
    return (cycle, user_id) if user_id <= 2**63 - 1 else None


def _discover_jobs(
    connection: Connection[Any], cycle: datetime, activation_at: datetime, now: datetime
) -> tuple[set[UUID], int]:
    """Commit the entire eligible member fan-out before any SMTP attempt."""
    scheduled_at = cycle - MONTH_END_LEAD
    if scheduled_at < activation_at:
        return set(), 0
    meter_ids = connection.execute(
        "SELECT id FROM monitor.meters WHERE created_at <= %s ORDER BY id",
        (scheduled_at,),
    ).fetchall()
    owned: set[UUID] = set()
    scanned = 0
    with connection.transaction():
        for (meter_id,) in meter_ids:
            try:
                lock_meter_access(connection, meter_id, None)
            except MeterNotFoundError:
                continue
            scanned += 1
            # Separate selection sees membership changes committed while locking.
            members = connection.execute(
                "SELECT user_id FROM monitor.user_meters WHERE meter_id = %s ORDER BY user_id",
                (meter_id,),
            ).fetchall()
            for (user_id,) in members:
                claim_id = claim_reminder_delivery(
                    connection, meter_id, "monthly", f"{cycle:%Y-%m}:{user_id}", now
                )
                if claim_id is not None:
                    owned.add(claim_id)
    return owned, scanned


def _deliver_job(
    connection: Connection[Any],
    job_id: UUID,
    meter_id: UUID,
    observed_claim: datetime,
    cycle: datetime,
    user_id: int,
    settings: Settings,
    sender: EmailSender,
    now: datetime,
) -> Literal["sent", "failed", "skipped"]:
    """Serialize one recipient with revocation/reclaim and commit independently."""
    try:
        with connection.transaction():
            meter = lock_meter_access(connection, meter_id, user_id)
            claim = connection.execute(
                """SELECT status, claimed_at FROM monitor.reminder_deliveries
                   WHERE id = %s FOR UPDATE""", (job_id,),
            ).fetchone()
            if claim != ("pending", observed_claim):
                return "skipped"
            connection.execute(
                "UPDATE monitor.reminder_deliveries SET claimed_at = %s WHERE id = %s",
                (now, job_id),
            )
            email = connection.execute(
                "SELECT email FROM monitor.users WHERE id = %s", (user_id,)
            ).fetchone()[0]
            # Reuse the legacy message DTO's recipient slots, not creator authority.
            candidate = ReminderCandidate(
                # Names may contain newlines; never copy those into an email header.
                meter_id=meter_id, meter_name=" ".join(meter.name.splitlines()),
                owner_user_id=user_id, owner_email=email,
                monthly_enabled=True, monthly_day=1,
                low_balance_enabled=False, low_balance_days=Decimal("0"), timezone="UTC",
            )
            try:
                forecast = run_forecast_model(
                    list_balance_entries(connection, meter_id, user_id),
                    list_top_up_entries(connection, meter_id, user_id), now,
                )
                message = build_monthly_reminder_message(candidate, forecast, settings.email_from)
                if cycle != forecast.planning_at:
                    message.set_content(
                        f"Delayed monthly check-in. Original notification cycle: {cycle:%Y-%m}.\n\n"
                        + message.get_content()
                    )
                get_meter(connection, meter_id, user_id)
                sender.send(message)
            except (EmailDeliveryError, ValueError, OverflowError):
                # Failed SMTP or unrepresentable estimates must not starve other jobs.
                # Retain pending with a renewed lease; never invent a forecast.
                return "failed"
            # SMTP acceptance and this commit cannot be atomic: crashes can repeat mail.
            complete_reminder_delivery(connection, job_id, now)
        return "sent"
    except MeterNotFoundError:
        return "skipped"


def run_monthly_reminders(
    settings: Settings,
    *,
    activation_at: datetime,
    sender: EmailSender | None = None,
    now: datetime | None = None,
) -> ReminderRunResult:
    """Run once on an owned connection; never enable scheduling or legacy retries."""
    calculation_time = now if now is not None else datetime.now(UTC)
    for instant in (activation_at, calculation_time):
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("Monthly reminder times must include a timezone")
    activation_at = activation_at.astimezone(UTC)
    calculation_time = calculation_time.astimezone(UTC)
    email_sender = sender if sender is not None else SmtpEmailSender(settings)
    counts = {"sent": 0, "failed": 0, "skipped": 0}
    with connect_database(settings) as connection:
        # Own the connection: SELECTs must not leave an implicit outer transaction.
        connection.autocommit = True
        owned, scanned = _discover_jobs(
            connection, _latest_cycle(calculation_time), activation_at, calculation_time
        )
        jobs = connection.execute(
            """SELECT id, meter_id, dedupe_key, claimed_at
               FROM monitor.reminder_deliveries
               WHERE reminder_type = 'monthly' AND status = 'pending'
                 AND ((id = ANY(%s) AND claimed_at = %s) OR claimed_at <= %s)
               ORDER BY meter_id, dedupe_key, id""",
            (list(owned), calculation_time, calculation_time - CLAIM_TIMEOUT),
        ).fetchall()
        for job_id, meter_id, key, observed_claim in jobs:
            parsed = _parse_key(key)
            if parsed is None or parsed[0] - MONTH_END_LEAD > calculation_time:
                continue
            cycle, user_id = parsed
            outcome = _deliver_job(
                connection, job_id, meter_id, observed_claim, cycle, user_id,
                settings, email_sender, calculation_time,
            )
            counts[outcome] += 1
    return ReminderRunResult(scanned, counts["sent"], counts["skipped"], counts["failed"])
