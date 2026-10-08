"""PostgreSQL and Mailpit integration tests for OTP email delivery."""

from datetime import UTC, datetime
import json
from pathlib import Path
import re
import time
from urllib.request import urlopen
from uuid import uuid4

from app.database import connect_database
from app.email_delivery import EmailDeliveryError, deliver_login_code
from app.migrations import run_migrations
from app.otp import code_digest
from app.settings import Settings
from pytest import raises

MIGRATIONS_DIRECTORY = Path("/migrations")


class FailingSender:
    """Simulate a delivery-domain failure after challenge issuance."""

    def send(self, message: object) -> None:
        raise EmailDeliveryError("Login email delivery failed")


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}@example.test"


def _remove_email(settings: Settings, email: str) -> None:
    with connect_database(settings) as connection:
        connection.execute(
            "DELETE FROM monitor.otp_challenges WHERE email = %s", (email,)
        )
        connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def _mailpit_message_for(email: str) -> dict[str, object]:
    for _ in range(20):
        with urlopen("http://mailpit:8025/api/v1/messages", timeout=2) as response:
            messages = json.load(response)["messages"]
        matches = [
            message
            for message in messages
            if [recipient["Address"] for recipient in message["To"]] == [email]
        ]
        if matches:
            return matches[0]
        time.sleep(0.1)
    raise AssertionError("Mailpit did not receive the OTP message")


def test_delivery_failure_invalidates_but_retains_challenge() -> None:
    """Failed sends remain counted but cannot later authenticate a user."""

    settings = Settings(otp_hmac_secret="delivery-test-secret")
    run_migrations(settings, MIGRATIONS_DIRECTORY)
    email = _unique_email("failed-delivery")
    now = datetime(2026, 10, 8, tzinfo=UTC)
    try:
        with connect_database(settings) as connection:
            with raises(EmailDeliveryError, match="delivery failed"):
                deliver_login_code(connection, email, settings, FailingSender(), now)
            row = connection.execute(
                """SELECT COUNT(*), COUNT(invalidated_at)
                   FROM monitor.otp_challenges WHERE email = %s""",
                (email,),
            ).fetchone()

        assert row == (1, 1)
    finally:
        _remove_email(settings, email)


def test_generated_code_reaches_only_requested_mailpit_recipient() -> None:
    """Real SMTP delivery matches the HMAC-only PostgreSQL challenge."""

    settings = Settings(otp_hmac_secret="mailpit-integration-secret")
    run_migrations(settings, MIGRATIONS_DIRECTORY)
    email = _unique_email("mailpit-delivery")
    try:
        with connect_database(settings) as connection:
            delivery = deliver_login_code(connection, email, settings)
            stored = connection.execute(
                "SELECT code_digest FROM monitor.otp_challenges WHERE id = %s",
                (delivery.challenge_id,),
            ).fetchone()

        summary = _mailpit_message_for(email)
        assert summary["Subject"] == "Your Roventics Monitor sign-in code"
        with urlopen(
            f"http://mailpit:8025/view/{summary['ID']}.txt", timeout=2
        ) as response:
            body = response.read().decode()
        code = re.search(r"\b\d{6}\b", body)

        assert code is not None
        assert stored == (
            code_digest(
                settings.otp_hmac_secret.get_secret_value(),
                email,
                delivery.challenge_id,
                code.group(),
            ),
        )
        assert stored[0] != code.group()
    finally:
        _remove_email(settings, email)
