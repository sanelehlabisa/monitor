"""Lifecycle and activation safety checks, with isolated synthetic fixtures only."""

import asyncio
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from threading import Event, Lock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from psycopg.conninfo import conninfo_to_dict
from pytest import LogCaptureFixture, MonkeyPatch, mark, raises

from app.database import connect_database
from app.main import create_app
from app.modules import monthly_reminders, reminder_scheduler
from app.modules.reminder_runner import ReminderRunResult
from app.settings import Settings
from tests.support import SharingCase
from tests.test_monthly_reminders import ACTIVATION, NOW, _job, _meter, _rows
from tests.test_reminder_runner import RecordingSender

EMPTY_RESULT = ReminderRunResult(0, 0, 0, 0)


def _settings(cutoff: datetime | str | int | None = ACTIVATION) -> Settings:
    """Set activation explicitly so unrelated process environment cannot enable it."""
    return Settings(environment="test", monthly_reminders_activated_at=cutoff)


@mark.parametrize("cutoff", [None, ""])
def test_empty_activation_disables_automation(cutoff: datetime | str | None) -> None:
    assert _settings(cutoff).monthly_reminders_activated_at is None


@mark.parametrize("cutoff", ["not-a-date", "2024-06-01T09:00:00", 42, True])
def test_invalid_or_naive_activation_is_rejected(cutoff: str | int) -> None:
    with raises(ValidationError):
        _settings(cutoff)


def test_saved_activation_is_normalized_to_utc_and_not_reset(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT", "2024-06-01T11:00:00+02:00")
    first = Settings(environment="test").monthly_reminders_activated_at
    second = Settings(environment="test").monthly_reminders_activated_at
    assert first == second == datetime(2024, 6, 1, 9, tzinfo=UTC)
    assert first.utcoffset() == timedelta(0)


@mark.parametrize("disabled", [True, False])
def test_disabled_or_stopped_pass_never_opens_database(
    monkeypatch: MonkeyPatch, disabled: bool,
) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("Disabled scheduling must not access the database")
    monkeypatch.setattr(monthly_reminders, "connect_database", forbidden)
    monkeypatch.setattr(reminder_scheduler, "run_monthly_reminders", forbidden)
    stop = Event()
    if not disabled:
        stop.set()
    assert reminder_scheduler.run_scheduled_reminders(
        _settings(None if disabled else ACTIVATION), stop,
    ) is None


def test_disabled_lifespan_creates_no_worker_and_health_stays_available(
    monkeypatch: MonkeyPatch,
) -> None:
    async def forbidden(*args, **kwargs):
        raise AssertionError("A disabled lifespan must not start a worker")
    monkeypatch.setattr(reminder_scheduler, "run_reminder_loop", forbidden)
    with TestClient(create_app(_settings(None))) as client:
        assert client.get("/health").status_code == 200


def test_startup_pass_runs_off_event_loop_without_blocking_requests(
    monkeypatch: MonkeyPatch,
) -> None:
    entered, release, finished = Event(), Event(), Event()
    calls: list[Settings] = []
    def blocking_pass(settings: Settings, stop: Event | None = None):
        with raises(RuntimeError, match="no running event loop"):
            asyncio.get_running_loop()
        calls.append(settings)
        entered.set()
        try:
            assert release.wait(timeout=5)
            return EMPTY_RESULT
        finally:
            finished.set()
    monkeypatch.setattr(reminder_scheduler, "run_scheduled_reminders", blocking_pass)
    with TestClient(create_app(_settings())) as client:
        try:
            assert entered.wait(timeout=5)  # Immediate startup, not first 60-second tick.
            assert client.get("/health").status_code == 200
            assert len(calls) == 1
        finally:
            release.set()
    assert finished.is_set()


def test_loop_retries_failure_sequentially_without_logging_private_error_text(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture,
) -> None:
    stop = Event()
    lock = Lock()
    calls = active = maximum_active = 0
    def pass_once(settings: Settings, worker_stop: Event | None = None):
        nonlocal calls, active, maximum_active
        with lock:
            calls += 1
            active += 1
            maximum_active = max(maximum_active, active)
        try:
            if calls == 1:
                raise RuntimeError("private-diagnostic-marker")
            stop.set()
            return EMPTY_RESULT
        finally:
            with lock:
                active -= 1
    monkeypatch.setattr(reminder_scheduler, "run_scheduled_reminders", pass_once)
    assert reminder_scheduler.CHECK_INTERVAL_SECONDS == 60
    monkeypatch.setattr(reminder_scheduler, "CHECK_INTERVAL_SECONDS", 0.001)
    async def exercise() -> None:
        await asyncio.wait_for(reminder_scheduler.run_reminder_loop(_settings(), stop), timeout=5)
    asyncio.run(exercise())
    assert calls == 2 and maximum_active == 1
    assert "private-diagnostic-marker" not in caplog.text


def test_shutdown_signals_stop_and_drains_inflight_work_instead_of_detaching(
    monkeypatch: MonkeyPatch,
) -> None:
    entered, observed_stop, release, finished = Event(), Event(), Event(), Event()
    def blocking_pass(settings: Settings, stop: Event | None = None):
        assert stop is not None
        entered.set()
        assert stop.wait(timeout=5)
        observed_stop.set()
        try:
            assert release.wait(timeout=5)
            return EMPTY_RESULT
        finally:
            finished.set()
    monkeypatch.setattr(reminder_scheduler, "run_scheduled_reminders", blocking_pass)
    async def exercise() -> None:
        context = reminder_scheduler.monthly_reminder_lifespan(FastAPI(), _settings())
        await context.__aenter__()
        assert await asyncio.to_thread(entered.wait, 5)
        closing = asyncio.create_task(context.__aexit__(None, None, None))
        try:
            assert await asyncio.to_thread(observed_stop.wait, 5)
            assert not closing.done() and not finished.is_set()
        finally:
            release.set()
            await asyncio.wait_for(closing, timeout=5)
        assert finished.is_set()
    asyncio.run(exercise())


def test_cancelled_loop_waits_for_its_actual_worker_to_finish(monkeypatch: MonkeyPatch) -> None:
    """Cancelling an asyncio wrapper is not treated as cancellation of its thread."""
    entered, observed_stop, release, finished = Event(), Event(), Event(), Event()
    stop = Event()
    def blocking_pass(settings: Settings, worker_stop: Event | None = None):
        entered.set()
        assert worker_stop is stop and stop.wait(timeout=5)
        observed_stop.set()
        try:
            assert release.wait(timeout=5)
            return EMPTY_RESULT
        finally:
            finished.set()
    monkeypatch.setattr(reminder_scheduler, "run_scheduled_reminders", blocking_pass)
    async def exercise() -> None:
        loop = asyncio.create_task(reminder_scheduler.run_reminder_loop(_settings(), stop))
        assert await asyncio.to_thread(entered.wait, 5)
        loop.cancel()
        try:
            assert await asyncio.to_thread(observed_stop.wait, 5)
            assert not loop.done() and not finished.is_set()
        finally:
            release.set()
            with raises(asyncio.CancelledError):
                await asyncio.wait_for(loop, timeout=5)
        assert finished.is_set()
    asyncio.run(exercise())


@mark.parametrize("legacy_key", ["2024-06", "malformed:recipient"])
@mark.parametrize("sent", [False, True])
def test_legacy_or_malformed_monthly_rows_block_before_any_job_writes(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch, legacy_key: str, sent: bool,
) -> None:
    case = sharing_case
    meter = _meter(case, case.user())
    _job(case, meter, legacy_key, sent=sent)
    before = _rows(case, meter.id)
    sender = RecordingSender()
    monkeypatch.setattr(monthly_reminders, "SmtpEmailSender", lambda settings: sender)
    with raises(monthly_reminders.LegacyMonthlyDeliveriesError):
        reminder_scheduler.run_scheduled_reminders(_settings())
    assert _rows(case, meter.id) == before
    assert not sender.messages


def test_compatibility_allows_new_format_and_ignores_legacy_low_balance(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner = case.user()
    meter = _meter(case, owner)
    _job(case, meter, f"2024-07:{owner.id}")
    _job(case, meter, f"2024-08:{owner.id}", sent=True)
    _job(case, meter, "2024-06-30", kind="low_balance")
    before = _rows(case, meter.id)
    with connect_database(case.settings) as connection:
        monthly_reminders.ensure_monthly_delivery_compatibility(connection)
    assert _rows(case, meter.id) == before


def test_scheduled_pass_forwards_fixed_cutoff_stop_and_bounded_io(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    captured: dict = {}
    stop = Event()
    def finite_pass(settings: Settings, **kwargs):
        captured.update(kwargs)
        return EMPTY_RESULT
    monkeypatch.setattr(reminder_scheduler, "run_monthly_reminders", finite_pass)
    assert reminder_scheduler.run_scheduled_reminders(_settings(), stop) == EMPTY_RESULT
    assert captured["activation_at"] == ACTIVATION
    assert captured["bounded_io"] is True
    assert captured["check_legacy"] is True
    assert captured["should_stop"]() is False
    stop.set()
    assert captured["should_stop"]() is True


def test_reminder_connection_bounds_do_not_change_normal_database_connections(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    case = sharing_case
    _meter(case, case.user())
    def bounds(connection) -> tuple:
        return (connection.execute("SHOW statement_timeout").fetchone()[0],
                connection.execute("SHOW lock_timeout").fetchone()[0])
    with connect_database(case.settings) as connection:
        original_bounds = bounds(connection)
    opened = []
    original = monthly_reminders.connect_database
    def tracked_connect(settings: Settings):
        assert conninfo_to_dict(settings.database_url)["connect_timeout"] == "5"
        connection = original(settings)
        opened.append(connection)
        return connection
    monkeypatch.setattr(monthly_reminders, "connect_database", tracked_connect)
    class ObservingSender(RecordingSender):
        def send(self, message: EmailMessage) -> None:
            assert bounds(opened[-1]) == ("5s", "2s")
            super().send(message)
    sender = ObservingSender()
    result = monthly_reminders.run_monthly_reminders(
        case.settings, activation_at=ACTIVATION, sender=sender, now=NOW, bounded_io=True,
    )
    assert result.messages_sent == 1
    with connect_database(case.settings) as connection:
        assert bounds(connection) == original_bounds


def test_stop_during_discovery_rolls_back_entire_uncommitted_fanout(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    case = sharing_case
    owner, member = case.user(), case.user()
    meter = _meter(case, owner, member)
    stop = Event()
    original = monthly_reminders.claim_reminder_delivery
    def claim_then_stop(*args, **kwargs):
        claim = original(*args, **kwargs)
        stop.set()
        return claim
    monkeypatch.setattr(monthly_reminders, "claim_reminder_delivery", claim_then_stop)
    sender = RecordingSender()
    result = monthly_reminders.run_monthly_reminders(
        case.settings, activation_at=ACTIVATION, sender=sender, now=NOW,
        should_stop=stop.is_set,
    )
    assert result.messages_sent == 0 and not sender.messages
    assert _rows(case, meter.id) == []


def test_stop_after_smtp_finishes_current_commit_and_preserves_remaining_jobs(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner, member = case.user(), case.user()
    meter = _meter(case, owner, member)
    stop = Event()
    class StopAfterSend(RecordingSender):
        def send(self, message: EmailMessage) -> None:
            super().send(message)
            stop.set()
    first = StopAfterSend()
    result = monthly_reminders.run_monthly_reminders(
        case.settings, activation_at=ACTIVATION, sender=first, now=NOW,
        should_stop=stop.is_set,
    )
    assert result.messages_sent == 1
    assert sorted(row[2] for row in _rows(case, meter.id)) == ["pending", "sent"]
    sender = RecordingSender()
    resumed = monthly_reminders.run_monthly_reminders(
        case.settings, activation_at=ACTIVATION, sender=sender, now=NOW + timedelta(minutes=30),
    )
    assert resumed.messages_sent == 1
    assert {message["To"] for message in first.messages + sender.messages} == {owner.email, member.email}
