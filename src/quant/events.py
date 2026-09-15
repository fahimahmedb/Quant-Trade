"""Append-only system event trace.

Every plane writes here. The status surface and ``CHIEF_BRIEF.md`` are rendered
from this trace plus persistent state, never from values held in memory by one
process. If an event is not in this log it did not happen.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .state import append_jsonl, read_jsonl, utc_now


SEVERITIES = ("INFO", "WARN", "FAULT")


@dataclass
class SystemEvent:
    plane: str
    component: str
    kind: str
    subject: str
    severity: str = "INFO"
    ts: str = field(default_factory=utc_now)
    detail: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"unknown severity: {self.severity}")
        if not self.event_id:
            seed = f"{self.ts}|{self.plane}|{self.component}|{self.kind}|{self.subject}"
            self.event_id = hashlib.sha256(seed.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventLog:
    def __init__(self, path: Path):
        self.path = path

    def emit(self, plane: str, component: str, kind: str, subject: str,
             severity: str = "INFO", **detail: Any) -> SystemEvent:
        event = SystemEvent(plane=plane, component=component, kind=kind, subject=subject,
                            severity=severity, detail=detail)
        append_jsonl(self.path, event.to_dict())
        return event

    def all(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.path))

    def recent(self, limit: int = 20, kinds: Iterable[str] | None = None) -> list[dict[str, Any]]:
        events = self.all()
        if kinds is not None:
            wanted = set(kinds)
            events = [event for event in events if event["kind"] in wanted]
        return events[-limit:][::-1]

    def faults(self) -> list[dict[str, Any]]:
        return [event for event in self.all() if event["severity"] == "FAULT"]

    def count(self) -> int:
        return len(self.all())
