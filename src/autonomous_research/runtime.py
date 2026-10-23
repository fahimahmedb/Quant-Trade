"""Restart-safe state and queue primitives for a persistent research campaign."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import wraps
import fcntl
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import threading
from typing import Any

from quant.state import read_json, write_json as _write_json


class CampaignStateConflict(RuntimeError):
    """Another campaign writer changed the snapshot this instance observed."""


class QueueConflict(RuntimeError):
    """A durable queue update invalidated this writer's observed snapshot."""


def _serialized_mutation(method):
    @wraps(method)
    def serialized(self, *args, **kwargs):
        with self._mutation_lock:
            return method(self, *args, **kwargs)
    return serialized


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _queue_clock(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("queue timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("queue timestamp must carry timezone information")
    return parsed.astimezone(timezone.utc)


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

    def __post_init__(self) -> None:
        # Runtime metadata is deliberately outside dataclass fields/wire state.
        self._mutation_lock = threading.RLock()
        self._persisted_by_path: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _unique_fields(pairs):
        document = {}
        for name, value in pairs:
            if name in document:
                raise ValueError("duplicate campaign state field: " + name)
            document[name] = value
        return document

    @classmethod
    def _read_document(cls, path: Path) -> dict[str, Any] | None:
        try:
            document = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=cls._unique_fields)
        except FileNotFoundError:
            return None
        if not isinstance(document, dict):
            raise ValueError("campaign state must be an object")
        json.dumps(document, allow_nan=False)  # Match the existing writer's finite JSON contract.
        cls(**document)  # Preserve existing field/default admission; reject malformed shape.
        return document

    def _adopt(self, key: str, document: dict[str, Any]) -> None:
        restored = type(self)(**deepcopy(document))
        for name, value in asdict(restored).items():
            setattr(self, name, value)
        self._persisted_by_path[key] = deepcopy(document)

    @classmethod
    def load_or_create(cls, path: Path, campaign_id: str, max_cycles: int | None = None) -> "CampaignState":
        path = Path(path)
        document = cls._read_document(path)
        if document is not None:
            state = cls(**document)
            state._persisted_by_path[str(path.resolve())] = deepcopy(document)
            return state
        state = cls(campaign_id=campaign_id, research_budget={"max_cycles": max_cycles})
        try:
            state.save(path)
        except CampaignStateConflict:
            # A concurrent creator won. Loading that truth matches the existing
            # load_or_create contract; do not replace it with our fresh defaults.
            document = cls._read_document(path)
            if document is None:
                raise
            state._adopt(str(path.resolve()), document)
        return state

    @_serialized_mutation
    def save(self, path: Path) -> None:
        path = Path(path)
        key = str(path.resolve())
        fd = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(path.with_name(path.name + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            current = self._read_document(path)
            document = asdict(self)
            # Serialized identity distinguishes bool/int/float aliases as well.
            def encode(value: Any) -> str:
                return json.dumps(value, sort_keys=True, allow_nan=False)
            current_wire, document_wire = encode(current), encode(document)
            if (current_wire != encode(self._persisted_by_path.get(key))
                    and current_wire != document_wire):
                raise CampaignStateConflict("CAMPAIGN_CHANGED_SINCE_READ")
            if current_wire != document_wire:
                _write_json(path, document)
            self._persisted_by_path[key] = deepcopy(document)
        except BaseException:
            try:
                durable = self._read_document(path)
            except (OSError, ValueError, TypeError):
                durable = self._persisted_by_path.get(key)
            if durable is not None:
                self._adopt(key, durable)
            raise
        finally:
            if fd is not None:
                os.close(fd)

    @_serialized_mutation
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
    #: When the current attempt started and how long it may run before its lease
    #: is stale. RUNNING on its own says nothing about health; these do.
    started_at: str | None = None
    lease_seconds: int = 600
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
        if not hasattr(self, "_mutation_lock"):
            self._mutation_lock = threading.RLock()
        self.path = path
        self.tasks: dict[str, ResearchTask] = {}
        observed = read_json(path)
        self._persisted = deepcopy(observed)
        if path.exists():
            if not isinstance(observed, dict):
                raise ValueError("queue state must be an object")
            payload = observed
            if type(payload.get("version")) is not int or payload["version"] != 1:
                raise ValueError("unknown queue schema version")
            self.tasks = {item["task_id"]: ResearchTask(**item) for item in payload["tasks"]}
            if len(self.tasks) != len(payload["tasks"]):
                raise ValueError("duplicate queue task identity")

    @_serialized_mutation
    def save(self) -> None:
        fd = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(self.path.with_name(self.path.name + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX)
            if read_json(self.path) != self._persisted:
                raise QueueConflict("QUEUE_CHANGED_SINCE_READ")
            ordered = sorted(self.tasks.values(), key=lambda task: (task.created_at, task.task_id))
            document = {"version": 1, "tasks": [asdict(task) for task in ordered]}
            _write_json(self.path, document)
            self._persisted = deepcopy(document)
        except BaseException:
            self.__init__(self.path)
            raise
        finally:
            if fd is not None:
                os.close(fd)

    @_serialized_mutation
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
        instant = _queue_clock(utc_now() if now is None else now)
        due = [task for task in self.tasks.values()
               if task.status == "PENDING"
               and (task.due_at is None or _queue_clock(task.due_at) <= instant)]
        return min(due, key=lambda task: (-task.priority, _queue_clock(task.created_at), task.task_id),
                   default=None)

    def has_completed(self, task_id: str, fingerprint: str | None) -> bool:
        task = self.tasks.get(task_id)
        return bool(task and task.status == "COMPLETED" and task.data_fingerprint == fingerprint)

    def counts(self) -> dict[str, int]:
        statuses = {name: 0 for name in ("PENDING", "RUNNING", "BLOCKED", "COMPLETED", "FAILED")}
        for task in self.tasks.values():
            statuses[task.status] = statuses.get(task.status, 0) + 1
        return statuses
