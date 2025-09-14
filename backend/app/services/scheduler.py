from __future__ import annotations
import asyncio
from datetime import datetime
from typing import Callable, Awaitable, Optional

from app.services.progress_service import log_progress

# Simple in-process scheduler for periodic tasks

class Scheduler:
    def __init__(self) -> None:
        self._tasks: list[asyncio.Task] = []
        self._running = False

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        # Add periodic jobs here
        self._tasks.append(asyncio.create_task(self._job_ingest_specs()))
        self._tasks.append(asyncio.create_task(self._job_alerts_eval()))

    async def _job_ingest_specs(self) -> None:
        # Run every 4 hours
        interval_sec = 4 * 60 * 60
        # First run after short delay to avoid startup race
        await asyncio.sleep(5)
        while self._running:
            try:
                from app.services.spec_ingest import ingest_specs
                log_progress("ingest", "auto_start")
                result = ingest_specs()
                log_progress(
                    "ingest",
                    "auto_done",
                    details=f"created={result.get('created')} updated={result.get('updated')} files={result.get('total_files')}"
                )
            except Exception as e:
                log_progress("ingest", "auto_error", details=str(e))
            await asyncio.sleep(interval_sec)

    
        async def _job_alerts_eval(self) -> None:
            # Run every 60 seconds
            interval_sec = 60
            await asyncio.sleep(10)
            while self._running:
                try:
                    from app.services import alerts_service
                    res = await alerts_service.evaluate_once()
                    if res.get("triggered"):
                        log_progress("alerts", "triggered", details=str(res.get("triggered")[:3]))
                except Exception as e:
                    log_progress("alerts", "error", details=str(e))
                await asyncio.sleep(interval_sec)

    async def stop(self) -> None:
        self._running = False
        for t in self._tasks:
            t.cancel()
        self._tasks.clear()

scheduler = Scheduler()