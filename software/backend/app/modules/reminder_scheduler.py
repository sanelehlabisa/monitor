"""Application-owned monthly reminder loop with cooperative worker shutdown."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import logging
import os
from threading import Event
from typing import Any

from fastapi import FastAPI

from app.modules.monthly_reminders import LegacyMonthlyDeliveriesError, run_monthly_reminders
from app.modules.reminder_runner import ReminderRunResult

CHECK_INTERVAL_SECONDS = 60
logger = logging.getLogger(__name__)


def read_activation_cutoff() -> datetime | None:
    """Read the saved aware cutoff once; blank disables automatic reminders."""
    value = os.environ.get("MONITOR_MONTHLY_REMINDERS_ACTIVATED_AT", "").strip()
    if not value:
        return None
    try:
        activation_at = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("Monthly reminder activation must be an ISO datetime") from None
    if activation_at.tzinfo is None or activation_at.utcoffset() is None:
        raise ValueError("Monthly reminder activation must include a timezone")
    return activation_at.astimezone(UTC)


def run_scheduled_reminders(
    activation_at: datetime | None, stop: Event | None = None
) -> ReminderRunResult | None:
    """Run the guarded finite pass without changing legacy CLI behavior."""
    if activation_at is None or (stop is not None and stop.is_set()):
        return None
    return run_monthly_reminders(
        activation_at=activation_at,
        should_stop=stop.is_set if stop is not None else None,
        bounded_io=True, check_legacy=True,
    )


async def _drain_worker(worker: asyncio.Task[Any], stop: Event) -> Any:
    """Cancellation cannot stop a thread: signal and await its real completion."""
    try:
        return await asyncio.shield(worker)
    except asyncio.CancelledError:
        stop.set()
        await worker
        raise


async def run_reminder_loop(activation_at: datetime, stop: Event) -> None:
    """Recover on startup, retry sequentially, and never block the event loop."""
    while not stop.is_set():
        try:
            result = await _drain_worker(
                asyncio.create_task(asyncio.to_thread(run_scheduled_reminders, activation_at, stop)), stop
            )
            if result is not None:
                logger.info("Monthly reminders: sent=%d failed=%d", result.messages_sent, result.delivery_failures)
        except LegacyMonthlyDeliveriesError:
            logger.warning("Monthly reminders blocked: saved delivery keys need reconciliation")
        except Exception:
            # Database/SMTP exceptions can contain credentials or private records.
            logger.warning("Monthly reminder pass failed; retrying after the interval")
        if not stop.is_set():
            await _drain_worker(
                asyncio.create_task(asyncio.to_thread(stop.wait, CHECK_INTERVAL_SECONDS)), stop
            )


@asynccontextmanager
async def monthly_reminder_lifespan(
    app: FastAPI, activation_at: datetime | None
) -> AsyncIterator[None]:
    """Own exactly one loop; disabled apps do not connect or send on startup."""
    stop = Event()
    worker = None
    if activation_at is not None:
        worker = asyncio.create_task(run_reminder_loop(activation_at, stop), name="monthly-reminders")
    try:
        yield
    finally:
        stop.set()
        if worker is not None:
            await _drain_worker(worker, stop)
