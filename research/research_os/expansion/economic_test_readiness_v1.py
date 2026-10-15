from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional
import math
import re

from research.research_os.scientific_store import sha256_json


READINESS_SCHEMA = "economic-test-readiness.v1"
PLAN_SCHEMA = "preoutcome-execution-plan.v1"
VALIDATOR_ID = "independent-validator.economic-test-readiness.v1"
RED_TEAM_ID = "red-team.economic-test-readiness.v1"

ALLOWED_RED_TEAM_RIGHTS = {
    "DATA",
    "LEAKAGE",
    "CLOCK",
    "PIT",
    "MULTIPLICITY",
    "TRIAL_ACCOUNTING",
    "IMPLEMENTABILITY",
    "COST_MODEL",
    "CAPACITY",
    "CLAIM_LEVEL",
    "REPRODUCIBILITY",
    "ECONOMIC_IDENTITY",
    "PORTFOLIO_DUPLICATION",
}

_REQUIRED_SPEC_FIELDS = (
    "universe_definition",
    "clock",
    "entry_definition",
    "exit_definition",
    "position_expression",
    "gross_metric",
    "net_metric",
    "cost_assumptions",
    "capacity_assumptions",
    "sample_window",
    "exclusions",
    "missing_data_policy",
    "revision_policy",
    "survivorship_policy",
    "falsification_rule",
    "decision_map",
    "observed_attempt_count",
    "effective_trials_estimate",
    "multiplicity_family",
    "seed",
    "environment",
    "code_sha",
    "dependency_environment_fingerprint",
)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().upper() not in {"UNKNOWN", "UNSPECIFIED", "TBD"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{40}", value) is not None


def _trial_accounting_valid(observed: Any, effective: Any) -> bool:
    if type(observed) is not int or observed < 0:
        return False
    if effective == "UNKNOWN":
        return True
    return type(effective) in (int, float) and math.isfinite(effective) and effective >= 0


def _source_snapshot(qualifications: Iterable[Dict[str, Any]]) -> Dict[str, str]:
    items = list(qualifications)
    snapshot: Dict[str, str] = {}
    for item in items:
        route_id = item.get("route_id")
        route_hash = item.get("route_hash")
        if route_id and route_hash:
            if route_id in snapshot and snapshot[route_id] != route_hash:
                raise ValueError(f"conflicting source snapshot for route {route_id}")
            snapshot[route_id] = route_hash
    return dict(sorted(snapshot.items()))


def freeze_economic_test_package(
    *,
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    source_qualifications: Iterable[Dict[str, Any]],
    specification: Mapping[str, Any],
) -> Dict[str, Any]:
    """Freeze a complete pre-outcome economic-test package.

    This function never reads economic outcomes and never grants execution
    authority. It only makes the next authorized test mechanically specific.
    """
    candidate = deepcopy(engine_output["candidate"])
    sources = [deepcopy(item) for item in source_qualifications]
    spec = deepcopy(dict(specification))
    blockers: List[str] = []

    if implementability.get("status") != "PASS":
        blockers.append("IMPLEMENTABILITY_BLOCKED")
    for field in _REQUIRED_SPEC_FIELDS:
        if field not in spec:
            blockers.append(f"MISSING_{field.upper()}")
    for field in _REQUIRED_SPEC_FIELDS:
        if field in {"observed_attempt_count", "effective_trials_estimate", "exclusions"}:
            continue
        if field in spec and not _present(spec[field]):
            blockers.append(f"UNQUALIFIED_{field.upper()}")

    if not _trial_accounting_valid(spec.get("observed_attempt_count"), spec.get("effective_trials_estimate")):
        blockers.append("TRIAL_ACCOUNTING_INVALID")
    if not _valid_sha(spec.get("code_sha")):
        blockers.append("CODE_SHA_INVALID")
    if spec.get("decision_map") != candidate.get("decision_map"):
        blockers.append("DECISION_MAP_NOT_BOUND_TO_CANDIDATE")
    if spec.get("falsification_rule") != candidate.get("falsification_scope"):
        blockers.append("FALSIFICATION_NOT_BOUND_TO_CANDIDATE")

    if not sources:
        blockers.append("SOURCE_SNAPSHOT_MISSING")
    if any(item.get("status") != "PASS" for item in sources):
        blockers.append("SOURCE_QUALIFICATION_BLOCKED")
    if any(item.get("point_in_time_qualified") is not True for item in sources):
        blockers.append("PIT_NOT_QUALIFIED")
    if any(item.get("outcome_accessed") is not False for item in sources):
        blockers.append("SOURCE_OUTCOME_ACCESS_DETECTED")
    if any(not item.get("route_id") or not item.get("route_hash") for item in sources):
        blockers.append("SOURCE_PROVENANCE_INCOMPLETE")

    try:
        source_snapshot_hashes = _source_snapshot(sources)
    except ValueError:
        source_snapshot_hashes = {}
        blockers.append("SOURCE_SNAPSHOT_CONFLICT")

    candidate_hash = sha256_json(candidate)
    protocol_payload = {
        "schema": READINESS_SCHEMA,
        "hypothesis_id": candidate.get("hypothesis_id"),
        "generation_id": candidate.get("generation_id"),
        "candidate_hash": candidate_hash,
        "source_snapshot_hashes": source_snapshot_hashes,
        "universe_definition": spec.get("universe_definition"),
        "clock": spec.get("clock"),
        "entry_definition": spec.get("entry_definition"),
        "exit_definition": spec.get("exit_definition"),
        "position_expression": spec.get("position_expression"),
        "benchmark": spec.get("benchmark"),
        "gross_metric": spec.get("gross_metric"),
        "net_metric": spec.get("net_metric"),
        "cost_assumptions": spec.get("cost_assumptions"),
        "capacity_assumptions": spec.get("capacity_assumptions"),
        "sample_window": spec.get("sample_window"),
        "exclusions": spec.get("exclusions", []),
        "missing_data_policy": spec.get("missing_data_policy"),
        "revision_policy": spec.get("revision_policy"),
        "survivorship_policy": spec.get("survivorship_policy"),
        "falsification_rule": spec.get("falsification_rule"),
        "decision_map": spec.get("decision_map"),
        "observed_attempt_count": spec.get("observed_attempt_count"),
        "effective_trials_estimate": spec.get("effective_trials_estimate"),
        "multiplicity_family": spec.get("multiplicity_family"),
        "seed": spec.get("seed"),
        "environment": spec.get("environment"),
        "code_sha": spec.get("code_sha"),
        "dependency_environment_fingerprint": spec.get("dependency_environment_fingerprint"),
    }
    protocol_hash = sha256_json(protocol_payload) if not blockers else None
    return {
        "schema": READINESS_SCHEMA,
        "experiment_id": f"EXP-{candidate.get('hypothesis_id')}-{candidate.get('generation_id')}",
        "hypothesis_id": candidate.get("hypothesis_id"),
        "generation_id": candidate.get("generation_id"),
        "candidate_hash": candidate_hash,
        "source_snapshot_hashes": source_snapshot_hashes,
        "status": "FROZEN_READY_NO_OUTCOME" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "protocol_hash": protocol_hash,
        "protocol_payload": protocol_payload,
        "candidate_snapshot": candidate,
        "source_qualifications": sources,
        "economic_outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "material_change_requires_new_generation_or_protocol": True,
    }


def build_preoutcome_execution_plan(package: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[str] = []
    if package.get("status") != "FROZEN_READY_NO_OUTCOME":
        blockers.append("PACKAGE_NOT_FROZEN")
    protocol = package.get("protocol_payload")
    if not isinstance(protocol, dict) or sha256_json(protocol) != package.get("protocol_hash"):
        blockers.append("PROTOCOL_BINDING_INVALID")
    if package.get("economic_outcome_accessed") is not False:
        blockers.append("OUTCOME_ALREADY_ACCESSED")

    binding = {
        "schema": PLAN_SCHEMA,
        "experiment_id": package.get("experiment_id"),
        "hypothesis_id": package.get("hypothesis_id"),
        "generation_id": package.get("generation_id"),
        "candidate_hash": package.get("candidate_hash"),
        "protocol_hash": package.get("protocol_hash"),
        "source_snapshot_hashes": deepcopy(package.get("source_snapshot_hashes") or {}),
        "code_sha": protocol.get("code_sha") if isinstance(protocol, dict) else None,
        "dependency_environment_fingerprint": (
            protocol.get("dependency_environment_fingerprint") if isinstance(protocol, dict) else None
        ),
        "seed": protocol.get("seed") if isinstance(protocol, dict) else None,
        "environment": deepcopy(protocol.get("environment")) if isinstance(protocol, dict) else None,
        "execution_mode": "PREOUTCOME_PLAN_ONLY",
    }
    return {
        "schema": PLAN_SCHEMA,
        "status": "READY_FOR_AUTHORIZED_ECONOMIC_TEST_PLAN" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "binding": binding,
        "execution_plan_hash": sha256_json(binding),
        "economic_execution_performed": False,
        "economic_outcome_accessed": False,
        "side_effects_authorized": False,
    }


def verify_preoutcome_execution_plan(
    *,
    plan: Dict[str, Any],
    package: Dict[str, Any],
    current_candidate: Dict[str, Any],
    current_source_qualifications: Iterable[Dict[str, Any]],
    current_code_sha: str,
    current_dependency_environment_fingerprint: str,
) -> Dict[str, Any]:
    blockers: List[str] = []
    binding = plan.get("binding") if isinstance(plan.get("binding"), dict) else {}
    protocol = package.get("protocol_payload") if isinstance(package.get("protocol_payload"), dict) else {}

    if plan.get("status") != "READY_FOR_AUTHORIZED_ECONOMIC_TEST_PLAN":
        blockers.append("PLAN_NOT_READY")
    if sha256_json(binding) != plan.get("execution_plan_hash"):
        blockers.append("EXECUTION_PLAN_MUTATED")
    if sha256_json(package.get("protocol_payload")) != package.get("protocol_hash"):
        blockers.append("PROTOCOL_CHANGED")
    if sha256_json(current_candidate) != package.get("candidate_hash"):
        blockers.append("CANDIDATE_CHANGED")
    if current_candidate.get("generation_id") != package.get("generation_id"):
        blockers.append("GENERATION_CHANGED")
    try:
        current_sources = _source_snapshot(current_source_qualifications)
    except ValueError:
        current_sources = {}
        blockers.append("SOURCE_CHANGED")
    if current_sources != package.get("source_snapshot_hashes"):
        blockers.append("SOURCE_CHANGED")
    if current_code_sha != protocol.get("code_sha") or current_code_sha != binding.get("code_sha"):
        blockers.append("CODE_BINDING_CHANGED")
    if (
        current_dependency_environment_fingerprint != protocol.get("dependency_environment_fingerprint")
        or current_dependency_environment_fingerprint != binding.get("dependency_environment_fingerprint")
    ):
        blockers.append("ENVIRONMENT_BINDING_CHANGED")
    for field in (
        "experiment_id",
        "hypothesis_id",
        "generation_id",
        "candidate_hash",
        "protocol_hash",
        "source_snapshot_hashes",
    ):
        if binding.get(field) != package.get(field):
            blockers.append(f"PLAN_{field.upper()}_DRIFT")

    return {
        "status": "REPLAY_MATCH" if not blockers else "BLOCK",
        "blockers": sorted(set(blockers)),
        "execution_plan_hash": plan.get("execution_plan_hash"),
        "economic_execution_performed": False,
        "economic_outcome_accessed": False,
    }


def validate_economic_test_readiness(
    *,
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    package: Dict[str, Any],
    plan: Dict[str, Any],
    replay: Dict[str, Any],
    validator_id: str = VALIDATOR_ID,
    economic_identity: Optional[Dict[str, Any]] = None,
    portfolio_interpretation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    candidate = engine_output["candidate"]
    sources = package.get("source_qualifications") or []
    protocol = package.get("protocol_payload") or {}
    checks: Dict[str, Dict[str, Any]] = {}

    def add(name: str, passed: bool, blocker: str) -> None:
        checks[name] = {"status": "PASS" if passed else "FAIL", "blocker": None if passed else blocker}

    add(
        "producer_separation",
        bool(validator_id) and validator_id != engine_output.get("engine_id"),
        "CLAIM_LEVEL",
    )
    add(
        "candidate_immutability",
        sha256_json(candidate) == package.get("candidate_hash")
        and candidate.get("generation_id") == package.get("generation_id"),
        "REPRODUCIBILITY",
    )
    add(
        "pit",
        bool(sources) and all(item.get("status") == "PASS" and item.get("point_in_time_qualified") is True for item in sources),
        "PIT",
    )
    add(
        "clock",
        _present(protocol.get("clock")) and _present(protocol.get("entry_definition")) and _present(protocol.get("exit_definition")),
        "CLOCK",
    )
    try:
        source_binding_ok = _source_snapshot(sources) == package.get("source_snapshot_hashes")
    except ValueError:
        source_binding_ok = False
    add(
        "provenance",
        source_binding_ok and all(item.get("outcome_accessed") is False for item in sources),
        "DATA",
    )
    add(
        "protocol_freeze",
        package.get("status") == "FROZEN_READY_NO_OUTCOME"
        and isinstance(package.get("protocol_payload"), dict)
        and sha256_json(package["protocol_payload"]) == package.get("protocol_hash"),
        "REPRODUCIBILITY",
    )
    add("multiplicity_declaration", _present(protocol.get("multiplicity_family")), "MULTIPLICITY")
    add(
        "trial_accounting",
        _trial_accounting_valid(protocol.get("observed_attempt_count"), protocol.get("effective_trials_estimate")),
        "TRIAL_ACCOUNTING",
    )
    add("implementability", implementability.get("status") == "PASS", "IMPLEMENTABILITY")
    add(
        "reproducibility",
        plan.get("status") == "READY_FOR_AUTHORIZED_ECONOMIC_TEST_PLAN" and replay.get("status") == "REPLAY_MATCH",
        "REPRODUCIBILITY",
    )
    add("cost_model", _present(protocol.get("cost_assumptions")), "COST_MODEL")
    add("capacity", _present(protocol.get("capacity_assumptions")), "CAPACITY")
    add(
        "falsification",
        protocol.get("falsification_rule") == candidate.get("falsification_scope") and _present(protocol.get("falsification_rule")),
        "CLAIM_LEVEL",
    )
    add(
        "decision_map",
        protocol.get("decision_map") == candidate.get("decision_map") and _present(protocol.get("decision_map")),
        "CLAIM_LEVEL",
    )
    add(
        "no_outcome_access",
        package.get("economic_outcome_accessed") is False
        and plan.get("economic_outcome_accessed") is False
        and replay.get("economic_outcome_accessed") is False,
        "LEAKAGE",
    )

    if economic_identity is not None:
        add(
            "economic_identity",
            economic_identity.get("hypothesis_id") == candidate.get("hypothesis_id")
            and economic_identity.get("generation_id") == candidate.get("generation_id")
            and economic_identity.get("empirical_correlation", "UNKNOWN") in {"UNKNOWN", "UNAVAILABLE", "UNAVAILABLE_BY_DESIGN"}
            and economic_identity.get("return_series_consumed", False) is False,
            "ECONOMIC_IDENTITY",
        )
    if portfolio_interpretation is not None:
        add(
            "portfolio_interpretation",
            portfolio_interpretation.get("capital_allocation_authorized") is False
            and portfolio_interpretation.get("position_sizing_authorized") is False
            and portfolio_interpretation.get("orders_authorized") is False
            and portfolio_interpretation.get("empirical_correlation", "UNKNOWN") in {"UNKNOWN", "UNAVAILABLE", "UNAVAILABLE_BY_DESIGN"}
            and portfolio_interpretation.get("marginal_contribution", "NOT_ESTIMATED") == "NOT_ESTIMATED",
            "PORTFOLIO_DUPLICATION",
        )

    failures = sorted(name for name, check in checks.items() if check["status"] != "PASS")
    blockers = sorted({checks[name]["blocker"] for name in failures if checks[name]["blocker"]})
    return {
        "validator": validator_id,
        "producer_engine": engine_output.get("engine_id"),
        "independent_from_producer": validator_id != engine_output.get("engine_id"),
        "status": "PASS" if not failures else "BLOCK",
        "checks": checks,
        "failures": failures,
        "blockers": blockers,
        "claim_mutated": False,
        "signal_repaired": False,
        "ready_for_authorized_economic_test": not failures,
        "owner_authorization_required": True,
        "economic_execution_authorized": False,
        "economic_outcome_accessed": False,
    }


def red_team_economic_test_readiness(validation: Dict[str, Any]) -> Dict[str, Any]:
    rights = sorted(set(validation.get("blockers") or []) & ALLOWED_RED_TEAM_RIGHTS)
    if validation.get("status") != "PASS" and not rights:
        rights = ["CLAIM_LEVEL"]
    return {
        "red_team": RED_TEAM_ID,
        "status": "PASS" if not rights else "BLOCK",
        "negative_rights": rights,
        "allowed_negative_rights": sorted(ALLOWED_RED_TEAM_RIGHTS),
        "repair_attempted": False,
        "optimization_attempted": False,
        "claim_mutated": False,
        "economic_outcome_accessed": False,
    }


def qualify_economic_test_readiness(
    *,
    engine_output: Dict[str, Any],
    implementability: Dict[str, Any],
    source_qualifications: Iterable[Dict[str, Any]],
    specification: Mapping[str, Any],
    current_code_sha: str,
    current_dependency_environment_fingerprint: str,
    economic_identity: Optional[Dict[str, Any]] = None,
    portfolio_interpretation: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Close the path to, but never cross, Owner-authorized economic execution."""
    sources = [deepcopy(item) for item in source_qualifications]
    package = freeze_economic_test_package(
        engine_output=engine_output,
        implementability=implementability,
        source_qualifications=sources,
        specification=specification,
    )
    plan = build_preoutcome_execution_plan(package)
    replay = verify_preoutcome_execution_plan(
        plan=plan,
        package=package,
        current_candidate=engine_output["candidate"],
        current_source_qualifications=sources,
        current_code_sha=current_code_sha,
        current_dependency_environment_fingerprint=current_dependency_environment_fingerprint,
    )
    validation = validate_economic_test_readiness(
        engine_output=engine_output,
        implementability=implementability,
        package=package,
        plan=plan,
        replay=replay,
        economic_identity=economic_identity,
        portfolio_interpretation=portfolio_interpretation,
    )
    red = red_team_economic_test_readiness(validation)
    ready = package.get("status") == "FROZEN_READY_NO_OUTCOME" and validation["status"] == "PASS" and red["status"] == "PASS"
    return {
        "schema": READINESS_SCHEMA,
        "status": "READY_FOR_OWNER_AUTHORIZED_TEST" if ready else "BLOCK",
        "package": package,
        "execution_plan": plan,
        "replay": replay,
        "validation": validation,
        "red_team": red,
        "ready_for_authorized_economic_test": ready,
        "authorization_barrier": {
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        },
        "economic_execution_performed": False,
        "economic_outcome_accessed": False,
        "prospective_started": False,
        "real_capital_used": False,
        "live_trading_performed": False,
    }
