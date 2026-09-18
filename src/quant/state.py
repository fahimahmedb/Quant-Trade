"""Durable state primitives shared by every plane.

Two rules hold everywhere in Quant:

* a process killed mid-write must never leave a truncated state document;
* state that a later process needs must be written before it is reported.
"""

from __future__ import annotations

import json
import os
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


def write_json(path: Path, value: Any) -> None:
    """Atomically replace a JSON document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _discard_torn_jsonl_tail(path: Path) -> None:
    """Remove only an unterminated final record left by an interrupted append.

    A malformed newline-terminated record is *not* repaired here: that is
    durable corruption and readers should raise.  The only automatically
    recoverable case is the final line lacking its terminating newline, which
    is exactly the shape a process kill can leave while appending one record.
    """
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


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Durably append one JSONL record and recover a torn final append first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    _discard_torn_jsonl_tail(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return iter(())

    def _iterate() -> Iterator[dict[str, Any]]:
        with path.open(encoding="utf-8") as handle:
            lines = handle.readlines()
        for index, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # A process may die between bytes of the final append.  Ignore
                # only that unterminated tail; corruption of any committed line
                # remains loud rather than being silently skipped.
                if index == len(lines) - 1 and not line.endswith("\n"):
                    return
                raise

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
