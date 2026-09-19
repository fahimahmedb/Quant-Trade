"""The global SEC traffic budget.

``NEXT_BUILD_MISSION.md``: "The limiter must be designed as a global SEC traffic
budget, not merely a local P0 loop limit, so future/parallel SEC consumers cannot
collectively exceed the frozen policy."

The budget is therefore keyed on a file rather than on an object. Every SEC
request in the process tree - discovery, filing acquisition, and every retry -
takes the same file lock and respects the same spacing, so adding a second
consumer later cannot double the rate. An advisory lock also gives the frozen
``max_concurrency = 1`` for free.

Two properties matter more than elegance here:

* the spacing timestamp is persisted *before* the request leaves, so a process
  killed mid-request cannot forget that it already spent a slot;
* an active cooldown lives in the file, not in memory, so restarting the
  collector cannot shorten a cooldown the SEC asked for.
"""

from __future__ import annotations

import fcntl
import os
import random
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from ...state import append_jsonl, parse_ts, read_json, write_json
from .policy import SecAccessPolicy
from .timebase import Timebase


class SecCooldownActive(RuntimeError):
    """A durable cooldown forbids the request. Not a fault: a policy decision."""

    def __init__(self, until: str, reason: str, remaining_seconds: float):
        super().__init__(f"SEC cooldown active until {until} ({reason})")
        self.until = until
        self.reason = reason
        self.remaining_seconds = remaining_seconds


@dataclass
class BudgetState:
    last_request_at_utc: str | None = None
    requests: int = 0
    cooldown_until_utc: str | None = None
    cooldown_reason: str | None = None
    #: Which entry of the frozen backoff schedule the next transient retry uses.
    backoff_step: int = 0
    waits: int = 0
    total_wait_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"last_request_at_utc": self.last_request_at_utc, "requests": self.requests,
                "cooldown_until_utc": self.cooldown_until_utc,
                "cooldown_reason": self.cooldown_reason, "backoff_step": self.backoff_step,
                "waits": self.waits, "total_wait_seconds": round(self.total_wait_seconds, 3)}


class SecTrafficBudget:
    """Process-shared, restart-durable request budget for all SEC traffic."""

    def __init__(self, path: Path, policy: SecAccessPolicy, timebase: Timebase | None = None,
                 rng: random.Random | None = None):
        self.path = Path(path)
        self.policy = policy
        self.timebase = timebase or Timebase()
        self.rng = rng or random.Random()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.path.with_suffix(".lock")

    # --- durable state -----------------------------------------------------
    def load(self) -> BudgetState:
        payload = read_json(self.path) or {}
        known = {field: payload[field] for field in BudgetState().to_dict() if field in payload}
        return BudgetState(**known)

    def save(self, state: BudgetState) -> None:
        write_json(self.path, state.to_dict())

    @contextmanager
    def _exclusive(self) -> Iterator[None]:
        """Advisory exclusive lock: this is the frozen ``max_concurrency = 1``."""
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)

    # --- cooldown ----------------------------------------------------------
    def cooldown_remaining(self, state: BudgetState | None = None) -> float:
        state = state or self.load()
        if not state.cooldown_until_utc:
            return 0.0
        remaining = (parse_ts(state.cooldown_until_utc) - self.timebase.now()).total_seconds()
        return max(remaining, 0.0)

    def enter_cooldown(self, seconds: float, reason: str) -> str:
        """Extend, never shorten. An authoritative cooldown is a floor."""
        with self._exclusive():
            state = self.load()
            proposed = self.timebase.now() + timedelta(seconds=max(seconds, 0.0))
            current = (parse_ts(state.cooldown_until_utc)
                       if state.cooldown_until_utc else None)
            chosen = proposed if current is None or proposed > current else current
            state.cooldown_until_utc = chosen.isoformat()
            if chosen == proposed:
                state.cooldown_reason = reason
            self.save(state)
            return state.cooldown_until_utc

    def clear_cooldown(self) -> None:
        with self._exclusive():
            state = self.load()
            state.cooldown_until_utc = None
            state.cooldown_reason = None
            state.backoff_step = 0
            self.save(state)

    def next_backoff_seconds(self, advance: bool = True) -> float:
        """Bounded exponential backoff with jitter, taken from the frozen table."""
        with self._exclusive():
            state = self.load()
            base = self.policy.backoff_seconds(state.backoff_step)
            if advance:
                state.backoff_step = min(state.backoff_step + 1,
                                         len(self.policy.backoff_schedule_seconds) - 1)
                self.save(state)
        jitter = base * self.policy.jitter_ratio
        return max(0.0, base + self.rng.uniform(-jitter, jitter))

    def reset_backoff(self) -> None:
        with self._exclusive():
            state = self.load()
            if state.backoff_step:
                state.backoff_step = 0
                self.save(state)

    # --- the slot ----------------------------------------------------------
    def reserve(self, endpoint_class: str, *, attempt_id: str | None = None) -> dict[str, Any]:
        """Wait for a compliant slot and durably record that it was spent.

        Raises ``SecCooldownActive`` rather than sleeping through a cooldown:
        a multi-minute SEC cooldown is a state the collector should report, not
        a pause it should hide inside one tick.
        """
        with self._exclusive():
            state = self.load()
            remaining = self.cooldown_remaining(state)
            if remaining > 0:
                raise SecCooldownActive(state.cooldown_until_utc or "",
                                        state.cooldown_reason or "unspecified", remaining)
            waited = self._wait_for_spacing(state)
            now = self.timebase.now()
            state.last_request_at_utc = now.isoformat()
            state.requests += 1
            if waited > 0:
                state.waits += 1
                state.total_wait_seconds += waited
            # Persisted before the caller is allowed to make the request, so a
            # kill during the request cannot re-spend this slot immediately.
            self.save(state)
            reservation = {
                "attempt_id": attempt_id or ("unbound-" + uuid.uuid4().hex),
                "reserved_at_utc": state.last_request_at_utc,
                "endpoint_class": endpoint_class,
                "waited_seconds": waited,
            }
            # Written before the caller receives authority to emit the request.
            # If this append fails, no request is sent and the spent budget slot
            # remains conservatively unavailable.
            append_jsonl(self.path.parent / "budget_reservations.jsonl", reservation)
            return reservation

    def _wait_for_spacing(self, state: BudgetState) -> float:
        if state.last_request_at_utc is None:
            return 0.0
        interval = self.policy.min_request_interval_seconds
        elapsed = (self.timebase.now() - parse_ts(state.last_request_at_utc)).total_seconds()
        if elapsed < 0:
            # The wall clock moved backwards. Spend a full interval rather than
            # inferring that a slot is free.
            elapsed = 0.0
        wait = interval - elapsed
        if wait <= 0:
            return 0.0
        self.timebase.sleep(wait)
        return wait

    def telemetry(self) -> dict[str, Any]:
        """Firewall-safe: rate/cooldown state only, no locator and no content."""
        state = self.load()
        return {"cooldown_active": self.cooldown_remaining(state) > 0,
                "max_requests_per_second": self.policy.max_requests_per_second,
                "max_concurrency": self.policy.max_concurrency}


def seconds_from_retry_after(value: str | None, now: datetime) -> float | None:
    """Parse ``Retry-After`` in either permitted form, or return None.

    The authoritative cooldown wins: the collector never retries sooner than
    this, even when its own backoff schedule would allow it.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return max(float(int(text)), 0.0)
    except ValueError:
        pass
    from email.utils import parsedate_to_datetime
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        from datetime import timezone as _tz
        when = when.replace(tzinfo=_tz.utc)
    return max((when - now).total_seconds(), 0.0)
