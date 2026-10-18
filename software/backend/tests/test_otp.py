"""Unit tests for passwordless OTP primitives."""

from uuid import UUID

from app.modules.otp import code_digest, generate_code, normalize_email
from pytest import MonkeyPatch, raises


def test_normalize_email_uses_one_canonical_key() -> None:
    """Surrounding whitespace and case do not create separate identities."""

    assert normalize_email("  User@Example.COM ") == "user@example.com"
    with raises(ValueError, match="must not be empty"):
        normalize_email("   ")


def test_generate_code_is_zero_padded(monkeypatch: MonkeyPatch) -> None:
    """All generated values fit the approved six-digit delivery format."""

    monkeypatch.setattr("app.modules.otp.secrets.randbelow", lambda limit: 7)

    assert generate_code() == "000007"


def test_digest_is_bound_to_email_and_challenge() -> None:
    """The same code cannot be replayed against another email or challenge."""

    first_id = UUID("00000000-0000-0000-0000-000000000001")
    second_id = UUID("00000000-0000-0000-0000-000000000002")
    first = code_digest("secret", "USER@example.com", first_id, "123456")

    assert len(first) == 64
    assert first != "123456"
    assert first == code_digest("secret", "user@example.com", first_id, "123456")
    assert first != code_digest("secret", "user@example.com", second_id, "123456")
    assert first != code_digest("secret", "other@example.com", first_id, "123456")
