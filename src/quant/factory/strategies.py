"""Versioned strategy definitions and their lifecycle.

``OPERATING_MODEL.md`` defines the lifecycle as

``RESEARCH -> VALIDATED -> SHADOW -> ACTIVE_SHADOW -> DECAYING -> RETIRED``

A strategy carries the evidence that justified it, the dataset version that
evidence came from, and its live shadow health. Nothing else in the system is
allowed to trade a strategy that is not in a tradable lifecycle state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json
from .signals import StrategySpec


LIFECYCLE = ("RESEARCH", "VALIDATED", "SHADOW", "ACTIVE_SHADOW", "DECAYING", "RETIRED")

#: Lifecycle states the Capital Desk may act on, and the capital fraction each
#: is entitled to. A strategy with evidence but no shadow track record trades
#: at probe size only.
TRADABLE = {"SHADOW": 0.35, "ACTIVE_SHADOW": 1.0, "DECAYING": 0.25}

#: Size used for a strategy on the evaluation track. Zero *authority* is not the
#: same as zero *size*: the counterfactual only answers "was rejecting this
#: right?" if it is measured at the size the strategy would actually have been
#: given, which for a newly validated strategy is the SHADOW fraction.
EVALUATION_FRACTION = TRADABLE["SHADOW"]

TRANSITIONS = {
    "RESEARCH": {"VALIDATED", "RETIRED"},
    "VALIDATED": {"SHADOW", "RETIRED"},
    "SHADOW": {"ACTIVE_SHADOW", "DECAYING", "RETIRED"},
    "ACTIVE_SHADOW": {"DECAYING", "RETIRED"},
    "DECAYING": {"ACTIVE_SHADOW", "RETIRED"},
    "RETIRED": set(),
}


@dataclass
class StrategyDefinition:
    strategy_id: str
    version: int
    lane: str
    spec: dict[str, Any]
    hypothesis: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    lifecycle: str = "RESEARCH"
    dataset_id: str | None = None
    dataset_fingerprint: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    lifecycle_history: list[dict[str, str]] = field(default_factory=list)
    shadow: dict[str, Any] = field(default_factory=lambda: {
        "sessions": 0, "net_pnl": 0.0, "gross_pnl": 0.0, "costs": 0.0,
        "wins": 0, "losses": 0, "peak_pnl": 0.0, "max_drawdown": 0.0})
    #: Desk-side execution state. ``evaluation_track`` marks a strategy the desk
    #: runs at zero capital authority purely to measure whether rejecting it was
    #: the right call; such a strategy never touches the capital ledger.
    desk: dict[str, Any] = field(default_factory=lambda: {
        "evaluation_track": False, "last_rebalance_date": None, "sessions": 0,
        "tickets": 0, "no_trade": 0, "vetoed": 0, "booked": 0})
    retirement_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_spec(self) -> StrategySpec:
        return StrategySpec(**self.spec)

    @property
    def tradable(self) -> bool:
        return self.lifecycle in TRADABLE

    @property
    def capital_fraction(self) -> float:
        if self.tradable:
            return TRADABLE[self.lifecycle]
        return EVALUATION_FRACTION if self.desk.get("evaluation_track") else 0.0

    def transition(self, new_state: str, reason: str) -> None:
        if new_state not in TRANSITIONS.get(self.lifecycle, set()):
            raise ValueError(f"invalid lifecycle transition: {self.lifecycle} -> {new_state}")
        self.lifecycle_history.append({"from": self.lifecycle, "to": new_state,
                                       "reason": reason, "at": utc_now()})
        self.lifecycle = new_state
        self.updated_at = utc_now()
        if new_state == "RETIRED":
            self.retirement_reason = reason


class StrategyRegistry:
    """Persistent strategy store plus the dataset-level multiple-testing counter."""

    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.strategies: dict[str, StrategyDefinition] = {
            key: StrategyDefinition(**value)
            for key, value in (payload.get("strategies") or {}).items()}
        #: How many distinct expressions have been tested against each dataset
        #: version. Validation thresholds tighten as this grows.
        self.trials: dict[str, int] = dict(payload.get("trials") or {})

    def save(self) -> None:
        write_json(self.path, {
            "version": 1,
            "strategies": {key: value.to_dict()
                           for key, value in sorted(self.strategies.items())},
            "trials": dict(sorted(self.trials.items()))})

    def record_trials(self, dataset_key: str, count: int) -> int:
        """Count tested expressions. Returns the cumulative total."""
        self.trials[dataset_key] = self.trials.get(dataset_key, 0) + count
        self.save()
        return self.trials[dataset_key]

    def trial_count(self, dataset_key: str) -> int:
        return self.trials.get(dataset_key, 0)

    def upsert(self, definition: StrategyDefinition) -> StrategyDefinition:
        self.strategies[definition.strategy_id] = definition
        self.save()
        return definition

    def get(self, strategy_id: str) -> StrategyDefinition | None:
        return self.strategies.get(strategy_id)

    def tradable(self) -> list[StrategyDefinition]:
        return sorted((item for item in self.strategies.values() if item.tradable),
                      key=lambda item: item.strategy_id)

    def by_lifecycle(self) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = {name: [] for name in LIFECYCLE}
        for definition in self.strategies.values():
            grouped[definition.lifecycle].append(definition.strategy_id)
        return {key: sorted(value) for key, value in grouped.items()}
