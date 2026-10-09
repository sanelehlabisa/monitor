"""Unit tests for opaque session-token primitives."""

import hashlib

from app.sessions import generate_session_token, session_token_digest
from pytest import MonkeyPatch, raises


def test_generate_session_token_requests_32_random_bytes(
    monkeypatch: MonkeyPatch,
) -> None:
    """Session credentials use the approved 256-bit random source."""

    requested: list[int] = []

    def fake_token_urlsafe(byte_count: int) -> str:
        requested.append(byte_count)
        return "opaque-session-token"

    monkeypatch.setattr("app.sessions.secrets.token_urlsafe", fake_token_urlsafe)

    assert generate_session_token() == "opaque-session-token"
    assert requested == [32]


def test_session_digest_is_deterministic_and_rejects_empty_tokens() -> None:
    """Only a one-way SHA-256 token representation is suitable for storage."""

    expected = hashlib.sha256(b"opaque-session-token").hexdigest()

    assert session_token_digest("opaque-session-token") == expected
    assert len(expected) == 64
    with raises(ValueError, match="must not be empty"):
        session_token_digest("")
