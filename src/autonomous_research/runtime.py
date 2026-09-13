"""Restart-safe state and queue primitives for a persistent research campaign."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, value: object) -> None:
    """Atomically replace a JSON document so a killed process cannot truncate it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@dataclass
class CampaignState:
    campaign_id: str
    status: str = "IDLE"
    started_at: str = field(default_factory=utc_now)
    last_heartbeat: str = field(default_factory=utc_now)
    cycles_completed: int = 0
    active_ticket_ids: list[str] = field(default_factory=list)
    queued_ticket_ids: list[str] = field(default_factory=list)
    blocked_tasks: list[dict[str, Any]] = field(default_factory=list)
    last_completed_ticket_id: str | None = None
    latest_lesson: str | None = None
    next_action: str | None = None
    processed_data_fingerprints: list[str] = field(default_factory=list)
    research_budget: dict[str, Any] = field(default_factory=lambda: {"max_cycles": None})
    budget_consumed: dict[str, Any] = field(default_factory=lambda: {"cycles": 0})
    pause_reason: str | None = None
    stop_reason: str | None = None

    @classmethod
    def load_or_create(cls, path: Path, campaign_id: str, max_cycles: int | None = None) -> "CampaignState":
        if path.exists():
            return cls(**json.loads(path.read_text(encoding="utf-8")))
        state = cls(campaign_id=campaign_id, research_budget={"max_cycles": max_cycles})
        state.save(path)
        return state

    def save(self, path: Path) -> None:
        _write_json(path, asdict(self))

    def heartbeat(self, path: Path) -> None:
        self.last_heartbeat = utc_now()
        self.save(path)


@dataclass
class ResearchTask:
    task_id: str
    lane: str
    priority: float
    reason: str
    worker: str
    parent: str | None = None
    required_resources: list[str] = field(default_factory=list)
    status: str = "PENDING"
    attempts: int = 0
    blocked_reason: str | None = None
    data_fingerprint: str | None = None
    due_at: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def execution_key(self) -> str:
        return f"{self.task_id}@{self.data_fingerprint or 'no-data'}"


class PersistentQueue:
    """A small JSON queue with stable ordering and durable terminal records."""

    def __init__(self, path: Path):
        self.path = path
        self.tasks: dict[str, ResearchTask] = {}
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.tasks = {item["task_id"]: ResearchTask(**item) for item in payload["tasks"]}

    def save(self) -> None:
        ordered = sorted(self.tasks.values(), key=lambda task: (task.created_at, task.task_id))
        _write_json(self.path, {"version": 1, "tasks": [asdict(task) for task in ordered]})

    def add(self, task: ResearchTask) -> bool:
        existing = self.tasks.get(task.task_id)
        if existing and existing.execution_key == task.execution_key:
            return False
        if existing and existing.status not in {"COMPLETED", "FAILED"}:
            return False
        self.tasks[task.task_id] = task
        self.save()
        return True

    def next_due(self, now: str | None = None) -> ResearchTask | None:
        now = now or utc_now()
        due = [task for task in self.tasks.values()
               if task.status == "PENDING" and (task.due_at is None or task.due_at <= now)]
        return min(due, key=lambda task: (-task.priority, task.created_at, task.task_id), default=None)

    def has_completed(self, task_id: str, fingerprint: str | None) -> bool:
        task = self.tasks.get(task_id)
        return bool(task and task.status == "COMPLETED" and task.data_fingerprint == fingerprint)

    def counts(self) -> dict[str, int]:
        statuses = {name: 0 for name in ("PENDING", "RUNNING", "BLOCKED", "COMPLETED", "FAILED")}
        for task in self.tasks.values():
            statuses[task.status] = statuses.get(task.status, 0) + 1
        return statuses
