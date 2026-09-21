"""The event-level causal timeline: signal -> order -> fill -> net P&L.

The V1 desk already runs one causal session timeline (decision after close(t),
fill at open(t+1), mark at close(t+1)).  An event lane needs the same discipline
per *event*, because the thing that goes wrong in event studies is not the
session ordering, it is an input that was not yet public at the moment the
decision claims to have been taken.

So every input carries the instant it became available, and the timeline refuses
a decision that consumed an input from its own future.  It also refuses three
quieter defects:

* entry before the authorized public-observability instant;
* a net-of-friction return fed into a coordinate that is defined gross and then
  charged separately, which double counts the frictions;
* research evidence charging *less* friction than the executable path, which
  makes the research object more favourable than the strategy it claims to
  describe.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from ..state import append_jsonl, read_jsonl


#: Ordered stages of one event's life. Each must be at or after the previous one.
TIMELINE_STAGES = ("PUBLIC_OBSERVABILITY", "DECISION", "EXECUTABLE", "ENTRY_FILL",
                   "EXIT_DECISION", "EXIT_FILL", "MARK")

#: The primitive outcome ``T_j`` is gross of Form 4 deployment frictions (EC1 s1).
BASIS_GROSS = "GROSS_OF_DEPLOYMENT_FRICTIONS"
BASIS_NET = "NET_OF_DEPLOYMENT_FRICTIONS"


def instant(value: str) -> datetime:
    """Normalise a date or timestamp to an aware UTC instant.

    A bare date is the session's start of day in UTC. Mixing a date and a
    timestamp in one comparison is exactly how an off-by-one-session lookahead
    hides, so both shapes are normalised rather than compared as strings.
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class InformationInput:
    """One input the decision consumed, and when it became available."""

    name: str
    available_at: str
    #: Where it came from, for provenance.
    source: str = ""
    #: True for an input that is point-in-time by construction.
    point_in_time: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EventTimeline:
    """One event's causal ordering, declared and checkable."""

    event_id: str
    #: Instant the information became publicly observable under the authorized
    #: public-knowledge rule. Entry may not precede it (EC1 s1).
    public_observability_at: str
    decision_at: str
    #: First authorized regular-session open after the decision.
    executable_at: str
    entry_fill_at: str
    exit_decision_at: str | None = None
    exit_fill_at: str | None = None
    marked_at: str | None = None
    inputs: tuple[InformationInput, ...] = ()

    def _ordered(self) -> list[tuple[str, str]]:
        pairs = [("PUBLIC_OBSERVABILITY", self.public_observability_at),
                 ("DECISION", self.decision_at),
                 ("EXECUTABLE", self.executable_at),
                 ("ENTRY_FILL", self.entry_fill_at)]
        for stage, value in (("EXIT_DECISION", self.exit_decision_at),
                             ("EXIT_FILL", self.exit_fill_at),
                             ("MARK", self.marked_at)):
            if value is not None:
                pairs.append((stage, value))
        return pairs

    def violations(self) -> list[str]:
        problems: list[str] = []
        try:
            pairs = [(stage, instant(value)) for stage, value in self._ordered()]
        except ValueError as error:
            return [f"{self.event_id}: TIMESTAMP_NOT_ISO8601:{error}"]

        for (earlier_stage, earlier), (later_stage, later) in zip(pairs, pairs[1:]):
            if later < earlier:
                problems.append(
                    f"{self.event_id}: STAGE_OUT_OF_CAUSAL_ORDER:{later_stage}_BEFORE_"
                    f"{earlier_stage}")

        decision = instant(self.decision_at)
        for item in self.inputs:
            try:
                available = instant(item.available_at)
            except ValueError:
                problems.append(f"{self.event_id}: TIMESTAMP_NOT_ISO8601:{item.name}")
                continue
            if available > decision:
                problems.append(
                    f"{self.event_id}: LOOKAHEAD_INPUT_NOT_YET_AVAILABLE:{item.name}")
            if not item.point_in_time:
                problems.append(
                    f"{self.event_id}: INPUT_NOT_POINT_IN_TIME:{item.name}")
        if instant(self.entry_fill_at) < instant(self.public_observability_at):
            problems.append(f"{self.event_id}: ENTRY_PRECEDES_PUBLIC_OBSERVABILITY")
        if self.marked_at is not None and \
                instant(self.marked_at) < instant(self.entry_fill_at):
            problems.append(f"{self.event_id}: BOOK_MARKED_BEFORE_FILL")
        return problems

    @property
    def causal(self) -> bool:
        return not self.violations()

    def to_dict(self) -> dict[str, Any]:
        document = asdict(self)
        document["inputs"] = [item.to_dict() for item in self.inputs]
        return document


#: Basis a friction charge is expressed against.
BASIS_ENTRY_NOTIONAL = "ENTRY_NOTIONAL"
BASIS_EXIT_NOTIONAL = "EXIT_NOTIONAL"
BASIS_TURNOVER = "ROUND_TRIP_TURNOVER"
CHARGE_BASES = (BASIS_ENTRY_NOTIONAL, BASIS_EXIT_NOTIONAL, BASIS_TURNOVER)


@dataclass(frozen=True)
class FrictionCharge:
    """One friction actually charged against one event."""

    cost_class: str
    bps: float
    basis: str = BASIS_ENTRY_NOTIONAL

    def violations(self) -> list[str]:
        problems: list[str] = []
        if self.basis not in CHARGE_BASES:
            problems.append(f"{self.cost_class}: CHARGE_BASIS_NOT_RECOGNISED")
        if self.bps < 0:
            problems.append(f"{self.cost_class}: NEGATIVE_FRICTION_CHARGE")
        return problems

    def multiplier(self) -> float:
        return 2.0 if self.basis == BASIS_TURNOVER else 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NetOutcome:
    """Gross excess return, frictions, and the net P&L of one event."""

    event_id: str
    notional: float
    security_return: float
    benchmark_return: float
    charges: tuple[FrictionCharge, ...] = ()
    benchmark_symbol: str = "SPY"
    #: Whether ``security_return`` is gross of deployment frictions. It must be:
    #: the frictions are charged once, here, not twice.
    return_basis: str = BASIS_GROSS
    #: One-way friction the *research* object assumed, in bps of notional. It may
    #: not be cheaper than what execution actually charged.
    research_charge_bps: float | None = None

    @property
    def excess_return(self) -> float:
        """``T_j = R_security - R_SPY``, gross."""
        return self.security_return - self.benchmark_return

    @property
    def gross_pnl(self) -> float:
        return self.notional * self.excess_return

    @property
    def executed_charge_bps(self) -> float:
        return sum(charge.bps * charge.multiplier() for charge in self.charges)

    @property
    def friction_cost(self) -> float:
        return self.notional * self.executed_charge_bps / 10_000.0

    @property
    def net_pnl(self) -> float:
        return self.gross_pnl - self.friction_cost

    def violations(self) -> list[str]:
        problems: list[str] = []
        for charge in self.charges:
            problems.extend(f"{self.event_id}: {problem}" for problem in charge.violations())
        if self.benchmark_symbol != "SPY":
            problems.append(f"{self.event_id}: SCIENTIFIC_BENCHMARK_REMAINS_SPY")
        if self.return_basis != BASIS_GROSS:
            problems.append(
                f"{self.event_id}: DELTA_IS_GROSS_OF_FORM4_DEPLOYMENT_FRICTIONS")
        if self.notional < 0:
            problems.append(f"{self.event_id}: NEGATIVE_EVENT_NOTIONAL")
        if (self.research_charge_bps is not None
                and self.research_charge_bps + 1e-12 < self.executed_charge_bps):
            problems.append(
                f"{self.event_id}: RESEARCH_EVIDENCE_CHEAPER_THAN_EXECUTION")
        classes = [charge.cost_class for charge in self.charges]
        if len(set(classes)) != len(classes):
            problems.append(f"{self.event_id}: DUPLICATE_FRICTION_CHARGE_CLASS")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {"event_id": self.event_id, "notional": self.notional,
                "security_return": self.security_return,
                "benchmark_return": self.benchmark_return,
                "benchmark_symbol": self.benchmark_symbol,
                "return_basis": self.return_basis,
                "excess_return": self.excess_return, "gross_pnl": self.gross_pnl,
                "charges": [charge.to_dict() for charge in self.charges],
                "executed_charge_bps": self.executed_charge_bps,
                "friction_cost": self.friction_cost, "net_pnl": self.net_pnl,
                "research_charge_bps": self.research_charge_bps,
                "violations": self.violations()}


def aggregate_allocation_weighted(outcomes: Iterable[NetOutcome]) -> dict[str, Any]:
    """``sum_j a_j T_j / sum_j a_j`` with the exposure as the weight.

    This is the estimator EC1 section 6 names, with its denominator reported
    because the denominator is random: event count, eligibility, overlap and
    capacity all move it, so a variance derived from one primitive return divided
    by an event count would be wrong
    (``PRIMITIVE_RETURN_VARIANCE_IS_NOT_AGGREGATE_ESTIMATOR_VARIANCE``).
    """
    rows = list(outcomes)
    problems: list[str] = []
    for outcome in rows:
        problems.extend(outcome.violations())
    denominator = sum(outcome.notional for outcome in rows)
    if denominator <= 0:
        return {"delta_hat": None, "state": "NO_DEPLOYED_EXPOSURE",
                "event_count": len(rows), "denominator": denominator,
                "violations": problems}
    numerator = sum(outcome.notional * outcome.excess_return for outcome in rows)
    net = sum(outcome.net_pnl for outcome in rows)
    return {"delta_hat": numerator / denominator, "state": "AGGREGATED",
            "event_count": len(rows), "denominator": denominator,
            "gross_pnl": sum(outcome.gross_pnl for outcome in rows),
            "friction_cost": sum(outcome.friction_cost for outcome in rows),
            "net_pnl": net, "violations": problems}


class CausalEventLedger:
    """Append-only, idempotent record of event stages.

    One operation id per (event, stage). A crash between the append and the
    caller's own bookkeeping replays to the same state, and a second attempt to
    record the same stage is a no-op rather than a duplicate row.
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._applied: set[str] = set()
        for record in read_jsonl(self.path):
            operation_id = record.get("operation_id")
            if operation_id:
                self._applied.add(str(operation_id))

    @staticmethod
    def operation_id(event_id: str, stage: str) -> str:
        return hashlib.sha256(f"{event_id}|{stage}".encode("utf-8")).hexdigest()[:24]

    def has_applied(self, operation_id: str) -> bool:
        return operation_id in self._applied

    def record(self, event_id: str, stage: str, payload: Mapping[str, Any],
               operation_id: str | None = None) -> bool:
        """Append one stage. Returns False when it was already recorded."""
        if stage not in TIMELINE_STAGES:
            raise ValueError(f"unknown timeline stage: {stage}")
        identifier = operation_id or self.operation_id(event_id, stage)
        if identifier in self._applied:
            return False
        append_jsonl(self.path, {"operation_id": identifier, "event_id": event_id,
                                 "stage": stage, "payload": dict(payload)})
        self._applied.add(identifier)
        return True

    def replay(self) -> dict[str, dict[str, Any]]:
        """Rebuild per-event stage state from the journal."""
        state: dict[str, dict[str, Any]] = {}
        seen: set[str] = set()
        for record in read_jsonl(self.path):
            operation_id = str(record.get("operation_id", ""))
            if operation_id in seen:
                continue
            seen.add(operation_id)
            event_id = str(record.get("event_id", ""))
            state.setdefault(event_id, {})[str(record.get("stage"))] = record.get("payload")
        return state

    def __len__(self) -> int:
        return len(self._applied)
