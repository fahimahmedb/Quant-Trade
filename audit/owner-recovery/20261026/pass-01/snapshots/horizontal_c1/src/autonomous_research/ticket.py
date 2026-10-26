"""Persistent research ticket and deliberately restrictive state machine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


TRANSITIONS = {
    "DETECTED": {"FILTERED", "RESEARCHING", "REJECTED"},
    "FILTERED": {"LEARNED"},
    "RESEARCHING": {"REJECTED", "REVISE", "VALIDATED"},
    "REJECTED": {"LEARNED"},
    "REVISE": {"RESEARCHING", "LEARNED"},
    "VALIDATED": {"LEARNED"},
    "LEARNED": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ResearchTicket:
    ticket_id: str
    lane: str
    observation: str
    created_at: str = field(default_factory=utc_now)
    status: str = "DETECTED"
    updated_at: str | None = None
    market: str | None = None
    instruments: list[str] = field(default_factory=list)
    observed_at: str | None = None
    information_available_at: str | None = None
    source_refs: list[str] = field(default_factory=list)
    candidate_data: dict[str, Any] = field(default_factory=dict)
    filter_result: dict[str, Any] = field(default_factory=dict)
    hypothesis: dict[str, Any] = field(default_factory=dict)
    test_result: dict[str, Any] = field(default_factory=dict)
    validation_result: dict[str, Any] = field(default_factory=dict)
    paper_decision: dict[str, Any] = field(default_factory=dict)
    lesson: str | None = None
    next_action_hint: str | None = None

    def transition(self, new_status: str) -> None:
        if new_status not in TRANSITIONS.get(self.status, set()):
            raise ValueError(f"invalid ticket transition: {self.status} -> {new_status}")
        self.status = new_status
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
