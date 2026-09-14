"""Outcome-blind experiment contracts and registry for Quant's Research Factory.

The scientific protocol is immutable within a version. Scientific changes create a new
version. Dataset references may be attached only after preregistration and are frozen by
the Blue Team gate. This module deliberately has no dependency on market-price code.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime
from enum import Enum
import hashlib
import json
from typing import Any, Iterable


class ExperimentError(ValueError):
    """Raised when an experiment contract or lifecycle transition is invalid."""


class ExperimentStatus(str, Enum):
    PROPOSED = "PROPOSED"
    PREREGISTERED = "PREREGISTERED"
    DATA_READY = "DATA_READY"
    BLUE_FROZEN = "BLUE_FROZEN"
    TESTING = "TESTING"
    PROMISING = "PROMISING"
    REJECT = "REJECT"
    INSUFFICIENT = "INSUFFICIENT"
    RETIRED = "RETIRED"


_ALLOWED_TRANSITIONS: dict[ExperimentStatus, frozenset[ExperimentStatus]] = {
    ExperimentStatus.PROPOSED: frozenset({ExperimentStatus.PREREGISTERED}),
    ExperimentStatus.PREREGISTERED: frozenset({ExperimentStatus.DATA_READY}),
    ExperimentStatus.DATA_READY: frozenset({ExperimentStatus.BLUE_FROZEN}),
    ExperimentStatus.BLUE_FROZEN: frozenset({ExperimentStatus.TESTING}),
    ExperimentStatus.TESTING: frozenset({
        ExperimentStatus.PROMISING,
        ExperimentStatus.REJECT,
        ExperimentStatus.INSUFFICIENT,
    }),
    ExperimentStatus.PROMISING: frozenset({ExperimentStatus.RETIRED}),
    ExperimentStatus.REJECT: frozenset({ExperimentStatus.RETIRED}),
    ExperimentStatus.INSUFFICIENT: frozenset({ExperimentStatus.RETIRED}),
    ExperimentStatus.RETIRED: frozenset(),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EventRecord:
    """Only event fields the generic Research Factory is allowed to depend on."""

    event_id: str
    issuer_id: str
    event_time: str
    formation_date: str
    provenance: str
    status: str

    def __post_init__(self) -> None:
        for name in ("event_id", "issuer_id", "event_time", "formation_date", "provenance", "status"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ExperimentError(f"{name} must be a non-empty string")
        try:
            date.fromisoformat(self.formation_date)
        except ValueError as exc:
            raise ExperimentError("formation_date must be a valid ISO YYYY-MM-DD date") from exc
        try:
            timestamp = datetime.fromisoformat(self.event_time.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ExperimentError("event_time must be a valid ISO date-time") from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ExperimentError("event_time must be timezone-aware")


@dataclass(frozen=True)
class DatasetRef:
    dataset_id: str
    version: str
    content_hash: str
    role: str = "formation"

    def __post_init__(self) -> None:
        if not self.dataset_id or not self.version or not self.content_hash:
            raise ExperimentError("dataset_id, version and content_hash are required")
        if self.role not in {"formation", "outcome", "benchmark", "synthetic"}:
            raise ExperimentError(f"unsupported dataset role: {self.role}")

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class PreregistrationContract:
    """Immutable scientific decisions fixed before outcomes may be inspected."""

    signal_definition: str
    entry_rule: str
    horizon_sessions: int
    benchmark: str
    exclusions: tuple[str, ...]
    inference_plan: str
    entry_timing: str = "NEXT_SESSION_OPEN"
    immutable_fields: tuple[str, ...] = field(default=(
        "signal_definition",
        "entry_rule",
        "entry_timing",
        "horizon_sessions",
        "benchmark",
        "exclusions",
        "inference_plan",
    ))

    def __post_init__(self) -> None:
        if not self.signal_definition.strip():
            raise ExperimentError("signal_definition is required")
        if not self.entry_rule.strip():
            raise ExperimentError("entry_rule is required")
        if self.entry_timing != "NEXT_SESSION_OPEN":
            raise ExperimentError("entry_timing must be representable as NEXT_SESSION_OPEN")
        if not isinstance(self.horizon_sessions, int) or self.horizon_sessions <= 0:
            raise ExperimentError("horizon_sessions must be a positive integer")
        if not self.benchmark.strip():
            raise ExperimentError("benchmark is required")
        if not self.inference_plan.strip():
            raise ExperimentError("inference_plan is required")
        if tuple(self.immutable_fields) != (
            "signal_definition", "entry_rule", "entry_timing", "horizon_sessions",
            "benchmark", "exclusions", "inference_plan",
        ):
            raise ExperimentError("immutable_fields cannot be weakened or redefined")

    def scientific_dict(self) -> dict[str, Any]:
        return {
            "signal_definition": self.signal_definition,
            "entry_rule": self.entry_rule,
            "entry_timing": self.entry_timing,
            "horizon_sessions": self.horizon_sessions,
            "benchmark": self.benchmark,
            "exclusions": list(self.exclusions),
            "inference_plan": self.inference_plan,
            "immutable_fields": list(self.immutable_fields),
        }

    @property
    def protocol_hash(self) -> str:
        return _sha256(self.scientific_dict())


@dataclass(frozen=True)
class ExperimentRecord:
    experiment_id: str
    experiment_key: str
    version: int
    lane: str
    status: ExperimentStatus
    dataset_refs: tuple[DatasetRef, ...]
    protocol: PreregistrationContract
    protocol_hash: str

    def __post_init__(self) -> None:
        if self.version <= 0:
            raise ExperimentError("version must be positive")
        if not self.lane.strip():
            raise ExperimentError("lane is required")
        if self.protocol_hash != self.protocol.protocol_hash:
            raise ExperimentError("protocol_hash does not match protocol")

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "experiment_key": self.experiment_key,
            "version": self.version,
            "lane": self.lane,
            "status": self.status.value,
            "dataset_refs": [ref.to_dict() for ref in self.dataset_refs],
            "protocol": self.protocol.scientific_dict(),
            "protocol_hash": self.protocol_hash,
        }


@dataclass(frozen=True)
class BlueTeamGate:
    """Capability token proving Blue Team freeze of one exact protocol and dataset set."""

    experiment_id: str
    version: int
    protocol_hash: str
    dataset_set_hash: str
    authority: str = "BLUE_TEAM"

    def __post_init__(self) -> None:
        if self.authority != "BLUE_TEAM":
            raise ExperimentError("Blue Team gate authority is immutable")


class ExperimentRegistry:
    """In-memory registry with deterministic identities and monotonic versions.

    Persistence is intentionally transport-agnostic: ``snapshot()`` returns canonical JSON-ready
    records so the Control/Data Plane can choose the durable store without changing scientific
    behavior. The stable identity namespace is the pair ``(lane, experiment_key)``, allowing the
    same semantic key to exist independently in Form 4, crypto, futures, and future lanes.
    """

    def __init__(self) -> None:
        self._records: dict[tuple[str, int], ExperimentRecord] = {}
        self._keys: dict[tuple[str, str], str] = {}

    @staticmethod
    def stable_id(experiment_key: str, lane: str) -> str:
        key = experiment_key.strip()
        lane_key = lane.strip()
        if not key or not lane_key:
            raise ExperimentError("experiment_key and lane are required")
        identity = f"{lane_key}:{key}"
        return "EXP-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16].upper()

    def propose(self, experiment_key: str, lane: str,
                protocol: PreregistrationContract) -> ExperimentRecord:
        key = experiment_key.strip()
        lane_key = lane.strip()
        experiment_id = self.stable_id(key, lane_key)
        identity_key = (lane_key, key)
        known = self._keys.get(identity_key)
        if known is not None and known != experiment_id:
            raise ExperimentError("experiment identity collision")
        self._keys[identity_key] = experiment_id
        prior = [version for (eid, version) in self._records if eid == experiment_id]
        version = max(prior, default=0) + 1
        record = ExperimentRecord(
            experiment_id=experiment_id,
            experiment_key=key,
            version=version,
            lane=lane_key,
            status=ExperimentStatus.PROPOSED,
            dataset_refs=(),
            protocol=protocol,
            protocol_hash=protocol.protocol_hash,
        )
        self._records[(experiment_id, version)] = record
        return record

    def get(self, experiment_id: str, version: int) -> ExperimentRecord:
        try:
            return self._records[(experiment_id, version)]
        except KeyError as exc:
            raise ExperimentError("unknown experiment/version") from exc

    def attach_datasets(self, experiment_id: str, version: int,
                        dataset_refs: Iterable[DatasetRef]) -> ExperimentRecord:
        record = self.get(experiment_id, version)
        if record.status is not ExperimentStatus.PREREGISTERED:
            raise ExperimentError("formation dataset refs may attach only after PREREGISTERED and are immutable once DATA_READY")
        refs = tuple(dataset_refs)
        if not refs:
            raise ExperimentError("at least one dataset ref is required")
        if any(ref.role == "outcome" for ref in refs):
            raise ExperimentError("outcome datasets cannot be attached as formation data")
        updated = replace(record, dataset_refs=refs)
        self._records[(experiment_id, version)] = updated
        return updated

    def advance(self, experiment_id: str, version: int,
                target: ExperimentStatus) -> ExperimentRecord:
        record = self.get(experiment_id, version)
        if target not in _ALLOWED_TRANSITIONS[record.status]:
            raise ExperimentError(f"invalid transition {record.status.value} -> {target.value}")
        if target == ExperimentStatus.DATA_READY and not record.dataset_refs:
            raise ExperimentError("DATA_READY requires frozen formation dataset refs")
        updated = replace(record, status=target)
        self._records[(experiment_id, version)] = updated
        return updated

    def blue_freeze(self, experiment_id: str, version: int) -> tuple[ExperimentRecord, BlueTeamGate]:
        frozen = self.advance(experiment_id, version, ExperimentStatus.BLUE_FROZEN)
        dataset_set_hash = _sha256([ref.to_dict() for ref in frozen.dataset_refs])
        gate = BlueTeamGate(
            experiment_id=frozen.experiment_id,
            version=frozen.version,
            protocol_hash=frozen.protocol_hash,
            dataset_set_hash=dataset_set_hash,
        )
        return frozen, gate

    def snapshot(self) -> list[dict[str, Any]]:
        return [self._records[key].to_dict() for key in sorted(self._records)]
