"""Canonical immutable experiment-registry binding for the Research Core.

This adapts the historical in-memory Factory registry into a pure identity/binding
contract. It deliberately persists nothing and therefore cannot become a second
scientific truth store. The canonical envelope/frozen protocol remains authority.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from math import isfinite
from typing import Any, Mapping
import hashlib
import json
import re

from .experiment_geometry import GeometryDeclaration
from .experiment_outcome_firewall import assert_pre_outcome_payload
from .experiment_power import PowerDeclaration

UNKNOWN = "UNKNOWN"
NOT_OBSERVED = "NOT_OBSERVED"
_BINDING_KEYS = ("generation", "candidate", "protocol", "source", "pit", "code_environment")
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class ExperimentRegistryError(ValueError):
    pass


class ExperimentLifecycle(str, Enum):
    FROZEN = "FROZEN"
    PREPARED = "PREPARED"
    RECEIPT_BOUND = "RECEIPT_BOUND"
    REPLAY_VERIFIED = "REPLAY_VERIFIED"


_ALLOWED = {
    ExperimentLifecycle.FROZEN: {ExperimentLifecycle.PREPARED},
    ExperimentLifecycle.PREPARED: {ExperimentLifecycle.RECEIPT_BOUND},
    ExperimentLifecycle.RECEIPT_BOUND: {ExperimentLifecycle.REPLAY_VERIFIED},
    ExperimentLifecycle.REPLAY_VERIFIED: set(),
}


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExperimentRegistryError(f"{name} must be a non-empty string")
    return value


def _require_hash(name: str, value: Any) -> str:
    if not isinstance(value, str) or not _HASH_RE.fullmatch(value):
        raise ExperimentRegistryError(f"{name} must be a lowercase sha256 hex digest")
    return value


def _validate_trial_record(trial: Mapping[str, Any], *, hypothesis_id: str, generation_id: str) -> None:
    if not isinstance(trial, Mapping):
        raise ExperimentRegistryError("trial_accounting must be a mapping")
    if trial.get("hypothesis_id") not in (None, hypothesis_id):
        raise ExperimentRegistryError("TRIAL_HYPOTHESIS_BINDING_MISMATCH")
    if trial.get("generation_id") not in (None, generation_id):
        raise ExperimentRegistryError("TRIAL_GENERATION_BINDING_MISMATCH")
    attempts = trial.get("observed_attempt_count")
    if isinstance(attempts, bool) or not isinstance(attempts, int) or attempts < 0:
        raise ExperimentRegistryError("TRIAL_OBSERVED_ATTEMPT_COUNT_INVALID")
    status = trial.get("effective_trials_status", UNKNOWN)
    estimate = trial.get("estimated_effective_trials")
    if status == UNKNOWN:
        if estimate is not None:
            raise ExperimentRegistryError("UNKNOWN_EFFECTIVE_TRIALS_MUST_NOT_HAVE_ESTIMATE")
    elif status in {"KNOWN", "ESTIMATED", "PARTIALLY_BOUNDED"}:
        if isinstance(estimate, bool) or type(estimate) not in (int, float) or not isfinite(float(estimate)) or float(estimate) < 0:
            raise ExperimentRegistryError("EFFECTIVE_TRIALS_ESTIMATE_INVALID")
    else:
        raise ExperimentRegistryError("EFFECTIVE_TRIALS_STATUS_INVALID")


@dataclass(frozen=True)
class ExperimentRegistryEntry:
    registry_id: str
    experiment_id: str
    hypothesis_id: str
    generation_id: str
    candidate_hash: str
    protocol_hash: str
    frozen_protocol_hash: str
    reproducibility_hash: str
    binding_hashes: Mapping[str, str]
    trial_accounting_hash: str
    geometry_hash: str
    power_hash: str
    lifecycle: ExperimentLifecycle = ExperimentLifecycle.FROZEN
    execution_plan_hash: str | None = None
    receipt_hash: str | None = None
    replay_hash: str | None = None
    outcome_accessed: bool = False
    economic_result: str = NOT_OBSERVED
    economic_experiment_authorized: bool = False
    prospective_observation_authorized: bool = False
    real_capital_authorized: bool = False
    live_trading_authorized: bool = False
    entry_hash: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle, ExperimentLifecycle):
            try:
                object.__setattr__(self, "lifecycle", ExperimentLifecycle(self.lifecycle))
            except (TypeError, ValueError) as exc:
                raise ExperimentRegistryError("invalid lifecycle") from exc
        _required_text("registry_id", self.registry_id)
        _required_text("experiment_id", self.experiment_id)
        _required_text("hypothesis_id", self.hypothesis_id)
        _required_text("generation_id", self.generation_id)
        for name in (
            "candidate_hash", "protocol_hash", "frozen_protocol_hash", "reproducibility_hash",
            "trial_accounting_hash", "geometry_hash", "power_hash",
        ):
            _require_hash(name, getattr(self, name))
        if set(self.binding_hashes) != set(_BINDING_KEYS):
            raise ExperimentRegistryError("binding_hashes must contain the exact canonical binding set")
        for name, value in self.binding_hashes.items():
            _require_hash(f"binding_hashes.{name}", value)
        if self.outcome_accessed is not False or self.economic_result != NOT_OBSERVED:
            raise ExperimentRegistryError("registry entries are pre-outcome only")
        for name in (
            "economic_experiment_authorized", "prospective_observation_authorized",
            "real_capital_authorized", "live_trading_authorized",
        ):
            if getattr(self, name) is not False:
                raise ExperimentRegistryError(f"{name} must remain false")
        for name in ("execution_plan_hash", "receipt_hash", "replay_hash"):
            value = getattr(self, name)
            if value is not None:
                _require_hash(name, value)
        expected = canonical_hash(self.identity_payload())
        if self.entry_hash and self.entry_hash != expected:
            raise ExperimentRegistryError("ENTRY_HASH_MISMATCH")
        if not self.entry_hash:
            object.__setattr__(self, "entry_hash", expected)

    def identity_payload(self) -> dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "experiment_id": self.experiment_id,
            "hypothesis_id": self.hypothesis_id,
            "generation_id": self.generation_id,
            "candidate_hash": self.candidate_hash,
            "protocol_hash": self.protocol_hash,
            "frozen_protocol_hash": self.frozen_protocol_hash,
            "reproducibility_hash": self.reproducibility_hash,
            "binding_hashes": dict(self.binding_hashes),
            "trial_accounting_hash": self.trial_accounting_hash,
            "geometry_hash": self.geometry_hash,
            "power_hash": self.power_hash,
            "lifecycle": self.lifecycle.value,
            "execution_plan_hash": self.execution_plan_hash,
            "receipt_hash": self.receipt_hash,
            "replay_hash": self.replay_hash,
            "outcome_accessed": False,
            "economic_result": NOT_OBSERVED,
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "entry_hash": self.entry_hash}


def create_registry_entry(
    *, envelope: Mapping[str, Any], frozen_protocol: Mapping[str, Any],
    binding_hashes: Mapping[str, str], trial_accounting: Mapping[str, Any],
    geometry: GeometryDeclaration, power: PowerDeclaration,
) -> ExperimentRegistryEntry:
    assert_pre_outcome_payload(envelope)
    assert_pre_outcome_payload(frozen_protocol)
    assert_pre_outcome_payload(trial_accounting)
    if envelope.get("status") != "FROZEN_READY_NO_OUTCOME":
        raise ExperimentRegistryError("ENVELOPE_NOT_FROZEN")
    experiment_id = _required_text("experiment_id", envelope.get("experiment_id"))
    protocol_hash = _require_hash("protocol_hash", envelope.get("protocol_hash"))
    payload = envelope.get("protocol_payload")
    if not isinstance(payload, Mapping):
        raise ExperimentRegistryError("PROTOCOL_PAYLOAD_MISSING")
    candidate = payload.get("candidate")
    if not isinstance(candidate, Mapping):
        raise ExperimentRegistryError("CANDIDATE_MISSING")
    hypothesis_id = _required_text("hypothesis_id", payload.get("hypothesis_id"))
    generation_id = _required_text("generation_id", payload.get("generation_id"))
    if candidate.get("hypothesis_id") != hypothesis_id:
        raise ExperimentRegistryError("CANDIDATE_HYPOTHESIS_BINDING_MISMATCH")
    if candidate.get("generation_id") != generation_id:
        raise ExperimentRegistryError("CANDIDATE_GENERATION_BINDING_MISMATCH")
    candidate_hash = canonical_hash(candidate)
    if frozen_protocol.get("candidate_hash") != candidate_hash:
        raise ExperimentRegistryError("FROZEN_CANDIDATE_BINDING_MISMATCH")
    if frozen_protocol.get("protocol_hash") != protocol_hash:
        raise ExperimentRegistryError("FROZEN_PROTOCOL_BINDING_MISMATCH")
    if frozen_protocol.get("hypothesis_id") != hypothesis_id or frozen_protocol.get("generation_id") != generation_id:
        raise ExperimentRegistryError("FROZEN_GENERATION_BINDING_MISMATCH")
    if set(binding_hashes) != set(_BINDING_KEYS):
        raise ExperimentRegistryError("CANONICAL_BINDINGS_INCOMPLETE")
    for key in _BINDING_KEYS:
        _require_hash(f"binding_hashes.{key}", binding_hashes[key])
    _validate_trial_record(trial_accounting, hypothesis_id=hypothesis_id, generation_id=generation_id)
    if geometry.protocol_hash != protocol_hash:
        raise ExperimentRegistryError("GEOMETRY_PROTOCOL_BINDING_MISMATCH")
    if power.protocol_hash != protocol_hash:
        raise ExperimentRegistryError("POWER_PROTOCOL_BINDING_MISMATCH")
    frozen_protocol_hash = canonical_hash(frozen_protocol)
    reproducibility_hash = canonical_hash({
        "source": binding_hashes["source"], "pit": binding_hashes["pit"],
        "code_environment": binding_hashes["code_environment"],
    })
    trial_hash = canonical_hash(dict(trial_accounting))
    identity = {
        "experiment_id": experiment_id, "hypothesis_id": hypothesis_id, "generation_id": generation_id,
        "candidate_hash": candidate_hash, "protocol_hash": protocol_hash,
        "frozen_protocol_hash": frozen_protocol_hash, "reproducibility_hash": reproducibility_hash,
        "binding_hashes": dict(binding_hashes), "trial_accounting_hash": trial_hash,
        "geometry_hash": geometry.declaration_hash, "power_hash": power.declaration_hash,
    }
    registry_id = "EXR-" + canonical_hash(identity)[:24].upper()
    return ExperimentRegistryEntry(
        registry_id=registry_id, experiment_id=experiment_id, hypothesis_id=hypothesis_id,
        generation_id=generation_id, candidate_hash=candidate_hash, protocol_hash=protocol_hash,
        frozen_protocol_hash=frozen_protocol_hash, reproducibility_hash=reproducibility_hash,
        binding_hashes=dict(binding_hashes), trial_accounting_hash=trial_hash,
        geometry_hash=geometry.declaration_hash, power_hash=power.declaration_hash,
    )


def _advance(entry: ExperimentRegistryEntry, target: ExperimentLifecycle, **changes: Any) -> ExperimentRegistryEntry:
    if target not in _ALLOWED[entry.lifecycle]:
        raise ExperimentRegistryError(f"INVALID_EXPERIMENT_TRANSITION:{entry.lifecycle.value}->{target.value}")
    return replace(entry, lifecycle=target, entry_hash="", **changes)


def bind_execution_plan(entry: ExperimentRegistryEntry, plan: Mapping[str, Any]) -> ExperimentRegistryEntry:
    assert_pre_outcome_payload(plan)
    if entry.lifecycle is not ExperimentLifecycle.FROZEN:
        raise ExperimentRegistryError("EXECUTION_PLAN_BIND_REQUIRES_FROZEN")
    if plan.get("status") != "READY_FOR_REPRODUCIBLE_DRY_RUN":
        raise ExperimentRegistryError("EXECUTION_PLAN_NOT_READY")
    if plan.get("experiment_id") != entry.experiment_id:
        raise ExperimentRegistryError("FOREIGN_EXPERIMENT_PLAN")
    body = plan.get("plan")
    if not isinstance(body, Mapping):
        raise ExperimentRegistryError("EXECUTION_PLAN_BODY_MISSING")
    plan_hash = _require_hash("execution_plan_hash", plan.get("execution_plan_hash"))
    if canonical_hash(body) != plan_hash:
        raise ExperimentRegistryError("EXECUTION_PLAN_HASH_MISMATCH")
    if body.get("frozen_protocol_hash") != entry.frozen_protocol_hash:
        raise ExperimentRegistryError("EXECUTION_PLAN_FROZEN_PROTOCOL_MISMATCH")
    if dict(body.get("binding_hashes") or {}) != dict(entry.binding_hashes):
        raise ExperimentRegistryError("EXECUTION_PLAN_BINDINGS_MISMATCH")
    return _advance(entry, ExperimentLifecycle.PREPARED, execution_plan_hash=plan_hash)


def bind_receipt(entry: ExperimentRegistryEntry, receipt: Mapping[str, Any]) -> ExperimentRegistryEntry:
    assert_pre_outcome_payload(receipt)
    if entry.lifecycle is not ExperimentLifecycle.PREPARED:
        raise ExperimentRegistryError("RECEIPT_BIND_REQUIRES_PREPARED")
    if receipt.get("experiment_id") != entry.experiment_id:
        raise ExperimentRegistryError("FOREIGN_EXPERIMENT_RECEIPT")
    if receipt.get("execution_plan_hash") != entry.execution_plan_hash:
        raise ExperimentRegistryError("RECEIPT_PLAN_BINDING_MISMATCH")
    if receipt.get("frozen_protocol_hash") != entry.frozen_protocol_hash:
        raise ExperimentRegistryError("RECEIPT_PROTOCOL_BINDING_MISMATCH")
    if dict(receipt.get("binding_hashes") or {}) != dict(entry.binding_hashes):
        raise ExperimentRegistryError("RECEIPT_BINDINGS_MISMATCH")
    supplied = _require_hash("receipt_hash", receipt.get("receipt_hash"))
    payload = {key: value for key, value in receipt.items() if key != "receipt_hash"}
    if canonical_hash(payload) != supplied:
        raise ExperimentRegistryError("RECEIPT_HASH_MISMATCH")
    return _advance(entry, ExperimentLifecycle.RECEIPT_BOUND, receipt_hash=supplied)


def bind_replay(entry: ExperimentRegistryEntry, replay: Mapping[str, Any]) -> ExperimentRegistryEntry:
    assert_pre_outcome_payload(replay)
    if entry.lifecycle is not ExperimentLifecycle.RECEIPT_BOUND:
        raise ExperimentRegistryError("REPLAY_BIND_REQUIRES_RECEIPT")
    if replay.get("experiment_id") != entry.experiment_id:
        raise ExperimentRegistryError("FOREIGN_EXPERIMENT_REPLAY")
    if replay.get("execution_plan_hash") != entry.execution_plan_hash:
        raise ExperimentRegistryError("REPLAY_PLAN_BINDING_MISMATCH")
    if replay.get("status") not in {"REPLAY_MATCH", "FROZEN_BINDINGS_MATCH"}:
        raise ExperimentRegistryError("REPLAY_NOT_VERIFIED")
    replay_hash = canonical_hash(dict(replay))
    return _advance(entry, ExperimentLifecycle.REPLAY_VERIFIED, replay_hash=replay_hash)


def assert_registry_matches(entry: ExperimentRegistryEntry, *, experiment_id: str, candidate_hash: str, protocol_hash: str) -> None:
    if entry.experiment_id != experiment_id:
        raise ExperimentRegistryError("FOREIGN_REGISTRY_EXPERIMENT")
    if entry.candidate_hash != candidate_hash:
        raise ExperimentRegistryError("REGISTRY_CANDIDATE_IDENTITY_MISMATCH")
    if entry.protocol_hash != protocol_hash:
        raise ExperimentRegistryError("REGISTRY_PROTOCOL_IDENTITY_MISMATCH")
