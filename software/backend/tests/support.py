"""Small synthetic fixture helpers; never intended for the source database."""

from dataclasses import dataclass
from typing import Any, Literal, Sequence
from uuid import uuid4

from fastapi.testclient import TestClient
from psycopg import Connection

from app.database import connect_database
from app.endpoints.auth import COOKIE_NAME
from app.main import create_app
from app.modules.sessions import create_session


def cleanup_users(connection: Connection[Any], emails: Sequence[str]) -> None:
    """Delete only named synthetic fixtures, respecting creator/member FKs."""
    assert emails and all(email.endswith("@example.test") for email in emails)
    values = (list(emails),)
    connection.execute(
        """DELETE FROM monitor.meters WHERE user_id IN
           (SELECT id FROM monitor.users WHERE email = ANY(%s))""", values)
    connection.execute(
        """DELETE FROM monitor.user_meters WHERE user_id IN
           (SELECT id FROM monitor.users WHERE email = ANY(%s))""", values)
    connection.execute("DELETE FROM monitor.users WHERE email = ANY(%s)", values)
    connection.execute("DELETE FROM monitor.otp_challenges WHERE email = ANY(%s)", values)


@dataclass(frozen=True)
class Person:
    """One synthetic authenticated account, not a production login shortcut."""

    id: int
    email: str
    client: TestClient


class SharingCase:
    """Track exact synthetic account identities for deterministic teardown."""

    def __init__(self) -> None:
        self.emails: list[str] = []
        self.clients: list[TestClient] = []

    def email(self, prefix: str = "sharing") -> str:
        """Reserve an isolated address even if its later provisioning rolls back."""
        email = f"{prefix}-{uuid4().hex}@example.test"
        self.emails.append(email)
        return email

    def user(self, user_type: Literal["user", "admin"] = "user") -> Person:
        """Create an explicit isolated account/session fixture."""
        email = self.email()
        with connect_database() as connection:
            row = connection.execute(
                "INSERT INTO monitor.users (email, type) VALUES (%s, %s) RETURNING id",
                (email, user_type),
            ).fetchone()
            assert row is not None
            session = create_session(connection, row[0])
        client = self.client()
        client.cookies.set(COOKIE_NAME, session.token)
        return Person(row[0], email, client)

    def client(self) -> TestClient:
        """Return a tracked unauthenticated test client."""
        client = TestClient(create_app(), base_url="https://testserver")
        self.clients.append(client)
        return client

    def close(self) -> None:
        """Remove only this case's synthetic users and close its clients."""
        for client in self.clients:
            client.close()
        if self.emails:
            with connect_database() as connection:
                cleanup_users(connection, self.emails)
