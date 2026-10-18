"""Fixtures for isolated sharing checks only."""

from collections.abc import Iterator

from pytest import fixture

from tests.support import SharingCase


@fixture
def sharing_case() -> Iterator[SharingCase]:
    """Clean synthetic fixtures even when an assertion fails."""
    case = SharingCase()
    try:
        yield case
    finally:
        case.close()
