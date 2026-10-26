"""Read-only watchdog checks for liveness and pathological runtime behavior."""

from __future__ import annotations

from datetime import datetime, timezone
import math

from .runtime import CampaignState, PersistentQueue


def _qualified_duration(value) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def _elapsed_seconds(timestamp, now: datetime) -> float | None:
    """Unknown, naive or future clocks cannot provide positive liveness proof."""
    try:
        if not isinstance(timestamp, str) or not isinstance(now, datetime):
            return None
        recorded = datetime.fromisoformat(timestamp)
        if recorded.utcoffset() is None or now.utcoffset() is None:
            return None
        elapsed = (now.astimezone(timezone.utc) - recorded.astimezone(timezone.utc)).total_seconds()
        return elapsed if elapsed >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def is_lease_stale(task, now: datetime) -> bool:
    """A worker is healthy only with a qualified, unexpired start/duration.

    Missing, malformed, future or timezone-ambiguous proof raises an alert rather
    than hiding a genuinely dead worker. Equality with expiry is already stale.
    """
    age = _elapsed_seconds(getattr(task, "started_at", None), now)
    duration = getattr(task, "lease_seconds", 600)
    return age is None or not _qualified_duration(duration) or age >= duration


def inspect_health(state: CampaignState, queue: PersistentQueue,
                   heartbeat_timeout_seconds: int = 300, max_attempts: int = 3) -> list[dict[str, str]]:
    if not _qualified_duration(heartbeat_timeout_seconds):
        raise ValueError("heartbeat timeout must be a finite nonnegative number")
    now = datetime.now(timezone.utc)
    heartbeat_age = _elapsed_seconds(state.last_heartbeat, now)
    alerts: list[dict[str, str]] = []
    if heartbeat_age is None or heartbeat_age >= heartbeat_timeout_seconds:
        alerts.append({"code": "HEARTBEAT_MISSING", "detail": str(state.last_heartbeat)})
    for task in queue.tasks.values():
        if task.status == "RUNNING" and is_lease_stale(task, now):
            alerts.append({"code": "WORKER_STUCK", "detail": task.task_id})
        if task.attempts >= max_attempts and task.status in {"PENDING", "FAILED"}:
            alerts.append({"code": "REPEATED_CRASH", "detail": task.task_id})
    keys = [task.execution_key for task in queue.tasks.values()]
    if len(keys) != len(set(keys)):
        alerts.append({"code": "REPEATED_TASK", "detail": "duplicate execution identity"})
    if state.status == "IDLE" and queue.next_due() is not None:
        alerts.append({"code": "QUEUE_STARVATION", "detail": queue.next_due().task_id})
    return alerts
