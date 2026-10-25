"""PostgreSQL integration tests for OTP request and verification policy."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.database import connect_database
from app.modules.otp import (
    OtpRateLimitError,
    OtpVerificationError,
    code_digest,
    issue_otp,
    verify_otp,
)
from psycopg.errors import CheckViolation
from pytest import raises

SECRET = "integration-test-secret"


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}@example.test"


def _remove_email(email: str) -> None:
    with connect_database() as connection:
        connection.execute("DELETE FROM monitor.otp_challenges WHERE email = %s", (email,))
        connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_issue_enforces_limits_and_stores_only_digest() -> None:
    """Issuance applies cooldown/hour policy and supersedes the previous code."""

    email = _unique_email("issue")
    start = datetime(2026, 1, 1, tzinfo=UTC)
    try:
        with connect_database() as connection:
            first = issue_otp(connection, email.upper(), SECRET, start)
            with raises(OtpRateLimitError, match="cooldown"):
                issue_otp(connection, email, SECRET, start + timedelta(seconds=59))

            issued = [first]
            for minute in range(1, 5):
                issued.append(
                    issue_otp(connection, email, SECRET, start + timedelta(minutes=minute))
                )
            with raises(OtpRateLimitError, match="hourly"):
                issue_otp(connection, email, SECRET, start + timedelta(minutes=5))

            rows = connection.execute(
                """SELECT id, code_digest, invalidated_at
                   FROM monitor.otp_challenges
                   WHERE email = %s ORDER BY created_at""",
                (email,),
            ).fetchall()

        assert len(rows) == 5
        assert rows[0][2] is not None
        assert rows[-1][2] is None
        assert rows[0][1] == code_digest(SECRET, email, issued[0].challenge_id, issued[0].code)
        assert all(row[1] not in {item.code for item in issued} for row in rows)
    finally:
        _remove_email(email)


def test_verification_enforces_attempts_one_use_and_user_creation() -> None:
    """Only a valid live code creates a user, and successful codes work once."""

    email = _unique_email("verify")
    start = datetime(2026, 1, 2, tzinfo=UTC)
    try:
        with connect_database() as connection:
            locked = issue_otp(connection, email, SECRET, start)
            wrong_code = "000000" if locked.code != "000000" else "000001"
            for attempt in range(5):
                with raises(OtpVerificationError, match="invalid"):
                    verify_otp(
                        connection,
                        email,
                        wrong_code,
                        SECRET,
                        start + timedelta(seconds=attempt + 1),
                    )
            with raises(OtpVerificationError, match="unavailable"):
                verify_otp(connection, email, locked.code, SECRET, start + timedelta(seconds=6))

            assert connection.execute(
                "SELECT COUNT(*) FROM monitor.users WHERE email = %s", (email,)
            ).fetchone() == (0,)

            live = issue_otp(connection, email, SECRET, start + timedelta(minutes=1))
            user = verify_otp(connection, email.upper(), live.code, SECRET, start + timedelta(minutes=2))
            with raises(OtpVerificationError, match="unavailable"):
                verify_otp(connection, email, live.code, SECRET, start + timedelta(minutes=2))

            next_code = issue_otp(connection, email, SECRET, start + timedelta(minutes=3))
            same_user = verify_otp(
                connection, email, next_code.code, SECRET, start + timedelta(minutes=4)
            )

        assert user.email == email
        assert same_user.id == user.id
        assert user.type == same_user.type == "user"
    finally:
        _remove_email(email)


def test_returning_otp_preserves_admin_and_manual_demotion() -> None:
    """Repeated verification reads stored roles instead of changing them."""

    email = _unique_email("returning-role")
    start = datetime(2026, 1, 4, tzinfo=UTC)
    try:
        with connect_database() as connection:
            first = issue_otp(connection, email, SECRET, start)
            user = verify_otp(connection, email, first.code, SECRET, start + timedelta(seconds=1))
            assert user.type == "user"
            for minute, user_type in ((1, "admin"), (2, "user")):
                connection.execute(
                    "UPDATE monitor.users SET type = %s WHERE id = %s", (user_type, user.id)
                )
                requested_at = start + timedelta(minutes=minute)
                issued = issue_otp(connection, email, SECRET, requested_at)
                returning = verify_otp(
                    connection, email, issued.code, SECRET, requested_at + timedelta(seconds=1)
                )
                assert returning.id == user.id
                assert returning.type == user_type
    finally:
        _remove_email(email)


def test_expired_codes_and_database_constraints_are_rejected() -> None:
    """Expiry and normalized-email checks protect invalid stored state."""

    email = _unique_email("expired")
    start = datetime(2026, 1, 3, tzinfo=UTC)
    try:
        with connect_database() as connection:
            expired = issue_otp(connection, email, SECRET, start)
            with raises(OtpVerificationError, match="unavailable"):
                verify_otp(connection, email, expired.code, SECRET, expired.expires_at)

            with raises(CheckViolation):
                with connection.transaction():
                    connection.execute(
                        "INSERT INTO monitor.users (email) VALUES (%s)",
                        ("Not-Normalized@Example.test",),
                    )
    finally:
        _remove_email(email)
