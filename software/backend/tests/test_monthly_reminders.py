"""Finite monthly dispatch checks against synthetic, isolated database fixtures."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from email.message import EmailMessage
from queue import Queue
from threading import Event
from uuid import UUID, uuid4

from psycopg.pq import TransactionStatus
from pytest import MonkeyPatch, mark, raises

from app.database import connect_database
from app.modules import monthly_reminders
from app.modules.balance_entries import create_balance_entry
from app.modules.email_delivery import EmailDeliveryError
from app.modules.memberships import remove_member, share_member
from app.modules.meters import Meter, create_meter, delete_meter
from app.modules.top_up_entries import create_top_up_entry
from tests.support import Person, SharingCase
from tests.test_reminder_runner import RecordingSender
from tests.test_sharing_transactions import wait_for_locks

NOW = datetime(2024, 6, 30, 9, tzinfo=UTC)
ACTIVATION = datetime(2024, 6, 1, tzinfo=UTC)


def _meter(case: SharingCase, owner: Person, *members: Person) -> Meter:
    """Commit a meter predating the synthetic clock, never change seed records."""
    with connect_database(case.settings) as connection:
        meter = create_meter(connection, owner.id, f"Monthly {uuid4().hex[:8]}")
        connection.execute(
            "UPDATE monitor.meters SET created_at = %s WHERE id = %s",
            (datetime(2020, 1, 1, tzinfo=UTC), meter.id),
        )
        for member in members:
            share_member(connection, meter.id, owner.id, member.email)
    return meter


def _rows(case: SharingCase, meter_id: UUID) -> list[tuple]:
    """Read committed delivery state through an independent connection."""
    with connect_database(case.settings) as connection:
        return connection.execute(
            """SELECT id, dedupe_key, status, claimed_at, sent_at, reminder_type
               FROM monitor.reminder_deliveries WHERE meter_id = %s
               ORDER BY dedupe_key, reminder_type""", (meter_id,)
        ).fetchall()


def _job(case: SharingCase, meter: Meter, key: str, *, kind: str = "monthly",
         sent: bool = False, claimed_at: datetime = NOW - timedelta(hours=1)) -> UUID:
    """Persist one exact synthetic pending/sent job, including legacy fixtures."""
    job_id = uuid4()
    with connect_database(case.settings) as connection:
        connection.execute(
            """INSERT INTO monitor.reminder_deliveries
               (id, meter_id, reminder_type, dedupe_key, status, claimed_at, sent_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (job_id, meter.id, kind, key, "sent" if sent else "pending",
             claimed_at, claimed_at if sent else None),
        )
    return job_id


def _run(case: SharingCase, sender: RecordingSender, now: datetime = NOW,
         activation: datetime = ACTIVATION):
    return monthly_reminders.run_monthly_reminders(
        case.settings, activation_at=activation, sender=sender, now=now,
    )


@mark.parametrize(("clock", "key"), [
    ("2024-02-28T09:00:00+00:00", None),
    ("2024-02-29T08:59:59+00:00", None),
    ("2024-02-29T09:00:00+00:00", "2024-03"),
    ("2023-02-28T09:00:00+00:00", "2023-03"),
    ("2024-04-30T09:00:00+00:00", "2024-05"),
    ("2024-06-30T09:00:00+00:00", "2024-07"),
    ("2024-06-30T11:00:00+02:00", "2024-07"),
    ("2024-12-31T09:00:00+00:00", "2025-01"),
])
def test_utc_month_end_boundary_and_target_cycle(
    sharing_case: SharingCase, clock: str, key: str | None,
) -> None:
    """Calendar length, leap days and year rollover use target, not send month."""
    case = sharing_case
    owner = case.user()
    meter = _meter(case, owner)
    now = datetime.fromisoformat(clock)
    activation = now.replace(day=1, hour=0, minute=0, second=0)
    sender = RecordingSender()
    result = _run(case, sender, now, activation)
    assert result.messages_sent == (1 if key else 0)
    assert [row[1] for row in _rows(case, meter.id)] == (
        [f"{key}:{owner.id}"] if key else []
    )


def test_explicit_aware_cutoff_and_clock_are_required(sharing_case: SharingCase) -> None:
    """Reject ambiguous clocks before discovering or sending any work."""
    case = sharing_case
    sender = RecordingSender()
    with raises(TypeError):
        monthly_reminders.run_monthly_reminders(case.settings, sender=sender, now=NOW)
    with raises(ValueError):
        _run(case, sender, activation=ACTIVATION.replace(tzinfo=None))
    with raises(ValueError):
        _run(case, sender, now=NOW.replace(tzinfo=None))
    assert not sender.messages


@mark.parametrize("offset, expected", [(0, 1), (1, 0)])
def test_activation_cutoff_is_inclusive(
    sharing_case: SharingCase, offset: int, expected: int,
) -> None:
    case = sharing_case
    meter = _meter(case, case.user())
    sender = RecordingSender()
    result = _run(case, sender, activation=NOW + timedelta(microseconds=offset))
    assert result.messages_sent == expected
    assert len(_rows(case, meter.id)) == expected


def test_discovery_uses_latest_cycle_and_excludes_newer_meters(sharing_case: SharingCase) -> None:
    """Downtime creates only the newest missed cycle, not a historical burst."""
    case = sharing_case
    owner = case.user()
    old = _meter(case, owner)
    new = _meter(case, owner)
    with connect_database(case.settings) as connection:
        connection.execute(
            "UPDATE monitor.meters SET created_at = %s WHERE id = %s",
            (NOW + timedelta(microseconds=1), new.id),
        )
    sender = RecordingSender()
    assert _run(case, sender, NOW + timedelta(days=10), datetime(2020, 1, 1, tzinfo=UTC)).messages_sent == 1
    assert [row[1] for row in _rows(case, old.id)] == [f"2024-07:{owner.id}"]
    assert _rows(case, new.id) == []


def test_current_late_members_receive_without_preferences_or_admin_override(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    creator, member, late = case.user("admin"), case.user(), case.user()
    case.user("admin")  # Global access alone must never become a recipient.
    meter = _meter(case, creator, member, late)
    with connect_database(case.settings) as connection:
        remove_member(connection, meter.id, member.id, creator.id)
        assert connection.execute(
            "SELECT count(*) FROM monitor.reminder_settings WHERE meter_id = %s", (meter.id,)
        ).fetchone() == (0,)
    sender = RecordingSender()
    assert _run(case, sender).messages_sent == 2
    assert {message["To"] for message in sender.messages} == {member.email, late.email}
    assert {row[1] for row in _rows(case, meter.id)} == {
        f"2024-07:{member.id}", f"2024-07:{late.id}",
    }


def test_full_fanout_and_each_success_are_committed_before_next_send(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner, second, third = case.user(), case.user(), case.user()
    meter = _meter(case, owner, second, third)
    other_meter = _meter(case, owner)
    expected = {f"2024-07:{person.id}" for person in (owner, second, third)}
    class ObservingSender(RecordingSender):
        def send(self, message: EmailMessage) -> None:
            rows = _rows(case, meter.id)
            assert {row[1] for row in rows} == expected
            other_rows = _rows(case, other_meter.id)
            assert [row[1] for row in other_rows] == [f"2024-07:{owner.id}"]
            rows += other_rows
            assert sum(row[2] == "sent" for row in rows) == len(self.messages)
            super().send(message)
    sender = ObservingSender()
    assert _run(case, sender).messages_sent == 4
    assert all(row[2] == "sent" for row in _rows(case, meter.id))


def test_failure_stays_pending_until_lease_expiry_without_resending_successes(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner, other = case.user(), case.user()
    meter = _meter(case, owner, other)
    class FailFirstSender(RecordingSender):
        failed_email: str | None = None
        def send(self, message: EmailMessage) -> None:
            if self.failed_email is None:
                self.failed_email = message["To"]
                raise EmailDeliveryError("Synthetic recipient failure")
            super().send(message)
    failing = FailFirstSender()
    first = _run(case, failing)
    original = _rows(case, meter.id)
    assert (first.messages_sent, first.delivery_failures) == (1, 1)
    assert sorted(row[2] for row in original) == ["pending", "sent"]
    sender = RecordingSender()
    assert _run(case, sender, NOW + timedelta(minutes=29, seconds=59)).messages_sent == 0
    assert _run(case, sender, NOW + timedelta(minutes=30)).messages_sent == 1
    assert [message["To"] for message in sender.messages] == [failing.failed_email]
    final = _rows(case, meter.id)
    assert [(row[0], row[1]) for row in final] == [(row[0], row[1]) for row in original]
    assert all(row[2] == "sent" for row in final)
    original_sent = next(row for row in original if row[2] == "sent")
    assert next(row for row in final if row[0] == original_sent[0]) == original_sent


def test_old_pending_cycles_retry_but_legacy_and_sent_history_are_untouched(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner = case.user()
    meter = _meter(case, owner)
    old_id = _job(case, meter, f"2023-12:{owner.id}")
    _job(case, meter, f"2024-01:{owner.id}")
    _job(case, meter, f"2024-02:{owner.id}", sent=True)
    _job(case, meter, "2024-06")
    _job(case, meter, "2024-06-30", kind="low_balance")
    _job(case, meter, "invalid-monthly-key")
    _job(case, meter, f"2024-13:{owner.id}")
    _job(case, meter, f"2025-01:{owner.id}")
    before = _rows(case, meter.id)
    sender = RecordingSender()
    assert _run(case, sender, activation=NOW + timedelta(days=365)).messages_sent == 2
    after = _rows(case, meter.id)
    changed = {old_id, next(row[0] for row in before if row[1] == f"2024-01:{owner.id}")}
    assert all(row[2] == "sent" for row in after if row[0] in changed)
    assert [row for row in after if row[0] not in changed] == [row for row in before if row[0] not in changed]
    assert {row[1] for row in after} == {row[1] for row in before}


def test_removed_member_pending_job_is_not_sent_and_deletion_cascades(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    case = sharing_case
    owner, member = case.user(), case.user()
    meter = _meter(case, owner, member)
    _job(case, meter, f"2024-01:{owner.id}")
    _job(case, meter, f"2024-01:{member.id}")
    deleted = _meter(case, owner)
    _job(case, deleted, f"2024-01:{owner.id}")
    original = monthly_reminders._deliver_job
    changed = False
    def mutate_after_selection(connection, *args):
        nonlocal changed
        if not changed:
            changed = True
            with connect_database(case.settings) as writer:
                remove_member(writer, meter.id, member.id, owner.id)
                delete_meter(writer, deleted.id, owner.id)
        return original(connection, *args)
    monkeypatch.setattr(monthly_reminders, "_deliver_job", mutate_after_selection)
    sender = RecordingSender()
    assert _run(case, sender, activation=NOW + timedelta(days=365)).messages_sent == 1
    assert [message["To"] for message in sender.messages] == [member.email]
    assert next(row for row in _rows(case, meter.id) if row[1].endswith(f":{owner.id}"))[2] == "pending"
    assert _rows(case, deleted.id) == []


def test_worker_rechecks_lease_ownership_after_another_worker_reclaims(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    """An observed stale row is not permission to send after its lease changes."""
    case = sharing_case
    owner = case.user()
    meter = _meter(case, owner)
    job_id = _job(case, meter, f"2024-01:{owner.id}")
    original = monthly_reminders._deliver_job
    reclaimed = False
    def reclaim_before_lock(connection, *args):
        nonlocal reclaimed
        if not reclaimed:
            reclaimed = True
            result = _run(case, RecordingSender(fail=True), NOW + timedelta(minutes=31),
                          NOW + timedelta(days=365))
            assert result.delivery_failures == 1
        return original(connection, *args)
    monkeypatch.setattr(monthly_reminders, "_deliver_job", reclaim_before_lock)
    sender = RecordingSender()
    result = _run(case, sender, activation=NOW + timedelta(days=365))
    assert (result.messages_sent, result.duplicates_skipped) == (0, 1)
    assert not sender.messages
    row = _rows(case, meter.id)[0]
    assert row[:3] == (job_id, f"2024-01:{owner.id}", "pending")
    assert row[3] == NOW + timedelta(minutes=31)
    assert _run(case, sender, NOW + timedelta(minutes=61), NOW + timedelta(days=365)).messages_sent == 1


def test_delayed_message_keeps_notification_cycle_and_uses_fresh_forecast(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner = case.user()
    meter = _meter(case, owner)
    now = datetime(2024, 7, 20, 10, tzinfo=UTC)
    _job(case, meter, f"2024-02:{owner.id}")
    with connect_database(case.settings) as connection:
        create_balance_entry(connection, meter.id, owner.id, Decimal("450"), now - timedelta(days=30))
        create_top_up_entry(connection, meter.id, owner.id, Decimal("300"), now - timedelta(days=15))
        create_balance_entry(connection, meter.id, owner.id, Decimal("300"), now)
    sender = RecordingSender()
    assert _run(case, sender, now, now + timedelta(days=365)).messages_sent == 1
    body = sender.messages[0].get_content()
    assert "2024-02" in body and "2024-08-01" in body
    assert "165.000 additional kWh" in body and "31-day" in body
    assert _rows(case, meter.id)[0][1] == f"2024-02:{owner.id}"


def test_unavailable_history_requests_actual_reading_without_estimate(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    _meter(case, case.user())
    sender = RecordingSender()
    assert _run(case, sender).messages_sent == 1
    body = sender.messages[0].get_content()
    assert "fresh balance" in body and "2024-07-01" in body
    assert "additional kWh" not in body and "may run low" not in body


def test_multiline_meter_name_cannot_inject_headers_or_abort_other_recipients(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner, other = case.user(), case.user()
    meter = _meter(case, owner)
    _meter(case, other)
    with connect_database(case.settings) as connection:
        connection.execute(
            "UPDATE monitor.meters SET name = %s WHERE id = %s",
            ("Home\r\nBcc: nobody@example.test", meter.id),
        )
    sender = RecordingSender()
    assert _run(case, sender).messages_sent == 2
    assert {message["To"] for message in sender.messages} == {owner.email, other.email}
    assert all(message["Bcc"] is None and "\n" not in str(message["Subject"])
               for message in sender.messages)


def test_unrepresentable_runout_keeps_job_pending_and_other_meter_continues(
    sharing_case: SharingCase,
) -> None:
    """Valid stored extremes must not abort the pass or invent an estimate."""
    case = sharing_case
    owner, other = case.user(), case.user()
    meter = _meter(case, owner)
    _meter(case, other)
    with connect_database(case.settings) as connection:
        create_balance_entry(connection, meter.id, owner.id, Decimal("999999999.999"),
                             NOW - timedelta(days=1))
        create_balance_entry(connection, meter.id, owner.id, Decimal("999999999.998"), NOW)
    sender = RecordingSender()
    result = _run(case, sender)
    assert (result.messages_sent, result.delivery_failures) == (1, 1)
    assert [message["To"] for message in sender.messages] == [other.email]
    assert _rows(case, meter.id)[0][2] == "pending"


def test_owned_connection_never_commits_unrelated_caller_work(sharing_case: SharingCase) -> None:
    case = sharing_case
    owner = case.user()
    with connect_database(case.settings) as connection:
        connection.execute("SELECT 1")  # Make repository transactions nested savepoints.
        meter = create_meter(connection, owner.id, "Uncommitted monthly fixture")
        connection.execute(
            "UPDATE monitor.meters SET created_at = %s WHERE id = %s", (ACTIVATION, meter.id)
        )
        assert _run(case, RecordingSender()).messages_sent == 0
        assert connection.info.transaction_status == TransactionStatus.INTRANS
        connection.rollback()
    with connect_database(case.settings) as observer:
        assert observer.execute("SELECT id FROM monitor.meters WHERE id = %s", (meter.id,)).fetchone() is None


def test_overlapping_workers_do_not_send_the_same_valid_claim(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch,
) -> None:
    case = sharing_case
    _meter(case, case.user())
    entered, release = Event(), Event()
    pids: Queue[int] = Queue()
    original = monthly_reminders.connect_database
    def tracked_connect(settings):
        connection = original(settings)
        connection.autocommit = True
        pids.put(connection.execute("SELECT pg_backend_pid()").fetchone()[0])
        return connection
    monkeypatch.setattr(monthly_reminders, "connect_database", tracked_connect)
    class BlockingSender(RecordingSender):
        def send(self, message: EmailMessage) -> None:
            entered.set()
            assert release.wait(timeout=15)
            super().send(message)
    first, second = BlockingSender(), RecordingSender()
    with ThreadPoolExecutor(max_workers=2) as executor:
        job = executor.submit(_run, case, first)
        try:
            assert entered.wait(timeout=10)
            pids.get(timeout=10)
            overlap = executor.submit(_run, case, second)
            wait_for_locks(case, [pids.get(timeout=10)])
            assert not second.messages
        finally:
            release.set()
        assert job.result(timeout=15).messages_sent == 1
        assert overlap.result(timeout=15).messages_sent == 0
    assert len(first.messages) == 1 and not second.messages


def test_membership_revocation_waits_for_send_then_stops_later_cycles(
    sharing_case: SharingCase,
) -> None:
    case = sharing_case
    owner, member = case.user(), case.user()
    meter = _meter(case, owner, member)
    entered, release = Event(), Event()
    pids: Queue[int] = Queue()
    class BlockingSender(RecordingSender):
        def send(self, message: EmailMessage) -> None:
            if message["To"] == owner.email:
                entered.set()
                assert release.wait(timeout=15)
            super().send(message)
    def revoke() -> None:
        with connect_database(case.settings) as connection:
            pids.put(connection.execute("SELECT pg_backend_pid()").fetchone()[0])
            remove_member(connection, meter.id, member.id, owner.id)
    sender = BlockingSender()
    with ThreadPoolExecutor(max_workers=2) as executor:
        dispatch = executor.submit(_run, case, sender)
        try:
            assert entered.wait(timeout=10)
            removal = executor.submit(revoke)
            wait_for_locks(case, [pids.get(timeout=10)])
        finally:
            release.set()
        assert dispatch.result(timeout=15).messages_sent == 2
        removal.result(timeout=15)
    next_sender = RecordingSender()
    assert _run(case, next_sender, datetime(2024, 7, 31, 9, tzinfo=UTC)).messages_sent == 1
    assert [message["To"] for message in next_sender.messages] == [member.email]
