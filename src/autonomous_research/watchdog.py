"""Read-only watchdog checks for liveness and pathological runtime behavior."""

from __future__ import annotations

from datetime import datetime, timezone

from .runtime import CampaignState, PersistentQueue


def inspect_health(state: CampaignState, queue: PersistentQueue,
                   heartbeat_timeout_seconds: int = 300, max_attempts: int = 3) -> list[dict[str, str]]:
    now = datetime.now(timezone.utc)
    heartbeat = datetime.fromisoformat(state.last_heartbeat)
    alerts: list[dict[str, str]] = []
    if (now - heartbeat).total_seconds() > heartbeat_timeout_seconds:
        alerts.append({"code": "HEARTBEAT_MISSING", "detail": state.last_heartbeat})
    for task in queue.tasks.values():
        if task.status == "RUNNING":
            alerts.append({"code": "WORKER_STUCK", "detail": task.task_id})
        if task.attempts >= max_attempts and task.status in {"PENDING", "FAILED"}:
            alerts.append({"code": "REPEATED_CRASH", "detail": task.task_id})
    keys = [task.execution_key for task in queue.tasks.values()]
    if len(keys) != len(set(keys)):
        alerts.append({"code": "REPEATED_TASK", "detail": "duplicate execution identity"})
    if state.status == "IDLE" and queue.next_due() is not None:
        alerts.append({"code": "QUEUE_STARVATION", "detail": queue.next_due().task_id})
    return alerts
