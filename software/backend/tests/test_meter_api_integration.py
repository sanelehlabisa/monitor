"""Live PostgreSQL authorization tests for the meter CRUD API."""

from typing import Literal
from uuid import uuid4

from app.endpoints.auth import COOKIE_NAME
from app.database import connect_database
from app.main import create_app
from app.modules.sessions import create_session
from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from tests.support import cleanup_users


def _client_for(
    email: str, user_type: Literal["user", "admin"] = "user"
) -> tuple[TestClient, int]:
    with connect_database() as connection:
        row = connection.execute(
            "INSERT INTO monitor.users (email, type) VALUES (%s, %s) RETURNING id",
            (email, user_type),
        ).fetchone()
        assert row
        session = create_session(connection, row[0])
    client = TestClient(create_app())
    client.cookies.set(COOKIE_NAME, session.token)
    return client, row[0]


def test_meter_api_enforces_owner_scope_and_admin_access() -> None:
    """Users manage their meters while an admin manages every existing meter."""

    normal_email = f"meter-user-{uuid4().hex}@example.test"
    other_email = f"meter-other-{uuid4().hex}@example.test"
    admin_email = f"meter-admin-{uuid4().hex}@example.test"
    normal, _ = _client_for(normal_email)
    other, _ = _client_for(other_email)
    admin, _ = _client_for(admin_email, "admin")
    try:
        existing = admin.get("/api/meters")
        assert existing.status_code == 200
        existing_meters = {
            item["id"]: item["owner_email"] for item in existing.json()
        }
        denied = TestClient(create_app()).get("/api/meters")
        home = normal.post("/api/meters", json={"name": " Home "})
        shop = other.post("/api/meters", json={"name": "Shop"})
        duplicate = normal.post("/api/meters", json={"name": "home"})

        assert denied.status_code == 401
        assert home.status_code == 201
        assert home.json()["name"] == "Home"
        assert home.json()["owner_email"] == normal_email
        assert duplicate.status_code == 409
        assert [item["id"] for item in normal.get("/api/meters").json()] == [
            home.json()["id"]
        ]
        assert normal.get("/api/meters", params={"q": "HOM"}).json() == [home.json()]
        assert normal.get("/api/meters", params={"q": "Shop"}).json() == []
        assert normal.get(f"/api/meters/{shop.json()['id']}").status_code == 404
        assert normal.patch(
            f"/api/meters/{shop.json()['id']}", json={"name": "Hidden"}
        ).status_code == 404
        assert normal.delete(f"/api/meters/{shop.json()['id']}").status_code == 404

        admin_list = admin.get("/api/meters")
        assert admin_list.status_code == 200
        assert {
            item["id"]: item["owner_email"] for item in admin_list.json()
        } == existing_meters | {
            home.json()["id"]: normal_email,
            shop.json()["id"]: other_email,
        }
        owner_match = admin.get(
            "/api/meters", params={"q": other_email[6:24].upper()}
        )
        assert [item["id"] for item in owner_match.json()] == [shop.json()["id"]]
        renamed = admin.patch(
            f"/api/meters/{shop.json()['id']}", json={"name": "Workshop"}
        )
        assert renamed.status_code == 200
        assert renamed.json()["name"] == "Workshop"
        assert admin.delete(f"/api/meters/{shop.json()['id']}").status_code == 204
        assert admin.get(f"/api/meters/{shop.json()['id']}").status_code == 404

        me = admin.get("/api/me")
        assert me.json()["is_admin"] is True
    finally:
        with connect_database() as connection:
            cleanup_users(connection, (normal_email, other_email, admin_email))


def test_same_cookie_observes_promotion_and_demotion(monkeypatch: MonkeyPatch) -> None:
    """The next request reads its DB role; stale admin env grants nothing."""

    email = f"role-session-{uuid4().hex}@example.test"
    owner_email = f"role-owner-{uuid4().hex}@example.test"
    monkeypatch.setenv("MONITOR_ADMIN_EMAILS", email)  # Negative legacy-env regression.
    client, user_id = _client_for(email)
    owner, _ = _client_for(owner_email)
    cookie = client.cookies.get(COOKIE_NAME)
    assert cookie
    try:
        meter = owner.post("/api/meters", json={"name": "Foreign meter"})
        assert meter.status_code == 201
        url = f"/api/meters/{meter.json()['id']}"
        for user_type, expected_admin in (
            ("user", False), ("admin", True), ("user", False)
        ):
            with connect_database() as connection:
                connection.execute(
                    "UPDATE monitor.users SET type = %s WHERE id = %s", (user_type, user_id)
                )
            current = client.get("/api/me")
            assert current.status_code == 200
            assert current.json()["is_admin"] is expected_admin
            assert client.get(url).status_code == (200 if expected_admin else 404)
            assert client.cookies.get(COOKIE_NAME) == cookie
    finally:
        with connect_database() as connection:
            cleanup_users(connection, (email, owner_email))
