"""Restart-safe orchestration for autonomous research campaigns.

The runtime deliberately separates durable scheduling state from research
workers.  A worker receives one task, returns an outcome, and cannot decide
that the campaign is finished merely because its experiment failed.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


Clock = Callable[[], str]
Worker = Callable[[dict[str, Any]], "TaskOutcome"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_json(path: Path, value: Any) -> None:
    """Durably replace a JSON document without exposing a partial write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


@dataclass(frozen=True)
class TaskOutcome:
    status: str
    lesson: str
    next_action: str | None = None
    completed_ticket_id: str | None = None
    data_fingerprint: str | None = None
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"COMPLETED", "BLOCKED"}:
            raise ValueError(f"unsupported task outcome: {self.status}")
        if self.status == "BLOCKED" and not self.blocked_reason:
            raise ValueError("a blocked outcome requires blocked_reason")


@dataclass
class ResearchTask:
    task_id: str
    kind: str
    priority: float
    payload: dict[str, Any] = field(default_factory=dict)
    status: str = "QUEUED"
    attempts: int = 0
    created_at: str = field(default_factory=utc_now)
    started_at: str | None = None
    finished_at: str | None = None
    blocked_reason: str | None = None
    lesson: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ResearchTask":
        return cls(**value)


class CampaignRuntime:
    """Run the highest-value executable task and checkpoint every transition."""

    def __init__(self, state_path: Path, queue_path: Path,
                 workers: dict[str, Worker] | None = None, clock: Clock = utc_now):
        self.state_path, self.queue_path = Path(state_path), Path(queue_path)
        self.workers = workers or {}
        self.clock = clock
        self.state = self._load_or_create_state()
        self.tasks = self._load_queue()
        self._recover_interrupted_tasks()
        self._sync_and_save()

    def _load_or_create_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        now = self.clock()
        return {
            "campaign_id": f"campaign-{uuid.uuid4().hex[:12]}",
            "status": "IDLE", "started_at": now, "last_heartbeat": now,
            "cycles_completed": 0, "active_ticket_ids": [],
            "queued_ticket_ids": [], "blocked_tasks": [],
            "last_completed_ticket_id": None, "latest_lesson": None,
            "next_action": "Enqueue the highest-value available research task.",
            "processed_data_fingerprints": [], "research_budget": {},
            "budget_consumed": {"tasks": 0}, "pause_reason": None,
            "stop_reason": None,
        }

    def _load_queue(self) -> list[ResearchTask]:
        if not self.queue_path.exists():
            return []
        raw = json.loads(self.queue_path.read_text(encoding="utf-8"))
        return [ResearchTask.from_dict(item) for item in raw]

    def _recover_interrupted_tasks(self) -> None:
        for task in self.tasks:
            if task.status == "ACTIVE":
                task.status = "QUEUED"
                task.started_at = None
        self.state["active_ticket_ids"] = []

    def enqueue(self, task: ResearchTask) -> bool:
        """Add unique work; completed and blocked tasks are also deduplication keys."""
        if any(existing.task_id == task.task_id for existing in self.tasks):
            return False
        task.created_at = self.clock()
        self.tasks.append(task)
        self._sync_and_save()
        return True

    def heartbeat(self) -> None:
        self.state["last_heartbeat"] = self.clock()
        self._sync_and_save()

    def pause(self, reason: str) -> None:
        self.state.update(status="PAUSED", pause_reason=reason)
        self.heartbeat()

    def stop(self, reason: str) -> None:
        self.state.update(status="STOPPED", stop_reason=reason)
        self.heartbeat()

    def run_once(self) -> TaskOutcome | None:
        if self.state["status"] in {"PAUSED", "STOPPED"}:
            self.heartbeat()
            return None
        budget = self.state.get("research_budget", {}).get("max_tasks")
        consumed = self.state.get("budget_consumed", {}).get("tasks", 0)
        if budget is not None and consumed >= budget:
            self.pause("configured task budget exhausted")
            return None

        executable = [task for task in self.tasks
                      if task.status == "QUEUED" and task.kind in self.workers]
        if not executable:
            self.state.update(status="IDLE", next_action=self._idle_reason())
            self.heartbeat()
            return None

        task = sorted(executable, key=lambda item: (-item.priority, item.created_at, item.task_id))[0]
        task.status, task.started_at = "ACTIVE", self.clock()
        task.attempts += 1
        self.state.update(status="RUNNING", active_ticket_ids=[task.task_id])
        self._sync_and_save()  # restart can now see in-flight work
        try:
            outcome = self.workers[task.kind](task.payload)
        except Exception as exc:
            task.status, task.blocked_reason = "BLOCKED", f"worker error: {type(exc).__name__}: {exc}"
            outcome = TaskOutcome("BLOCKED", "Worker failure preserved for inspection.",
                                  blocked_reason=task.blocked_reason)
        task.status, task.finished_at = outcome.status, self.clock()
        task.lesson, task.blocked_reason = outcome.lesson, outcome.blocked_reason
        self.state["cycles_completed"] += 1
        self.state["budget_consumed"]["tasks"] = consumed + 1
        self.state["latest_lesson"] = outcome.lesson
        if outcome.completed_ticket_id:
            self.state["last_completed_ticket_id"] = outcome.completed_ticket_id
        if outcome.data_fingerprint and outcome.data_fingerprint not in self.state["processed_data_fingerprints"]:
            self.state["processed_data_fingerprints"].append(outcome.data_fingerprint)
        more_work = any(item.status == "QUEUED" and item.kind in self.workers for item in self.tasks)
        self.state.update(
            status="RUNNING" if more_work else "IDLE",
            active_ticket_ids=[],
            next_action=outcome.next_action or (None if more_work else self._idle_reason()),
        )
        self._sync_and_save()
        return outcome

    def run_forever(self, poll_seconds: float = 60.0) -> None:
        while self.state["status"] not in {"PAUSED", "STOPPED"}:
            self.run_once()
            time.sleep(poll_seconds)

    def _idle_reason(self) -> str:
        blocked = [task for task in self.tasks if task.status == "BLOCKED"]
        unknown = [task for task in self.tasks if task.status == "QUEUED"]
        if unknown:
            return "Queued work has no registered worker; install or enable the required capability."
        if blocked:
            return "All remaining work is blocked; retain tasks and wait for the required resource."
        return "No credible task is queued; wait for new data or enqueue the next scan."

    def _sync_and_save(self) -> None:
        self.state["queued_ticket_ids"] = [task.task_id for task in self.tasks if task.status == "QUEUED"]
        self.state["blocked_tasks"] = [
            {"task_id": task.task_id, "kind": task.kind, "reason": task.blocked_reason}
            for task in self.tasks if task.status == "BLOCKED"
        ]
        _atomic_json(self.queue_path, [asdict(task) for task in self.tasks])
        _atomic_json(self.state_path, self.state)
