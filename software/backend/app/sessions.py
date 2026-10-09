"""Opaque login-session storage and policy without HTTP concerns."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from typing import Any
from uuid import UUID, uuid4

from psycopg import Connection

from app.otp import User

SESSION_TTL = timedelta(days=30)


class SessionAuthenticationError(Exception):
    """Raised when a presented session cannot authenticate a user."""


@dataclass(frozen=True)
class CreatedSession:
    """Plaintext cookie value plus persisted session metadata."""

    id: UUID
    token: str = field(repr=False)
    expires_at: datetime


def generate_session_token() -> str:
    """Generate a URL-safe token with 256 bits of randomness."""

    return secrets.token_urlsafe(32)


def session_token_digest(token: str) -> str:
    """Return the storage-safe SHA-256 digest for a high-entropy token."""

    if not token:
        raise ValueError("Session token must not be empty")
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(
    connection: Connection[Any], user_id: int, now: datetime | None = None
) -> CreatedSession:
    """Create one independent fixed-lifetime session for a verified user."""

    created_at = now or datetime.now(UTC)
    session_id = uuid4()
    token = generate_session_token()
    expires_at = created_at + SESSION_TTL
    with connection.transaction():
        connection.execute(
            """INSERT INTO monitor.user_sessions
               (id, user_id, token_digest, created_at, expires_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                session_id,
                user_id,
                session_token_digest(token),
                created_at,
                expires_at,
            ),
        )
    return CreatedSession(session_id, token, expires_at)


def authenticate_session(
    connection: Connection[Any], token: str, now: datetime | None = None
) -> User:
    """Resolve one live session token to its owning user."""

    if not token:
        raise SessionAuthenticationError("Session is unavailable")
    authenticated_at = now or datetime.now(UTC)
    row = connection.execute(
        """SELECT users.id, users.email, users.created_at
           FROM monitor.user_sessions AS sessions
           JOIN monitor.users AS users ON users.id = sessions.user_id
           WHERE sessions.token_digest = %s
             AND sessions.revoked_at IS NULL
             AND sessions.expires_at > %s""",
        (session_token_digest(token), authenticated_at),
    ).fetchone()
    if not row:
        raise SessionAuthenticationError("Session is unavailable")
    return User(*row)


def revoke_session(
    connection: Connection[Any], token: str, now: datetime | None = None
) -> None:
    """Revoke the live session represented by the presented token."""

    if not token:
        raise SessionAuthenticationError("Session is unavailable")
    revoked_at = now or datetime.now(UTC)
    with connection.transaction():
        result = connection.execute(
            """UPDATE monitor.user_sessions SET revoked_at = %s
               WHERE token_digest = %s
                 AND revoked_at IS NULL
                 AND expires_at > %s""",
            (revoked_at, session_token_digest(token), revoked_at),
        )
    if result.rowcount != 1:
        raise SessionAuthenticationError("Session is unavailable")
