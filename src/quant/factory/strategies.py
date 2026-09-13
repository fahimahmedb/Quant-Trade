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
import hashlib
import json

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
    #: Marks a strategy the desk runs at zero capital authority purely to measure
    #: whether rejecting it was the right call. Such a strategy never touches the
    #: capital ledger. Desk counters live in the desk journal, not here, so a
    #: session commits its work and its bookkeeping in one durable write.
    evaluation_track: bool = False
    #: Superseded documents of this strategy, oldest first. Without these the
    #: registry would not be version-preserving, only version-numbered.
    previous_versions: list[dict[str, Any]] = field(default_factory=list)
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
        return EVALUATION_FRACTION if self.evaluation_track else 0.0

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
    """Persistent strategy store plus research-integrity state.

    Two pieces of state deliberately live beside strategy evidence:

    * ``research_partitions`` freezes the discovery/validation boundary for a
      dataset lineage. Appending new market data therefore extends SHADOW rather
      than moving yesterday's holdout back into research.
    * ``trial_reservations`` makes the multiple-testing budget idempotent. A
      crash/retry of the same declared grid returns the original reservation
      instead of buying another Bonferroni penalty for no new hypothesis.
    """

    def __init__(self, path: Path):
        self.path = path
        payload = read_json(path, {}) or {}
        self.strategies: dict[str, StrategyDefinition] = {
            key: StrategyDefinition(**value)
            for key, value in (payload.get("strategies") or {}).items()}
        self.trials: dict[str, int] = dict(payload.get("trials") or {})
        self.trial_reservations: dict[str, dict[str, Any]] = dict(
            payload.get("trial_reservations") or {})
        self.research_partitions: dict[str, dict[str, dict[str, str]]] = dict(
            payload.get("research_partitions") or {})
        self.research_cohorts: dict[str, str] = dict(payload.get("research_cohorts") or {})

    def save(self) -> None:
        write_json(self.path, {
            "version": 2,
            "strategies": {key: value.to_dict()
                           for key, value in sorted(self.strategies.items())},
            "trials": dict(sorted(self.trials.items())),
            "trial_reservations": dict(sorted(self.trial_reservations.items())),
            "research_partitions": dict(sorted(self.research_partitions.items())),
            "research_cohorts": dict(sorted(self.research_cohorts.items()))})

    def record_trials(self, dataset_key: str, count: int,
                      experiment_key: str | None = None) -> int:
        """Reserve a declared grid exactly once and return the cumulative total.

        ``experiment_key`` must identify the scientific experiment, not the
        worker attempt. Retrying the same experiment after a crash is therefore
        idempotent, while a genuinely different declared grid receives a new
        reservation and tightens the threshold.
        """
        if count < 0:
            raise ValueError("trial count cannot be negative")
        if experiment_key:
            existing = self.trial_reservations.get(experiment_key)
            if existing is not None:
                if existing.get("dataset_key") != dataset_key or int(existing.get("count", -1)) != count:
                    raise ValueError("experiment key reused for a different trial reservation")
                return int(existing["cumulative"])
        cumulative = self.trials.get(dataset_key, 0) + count
        self.trials[dataset_key] = cumulative
        if experiment_key:
            self.trial_reservations[experiment_key] = {
                "dataset_key": dataset_key, "count": count,
                "cumulative": cumulative, "reserved_at": utc_now()}
        self.save()
        return cumulative

    def trial_count(self, dataset_key: str) -> int:
        return self.trials.get(dataset_key, 0)

    def research_partition(self, dataset_id: str) -> dict[str, dict[str, str]] | None:
        partition = self.research_partitions.get(dataset_id)
        return dict(partition) if partition else None

    def preserve_research_partition(self, dataset_id: str,
                                    windows: dict[str, Any]) -> dict[str, dict[str, str]]:
        """Freeze the first declared research split for this dataset lineage."""
        existing = self.research_partitions.get(dataset_id)
        if existing is not None:
            return existing
        documents = {
            name: (window.to_dict() if hasattr(window, "to_dict") else dict(window))
            for name, window in windows.items()}
        required = {"DISCOVERY", "VALIDATION", "SHADOW"}
        if set(documents) != required:
            raise ValueError(f"research partition must contain {sorted(required)}")
        self.research_partitions[dataset_id] = documents
        self.save()
        return documents

    def preserve_research_cohort(self, dataset_id: str, rows: list[dict[str, Any]]) -> str:
        """Freeze a digest of all bytes/values inside the declared research cohort.

        Appends beyond VALIDATION do not alter this digest; a historical rewrite
        does, and is therefore a review boundary rather than a fresh experiment.
        """
        digest = "sha256:" + hashlib.sha256(
            json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        existing = self.research_cohorts.get(dataset_id)
        if existing is not None and existing != digest:
            raise ValueError(f"historical research cohort changed for {dataset_id}")
        if existing is None:
            self.research_cohorts[dataset_id] = digest
            self.save()
        return digest

    def upsert(self, definition: StrategyDefinition) -> StrategyDefinition:
        """Store a strategy, keeping any superseded document inspectable."""
        existing = self.strategies.get(definition.strategy_id)
        if existing is not None and existing.version != definition.version:
            archived = existing.to_dict()
            archived.pop("previous_versions", None)
            definition.previous_versions = existing.previous_versions + [archived]
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
