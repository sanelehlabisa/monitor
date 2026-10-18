"""Legacy creator reminders remain safe when memberships change during dispatch."""

from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event

from pytest import MonkeyPatch

from app.database import connect_database
from app.modules import reminder_runner
from app.modules.memberships import remove_member, share_member
from tests.support import SharingCase
from tests.test_reminder_runner import NOW, RecordingSender, _configured_meter
from tests.test_sharing_transactions import wait_for_locks


def test_removed_admin_creator_is_not_a_reminder_recipient(sharing_case: SharingCase) -> None:
    """Global admin privilege does not restore legacy recipient membership."""
    case = sharing_case
    creator, member = case.user("admin"), case.user()
    with connect_database(case.settings) as connection:
        meter = _configured_meter(connection, creator.id)
        share_member(connection, meter.id, creator.id, member.email)
        remove_member(connection, meter.id, member.id, creator.id)
        sender = RecordingSender()
        result = reminder_runner.run_due_reminders(connection, case.settings, sender, NOW)
    assert result.messages_sent == 0
    assert sender.messages == []


def test_removal_after_candidate_selection_does_not_abort_other_meters(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch
) -> None:
    """A stale candidate is skipped while another eligible creator still receives."""
    case = sharing_case
    creator, member, other = case.user(), case.user(), case.user()
    with connect_database(case.settings) as connection:
        stale = _configured_meter(connection, creator.id, "Stale")
        share_member(connection, stale.id, creator.id, member.email)
        _configured_meter(connection, other.id, "Still eligible")
    original = reminder_runner.list_reminder_candidates
    def select_then_remove(connection):
        candidates = original(connection)
        with connect_database(case.settings) as revoker:
            remove_member(revoker, stale.id, member.id, creator.id)
        return candidates
    monkeypatch.setattr(reminder_runner, "list_reminder_candidates", select_then_remove)
    sender = RecordingSender()
    with connect_database(case.settings) as connection:
        result = reminder_runner.run_due_reminders(connection, case.settings, sender, NOW)
    assert result.messages_sent == 2
    assert {message["To"] for message in sender.messages} == {other.email}


def test_eligibility_is_rechecked_immediately_before_send(
    sharing_case: SharingCase, monkeypatch: MonkeyPatch
) -> None:
    """A same-transaction mutation hook exercises the final recheck without SMTP."""
    case = sharing_case
    creator, member, other = case.user(), case.user(), case.user()
    with connect_database(case.settings) as connection:
        stale = _configured_meter(connection, creator.id, "Before send")
        share_member(connection, stale.id, creator.id, member.email)
        _configured_meter(connection, other.id, "Continue")
    original = reminder_runner.claim_reminder_delivery
    def claim_then_remove(connection, meter_id, *args):
        claim = original(connection, meter_id, *args)
        if meter_id == stale.id:
            connection.execute("DELETE FROM monitor.user_meters WHERE meter_id = %s AND user_id = %s", (stale.id, creator.id))
        return claim
    monkeypatch.setattr(reminder_runner, "claim_reminder_delivery", claim_then_remove)
    sender = RecordingSender()
    with connect_database(case.settings) as connection:
        result = reminder_runner.run_due_reminders(connection, case.settings, sender, NOW)
    assert result.messages_sent == 2
    assert {message["To"] for message in sender.messages} == {other.email}
    # The synthetic hook is rolled back with the stale candidate's transaction;
    # this checks the recheck branch, not a claim that concurrent removal bypasses locks.


def test_revocation_waits_until_dispatch_lock_is_released(sharing_case: SharingCase) -> None:
    """A concurrent removal waits for dispatch, then prevents the next run."""
    case = sharing_case
    creator, member = case.user(), case.user()
    with connect_database(case.settings) as connection:
        meter = _configured_meter(connection, creator.id)
        share_member(connection, meter.id, creator.id, member.email)
    entered, release = Event(), Event()
    pids: Queue[int] = Queue()
    class BlockingSender(RecordingSender):
        def send(self, message):
            if not self.messages:
                entered.set()
                assert release.wait(timeout=15)
            super().send(message)
    sender = BlockingSender()
    def dispatch():
        with connect_database(case.settings) as connection:
            return reminder_runner.run_due_reminders(connection, case.settings, sender, NOW)
    def revoke():
        with connect_database(case.settings) as connection:
            pids.put(connection.execute("SELECT pg_backend_pid()").fetchone()[0])
            remove_member(connection, meter.id, member.id, creator.id)
    with ThreadPoolExecutor(max_workers=2) as executor:
        dispatch_job = executor.submit(dispatch)
        try:
            assert entered.wait(timeout=10)
            revoke_job = executor.submit(revoke)
            wait_for_locks(case, [pids.get(timeout=10)])
        finally:
            release.set()
        assert dispatch_job.result(timeout=15).messages_sent == 2
        revoke_job.result(timeout=15)
    with connect_database(case.settings) as connection:
        assert reminder_runner.run_due_reminders(connection, case.settings, RecordingSender(), NOW).messages_sent == 0
