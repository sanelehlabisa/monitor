"""Live PostgreSQL authorization tests for the meter CRUD API."""

from pathlib import Path
from uuid import uuid4

from app.auth_api import COOKIE_NAME
from app.database import connect_database
from app.main import create_app
from app.migrations import run_migrations
from app.sessions import create_session
from app.settings import Settings
from fastapi.testclient import TestClient

MIGRATIONS_DIRECTORY = Path("/migrations")


def _client_for(settings: Settings, email: str) -> tuple[TestClient, int]:
    with connect_database(settings) as connection:
        row = connection.execute(
            "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id", (email,)
        ).fetchone()
        assert row
        session = create_session(connection, row[0])
    client = TestClient(create_app(settings))
    client.cookies.set(COOKIE_NAME, session.token)
    return client, row[0]


def test_meter_api_enforces_owner_scope_and_admin_access() -> None:
    """Users manage their meters while an admin manages every existing meter."""

    normal_email = f"meter-user-{uuid4().hex}@example.test"
    other_email = f"meter-other-{uuid4().hex}@example.test"
    admin_email = f"meter-admin-{uuid4().hex}@example.test"
    settings = Settings(environment="test", admin_emails=admin_email)
    run_migrations(settings, MIGRATIONS_DIRECTORY)
    normal, _ = _client_for(settings, normal_email)
    other, _ = _client_for(settings, other_email)
    admin, _ = _client_for(settings, admin_email)
    try:
        denied = TestClient(create_app(settings)).get("/api/meters")
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
        assert normal.get(f"/api/meters/{shop.json()['id']}").status_code == 404
        assert normal.patch(
            f"/api/meters/{shop.json()['id']}", json={"name": "Hidden"}
        ).status_code == 404
        assert normal.delete(f"/api/meters/{shop.json()['id']}").status_code == 404

        admin_list = admin.get("/api/meters")
        assert admin_list.status_code == 200
        assert {item["owner_email"] for item in admin_list.json()} == {
            normal_email,
            other_email,
        }
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
        with connect_database(settings) as connection:
            connection.execute(
                "DELETE FROM monitor.users WHERE email IN (%s, %s, %s)",
                (normal_email, other_email, admin_email),
            )
