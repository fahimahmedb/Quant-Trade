"""The opportunity ticket.

One ticket per strategy per session. It carries the verdict of every stage it
reached and the reason it stopped, so a rejected opportunity leaves exactly as
much evidence as an accepted one. ``OPERATING_MODEL.md`` requires that: the
system has to learn from false rejects, and it cannot do that if rejections
are silent.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..state import utc_now


STAGES = ("SCAN", "VET", "SIZE", "RISK", "FILLS", "BOOK")
TERMINAL = ("BOOKED", "NO_TRADE", "REJECTED", "VETOED", "BLOCKED", "FAULT")


@dataclass
class OpportunityTicket:
    opportunity_id: str
    session_date: str
    strategy_id: str
    lifecycle: str
    ledger: str
    created_at: str = field(default_factory=utc_now)
    #: Session whose open the orders would execute at. Decisions are made after
    #: the close of ``session_date``; nothing can fill earlier than this.
    execution_date: str | None = None
    stage: str = "SCAN"
    status: str = "OPEN"
    reason: str | None = None
    target_weights: dict[str, float] = field(default_factory=dict)
    sized_notional: float = 0.0
    legs: list[dict[str, Any]] = field(default_factory=list)
    fills: list[dict[str, Any]] = field(default_factory=list)
    stage_trace: list[dict[str, Any]] = field(default_factory=list)
    book_effect: dict[str, Any] = field(default_factory=dict)

    def record(self, stage: str, verdict: str, reason: str, **detail: Any) -> None:
        if stage not in STAGES:
            raise ValueError(f"unknown desk stage: {stage}")
        self.stage = stage
        self.stage_trace.append({"stage": stage, "verdict": verdict, "reason": reason,
                                 "at": utc_now(), "detail": detail})

    def stop(self, stage: str, status: str, reason: str, **detail: Any) -> "OpportunityTicket":
        if status not in TERMINAL:
            raise ValueError(f"unknown terminal status: {status}")
        self.record(stage, status, reason, **detail)
        self.status = status
        self.reason = reason
        return self

    def complete(self, reason: str, **detail: Any) -> "OpportunityTicket":
        self.record("BOOK", "BOOKED", reason, **detail)
        self.status = "BOOKED"
        self.reason = reason
        return self

    @property
    def reached(self) -> list[str]:
        return [entry["stage"] for entry in self.stage_trace]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
