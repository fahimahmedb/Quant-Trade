"""Injectable time source for the capture lane.

The Control Plane already owns an injectable ``Timer``; importing it here would
create a cycle, because the Clock imports the Data Plane. This is the same
contract, declared where the capture lane can use it: a test can drive cadence,
backoff and cooldown deterministically instead of sleeping.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone


class Timebase:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def now_iso(self) -> str:
        return self.now().isoformat()

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            time.sleep(seconds)


class FrozenTimebase(Timebase):
    """Advances only when told to. Sleeping moves the clock, it does not wait."""

    def __init__(self, start: datetime | None = None):
        self._now = start or datetime(2026, 9, 18, 12, 0, 0, tzinfo=timezone.utc)
        self.slept: list[float] = []

    def now(self) -> datetime:
        return self._now

    def sleep(self, seconds: float) -> None:
        if seconds > 0:
            self.slept.append(seconds)
            self.advance(seconds)

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)
