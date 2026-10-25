"""Fixtures for isolated sharing checks only."""

from collections.abc import Iterator

from pytest import MonkeyPatch, fixture

from tests.support import SharingCase


@fixture(autouse=True)
def test_runtime_mode(monkeypatch: MonkeyPatch) -> None:
    """Keep per-test mode and activation independent of the runner's environment."""
    monkeypatch.setenv("MONITOR_ENVIRONMENT", "test")
    monkeypatch.delenv("MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT", raising=False)


@fixture
def sharing_case() -> Iterator[SharingCase]:
    """Clean synthetic fixtures even when an assertion fails."""
    case = SharingCase()
    try:
        yield case
    finally:
        case.close()
