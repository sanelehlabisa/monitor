"""Live PostgreSQL and Mailpit test for the human authentication API."""

import json
import re
import time
from urllib.request import urlopen
from uuid import uuid4

from app.database import connect_database
from app.main import create_app
from app.settings import Settings
from fastapi.testclient import TestClient


def _mailpit_code_for(email: str) -> str:
    for _ in range(20):
        with urlopen("http://mailpit:8025/api/v1/messages", timeout=2) as response:
            messages = json.load(response)["messages"]
        matches = [
            message
            for message in messages
            if [recipient["Address"] for recipient in message["To"]] == [email]
        ]
        if matches:
            with urlopen(
                f"http://mailpit:8025/view/{matches[0]['ID']}.txt", timeout=2
            ) as response:
                body = response.read().decode()
            code = re.search(r"\b\d{6}\b", body)
            assert code is not None
            return code.group()
        time.sleep(0.1)
    raise AssertionError("Mailpit did not receive the OTP message")


def _remove_identity(settings: Settings, email: str) -> None:
    with connect_database(settings) as connection:
        connection.execute(
            "DELETE FROM monitor.otp_challenges WHERE email = %s", (email,)
        )
        connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_new_user_can_sign_in_use_me_and_log_out() -> None:
    """The complete open-signup flow uses Mailpit and an opaque cookie."""

    settings = Settings(environment="development")
    email = f"auth-api-{uuid4().hex}@example.test"
    client = TestClient(create_app(settings))
    try:
        requested = client.post("/api/auth/request-otp", json={"email": email})
        code = _mailpit_code_for(email)
        verified = client.post(
            "/api/auth/verify-otp", json={"email": email, "code": code}
        )
        current = client.get("/api/me")
        logged_out = client.post("/api/auth/logout")
        denied = client.get("/api/me")

        assert requested.status_code == 202
        assert verified.status_code == 200
        assert verified.json()["email"] == email
        assert set(verified.json()) == {"id", "email", "is_admin"}
        assert verified.json()["is_admin"] is False
        assert "HttpOnly" in verified.headers["set-cookie"]
        assert "Secure" not in verified.headers["set-cookie"]
        assert current.status_code == 200
        assert current.json() == verified.json()
        assert logged_out.status_code == 204
        assert denied.status_code == 401

        with connect_database(settings) as connection:
            assert connection.execute(
                "SELECT type FROM monitor.users WHERE email = %s", (email,)
            ).fetchone() == ("user",)
            row = connection.execute(
                """SELECT COUNT(*), COUNT(revoked_at)
                   FROM monitor.user_sessions AS sessions
                   JOIN monitor.users AS users ON users.id = sessions.user_id
                   WHERE users.email = %s""",
                (email,),
            ).fetchone()
        assert row == (1, 1)
    finally:
        _remove_identity(settings, email)
