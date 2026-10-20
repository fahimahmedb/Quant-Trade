"""Non-authoritative Oracle V2 -> Live Lab projection bridge.

Scientific truth remains in GitHub. This module mirrors already-committed Oracle
worker events to a local durable outbox. Network delivery is handled by a
separate process so Site availability can never gate research execution.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Mapping

from .github_state import PREFIX
from .live_lab_contract import live_ui_metadata
from .oracle_worker import next_stage

OUTBOX_SCHEMA = "oracle-live-lab-outbox-v1"
DEFAULT_OUTBOX = Path("/var/lib/quant-research-v2/live-lab-outbox")
EVENT_FIELDS = (
    "event_id",
    "session_id",
    "worker_id",
    "action_id",
    "event_type",
    "event_seq",
    "generation",
    "emitted_at",
    "payload",
)
SAFE_EVENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,240}$")


class LiveLabProjectionError(RuntimeError):
    pass


def _canonical_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _lane_from_worker_id(worker_id: str) -> str:
    if "." not in worker_id:
        raise LiveLabProjectionError("LIVE_LAB_EVENT_WORKER_LANE_MISSING")
    return worker_id.rsplit(".", 1)[1]


def _task_from_writes(writes: Mapping[str, Any], action_id: str) -> Mapping[str, Any] | None:
    value = writes.get(PREFIX + f"tasks/{action_id}.json")
    return value if isinstance(value, Mapping) else None


def project_live_event(event: Mapping[str, Any], writes: Mapping[str, Any]) -> dict[str, Any]:
    """Create a factual Site projection without mutating the canonical event."""
    missing = [key for key in EVENT_FIELDS if key not in event]
    if missing:
        raise LiveLabProjectionError("LIVE_LAB_EVENT_FIELDS_MISSING:" + ",".join(missing))
    if not isinstance(event["payload"], Mapping):
        raise LiveLabProjectionError("LIVE_LAB_EVENT_PAYLOAD_NOT_OBJECT")
    if not isinstance(event["event_seq"], int) or event["event_seq"] < 1:
        raise LiveLabProjectionError("LIVE_LAB_EVENT_SEQUENCE_INVALID")
    if not isinstance(event["generation"], int) or event["generation"] < 1:
        raise LiveLabProjectionError("LIVE_LAB_EVENT_GENERATION_INVALID")
    if not SAFE_EVENT_ID.fullmatch(str(event["event_id"])):
        raise LiveLabProjectionError("LIVE_LAB_EVENT_ID_UNSAFE")

    projected = deepcopy(dict(event))
    payload = deepcopy(dict(event["payload"]))
    lane = _lane_from_worker_id(str(event["worker_id"]))
    stage = payload.get("stage")

    if event["event_type"] == "ACTION_STARTED":
        task = _task_from_writes(writes, str(event["action_id"]))
        if task is None:
            raise LiveLabProjectionError("LIVE_LAB_STARTED_EVENT_TASK_CONTEXT_MISSING")
        stage = next_stage(task, lane)

    if stage:
        payload.update(live_ui_metadata(lane, str(stage)))
    else:
        payload.setdefault("ui_activity", "none")

    # Keep the actual Oracle worker identity unchanged. The Site must validate
    # the source identity it receives rather than accepting an invented alias.
    projected["payload"] = payload
    return projected


@dataclass
class LocalLiveLabOutbox:
    root: Path = DEFAULT_OUTBOX

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.pending_dir = self.root / "pending"
        self.sent_dir = self.root / "sent"
        self.session_dir = self.root / "sessions"
        for path in (self.root, self.pending_dir, self.sent_dir, self.session_dir):
            path.mkdir(parents=True, exist_ok=True)
            os.chmod(path, 0o700)

    @staticmethod
    def _name(event_id: str) -> str:
        digest = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
        return digest + ".json"

    def enqueue(self, event: Mapping[str, Any]) -> Path:
        event = deepcopy(dict(event))
        event_hash = hashlib.sha256(_canonical_bytes(event)).hexdigest()
        envelope = {
            "schema_version": OUTBOX_SCHEMA,
            "event_hash": event_hash,
            "event": event,
        }
        target = self.pending_dir / self._name(str(event["event_id"]))
        sent = self.sent_dir / target.name
        for existing in (target, sent):
            if existing.exists():
                prior = json.loads(existing.read_text())
                if prior.get("event_hash") != event_hash:
                    raise LiveLabProjectionError("LIVE_LAB_EVENT_ID_COLLISION")
                return existing

        temp = self.pending_dir / ("." + target.name + f".{os.getpid()}.tmp")
        data = _canonical_bytes(envelope) + b"\n"
        fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
            dirfd = os.open(self.pending_dir, os.O_RDONLY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        finally:
            if temp.exists():
                temp.unlink()
        return target

    def pending(self) -> list[Path]:
        return sorted(self.pending_dir.glob("*.json"))

    def mark_sent(self, pending: Path) -> Path:
        target = self.sent_dir / pending.name
        if target.exists():
            pending.unlink(missing_ok=True)
            return target
        os.replace(pending, target)
        return target

    def session_marker(self, session_id: str) -> Path:
        return self.session_dir / (hashlib.sha256(session_id.encode("utf-8")).hexdigest() + ".ok")

    def mark_session(self, session_id: str) -> None:
        target = self.session_marker(session_id)
        if target.exists():
            return
        temp = target.with_name("." + target.name + f".{os.getpid()}.tmp")
        fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write((session_id + "\n").encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        finally:
            if temp.exists():
                temp.unlink()


class LiveLabProjectionStore:
    """Mirror canonical event writes after the authoritative commit succeeds."""

    def __init__(self, store: Any, outbox: LocalLiveLabOutbox):
        self.store = store
        self.outbox = outbox
        self.last_projection_error: str | None = None

    def __getattr__(self, name: str) -> Any:
        return getattr(self.store, name)

    def commit(self, snapshot, writes, **kwargs):
        commit_sha = self.store.commit(snapshot, writes, **kwargs)
        try:
            for path, value in writes.items():
                if not path.startswith(PREFIX + "events/") or not isinstance(value, Mapping):
                    continue
                self.outbox.enqueue(project_live_event(value, writes))
            self.last_projection_error = None
        except Exception as exc:  # projection must never invalidate a scientific commit
            self.last_projection_error = f"{type(exc).__name__}:{exc}"
            print("LIVE_LAB_PROJECTION_DEGRADED:" + self.last_projection_error, file=sys.stderr)
        return commit_sha


def attach_live_lab_projection(worker, outbox_root: Path | str = DEFAULT_OUTBOX):
    """Attach post-commit projection to an already-built V2 worker."""
    if isinstance(worker.store, LiveLabProjectionStore):
        return worker
    worker.store = LiveLabProjectionStore(worker.store, LocalLiveLabOutbox(Path(outbox_root)))
    return worker
