"""Finite command for sending due meter reminders through email."""

from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage
from typing import Any
from zoneinfo import ZoneInfo

from psycopg import Connection

from app.modules.balance_entries import list_balance_entries
from app.database import connect_database
from app.modules.email_delivery import (
    EmailDeliveryError,
    EmailSender,
    SmtpEmailSender,
)
from app.modules.forecasting import ForecastResult, run_forecast_model
from app.modules.meters import MeterNotFoundError, get_meter, lock_meter_access
from app.modules.otp import normalize_email
from app.modules.reminder_deliveries import (
    ReminderCandidate,
    ReminderType,
    claim_reminder_delivery,
    complete_reminder_delivery,
    list_reminder_candidates,
    release_reminder_delivery,
)
from app.settings import Settings
from app.modules.top_up_entries import list_top_up_entries


@dataclass(frozen=True)
class ReminderRunResult:
    """Aggregate command result that contains no customer information."""

    meters_scanned: int
    messages_sent: int
    duplicates_skipped: int
    delivery_failures: int


@dataclass(frozen=True)
class DueReminder:
    """One message type and stable deduplication key due in this run."""

    reminder_type: ReminderType
    dedupe_key: str


def build_monthly_reminder_message(
    candidate: ReminderCandidate,
    forecast: ForecastResult,
    sender: str,
) -> EmailMessage:
    """Build a monthly check-in with a recommendation only when available."""

    if forecast.status == "available":
        planning = (
            "Monitor currently recommends approximately "
            f"{forecast.recommended_monthly_top_up_kwh} additional kWh for the "
            f"{forecast.planning_days}-day calendar month, based on the current estimated balance."
        )
    else:
        planning = (
            "Monitor does not have enough consistent history for a recommendation. "
            "Record a fresh balance in the app."
        )
    return _message(
        candidate,
        sender,
        f"Monthly electricity reminder for {candidate.meter_name}",
        f"This is your monthly electricity check-in for {candidate.meter_name}.\n\n"
        f"Planning date: {forecast.planning_at:%Y-%m-%d} UTC.\n\n"
        f"{planning}\n\nEstimates are planning guidance, not a purchase or guarantee.\n",
    )


def build_low_balance_message(
    candidate: ReminderCandidate,
    forecast: ForecastResult,
    sender: str,
) -> EmailMessage:
    """Build a warning using only an available deterministic forecast."""

    assert forecast.status == "available" and forecast.run_out_at is not None
    local_run_out = forecast.run_out_at.astimezone(ZoneInfo(candidate.timezone))
    return _message(
        candidate,
        sender,
        f"Electricity may run low soon for {candidate.meter_name}",
        f"Monitor estimates {candidate.meter_name} has "
        f"{forecast.remaining_days} days remaining and may run out around "
        f"{local_run_out.date().isoformat()}.\n\n"
        f"Estimated balance: {forecast.estimated_balance_kwh} kWh. "
        "Check the physical meter before making decisions.\n\n"
        "This estimate is planning guidance, not a purchase or guarantee.\n",
    )


def _message(
    candidate: ReminderCandidate,
    sender: str,
    subject: str,
    body: str,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = sender
    message["To"] = normalize_email(candidate.owner_email)
    message["Subject"] = subject
    message.set_content(body)
    return message


def _due_reminders(
    candidate: ReminderCandidate,
    forecast: ForecastResult,
    now: datetime,
) -> list[DueReminder]:
    local_now = now.astimezone(ZoneInfo(candidate.timezone))
    due: list[DueReminder] = []
    if candidate.monthly_enabled and local_now.day == candidate.monthly_day:
        due.append(DueReminder("monthly", local_now.strftime("%Y-%m")))
    if (
        candidate.low_balance_enabled
        and forecast.status == "available"
        and forecast.remaining_days is not None
        and forecast.run_out_at is not None
        and forecast.remaining_days <= candidate.low_balance_days
    ):
        run_out_key = forecast.run_out_at.astimezone(
            ZoneInfo(candidate.timezone)
        ).date().isoformat()
        due.append(DueReminder("low_balance", run_out_key))
    return due


def run_due_reminders(
    connection: Connection[Any],
    settings: Settings,
    sender: EmailSender | None = None,
    now: datetime | None = None,
) -> ReminderRunResult:
    """Evaluate all opted-in meters once and deliver every unclaimed reminder."""

    calculation_time = (now or datetime.now(UTC)).astimezone(UTC)
    email_sender = sender or SmtpEmailSender(settings)
    candidates = list_reminder_candidates(connection)
    sent = skipped = failures = 0
    for candidate in candidates:
        try:
            # Serialize dispatch with membership removal and meter deletion.
            # SMTP is not transactional: a process crash may still repeat mail.
            with connection.transaction():
                lock_meter_access(connection, candidate.meter_id, candidate.owner_user_id)
                balances = list_balance_entries(
                    connection, candidate.meter_id, candidate.owner_user_id
                )
                top_ups = list_top_up_entries(
                    connection, candidate.meter_id, candidate.owner_user_id
                )
                forecast = run_forecast_model(balances, top_ups, calculation_time)
                for due in _due_reminders(candidate, forecast, calculation_time):
                    claim_id = claim_reminder_delivery(
                        connection, candidate.meter_id, due.reminder_type,
                        due.dedupe_key, calculation_time,
                    )
                    if claim_id is None:
                        skipped += 1
                        continue
                    message = (
                        build_monthly_reminder_message(candidate, forecast, settings.email_from)
                        if due.reminder_type == "monthly"
                        else build_low_balance_message(candidate, forecast, settings.email_from)
                    )
                    get_meter(connection, candidate.meter_id, candidate.owner_user_id)
                    try:
                        email_sender.send(message)
                    except EmailDeliveryError:
                        release_reminder_delivery(connection, claim_id)
                        failures += 1
                        continue
                    complete_reminder_delivery(connection, claim_id, calculation_time)
                    sent += 1
        except MeterNotFoundError:
            # Candidate selection can race a legitimate leave/delete request.
            continue
    return ReminderRunResult(len(candidates), sent, skipped, failures)


def main() -> None:
    """Run one reminder pass for an external scheduler."""

    settings = Settings()
    with connect_database(settings) as connection:
        result = run_due_reminders(connection, settings)
    print(
        "Reminder run complete: "
        f"meters={result.meters_scanned} sent={result.messages_sent} "
        f"skipped={result.duplicates_skipped} failures={result.delivery_failures}"
    )


if __name__ == "__main__":
    main()
