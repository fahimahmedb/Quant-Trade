"""Durable state primitives shared by every plane.

Two rules hold everywhere in Quant:

* a process killed mid-write must never leave a truncated state document;
* state that a later process needs must be written before it is reported.
"""

from __future__ import annotations

import json
import os
import fcntl
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


COMPONENT_STATES = ("RUN", "IDLE", "BLOCKED", "FAULT", "PAUSED")

#: Logical functions the North Star requires the system to expose state for.
COMPONENTS = ("CONTROL", "DATA", "SEC_CAPTURE", "RESEARCH", "SCAN", "VET", "SIZE",
              "RISK", "FILLS", "BOOK", "LEARNING", "BUILD")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _sec_evidence_path(path: Path) -> bool:
    """SEC P0 journals fail closed on any torn/corrupt tail."""
    return "sec" in path.parts


def write_json(path: Path, value: Any) -> None:
    """Atomically and durably replace a JSON document.

    A unique staging file prevents two writers from sharing the old fixed .tmp
    name.  fsync of both file and directory makes a successful return durable
    across a crash rather than merely visible in page cache.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def create_json_once(path: Path, value: Any) -> None:
    """Durably create a JSON document exactly once, never overwrite it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.freeze.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _discard_torn_jsonl_tail(path: Path) -> None:
    """Repair only non-SEC generic logs.

    Acquisition-critical SEC journals never self-repair: a torn tail is evidence
    of an interrupted durable operation and must invalidate readiness until an
    explicit recovery procedure accounts for it.
    """
    if _sec_evidence_path(path):
        return
    if not path.exists() or path.stat().st_size == 0:
        return
    with path.open("rb+") as handle:
        handle.seek(-1, os.SEEK_END)
        if handle.read(1) == b"\n":
            return
        handle.seek(0)
        data = handle.read()
        last_newline = data.rfind(b"\n")
        handle.seek(0)
        handle.truncate(last_newline + 1 if last_newline >= 0 else 0)
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(path.parent)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Durably serialize one JSONL append.

    Writers share a lock.  SEC evidence refuses an existing torn tail rather
    than discarding it and manufacturing a clean-looking history.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if _sec_evidence_path(path) and path.exists() and path.stat().st_size:
            with path.open("rb") as check:
                check.seek(-1, os.SEEK_END)
                if check.read(1) != b"\n":
                    raise ValueError("SEC_JOURNAL_TORN_TAIL")
        else:
            _discard_torn_jsonl_tail(path)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_directory(path.parent)
    finally:
        os.close(lock_fd)


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return iter(())

    def _iterate() -> Iterator[dict[str, Any]]:
        data = path.read_bytes()
        if _sec_evidence_path(path) and data and not data.endswith(b"\n"):
            raise ValueError("SEC_JOURNAL_TORN_TAIL")
        lines = data.decode("utf-8").splitlines(keepends=True)
        for index, line in enumerate(lines):
            if not line.strip():
                if _sec_evidence_path(path):
                    raise ValueError("SEC_JOURNAL_EMPTY_RECORD")
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                if (not _sec_evidence_path(path)
                        and index == len(lines) - 1 and not line.endswith("\n")):
                    return
                raise ValueError("JOURNAL_CORRUPT") from None
            if not isinstance(value, dict):
                raise ValueError("JOURNAL_RECORD_NOT_OBJECT")
            yield value

    return _iterate()


@dataclass
class ComponentStatus:
    """State of one logical function, as required by ``OPERATING_MODEL.md``."""

    component: str
    state: str = "IDLE"
    since: str = field(default_factory=utc_now)
    detail: str | None = None
    last_active_at: str | None = None
    runs: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"component": self.component, "state": self.state, "since": self.since,
                "detail": self.detail, "last_active_at": self.last_active_at, "runs": self.runs}


class ComponentRegistry:
    """Persistent RUN/IDLE/BLOCKED/FAULT/PAUSED state for every logical function."""

    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.statuses: dict[str, ComponentStatus] = {
            name: ComponentStatus(**payload[name]) if name in payload else ComponentStatus(name)
            for name in COMPONENTS}

    def set(self, component: str, state: str, detail: str | None = None) -> None:
        if state not in COMPONENT_STATES:
            raise ValueError(f"unknown component state: {state}")
        status = self.statuses.setdefault(component, ComponentStatus(component))
        if status.state != state:
            status.since = utc_now()
        status.state = state
        status.detail = detail
        if state == "RUN":
            status.last_active_at = utc_now()
            status.runs += 1
        self.save()

    def get(self, component: str) -> ComponentStatus:
        return self.statuses.setdefault(component, ComponentStatus(component))

    def save(self) -> None:
        write_json(self.path, {name: status.to_dict() for name, status in self.statuses.items()})

    def snapshot(self) -> dict[str, dict[str, Any]]:
        return {name: status.to_dict() for name, status in sorted(self.statuses.items())}
