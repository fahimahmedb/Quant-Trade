from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from math import isfinite
from typing import Any, Dict, List, Mapping, Optional

from research.research_os.scientific_store import sha256_json
from .experiment_geometry import geometry_from_mapping
from .experiment_outcome_firewall import OutcomeFirewallError, assert_pre_outcome_payload
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
    "frozen_input_binding",
    "reproducibility_binding",
    "experiment_infrastructure",
    "multiplicity_declaration",
    "trial_accounting",
    "cost_model_declaration",
    "capacity_declaration",
    "falsification",
    "decision_map",
    "outcome_firewall",
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
    "frozen_input_binding": "FROZEN_INPUT_BINDING_FAILED",
    "reproducibility_binding": "REPRODUCIBILITY_BINDING_FAILED",
    "experiment_infrastructure": "EXPERIMENT_INFRASTRUCTURE_NOT_QUALIFIED",
    "multiplicity_declaration": "MULTIPLICITY_DECLARATION_MISSING",
    "trial_accounting": "TRIAL_ACCOUNTING_INVALID",
    "cost_model_declaration": "COST_MODEL_DECLARATION_MISSING",
    "capacity_declaration": "CAPACITY_DECLARATION_MISSING",
    "falsification": "FALSIFICATION_SCOPE_MISSING",
    "decision_map": "DECISION_MAP_MISSING",
    "outcome_firewall": "OUTCOME_FIREWALL_REJECTED",
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


def _identifier(value: Any) -> bool:
    return (isinstance(value, str) and _present(value)
            and value.strip().upper() not in {"UNRESOLVED", "NOT_APPLICABLE", "NOT_YET_MEASURABLE",
                                               "NONE", "NULL", "N/A"})


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


def _frozen_input_binding(bundle: Mapping[str, Any], protocol: Mapping[str, Any]) -> bool:
    """Reconstruct readiness inputs from the frozen body, never mutable projections."""
    from .source_qualification import qualify_source_route
    try:
        payload = protocol["protocol_payload"]
        provenance = payload["dataset_provenance"]
        declared, sources = provenance["protocol"], provenance["sources"]
        implementation = payload["implementability_declaration"]
        if not isinstance(sources, list) or not sources or not isinstance(implementation, dict):
            return False
        pit = []
        for source in sources:
            route = source["route"]
            qualification = qualify_source_route(route, freeze_time=declared["clock"]["freeze_time"])
            if qualification["status"] != "PASS":
                return False
            pit.append({"source_id": route["route_id"], "snapshot_hash": source["snapshot_hash"],
                        "point_in_time_qualified": qualification["point_in_time_qualified"],
                        "available_at": source["available_at"], "route_available_at": route["availability_start"],
                        "revision_policy": route["revision_policy"]})
        expression = declared["economic_expression"]
        spec = {"instrument_rule": expression["instrument"], "side_rule": expression["direction_exposure_semantics"],
                "entry_rule": expression["entry_clock"], "exit_rule": expression["exit_clock"],
                "horizon_rule": expression["horizon"], "sizing_rule": expression["position_expression"]}
        effective = declared["effective_trials"]
        expected = {
            "clock": declared["clock"], "universe": declared["universe"],
            "economic_expression": {"status": "COMPLETE", "spec": spec, "expression_hash": sha256_json(spec)},
            "implementability": {"status": implementation["status"], "declaration_hash": sha256_json(implementation)},
            "multiplicity": {"declared": bool(declared["multiplicity_family"]), "method": declared["multiplicity_method"]},
            "trial_accounting": {"observed_attempt_count": declared["observed_attempt_count"],
                "effective_trials_status": "UNKNOWN" if effective == "UNKNOWN" else "KNOWN",
                "estimated_effective_trials": None if effective == "UNKNOWN" else effective},
        }
        for name, key in (("cost_model", "cost_assumptions"), ("capacity", "capacity_assumptions")):
            expected[name] = {"status": "DECLARED", "model_id": declared[key]["model_id"],
                              "declaration_hash": sha256_json(declared[key])}
        supplied = bundle["sources"]
        if (supplied["manifest_hash"] != sha256_json(sources)
                or sorted(supplied["snapshot_hashes"]) != sorted(s["snapshot_hash"] for s in sources)
                or sorted(sha256_json(row) for row in supplied["pit_metadata"]) != sorted(sha256_json(row) for row in pit)):
            return False
        return (payload["candidate"] == bundle["candidate"]
                and payload["hypothesis_id"] == bundle["candidate"]["hypothesis_id"]
                and payload["generation_id"] == bundle["candidate"]["generation_id"]
                and payload["declared_decision_map"] == bundle["candidate"]["decision_map"]
                and all(bundle.get(key) == value for key, value in expected.items())
                and declared["decision_map"] == bundle["candidate"]["decision_map"]
                and declared["entry_definition"] == expression["entry_clock"]
                and declared["exit_definition"] == expression["exit_clock"]
                and declared["universe"]["universe_id"] == expression["universe"])
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


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
        expected_geometry = geometry_from_mapping(protocol_hash, frozen_protocol.get("geometry_declaration"))
        expected_power = power_from_mapping(protocol_hash, frozen_protocol.get("power_declaration"))
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
    validator_id = bundle.get("validator_id")
    declared_candidate_hash = bundle.get("candidate_hash")

    pit_rows = source_bundle.get("pit_metadata", [])
    if not isinstance(pit_rows, list):
        pit_rows = []
    data_cutoff = _iso(clock.get("data_cutoff"))
    source_times = [_iso(row.get("available_at")) for row in pit_rows if isinstance(row, dict)]

    expression_spec = expression.get("spec") if isinstance(expression.get("spec"), dict) else {}
    expression_required = (
        "instrument_rule", "side_rule", "entry_rule", "exit_rule", "horizon_rule", "sizing_rule",
    )

    protocol_candidate_hash = _protocol_candidate_hash(protocol)
    source_hashes = _source_hashes(source_bundle)
    pit_hashes = [row.get("snapshot_hash") for row in pit_rows if isinstance(row, dict)]
    pit_coverage = (bool(source_hashes) and len(pit_rows) == len(source_hashes)
                    and len(pit_hashes) == len(pit_rows) and all(_is_hash(v) for v in pit_hashes)
                    and sorted(pit_hashes) == source_hashes)
    reproducibility_payload = reproducibility.get("binding_payload")
    binding_hash_valid = (
        isinstance(reproducibility_payload, dict)
        and _is_hash(reproducibility.get("binding_hash"))
        and sha256_json(reproducibility_payload) == reproducibility.get("binding_hash")
    )
    firewall_error: str | None = None
    try:
        assert_pre_outcome_payload(bundle)
    except OutcomeFirewallError as error:
        firewall_error = str(error)

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
        _identifier(producer_id) and _identifier(validator_id) and producer_id != validator_id,
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
        and pit_coverage,
        "Source manifest and each snapshot reference must have exact PIT metadata coverage.",
    )
    add(
        "pit",
        pit_coverage
        and all(
            isinstance(row, dict)
            and row.get("point_in_time_qualified") is True
            and _identifier(row.get("source_id"))
            and _iso(row.get("available_at")) is not None
            and _iso(row.get("route_available_at")) is not None and data_cutoff is not None
            and _iso(row["route_available_at"]) <= data_cutoff
            for row in pit_rows
        )
        and data_cutoff is not None
        and all(ts is not None and ts <= data_cutoff for ts in source_times),
        "Each bound snapshot and its qualified route must be available by the data cutoff.",
    )
    decision_time = _iso(clock.get("decision_time"))
    freeze_time = _iso(clock.get("freeze_time"))
    add(
        "clock",
        _present(clock.get("timezone"))
        and data_cutoff is not None
        and decision_time is not None
        and freeze_time is not None
        and data_cutoff <= decision_time <= freeze_time,
        "Timezone-aware timestamps must satisfy data cutoff <= decision <= freeze; later information cannot support an earlier decision.",
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
        implementability.get("status") == "PASS" and _is_hash(implementability.get("declaration_hash")),
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
    add(
        "frozen_input_binding",
        _frozen_input_binding(bundle, protocol),
        "Readiness projections must match the source, protocol and implementation declarations frozen in the envelope.",
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
        "outcome_firewall",
        firewall_error is None,
        "Entire Validator bundle is outcome-blind under the canonical firewall."
        if firewall_error is None else f"Canonical outcome firewall rejected bundle: {firewall_error}",
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
        {"code": checks[name]["reason_code"], "check": name, "detail": checks[name]["detail"]}
        for name in CHECK_ORDER if checks[name]["status"] != "PASS"
    ]
    mutated = candidate != candidate_before
    if mutated and checks["candidate_immutability"]["status"] == "PASS":
        checks["candidate_immutability"] = {
            "status": "FAIL",
            "reason_code": REASON_CODES["candidate_immutability"],
            "detail": "Validator mutated candidate state while evaluating readiness.",
        }
        block_reasons.insert(0, {
            "code": REASON_CODES["candidate_immutability"],
            "check": "candidate_immutability",
            "detail": checks["candidate_immutability"]["detail"],
        })

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
