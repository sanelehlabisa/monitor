"""Shared validation for manually entered kWh ledger values."""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

MAX_KWH = Decimal("999999999.999")
KWH_QUANTUM = Decimal("0.001")


def normalize_kwh(value: Decimal, *, allow_zero: bool) -> Decimal:
    """Validate finite kWh within NUMERIC(12,3) without silently rounding."""

    try:
        rounded = value.quantize(KWH_QUANTUM)
    except InvalidOperation as error:
        raise ValueError("kWh value is outside the supported range") from error
    if not value.is_finite() or value != rounded or value > MAX_KWH:
        raise ValueError("kWh must have at most three decimals and fit storage")
    if value < 0 or (not allow_zero and value == 0):
        comparison = "zero or greater" if allow_zero else "greater than zero"
        raise ValueError(f"kWh must be {comparison}")
    return rounded


def normalize_occurred_at(value: datetime) -> datetime:
    """Require an aware timestamp and normalize it to UTC for persistence."""

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Occurrence time must include a timezone")
    return value.astimezone(UTC)
