"""Atomic sharing, signup races and deterministic parent-lock checks."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from queue import Queue
from threading import Barrier
import time
from typing import Any

from pytest import raises, mark

from app.database import connect_database
from app.modules.otp import get_otp_secret
from app.modules.balance_entries import create_balance_entry, delete_balance_entry, update_balance_entry
from app.modules.memberships import LastMemberError, remove_member, share_member
from app.modules.meters import MeterNotFoundError, create_meter, delete_meter, get_meter, rename_meter
from app.modules.otp import issue_otp, verify_otp
from app.modules.reminder_settings import upsert_reminder_settings
from app.modules.top_up_entries import create_top_up_entry, delete_top_up_entry, update_top_up_entry
from tests.support import SharingCase


class FailingMembershipInsert:
    """Raise only after the parent/user insert, without adding database triggers."""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def __getattr__(self, name: str) -> Any:
        return getattr(self.connection, name)

    def execute(self, query: str, params: Any = None) -> Any:
        if "INSERT INTO monitor.user_meters" in query:
            raise RuntimeError("Synthetic membership failure")
        return self.connection.execute(query, params)


def wait_for_locks(case: SharingCase, pids: list[int]) -> None:
    """Observe real PostgreSQL lock waits instead of relying on thread timing."""
    deadline = time.monotonic() + 10
    with connect_database() as observer:
        while time.monotonic() < deadline:
            waiting = observer.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE pid = ANY(%s) AND wait_event_type = 'Lock'", (pids,)
            ).fetchone()[0]
            if waiting == len(pids):
                return
            observer.commit()
            time.sleep(0.02)
    raise AssertionError("Synthetic workers never reached the expected parent lock")


def test_failed_membership_insert_rolls_back_new_user_and_meter(sharing_case: SharingCase) -> None:
    """Creation/sharing are atomic even when the final membership write fails."""
    case = sharing_case
    owner = case.user()
    email = case.email("rollback")
    with connect_database() as connection:
        meter = create_meter(connection, owner.id, "Existing")
        proxy = FailingMembershipInsert(connection)
        with raises(RuntimeError, match="Synthetic"):
            create_meter(proxy, owner.id, "Must roll back")
        with raises(RuntimeError, match="Synthetic"):
            share_member(proxy, meter.id, owner.id, email)
        assert connection.execute("SELECT count(*) FROM monitor.meters WHERE name = 'Must roll back' AND user_id = %s", (owner.id,)).fetchone() == (0,)
        assert connection.execute("SELECT count(*) FROM monitor.users WHERE email = %s", (email,)).fetchone() == (0,)
        assert connection.execute("SELECT count(*) FROM monitor.user_meters WHERE meter_id = %s", (meter.id,)).fetchone() == (1,)


def test_concurrent_duplicate_shares_create_one_user_and_membership(sharing_case: SharingCase) -> None:
    """Concurrent duplicate requests return the same existing account ID."""
    case = sharing_case
    owner = case.user()
    email = case.email("duplicate")
    with connect_database() as connection:
        meter = create_meter(connection, owner.id, "Concurrent")
    barrier = Barrier(2)
    def share() -> int:
        with connect_database() as connection:
            barrier.wait(timeout=10)
            return share_member(connection, meter.id, owner.id, email).user_id
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = [executor.submit(share) for _ in range(2)]
        ids = [job.result(timeout=15) for job in jobs]
    assert ids[0] == ids[1]
    with connect_database() as connection:
        assert connection.execute("SELECT count(*) FROM monitor.users WHERE email = %s", (email,)).fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM monitor.user_meters WHERE meter_id = %s AND user_id = %s", (meter.id, ids[0])).fetchone() == (1,)


def test_signup_and_sharing_race_reuse_one_regular_user(sharing_case: SharingCase) -> None:
    """A verified signup concurrent with provisioning never duplicates/promotes."""
    case = sharing_case
    owner = case.user()
    email = case.email("signup-race")
    secret = get_otp_secret()
    with connect_database() as connection:
        meter = create_meter(connection, owner.id, "Signup race")
        otp = issue_otp(connection, email, secret)
    barrier = Barrier(2)
    def share() -> int:
        with connect_database() as connection:
            barrier.wait(timeout=10)
            return share_member(connection, meter.id, owner.id, email).user_id
    def signup() -> int:
        with connect_database() as connection:
            barrier.wait(timeout=10)
            return verify_otp(connection, email, otp.code, secret).id
    with ThreadPoolExecutor(max_workers=2) as executor:
        shared, signed = executor.submit(share), executor.submit(signup)
        assert shared.result(timeout=15) == signed.result(timeout=15)
    with connect_database() as connection:
        assert connection.execute("SELECT count(*), min(type) FROM monitor.users WHERE email = %s", (email,)).fetchone() == (1, "user")


def test_concurrent_last_member_removals_leave_one_member(sharing_case: SharingCase) -> None:
    """Two genuinely blocked removals serialize, rejecting the last departure."""
    case = sharing_case
    owner, member = case.user(), case.user()
    with connect_database() as connection:
        meter = create_meter(connection, owner.id, "Last member")
        share_member(connection, meter.id, owner.id, member.email)
    pids: Queue[int] = Queue()
    def leave(user_id: int) -> str:
        with connect_database() as connection:
            pids.put(connection.execute("SELECT pg_backend_pid()").fetchone()[0])
            try:
                remove_member(connection, meter.id, user_id, user_id)
                return "removed"
            except LastMemberError:
                return "last-member-rejected"
    with connect_database() as blocker, ThreadPoolExecutor(max_workers=2) as executor:
        blocker.execute("SELECT id FROM monitor.meters WHERE id = %s FOR UPDATE", (meter.id,))
        jobs = [executor.submit(leave, person.id) for person in (owner, member)]
        try:
            wait_for_locks(case, [pids.get(timeout=10), pids.get(timeout=10)])
        finally:
            blocker.commit()
        assert sorted(job.result(timeout=15) for job in jobs) == ["last-member-rejected", "removed"]
    with connect_database() as connection:
        assert connection.execute("SELECT count(*) FROM monitor.user_meters WHERE meter_id = %s", (meter.id,)).fetchone() == (1,)


@mark.parametrize("operation", ["share", "remove", "delete", "rename", "balance_create", "balance_update", "balance_delete", "top_up_create", "top_up_update", "top_up_delete", "reminders"])
def test_waited_mutation_rechecks_revoked_access(sharing_case: SharingCase, operation: str) -> None:
    """A request waiting for the parent lock cannot use its stale membership."""
    case = sharing_case
    owner, member = case.user(), case.user()
    email = case.email("must-not-provision")
    occurred = datetime.now(UTC) - timedelta(days=1)
    entry = None
    with connect_database() as connection:
        meter = create_meter(connection, owner.id, "Before revoke")
        share_member(connection, meter.id, owner.id, member.email)
        if operation in {"balance_update", "balance_delete"}:
            entry = create_balance_entry(connection, meter.id, owner.id, Decimal("20"), occurred)
        elif operation in {"top_up_update", "top_up_delete"}:
            entry = create_top_up_entry(connection, meter.id, owner.id, Decimal("20"), occurred)
    pids: Queue[int] = Queue()
    def mutate() -> None:
        with connect_database() as connection:
            pids.put(connection.execute("SELECT pg_backend_pid()").fetchone()[0])
            if operation == "share":
                share_member(connection, meter.id, member.id, email)
            elif operation == "remove":
                remove_member(connection, meter.id, member.id, owner.id)
            elif operation == "delete":
                delete_meter(connection, meter.id, member.id)
            elif operation == "rename":
                rename_meter(connection, meter.id, member.id, "Forbidden")
            elif operation == "balance_create":
                create_balance_entry(connection, meter.id, member.id, Decimal("20"), occurred)
            elif operation == "balance_update":
                update_balance_entry(connection, meter.id, entry.id, member.id, Decimal("99"), occurred)
            elif operation == "balance_delete":
                delete_balance_entry(connection, meter.id, entry.id, member.id)
            elif operation == "top_up_create":
                create_top_up_entry(connection, meter.id, member.id, Decimal("20"), occurred)
            elif operation == "top_up_update":
                update_top_up_entry(connection, meter.id, entry.id, member.id, Decimal("99"), occurred)
            elif operation == "top_up_delete":
                delete_top_up_entry(connection, meter.id, entry.id, member.id)
            else:
                upsert_reminder_settings(connection, meter.id, member.id, monthly_enabled=False,
                    monthly_day=1, low_balance_enabled=False, low_balance_days=Decimal("3"), timezone="UTC")
    with connect_database() as blocker, ThreadPoolExecutor(max_workers=1) as executor:
        blocker.execute("SELECT id FROM monitor.meters WHERE id = %s FOR UPDATE", (meter.id,))
        job = executor.submit(mutate)
        try:
            wait_for_locks(case, [pids.get(timeout=10)])
            blocker.execute("DELETE FROM monitor.user_meters WHERE meter_id = %s AND user_id = %s", (meter.id, member.id))
        finally:
            blocker.commit()
        with raises(MeterNotFoundError):
            job.result(timeout=15)
    with connect_database() as connection:
        assert get_meter(connection, meter.id, owner.id).name == "Before revoke"
        assert connection.execute("SELECT count(*) FROM monitor.users WHERE email = %s", (email,)).fetchone() == (0,)
        for table, prefix, amount in (("balance_entries", "balance", "balance_kwh"), ("top_up_entries", "top_up", "top_up_kwh")):
            expected = [(Decimal("20"),)] if entry is not None and operation.startswith(prefix) else []
            assert connection.execute(f"SELECT {amount} FROM monitor.{table} WHERE meter_id = %s", (meter.id,)).fetchall() == expected
        assert connection.execute("SELECT count(*) FROM monitor.reminder_settings WHERE meter_id = %s", (meter.id,)).fetchone() == (0,)
