"""CP069-first convergence facade for economic readiness validation.

The public contract remains ``validate_economic_test_readiness``. CP069 remains
authoritative for frozen-input/PIT semantics; W1 Factory contributes registry /
runner / geometry / power attestation and the canonical outcome firewall. The
two qualified validators are private components and their applicable checks are
intersected fail-closed.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from . import _validation_readiness_cp069 as _cp069
from . import _validation_readiness_factory as _factory


READY = _cp069.READY
BLOCK = _cp069.BLOCK

_FACTORY_ADDITIONS = ("experiment_infrastructure", "outcome_firewall")
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
REASON_CODES = {**_cp069.REASON_CODES, **{
    key: _factory.REASON_CODES[key] for key in _FACTORY_ADDITIONS
}}


def _cp069_projection(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Adapt additive Factory fields to the exact CP069 validator projection.

    Only missing PIT identity fields are reconstructed from the already-frozen
    protocol provenance. Supplied values are never overwritten, so tampering
    remains observable. Factory lineage fields are removed only from the private
    CP069 numeric trial-accounting projection; the Factory validator and the
    canonical v3 boundary validate the enriched lineage independently.
    """
    projected = deepcopy(dict(bundle))
    protocol = projected.get("protocol")
    payload = protocol.get("protocol_payload") if isinstance(protocol, Mapping) else None
    provenance = payload.get("dataset_provenance") if isinstance(payload, Mapping) else None
    frozen_sources = provenance.get("sources") if isinstance(provenance, Mapping) else None

    sources = projected.get("sources")
    pit_rows = sources.get("pit_metadata") if isinstance(sources, Mapping) else None
    if isinstance(pit_rows, list) and isinstance(frozen_sources, list):
        by_id = {}
        for source in frozen_sources:
            if not isinstance(source, Mapping):
                continue
            route = source.get("route")
            if not isinstance(route, Mapping):
                continue
            route_id = route.get("route_id")
            if isinstance(route_id, str):
                by_id[route_id] = source
        for row in pit_rows:
            if not isinstance(row, dict):
                continue
            frozen = by_id.get(row.get("source_id"))
            if not isinstance(frozen, Mapping):
                continue
            route = frozen.get("route")
            if "snapshot_hash" not in row and "snapshot_hash" in frozen:
                row["snapshot_hash"] = frozen["snapshot_hash"]
            if (isinstance(route, Mapping) and "route_available_at" not in row
                    and "availability_start" in route):
                row["route_available_at"] = route["availability_start"]

    trial = projected.get("trial_accounting")
    if isinstance(trial, dict):
        trial.pop("hypothesis_id", None)
        trial.pop("generation_id", None)
    return projected


def _pick_check(cp_check: Any, factory_check: Any) -> Dict[str, Any]:
    """Intersect duplicate checks; a failure on either qualified rail wins."""
    candidates = [
        item for item in (cp_check, factory_check) if isinstance(item, Mapping)
    ]
    for item in candidates:
        if item.get("status") != "PASS":
            return deepcopy(dict(item))
    if candidates:
        return deepcopy(dict(candidates[0]))
    return {
        "status": "FAIL",
        "reason_code": "CONVERGENCE_CHECK_MISSING",
        "detail": "Qualified convergence component did not emit the required check.",
    }


def validate_economic_test_readiness(bundle: Dict[str, Any]) -> Dict[str, Any]:
    cp_result = _cp069.validate_economic_test_readiness(_cp069_projection(bundle))
    factory_result = _factory.validate_economic_test_readiness(deepcopy(bundle))

    infrastructure = bundle.get("experiment_infrastructure")
    strict_factory = isinstance(infrastructure, Mapping) and bool(infrastructure)

    checks: Dict[str, Dict[str, Any]] = {}
    cp_checks = cp_result.get("checks") if isinstance(cp_result.get("checks"), Mapping) else {}
    factory_checks = (
        factory_result.get("checks")
        if isinstance(factory_result.get("checks"), Mapping)
        else {}
    )
    for name in CHECK_ORDER:
        if name == "experiment_infrastructure" and not strict_factory:
            continue
        checks[name] = _pick_check(cp_checks.get(name), factory_checks.get(name))

    block_reasons = []
    for name in CHECK_ORDER:
        check = checks.get(name)
        if not isinstance(check, Mapping) or check.get("status") == "PASS":
            continue
        block_reasons.append({
            "code": check.get("reason_code") or REASON_CODES.get(name, "CONVERGENCE_CHECK_FAILED"),
            "check": name,
            "detail": check.get("detail", "Qualified convergence check failed."),
        })

    result = deepcopy(cp_result)
    ready = not block_reasons
    result.update({
        "status": READY if ready else BLOCK,
        "ready_for_authorized_economic_test": ready,
        "checks": checks,
        "block_reasons": block_reasons,
        "economic_test_authorized": False,
        "economic_claim_authorized": False,
        "outcome_access_authorized": False,
        "candidate_mutated": bool(
            cp_result.get("candidate_mutated") or factory_result.get("candidate_mutated")
        ),
        "signal_repair_attempted": False,
        "parameter_optimization_attempted": False,
        "claim_ceiling": READY if ready else "BLOCKED_PRE_OUTCOME",
    })
    return result
