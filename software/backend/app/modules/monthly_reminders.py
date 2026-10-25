"""Finite member-based monthly delivery, shared by the guarded app scheduler."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
import os
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

MONTHLY_KEY = re.compile(r"([0-9]{4}-(?:0[1-9]|1[0-2])):([1-9][0-9]{0,18})")
MONTH_END_LEAD = timedelta(hours=15)  # 09:00 UTC on the day before the target 1st.


class LegacyMonthlyDeliveriesError(Exception):
    """Automatic delivery is blocked until incompatible monthly rows are reviewed."""


class _ReminderPassStopped(Exception):
    """Unwind incomplete discovery atomically, or stop before the next SMTP send."""


def _check_stop(should_stop: Callable[[], bool] | None) -> None:
    if should_stop is not None and should_stop():
        raise _ReminderPassStopped()


def ensure_monthly_delivery_compatibility(connection: Connection[Any]) -> None:
    """Reject unknown/legacy monthly keys without remapping or altering history."""
    keys = connection.execute(
        "SELECT DISTINCT dedupe_key FROM monitor.reminder_deliveries WHERE reminder_type = 'monthly'"
    ).fetchall()
    if any(_parse_key(key) is None for (key,) in keys):
        raise LegacyMonthlyDeliveriesError("Monthly delivery keys require reconciliation")


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
    connection: Connection[Any], cycle: datetime, activation_at: datetime, now: datetime,
    should_stop: Callable[[], bool] | None = None,
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
            _check_stop(should_stop)
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
                _check_stop(should_stop)
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
    sender: EmailSender,
    now: datetime,
    should_stop: Callable[[], bool] | None = None,
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
                message = build_monthly_reminder_message(candidate, forecast, os.environ["EMAIL_FROM"])
                if cycle != forecast.planning_at:
                    message.set_content(
                        f"Delayed monthly check-in. Original notification cycle: {cycle:%Y-%m}.\n\n"
                        + message.get_content()
                    )
                get_meter(connection, meter_id, user_id)
                _check_stop(should_stop)
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
    *,
    activation_at: datetime,
    sender: EmailSender | None = None,
    now: datetime | None = None,
    should_stop: Callable[[], bool] | None = None,
    bounded_io: bool = False,
    check_legacy: bool = False,
) -> ReminderRunResult:
    """Run once with independent commits and optional automatic-worker safeguards."""
    calculation_time = now if now is not None else datetime.now(UTC)
    for instant in (activation_at, calculation_time):
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise ValueError("Monthly reminder times must include a timezone")
    activation_at = activation_at.astimezone(UTC)
    calculation_time = calculation_time.astimezone(UTC)
    email_sender = sender if sender is not None else SmtpEmailSender()
    counts = {"sent": 0, "failed": 0, "skipped": 0}
    with connect_database(connect_timeout=5 if bounded_io else None) as connection:
        # Own the connection: SELECTs must not leave an implicit outer transaction.
        connection.autocommit = True
        if bounded_io:
            connection.execute("SET statement_timeout = 5000")
            connection.execute("SET lock_timeout = 2000")
        if check_legacy:
            ensure_monthly_delivery_compatibility(connection)
        try:
            _check_stop(should_stop)
            owned, scanned = _discover_jobs(
                connection, _latest_cycle(calculation_time), activation_at, calculation_time, should_stop
            )
        except _ReminderPassStopped:
            return ReminderRunResult(0, 0, 0, 0)
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
            try:
                _check_stop(should_stop)
                outcome = _deliver_job(
                    connection, job_id, meter_id, observed_claim, cycle, user_id,
                    email_sender, calculation_time, should_stop,
                )
            except _ReminderPassStopped:
                break
            counts[outcome] += 1
    return ReminderRunResult(scanned, counts["sent"], counts["skipped"], counts["failed"])
