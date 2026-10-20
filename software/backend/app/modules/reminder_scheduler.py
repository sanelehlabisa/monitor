"""Application-owned monthly reminder loop with cooperative worker shutdown."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from threading import Event
from typing import Any

from fastapi import FastAPI

from app.modules.monthly_reminders import LegacyMonthlyDeliveriesError, run_monthly_reminders
from app.modules.reminder_runner import ReminderRunResult
from app.settings import Settings

CHECK_INTERVAL_SECONDS = 60
logger = logging.getLogger(__name__)


def run_scheduled_reminders(
    settings: Settings, stop: Event | None = None
) -> ReminderRunResult | None:
    """Run the guarded finite pass without changing legacy CLI behavior."""
    if settings.monthly_reminders_activated_at is None or (stop is not None and stop.is_set()):
        return None
    return run_monthly_reminders(
        settings, activation_at=settings.monthly_reminders_activated_at,
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


async def run_reminder_loop(settings: Settings, stop: Event) -> None:
    """Recover on startup, retry sequentially, and never block the event loop."""
    while not stop.is_set():
        try:
            result = await _drain_worker(
                asyncio.create_task(asyncio.to_thread(run_scheduled_reminders, settings, stop)), stop
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
async def monthly_reminder_lifespan(app: FastAPI, settings: Settings) -> AsyncIterator[None]:
    """Own exactly one loop; disabled apps do not connect or send on startup."""
    stop = Event()
    worker = None
    if settings.monthly_reminders_activated_at is not None:
        worker = asyncio.create_task(run_reminder_loop(settings, stop), name="monthly-reminders")
    try:
        yield
    finally:
        stop.set()
        if worker is not None:
            await _drain_worker(worker, stop)
