from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from math import isfinite
from typing import Any, Dict, List, Mapping, Optional

from research.research_os.scientific_store import sha256_json
from .experiment_geometry import geometry_from_mapping
from .experiment_power import power_from_mapping
from .experiment_runner import DryRunExperimentRunner


READY = "READY_FOR_AUTHORIZED_ECONOMIC_TEST"
BLOCK = "BLOCK"

CHECK_ORDER = (
    "candidate_immutability",
    "producer_independence",
    "legacy_screening_evidence",
    "source_provenance",
    "pit",
    "clock",
    "universe_definition",
    "economic_expression_completeness",
    "implementability_declaration",
    "protocol_freeze",
    "reproducibility_binding",
    "experiment_infrastructure",
    "multiplicity_declaration",
    "trial_accounting",
    "cost_model_declaration",
    "capacity_declaration",
    "falsification",
    "decision_map",
    "no_outcome_access",
)

REASON_CODES = {
    "candidate_immutability": "CANDIDATE_IMMUTABILITY_FAILED",
    "producer_independence": "PRODUCER_VALIDATOR_NOT_INDEPENDENT",
    "legacy_screening_evidence": "LEGACY_SCREENING_EVIDENCE_MISSING",
    "source_provenance": "SOURCE_PROVENANCE_INCOMPLETE",
    "pit": "PIT_QUALIFICATION_FAILED",
    "clock": "CLOCK_DEFINITION_INVALID",
    "universe_definition": "UNIVERSE_DEFINITION_INCOMPLETE",
    "economic_expression_completeness": "ECONOMIC_EXPRESSION_INCOMPLETE",
    "implementability_declaration": "IMPLEMENTABILITY_DECLARATION_MISSING_OR_BLOCKED",
    "protocol_freeze": "PROTOCOL_NOT_FROZEN",
    "reproducibility_binding": "REPRODUCIBILITY_BINDING_FAILED",
    "experiment_infrastructure": "EXPERIMENT_INFRASTRUCTURE_NOT_QUALIFIED",
    "multiplicity_declaration": "MULTIPLICITY_DECLARATION_MISSING",
    "trial_accounting": "TRIAL_ACCOUNTING_INVALID",
    "cost_model_declaration": "COST_MODEL_DECLARATION_MISSING",
    "capacity_declaration": "CAPACITY_DECLARATION_MISSING",
    "falsification": "FALSIFICATION_SCOPE_MISSING",
    "decision_map": "DECISION_MAP_MISSING",
    "no_outcome_access": "OUTCOME_ACCESS_FORBIDDEN",
}

_AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)


def _present(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in (
            "UNKNOWN", "UNSPECIFIED", "UNAVAILABLE", "NOT_ESTIMATED")
    if isinstance(value, float):
        return isfinite(value)
    return bool(value)


def _is_hash(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def _iso(value: Any) -> Optional[datetime]:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _source_hashes(source_bundle: Mapping[str, Any]) -> List[str]:
    raw = source_bundle.get("snapshot_hashes", [])
    return sorted(raw) if isinstance(raw, list) else []


def _protocol_candidate_hash(protocol: Mapping[str, Any]) -> Optional[str]:
    explicit = protocol.get("candidate_hash")
    if _is_hash(explicit):
        return explicit
    payload = protocol.get("protocol_payload")
    if isinstance(payload, dict) and isinstance(payload.get("candidate"), dict):
        return sha256_json(payload["candidate"])
    return None


def _protocol_hash_valid(protocol: Mapping[str, Any]) -> bool:
    protocol_hash = protocol.get("protocol_hash")
    if not _is_hash(protocol_hash):
        return False
    payload = protocol.get("protocol_payload")
    if isinstance(payload, dict):
        return sha256_json(payload) == protocol_hash
    return protocol.get("frozen") is True


def _trial_accounting_valid(record: Mapping[str, Any]) -> bool:
    from .experiment_registry import ExperimentRegistryError, validate_trial_accounting
    try:
        validate_trial_accounting(record)
    except ExperimentRegistryError:
        return False
    return True


def _entry_hash_valid(record: Any) -> bool:
    if not isinstance(record, Mapping) or not _is_hash(record.get("entry_hash")):
        return False
    payload = {key: value for key, value in record.items() if key != "entry_hash"}
    return sha256_json(payload) == record.get("entry_hash")


def _factory_declarations_match_frozen_protocol(
    *, frozen_protocol: Mapping[str, Any], geometry: Mapping[str, Any],
    power: Mapping[str, Any], protocol_hash: str,
) -> bool:
    try:
        expected_geometry = geometry_from_mapping(
            protocol_hash, frozen_protocol.get("geometry_declaration")
        )
        expected_power = power_from_mapping(
            protocol_hash, frozen_protocol.get("power_declaration")
        )
    except (ValueError, TypeError):
        return False
    geometry_payload = {**expected_geometry.to_dict(), "declaration_hash": expected_geometry.declaration_hash}
    power_payload = {**expected_power.to_dict(), "declaration_hash": expected_power.declaration_hash}
    return dict(geometry) == geometry_payload and dict(power) == power_payload


def _experiment_infrastructure_valid(
    infrastructure: Mapping[str, Any], *, candidate_hash: str,
    protocol_hash: Any, reproducibility_payload: Any, multiplicity_method: Any,
    source_hashes: List[str], pit_rows: List[Mapping[str, Any]],
    trial_accounting: Mapping[str, Any],
) -> bool:
    if infrastructure.get("status") != "PASS" or infrastructure.get("blockers") not in ([], ()):
        return False
    supplied_hash = infrastructure.get("infrastructure_hash")
    if not _is_hash(supplied_hash):
        return False
    payload = {key: value for key, value in infrastructure.items() if key != "infrastructure_hash"}
    if sha256_json(payload) != supplied_hash:
        return False
    if infrastructure.get("outcome_accessed") is not False or infrastructure.get("economic_result") != "NOT_OBSERVED":
        return False
    if any(infrastructure.get(key) is not False for key in _AUTHORITY_KEYS):
        return False

    registry = infrastructure.get("registry")
    frozen_registry = infrastructure.get("frozen_registry")
    frozen_protocol = infrastructure.get("frozen_protocol")
    execution_plan = infrastructure.get("execution_plan")
    replay = infrastructure.get("replay")
    geometry = infrastructure.get("geometry")
    power = infrastructure.get("power")
    if not all(isinstance(item, Mapping) for item in (
        registry, frozen_registry, frozen_protocol, execution_plan, replay, geometry, power
    )):
        return False
    if not _entry_hash_valid(registry) or not _entry_hash_valid(frozen_registry):
        return False
    if registry.get("lifecycle") != "REPLAY_VERIFIED" or frozen_registry.get("lifecycle") != "FROZEN":
        return False
    if registry.get("candidate_hash") != candidate_hash or frozen_registry.get("candidate_hash") != candidate_hash:
        return False
    if registry.get("protocol_hash") != protocol_hash or frozen_registry.get("protocol_hash") != protocol_hash:
        return False
    if registry.get("registry_id") != frozen_registry.get("registry_id"):
        return False

    frozen_hash = sha256_json(frozen_protocol)
    if registry.get("frozen_protocol_hash") != frozen_hash or frozen_registry.get("frozen_protocol_hash") != frozen_hash:
        return False
    if frozen_protocol.get("candidate_hash") != candidate_hash or frozen_protocol.get("protocol_hash") != protocol_hash:
        return False
    if frozen_protocol.get("multiplicity_method") != multiplicity_method:
        return False
    if sorted(frozen_protocol.get("source_snapshot_hashes") or []) != sorted(source_hashes):
        return False
    if frozen_protocol.get("source_pit_metadata") != pit_rows:
        return False
    if not _factory_declarations_match_frozen_protocol(
        frozen_protocol=frozen_protocol, geometry=geometry, power=power,
        protocol_hash=protocol_hash,
    ):
        return False
    if registry.get("geometry_hash") != geometry.get("declaration_hash"):
        return False
    if registry.get("power_hash") != power.get("declaration_hash"):
        return False
    if registry.get("trial_accounting_hash") != sha256_json(dict(trial_accounting)):
        return False

    plan_frozen = execution_plan.get("frozen_protocol")
    plan_bindings = execution_plan.get("binding_hashes")
    if plan_frozen != frozen_protocol or not isinstance(plan_bindings, Mapping):
        return False
    if dict(registry.get("binding_hashes") or {}) != dict(plan_bindings):
        return False
    if dict(frozen_registry.get("binding_hashes") or {}) != dict(plan_bindings):
        return False
    expected_reproducibility_hash = sha256_json({
        "source": plan_bindings.get("source"),
        "pit": plan_bindings.get("pit"),
        "code_environment": plan_bindings.get("code_environment"),
    })
    if registry.get("reproducibility_hash") != expected_reproducibility_hash:
        return False
    if frozen_registry.get("reproducibility_hash") != expected_reproducibility_hash:
        return False

    try:
        replayed = DryRunExperimentRunner().replay(deepcopy(dict(execution_plan)))
    except (ValueError, PermissionError, KeyError, TypeError):
        return False
    if replayed != dict(replay):
        return False
    receipt = execution_plan.get("pre_outcome_receipt")
    if not isinstance(receipt, Mapping):
        return False
    if registry.get("execution_plan_hash") != execution_plan.get("execution_plan_hash"):
        return False
    if registry.get("receipt_hash") != receipt.get("receipt_hash"):
        return False
    if registry.get("replay_hash") != sha256_json(dict(replay)):
        return False

    if not isinstance(reproducibility_payload, Mapping):
        return False
    return (
        reproducibility_payload.get("experiment_registry_id") == registry.get("registry_id")
        and reproducibility_payload.get("experiment_registry_hash") == registry.get("entry_hash")
        and reproducibility_payload.get("experiment_infrastructure_hash") == supplied_hash
    )


def validate_economic_test_readiness(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Decide only whether a frozen candidate is ready for a later authorized test."""
    candidate = bundle.get("candidate") if isinstance(bundle.get("candidate"), dict) else {}
    candidate_before = deepcopy(candidate)
    actual_candidate_hash = sha256_json(candidate)

    protocol = bundle.get("protocol") if isinstance(bundle.get("protocol"), dict) else {}
    source_bundle = bundle.get("sources") if isinstance(bundle.get("sources"), dict) else {}
    clock = bundle.get("clock") if isinstance(bundle.get("clock"), dict) else {}
    universe = bundle.get("universe") if isinstance(bundle.get("universe"), dict) else {}
    expression = bundle.get("economic_expression") if isinstance(bundle.get("economic_expression"), dict) else {}
    implementability = bundle.get("implementability") if isinstance(bundle.get("implementability"), dict) else {}
    reproducibility = bundle.get("reproducibility") if isinstance(bundle.get("reproducibility"), dict) else {}
    infrastructure = bundle.get("experiment_infrastructure") if isinstance(bundle.get("experiment_infrastructure"), dict) else {}
    multiplicity = bundle.get("multiplicity") if isinstance(bundle.get("multiplicity"), dict) else {}
    trial_accounting = bundle.get("trial_accounting") if isinstance(bundle.get("trial_accounting"), dict) else {}
    cost_model = bundle.get("cost_model") if isinstance(bundle.get("cost_model"), dict) else {}
    capacity = bundle.get("capacity") if isinstance(bundle.get("capacity"), dict) else {}
    legacy = bundle.get("legacy_screening") if isinstance(bundle.get("legacy_screening"), dict) else {}
    outcome = bundle.get("outcome_access") if isinstance(bundle.get("outcome_access"), dict) else {}

    producer_id = bundle.get("producer_id")
    validator_id = bundle.get("validator_id") or "independent-validator.v3"
    declared_candidate_hash = bundle.get("candidate_hash")

    pit_rows = source_bundle.get("pit_metadata", [])
    if not isinstance(pit_rows, list):
        pit_rows = []
    data_cutoff = _iso(clock.get("data_cutoff"))
    source_times = [_iso(row.get("available_at")) for row in pit_rows if isinstance(row, dict)]

    expression_spec = expression.get("spec") if isinstance(expression.get("spec"), dict) else {}
    expression_required = (
        "instrument_rule",
        "side_rule",
        "entry_rule",
        "exit_rule",
        "horizon_rule",
        "sizing_rule",
    )

    protocol_candidate_hash = _protocol_candidate_hash(protocol)
    source_hashes = _source_hashes(source_bundle)
    reproducibility_payload = reproducibility.get("binding_payload")
    binding_hash_valid = (
        isinstance(reproducibility_payload, dict)
        and _is_hash(reproducibility.get("binding_hash"))
        and sha256_json(reproducibility_payload) == reproducibility.get("binding_hash")
    )

    checks: Dict[str, Dict[str, Any]] = {}

    def add(name: str, passed: bool, detail: str) -> None:
        checks[name] = {
            "status": "PASS" if passed else "FAIL",
            "reason_code": None if passed else REASON_CODES[name],
            "detail": detail,
        }

    add(
        "candidate_immutability",
        _is_hash(declared_candidate_hash)
        and declared_candidate_hash == actual_candidate_hash
        and protocol_candidate_hash == actual_candidate_hash,
        "Declared, computed, and frozen-protocol candidate hashes must match.",
    )
    add(
        "producer_independence",
        _present(producer_id) and _present(validator_id) and producer_id != validator_id,
        "Producer and validator identities must both be explicit and different.",
    )
    add(
        "legacy_screening_evidence",
        legacy.get("status") == "PASS" and _is_hash(legacy.get("evidence_hash")),
        "Legacy screening must have a PASS receipt and immutable evidence hash.",
    )
    add(
        "source_provenance",
        _is_hash(source_bundle.get("manifest_hash"))
        and bool(source_hashes)
        and all(_is_hash(item) for item in source_hashes)
        and bool(pit_rows),
        "Source manifest, snapshot hashes, and PIT metadata must be bound.",
    )
    add(
        "pit",
        bool(pit_rows)
        and all(
            isinstance(row, dict)
            and row.get("point_in_time_qualified") is True
            and _present(row.get("source_id"))
            and _iso(row.get("available_at")) is not None
            for row in pit_rows
        )
        and data_cutoff is not None
        and all(ts is not None and ts <= data_cutoff for ts in source_times),
        "Every source must be PIT-qualified and available no later than the declared data cutoff.",
    )
    decision_time = _iso(clock.get("decision_time"))
    freeze_time = _iso(clock.get("freeze_time"))
    add(
        "clock",
        _present(clock.get("timezone"))
        and data_cutoff is not None
        and decision_time is not None
        and freeze_time is not None
        and data_cutoff <= freeze_time
        and decision_time <= freeze_time,
        "Clock requires timezone-aware decision, data-cutoff, and freeze timestamps with coherent ordering.",
    )
    add(
        "universe_definition",
        universe.get("status") == "DEFINED"
        and _present(universe.get("universe_id"))
        and _is_hash(universe.get("definition_hash"))
        and _present(universe.get("membership_policy")),
        "Universe id, deterministic definition hash, and membership policy are required.",
    )
    add(
        "economic_expression_completeness",
        expression.get("status") == "COMPLETE"
        and all(_present(expression_spec.get(field)) for field in expression_required)
        and _is_hash(expression.get("expression_hash"))
        and sha256_json(expression_spec) == expression.get("expression_hash"),
        "Economic expression must fully specify instrument, side, entry, exit, horizon, and sizing rules.",
    )
    add(
        "implementability_declaration",
        implementability.get("status") == "PASS"
        and _is_hash(implementability.get("declaration_hash")),
        "Implementability must be explicitly PASS with a frozen declaration hash.",
    )
    add(
        "protocol_freeze",
        protocol.get("status") == "FROZEN_READY_NO_OUTCOME"
        and _protocol_hash_valid(protocol)
        and protocol_candidate_hash == actual_candidate_hash
        and protocol.get("outcome_opened") is False,
        "Protocol must be frozen, candidate-bound, hash-valid, and outcome-closed.",
    )
    binding_payload_matches = (
        isinstance(reproducibility_payload, dict)
        and reproducibility_payload.get("candidate_hash") == actual_candidate_hash
        and reproducibility_payload.get("protocol_hash") == protocol.get("protocol_hash")
        and sorted(reproducibility_payload.get("source_snapshot_hashes", [])) == source_hashes
    )
    add(
        "reproducibility_binding",
        reproducibility.get("status") in {"BOUND", "PASS"}
        and binding_hash_valid
        and binding_payload_matches,
        "Reproducibility binding must hash the same candidate, protocol, and source snapshots.",
    )
    add(
        "experiment_infrastructure",
        _experiment_infrastructure_valid(
            infrastructure,
            candidate_hash=actual_candidate_hash,
            protocol_hash=protocol.get("protocol_hash"),
            reproducibility_payload=reproducibility_payload,
            multiplicity_method=multiplicity.get("method"),
            source_hashes=source_hashes,
            pit_rows=pit_rows,
            trial_accounting=trial_accounting,
        ),
        "Registry, canonical runner plan/receipt/replay, geometry, power and trial accounting must form one exact pre-outcome attestation.",
    )
    add(
        "multiplicity_declaration",
        multiplicity.get("declared") is True and _present(multiplicity.get("method")),
        "Multiplicity handling must be declared before outcome access.",
    )
    add(
        "trial_accounting",
        _trial_accounting_valid(trial_accounting),
        "Observed attempts and effective-trials accounting must be explicit and internally coherent.",
    )
    add(
        "cost_model_declaration",
        cost_model.get("status") == "DECLARED"
        and isinstance(cost_model.get("model_id"), str)
        and _present(cost_model.get("model_id"))
        and _is_hash(cost_model.get("declaration_hash")),
        "A frozen cost-model declaration is required; feasibility alone is insufficient.",
    )
    add(
        "capacity_declaration",
        capacity.get("status") == "DECLARED"
        and isinstance(capacity.get("model_id"), str)
        and _present(capacity.get("model_id"))
        and _is_hash(capacity.get("declaration_hash")),
        "A frozen capacity declaration is required before any economic test can be authorized.",
    )
    add(
        "falsification",
        bool(candidate.get("falsification_scope")),
        "Candidate must state falsifying evidence before outcomes are opened.",
    )
    add(
        "decision_map",
        bool(candidate.get("decision_map")),
        "Candidate must carry a preregistered decision map.",
    )
    add(
        "no_outcome_access",
        protocol.get("outcome_opened") is False
        and reproducibility.get("outcome_accessed") is False
        and outcome.get("opened") is False
        and outcome.get("consumed") is False
        and outcome.get("result") == "NOT_OBSERVED",
        "All producer, validator, and runner surfaces must remain outcome-closed.",
    )

    block_reasons = [
        {
            "code": checks[name]["reason_code"],
            "check": name,
            "detail": checks[name]["detail"],
        }
        for name in CHECK_ORDER
        if checks[name]["status"] != "PASS"
    ]
    mutated = candidate != candidate_before
    if mutated and checks["candidate_immutability"]["status"] == "PASS":
        checks["candidate_immutability"] = {
            "status": "FAIL",
            "reason_code": REASON_CODES["candidate_immutability"],
            "detail": "Validator mutated candidate state while evaluating readiness.",
        }
        block_reasons.insert(
            0,
            {
                "code": REASON_CODES["candidate_immutability"],
                "check": "candidate_immutability",
                "detail": checks["candidate_immutability"]["detail"],
            },
        )

    ready = not block_reasons
    return {
        "hypothesis_id": candidate.get("hypothesis_id"),
        "generation_id": candidate.get("generation_id"),
        "validator": validator_id,
        "producer_id": producer_id,
        "status": READY if ready else BLOCK,
        "ready_for_authorized_economic_test": ready,
        "checks": checks,
        "block_reasons": block_reasons,
        "candidate_hash": actual_candidate_hash,
        "protocol_hash": protocol.get("protocol_hash"),
        "economic_test_authorized": False,
        "economic_claim_authorized": False,
        "outcome_access_authorized": False,
        "candidate_mutated": mutated,
        "signal_repair_attempted": False,
        "parameter_optimization_attempted": False,
        "claim_ceiling": READY if ready else "BLOCKED_PRE_OUTCOME",
    }