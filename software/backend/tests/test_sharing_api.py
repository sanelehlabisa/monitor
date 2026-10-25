"""Sharing behavior and every protected route on synthetic meter fixtures."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from pytest import raises
from psycopg.errors import ForeignKeyViolation

from app.database import connect_database
from app.modules.otp import get_otp_secret
from app.endpoints.auth import COOKIE_NAME
from app.modules.otp import issue_otp
from tests.support import SharingCase


def test_share_provisions_normalized_user_without_login_bypass(sharing_case: SharingCase) -> None:
    """Pre-created membership is idempotent but ordinary OTP is still required."""
    case = sharing_case
    owner, admin = case.user(), case.user("admin")
    meter = owner.client.post("/api/meters", json={"name": "Shared home"}).json()
    url = f"/api/meters/{meter['id']}/members"
    email = case.email("new-member")
    first = owner.client.post(url, json={"email": f" {email.upper()} "})
    repeated = owner.client.post(url, json={"email": email})
    assert first.status_code == repeated.status_code == 200
    assert first.json() == repeated.json()
    assert set(first.json()) == {"user_id", "email"}
    assert first.json()["email"] == email
    assert owner.client.post(url, json={"email": admin.email}).status_code == 200
    with connect_database() as connection:
        assert connection.execute("SELECT type FROM monitor.users WHERE email = %s", (email,)).fetchone() == ("user",)
        assert connection.execute("SELECT type FROM monitor.users WHERE id = %s", (admin.id,)).fetchone() == ("admin",)
        assert connection.execute("SELECT count(*) FROM monitor.user_sessions WHERE user_id = %s", (first.json()["user_id"],)).fetchone() == (0,)
        assert connection.execute("SELECT count(*) FROM monitor.otp_challenges WHERE email = %s", (email,)).fetchone() == (0,)
    client = case.client()
    assert client.get("/api/me").status_code == 401
    client.cookies.set(COOKIE_NAME, email)
    assert client.get(f"/api/meters/{meter['id']}").status_code == 401
    client.cookies.clear()
    assert client.post("/api/auth/verify-otp", json={"email": email, "code": "000000"}).status_code == 401
    with connect_database() as connection:
        otp = issue_otp(connection, email, get_otp_secret())
    verified = client.post("/api/auth/verify-otp", json={"email": email, "code": otp.code})
    assert verified.status_code == 200
    assert verified.json()["id"] == first.json()["user_id"]
    assert verified.json()["is_admin"] is False
    assert client.get(f"/api/meters/{meter['id']}").status_code == 200
    assert owner.client.post(url, json={"email": "not-an-email"}).status_code == 422


def test_member_email_search_deduplicates_and_creator_is_only_metadata(sharing_case: SharingCase) -> None:
    """Removed creators lose access/search matches, while shared members retain it."""
    case = sharing_case
    owner, member, other, admin = case.user(), case.user(), case.user(), case.user("admin")
    meter = owner.client.post("/api/meters", json={"name": "Shared home"}).json()
    url = f"/api/meters/{meter['id']}"
    for person in (member, other):
        assert owner.client.post(url + "/members", json={"email": person.email}).status_code == 200
    assert [item["id"] for item in member.client.get("/api/meters", params={"q": other.email.upper()}).json()] == [meter["id"]]
    assert [item["id"] for item in member.client.get("/api/meters", params={"q": "example.test"}).json()] == [meter["id"]]
    assert member.client.delete(url + f"/members/{owner.id}").status_code == 204
    assert owner.client.get(url).status_code == 404
    assert owner.client.get("/api/meters").json() == []
    assert admin.client.get("/api/meters", params={"q": owner.email}).json() == []
    assert member.client.get(url).json()["owner_email"] == owner.email
    assert member.client.patch(url, json={"name": "Updated by member"}).status_code == 200
    with connect_database() as connection:
        with raises(ForeignKeyViolation):
            with connection.transaction():
                connection.execute("DELETE FROM monitor.users WHERE id = %s", (owner.id,))
        assert connection.execute("SELECT 1 FROM monitor.meters WHERE id = %s", (UUID(meter["id"]),)).fetchone() == (1,)


def test_all_protected_paths_deny_nonmembers_and_immediate_removal(sharing_case: SharingCase) -> None:
    """Every protected resource checks scope; denied sharing creates no accounts."""
    case = sharing_case
    owner, member, outsider = case.user(), case.user(), case.user()
    meter = owner.client.post("/api/meters", json={"name": "Protected home"}).json()
    base = f"/api/meters/{meter['id']}"
    assert owner.client.post(base + "/members", json={"email": member.email}).status_code == 200
    occurred = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    balance = owner.client.post(base + "/balances", json={"balance_kwh": "40", "occurred_at": occurred}).json()
    top_up = owner.client.post(base + "/top-ups", json={"top_up_kwh": "20", "occurred_at": occurred}).json()
    target_email = case.email("must-not-exist")
    settings = {"monthly_enabled": False, "monthly_day": 1, "low_balance_enabled": False, "low_balance_days": "3", "timezone": "UTC"}
    operations = [
        ("GET", base, None), ("PATCH", base, {"name": "Denied"}), ("DELETE", base, None),
        ("GET", base + "/dashboard", None),
        ("GET", base + "/balances", None), ("POST", base + "/balances", {"balance_kwh": "30", "occurred_at": occurred}),
        ("GET", base + f"/balances/{balance['id']}", None),
        ("PATCH", base + f"/balances/{balance['id']}", {"balance_kwh": "30", "occurred_at": occurred}),
        ("DELETE", base + f"/balances/{balance['id']}", None),
        ("GET", base + "/top-ups", None), ("POST", base + "/top-ups", {"top_up_kwh": "30", "occurred_at": occurred}),
        ("GET", base + f"/top-ups/{top_up['id']}", None),
        ("PATCH", base + f"/top-ups/{top_up['id']}", {"top_up_kwh": "30", "occurred_at": occurred}),
        ("DELETE", base + f"/top-ups/{top_up['id']}", None),
        ("GET", base + "/reminders", None), ("PATCH", base + "/reminders", settings),
        ("GET", base + "/members", None), ("POST", base + "/members", {"email": target_email}),
        ("DELETE", base + f"/members/{owner.id}", None),
    ]
    anonymous = case.client()
    assert anonymous.get("/api/meters").status_code == 401
    assert anonymous.post("/api/meters", json={"name": "Denied"}).status_code == 401
    for method, path, payload in operations:
        assert anonymous.request(method, path, json=payload).status_code == 401, (method, path)
        assert outsider.client.request(method, path, json=payload).status_code == 404, (method, path)
    assert owner.client.delete(base + f"/members/{member.id}").status_code == 204
    for method, path, payload in operations:
        assert member.client.request(method, path, json=payload).status_code == 404, (method, path)
    for person in (outsider, member):
        assert person.client.get("/api/meters").json() == []
        assert person.client.get("/api/meters", params={"q": owner.email}).json() == []
    with connect_database() as connection:
        assert connection.execute("SELECT count(*) FROM monitor.users WHERE email = %s", (target_email,)).fetchone() == (0,)
        assert connection.execute("SELECT balance_kwh FROM monitor.balance_entries WHERE id = %s", (balance["id"],)).fetchone()[0] == 40


def test_shared_member_and_nonmember_admin_can_manage_and_delete(sharing_case: SharingCase) -> None:
    """Equal members/admins manage all data, but neither can remove the last member."""
    case = sharing_case
    owner, member, admin = case.user(), case.user(), case.user("admin")
    for actor in (member, admin):
        meter = owner.client.post("/api/meters", json={"name": "Manage " + str(actor.id)}).json()
        base = f"/api/meters/{meter['id']}"
        if actor is member:
            assert owner.client.post(base + "/members", json={"email": member.email}).status_code == 200
        shared = actor.client.post(base + "/members", json={"email": case.email("actor-provisioned")})
        assert shared.status_code == 200
        assert actor.client.delete(base + f"/members/{shared.json()['user_id']}").status_code == 204
        other_meter = owner.client.post("/api/meters", json={"name": "Other meter " + str(actor.id)}).json()
        assert actor.client.get(base).status_code == 200
        assert actor.client.get(base + "/members").status_code == 200
        assert actor.client.patch(base, json={"name": "Renamed " + str(actor.id)}).status_code == 200
        occurred = (datetime.now(UTC) - timedelta(days=2)).isoformat()
        for segment, key in (("balances", "balance_kwh"), ("top-ups", "top_up_kwh")):
            record = actor.client.post(base + "/" + segment, json={key: "50", "occurred_at": occurred})
            assert record.status_code == 201
            record_url = base + "/" + segment + "/" + record.json()["id"]
            mismatch = f"/api/meters/{other_meter['id']}/{segment}/{record.json()['id']}"
            assert actor.client.get(mismatch).status_code == 404
            assert actor.client.patch(mismatch, json={key: "40", "occurred_at": occurred}).status_code == 404
            assert actor.client.delete(mismatch).status_code == 404
            assert actor.client.get(record_url).status_code == 200
            assert actor.client.get(base + "/" + segment).status_code == 200
            assert actor.client.patch(record_url, json={key: "40", "occurred_at": occurred}).status_code == 200
            assert actor.client.delete(record_url).status_code == 204
            assert actor.client.post(base + "/" + segment, json={key: "30", "occurred_at": occurred}).status_code == 201
        assert actor.client.get(base + "/dashboard").status_code == 200
        preferences = {"monthly_enabled": False, "monthly_day": 1, "low_balance_enabled": False, "low_balance_days": "3", "timezone": "UTC"}
        assert actor.client.get(base + "/reminders").status_code == 200
        assert actor.client.patch(base + "/reminders", json=preferences).status_code == 200
        last_id = owner.id
        if actor is member:
            assert actor.client.delete(base + f"/members/{owner.id}").status_code == 204
            last_id = member.id
        assert actor.client.delete(base + f"/members/{last_id}").status_code == 409
        assert admin.client.delete(base + f"/members/{last_id}").status_code == 409
        assert actor.client.delete(base + "/members/9223372036854775807").status_code == 404
        assert actor.client.delete(base).status_code == 204
        with connect_database() as connection:
            for table in ("meters", "user_meters", "balance_entries", "top_up_entries", "reminder_settings", "reminder_deliveries"):
                field = "id" if table == "meters" else "meter_id"
                assert connection.execute(f"SELECT count(*) FROM monitor.{table} WHERE {field} = %s", (meter["id"],)).fetchone() == (0,)
