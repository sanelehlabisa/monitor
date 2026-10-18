"""PostgreSQL integration tests for opaque user sessions."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.database import connect_database
from app.sessions import (
    SESSION_TTL,
    SessionAuthenticationError,
    authenticate_session,
    create_session,
    revoke_session,
    session_token_digest,
)
from app.settings import Settings
from pytest import raises


def _create_user(settings: Settings, email: str) -> int:
    with connect_database(settings) as connection:
        row = connection.execute(
            "INSERT INTO monitor.users (email) VALUES (%s) RETURNING id", (email,)
        ).fetchone()
    assert row is not None
    return row[0]


def _remove_user(settings: Settings, email: str) -> None:
    with connect_database(settings) as connection:
        connection.execute("DELETE FROM monitor.users WHERE email = %s", (email,))


def test_multiple_sessions_authenticate_and_store_only_digests() -> None:
    """One user may sign in independently on more than one device."""

    settings = Settings()
    email = f"sessions-{uuid4().hex}@example.test"
    user_id = _create_user(settings, email)
    now = datetime(2026, 10, 9, tzinfo=UTC)
    try:
        with connect_database(settings) as connection:
            first = create_session(connection, user_id, now)
            second = create_session(connection, user_id, now + timedelta(seconds=1))
            first_user = authenticate_session(connection, first.token, now)
            second_user = authenticate_session(connection, second.token, now)
            rows = connection.execute(
                """SELECT token_digest FROM monitor.user_sessions
                   WHERE user_id = %s ORDER BY created_at""",
                (user_id,),
            ).fetchall()
            columns = {
                row[0]
                for row in connection.execute(
                    """SELECT column_name FROM information_schema.columns
                       WHERE table_schema = 'monitor'
                         AND table_name = 'user_sessions'"""
                ).fetchall()
            }

        assert first.token != second.token
        assert first.token not in repr(first)
        assert first.expires_at == now + SESSION_TTL
        assert first_user.id == second_user.id == user_id
        assert rows == [
            (session_token_digest(first.token),),
            (session_token_digest(second.token),),
        ]
        assert first.token not in {row[0] for row in rows}
        assert "token" not in columns
        assert "token_digest" in columns
    finally:
        _remove_user(settings, email)


def test_expired_and_revoked_sessions_share_one_error() -> None:
    """Callers cannot distinguish invalid session states through the domain."""

    settings = Settings()
    email = f"session-state-{uuid4().hex}@example.test"
    user_id = _create_user(settings, email)
    start = datetime(2026, 10, 9, tzinfo=UTC)
    try:
        with connect_database(settings) as connection:
            expired = create_session(connection, user_id, start)
            live = create_session(connection, user_id, start + timedelta(seconds=1))
            revoke_session(connection, live.token, start + timedelta(seconds=2))

            for token, checked_at in (
                (expired.token, expired.expires_at),
                (live.token, start + timedelta(seconds=3)),
                ("unknown-session-token", start + timedelta(seconds=3)),
                ("", start + timedelta(seconds=3)),
            ):
                with raises(SessionAuthenticationError, match="unavailable"):
                    authenticate_session(connection, token, checked_at)
            with raises(SessionAuthenticationError, match="unavailable"):
                revoke_session(connection, live.token, start + timedelta(seconds=4))
    finally:
        _remove_user(settings, email)
