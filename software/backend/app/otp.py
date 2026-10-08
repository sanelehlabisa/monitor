"""Passwordless email OTP storage and policy without HTTP or delivery concerns."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection

OTP_TTL = timedelta(minutes=10)
RESEND_COOLDOWN = timedelta(seconds=60)
REQUEST_WINDOW = timedelta(hours=1)
MAX_REQUESTS_PER_WINDOW = 5
MAX_ATTEMPTS = 5


class OtpPolicyError(Exception):
    """Base error that an HTTP layer must translate without email enumeration."""


class OtpRateLimitError(OtpPolicyError):
    """Raised when an email exceeds the configured OTP request policy."""


class OtpVerificationError(OtpPolicyError):
    """Raised when a challenge cannot be successfully verified."""


@dataclass(frozen=True)
class IssuedOtp:
    """Plaintext delivery value plus persisted challenge metadata."""

    challenge_id: UUID
    code: str
    expires_at: datetime


@dataclass(frozen=True)
class User:
    """Authenticated user created only after successful OTP verification."""

    id: int
    email: str
    created_at: datetime


def normalize_email(email: str) -> str:
    """Return the canonical email key used by storage and policy checks."""

    normalized = email.strip().lower()
    if not normalized:
        raise ValueError("Email must not be empty")
    return normalized


def generate_code() -> str:
    """Generate a cryptographically random, zero-padded six-digit code."""

    return f"{secrets.randbelow(1_000_000):06d}"


def code_digest(secret: str, email: str, challenge_id: UUID, code: str) -> str:
    """Bind a code to its challenge and normalized email using HMAC-SHA256."""

    if not secret:
        raise ValueError("OTP HMAC secret must not be empty")
    message = f"{challenge_id}:{normalize_email(email)}:{code}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


def issue_otp(
    connection: Connection[Any],
    email: str,
    secret: str,
    now: datetime | None = None,
) -> IssuedOtp:
    """Enforce request limits, supersede live codes and store a new challenge."""

    normalized = normalize_email(email)
    issued_at = now or datetime.now(UTC)
    challenge_id = uuid4()
    code = generate_code()
    expires_at = issued_at + OTP_TTL

    with connection.transaction():
        _lock_email(connection, normalized)
        latest = connection.execute(
            """SELECT created_at FROM monitor.otp_challenges
               WHERE email = %s ORDER BY created_at DESC LIMIT 1""",
            (normalized,),
        ).fetchone()
        if latest and latest[0] > issued_at - RESEND_COOLDOWN:
            raise OtpRateLimitError("OTP resend cooldown is active")

        count = connection.execute(
            """SELECT COUNT(*) FROM monitor.otp_challenges
               WHERE email = %s AND created_at > %s""",
            (normalized, issued_at - REQUEST_WINDOW),
        ).fetchone()
        if count and count[0] >= MAX_REQUESTS_PER_WINDOW:
            raise OtpRateLimitError("OTP hourly request limit reached")

        connection.execute(
            """UPDATE monitor.otp_challenges SET invalidated_at = %s
               WHERE email = %s AND used_at IS NULL AND invalidated_at IS NULL""",
            (issued_at, normalized),
        )
        connection.execute(
            """INSERT INTO monitor.otp_challenges
               (id, email, code_digest, created_at, expires_at, max_attempts)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                challenge_id,
                normalized,
                code_digest(secret, normalized, challenge_id, code),
                issued_at,
                expires_at,
                MAX_ATTEMPTS,
            ),
        )

    return IssuedOtp(challenge_id, code, expires_at)


def verify_otp(
    connection: Connection[Any],
    email: str,
    code: str,
    secret: str,
    now: datetime | None = None,
) -> User:
    """Consume the newest valid code and create or return its normalized user."""

    normalized = normalize_email(email)
    verified_at = now or datetime.now(UTC)
    failure: str | None = None
    user: User | None = None

    with connection.transaction():
        _lock_email(connection, normalized)
        row = connection.execute(
            """SELECT id, code_digest, expires_at, attempt_count, max_attempts,
                      used_at, invalidated_at
               FROM monitor.otp_challenges
               WHERE email = %s ORDER BY created_at DESC LIMIT 1 FOR UPDATE""",
            (normalized,),
        ).fetchone()

        if not row or row[5] is not None or row[6] is not None or row[2] <= verified_at:
            failure = "OTP is unavailable"
        elif row[3] >= row[4]:
            failure = "OTP attempt limit reached"
        elif not hmac.compare_digest(
            row[1], code_digest(secret, normalized, row[0], code)
        ):
            attempts = row[3] + 1
            connection.execute(
                """UPDATE monitor.otp_challenges
                   SET attempt_count = %s,
                       invalidated_at = CASE WHEN %s >= max_attempts THEN %s END
                   WHERE id = %s""",
                (attempts, attempts, verified_at, row[0]),
            )
            failure = "OTP is invalid"
        else:
            connection.execute(
                "UPDATE monitor.otp_challenges SET used_at = %s WHERE id = %s",
                (verified_at, row[0]),
            )
            connection.execute(
                "INSERT INTO monitor.users (email) VALUES (%s) ON CONFLICT DO NOTHING",
                (normalized,),
            )
            user_row = connection.execute(
                "SELECT id, email, created_at FROM monitor.users WHERE email = %s",
                (normalized,),
            ).fetchone()
            if user_row:
                user = User(*user_row)

    if failure or user is None:
        raise OtpVerificationError(failure or "User could not be created")
    return user


def invalidate_otp_challenge(
    connection: Connection[Any],
    challenge_id: UUID,
    now: datetime | None = None,
) -> None:
    """Make a delivered challenge unusable while retaining its request record."""

    invalidated_at = now or datetime.now(UTC)
    with connection.transaction():
        connection.execute(
            """UPDATE monitor.otp_challenges SET invalidated_at = %s
               WHERE id = %s AND used_at IS NULL AND invalidated_at IS NULL""",
            (invalidated_at, challenge_id),
        )


def _lock_email(connection: Connection[Any], email: str) -> None:
    """Serialize policy decisions for one normalized email within a transaction."""

    connection.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (email,))
