"""Tests for due-reminder policy, delivery claims and retry behavior."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from email.message import EmailMessage
from typing import Any
from uuid import uuid4

from app.balance_entries import create_balance_entry
from app.database import connect_database
from app.email_delivery import EmailDeliveryError
from app.meters import Meter, create_meter
from app.reminder_deliveries import (
    claim_reminder_delivery,
    complete_reminder_delivery,
)
from app.reminder_runner import run_due_reminders
from app.reminder_settings import upsert_reminder_settings
from app.settings import Settings
from psycopg import Connection

NOW = datetime(2026, 10, 10, 10, tzinfo=UTC)


class RecordingSender:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.messages: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        if self.fail:
            raise EmailDeliveryError("expected test failure")
        self.messages.append(message)


def _create_user(connection: Connection[Any], prefix: str) -> tuple[int, str]:
    email = f"{prefix}-{uuid4().hex}@example.test"
    row = connection.execute(
        "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id", (email,)
    ).fetchone()
    assert row
    return row[0], email


def _configured_meter(
    connection: Connection[Any], user_id: int, name: str = "Home"
) -> Meter:
    meter = create_meter(connection, user_id, name)
    upsert_reminder_settings(
        connection,
        meter.id,
        user_id,
        monthly_enabled=True,
        monthly_day=10,
        low_balance_enabled=True,
        low_balance_days=Decimal("30"),
        timezone="Africa/Johannesburg",
    )
    create_balance_entry(
        connection, meter.id, user_id, Decimal("30"), NOW - timedelta(days=2)
    )
    create_balance_entry(
        connection, meter.id, user_id, Decimal("20"), NOW - timedelta(days=1)
    )
    return meter


def test_runner_sends_due_messages_once_to_the_owner() -> None:
    """Monthly and low-balance messages are deduplicated per approved keys."""

    settings = Settings(environment="test")
    with connect_database(settings) as connection:
        user_id, email = _create_user(connection, "reminder-run")
        _configured_meter(connection, user_id)
        sender = RecordingSender()
        try:
            first = run_due_reminders(connection, settings, sender, NOW)
            second = run_due_reminders(connection, settings, sender, NOW)

            assert first.messages_sent == 2
            assert second.messages_sent == 0
            assert second.duplicates_skipped == 2
            assert len(sender.messages) == 2
            assert {message["To"] for message in sender.messages} == {email}
            assert any("Monthly electricity" in message["Subject"] for message in sender.messages)
            assert any("may run low" in message["Subject"] for message in sender.messages)
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_failed_delivery_releases_claim_for_retry() -> None:
    """SMTP failure is counted and the same due reminder can retry later."""

    settings = Settings(environment="test")
    with connect_database(settings) as connection:
        user_id, email = _create_user(connection, "reminder-retry")
        _configured_meter(connection, user_id)
        try:
            failed = run_due_reminders(
                connection, settings, RecordingSender(fail=True), NOW
            )
            retried = run_due_reminders(connection, settings, RecordingSender(), NOW)

            assert failed.delivery_failures == 2
            assert retried.messages_sent == 2
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_monthly_sends_without_forecast_but_low_balance_does_not() -> None:
    """Unavailable history prompts a reading without inventing a low warning."""

    settings = Settings(environment="test")
    with connect_database(settings) as connection:
        user_id, email = _create_user(connection, "reminder-empty")
        meter = create_meter(connection, user_id, "Home")
        upsert_reminder_settings(
            connection,
            meter.id,
            user_id,
            monthly_enabled=True,
            monthly_day=10,
            low_balance_enabled=True,
            low_balance_days=Decimal("3"),
            timezone="UTC",
        )
        sender = RecordingSender()
        try:
            result = run_due_reminders(connection, settings, sender, NOW)

            assert result.messages_sent == 1
            assert "fresh balance" in sender.messages[0].get_content()
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_stale_claim_can_recover_but_sent_or_active_claim_cannot() -> None:
    """Only an abandoned pending claim becomes available to a later runner."""

    settings = Settings(environment="test")
    with connect_database(settings) as connection:
        user_id, email = _create_user(connection, "reminder-claim")
        meter = create_meter(connection, user_id, "Home")
        try:
            first = claim_reminder_delivery(
                connection, meter.id, "monthly", "2026-10", NOW
            )
            active = claim_reminder_delivery(
                connection, meter.id, "monthly", "2026-10", NOW
            )
            recovered = claim_reminder_delivery(
                connection,
                meter.id,
                "monthly",
                "2026-10",
                NOW + timedelta(minutes=31),
            )
            assert first is not None
            assert active is None
            assert recovered == first
            complete_reminder_delivery(connection, recovered, NOW + timedelta(minutes=31))
            sent = claim_reminder_delivery(
                connection,
                meter.id,
                "monthly",
                "2026-10",
                NOW + timedelta(hours=2),
            )
            assert sent is None
        finally:
            connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))
