"""Authority-closed economic lifecycle kernel.

This module sits *downstream* of the qualified W1 Economic boundary. It binds
EconomicIdentityRef + PortfolioReadinessRef into immutable shadow/prospective
contracts and manages lifecycle dispositions without rebuilding economic
identity, portfolio diagnostics, empirical correlation, scheduling, execution,
or trading authority.

The kernel is intentionally outcome-blind. Review decisions accept only
metadata-only evidence references that attest to an externally adjudicated
scientific disposition; raw P&L/return/outcome payloads are rejected.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Dict, List, Mapping, Optional, Sequence


AUTHORITY_CLOSED: Dict[str, bool] = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "position_sizing_authorized": False,
    "orders_authorized": False,
}

LIFECYCLE_STATES = {
    "BLOCKED_BY_UPSTREAM_READINESS",
    "READY_AWAITING_OWNER_AUTHORITY",
    "REVIEW_REQUIRED",
    "RESIZE_ELIGIBLE",
    "PARKED",
    "RETIRED",
    "REPLACEMENT_REQUIRED",
    "SUPERSEDED",
}

REVIEW_DISPOSITIONS = {
    "CONTINUE",
    "RESIZE",
    "PARK",
    "RETIRE",
    "REPLACE",
    "INCONCLUSIVE",
}

EVIDENCE_CLASSES = {
    "MECHANISM",
    "WRAPPER",
    "IMPLEMENTATION",
    "COST_CAPACITY",
    "PORTFOLIO_RELATIONSHIP",
    "OTHER_SCOPED",
}

REPLACEMENT_DISTINCTIONS = {"MECHANISM", "WRAPPER", "IMPLEMENTATION", "MIXED", "UNKNOWN"}

_FORBIDDEN_OUTCOME_KEYS = {
    "return", "returns", "pnl", "profit", "loss", "sharpe", "sortino",
    "drawdown", "equity_curve", "price", "prices", "fill", "fills",
    "realized_pnl", "unrealized_pnl", "hit_rate", "win_rate", "outcome",
    "outcomes", "observations", "raw_observations", "return_series",
}


class EconomicLifecycleError(ValueError):
    """Raised when an invariant-breaking lifecycle input is supplied."""


def _hash(value: Any) -> str:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise EconomicLifecycleError(f"non-canonical lifecycle payload: {error}") from error
    return hashlib.sha256(raw).hexdigest()


def _known_string(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value.strip().upper() not in {
            "UNKNOWN", "UNAVAILABLE", "UNSPECIFIED", "NOT_ESTIMATED", "NOT_OBSERVED",
        }
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EconomicLifecycleError(message)


def _deep_forbidden_keys(value: Any) -> List[str]:
    found: List[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().casefold()
            if normalized in _FORBIDDEN_OUTCOME_KEYS:
                found.append(str(key))
            found.extend(_deep_forbidden_keys(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_deep_forbidden_keys(item))
    return sorted(set(found))


def _normalize_review_policy(policy: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    raw = deepcopy(dict(policy or {}))
    raw.setdefault("cadence", "OWNER_DEFINED")
    raw.setdefault("clock", "UNBOUND_UNTIL_EXTERNAL_AUTHORITY")
    raw["scheduler_owned"] = False
    raw["automatic_wake_authorized"] = False
    raw["outcome_access_authorized"] = False
    return raw


def build_economic_identity_ref(structural: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind a W1 structural identity without recomputing its fingerprint."""
    _require(isinstance(structural, Mapping), "economic identity must be a mapping")
    hypothesis_id = structural.get("hypothesis_id")
    generation_id = structural.get("generation_id")
    identity_hash = structural.get("identity_hash")
    binding = structural.get("candidate_binding")
    _require(_known_string(hypothesis_id), "economic identity hypothesis_id is not known")
    _require(_known_string(generation_id), "economic identity generation_id is not known")
    _require(_known_string(identity_hash), "economic identity hash is not known")
    _require(isinstance(binding, Mapping), "economic identity candidate binding is missing")
    _require(binding.get("status") == "BOUND", "economic identity candidate binding is not verified")
    candidate_hash = binding.get("candidate_hash")
    _require(_known_string(candidate_hash), "economic identity candidate hash is not known")
    ref = {
        "ref_type": "EconomicIdentityRef.v1",
        "hypothesis_id": hypothesis_id,
        "generation_id": generation_id,
        "identity_hash": identity_hash,
        "candidate_hash": candidate_hash,
        "identity_readiness": deepcopy(structural.get("identity_readiness", {})),
    }
    ref["ref_hash"] = _hash(ref)
    return ref


def build_portfolio_readiness_ref(portfolio: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind W1 portfolio readiness exactly; do not reinterpret its economics."""
    _require(isinstance(portfolio, Mapping), "portfolio diagnostics must be a mapping")
    readiness = portfolio.get("portfolio_readiness", portfolio)
    _require(isinstance(readiness, Mapping), "portfolio readiness is missing")
    structural = readiness.get("structural_mapping")
    decision = readiness.get("pre_outcome_decision")
    empirical = readiness.get("empirical_layer")
    _require(isinstance(structural, Mapping), "structural_mapping readiness is missing")
    _require(isinstance(decision, Mapping), "pre_outcome_decision readiness is missing")
    _require(isinstance(empirical, Mapping), "empirical_layer readiness is missing")

    for key in (
        "economic_experiment_authorized", "prospective_observation_authorized",
        "capital_allocation_authorized", "position_sizing_authorized",
        "orders_authorized", "real_capital_authorized", "live_trading_authorized",
        "portfolio_optimization_authorized",
    ):
        if key in portfolio:
            _require(portfolio.get(key) is False, f"upstream portfolio authority open: {key}")
    if "return_series_consumed" in portfolio:
        _require(portfolio.get("return_series_consumed") is False, "upstream portfolio consumed return series")

    readiness_payload = deepcopy(dict(readiness))
    current_clearance = (
        structural.get("status") == "QUALIFIED_CURRENT"
        and decision.get("status") == "QUALIFIED_CURRENT"
        and not structural.get("blockers", [])
        and not decision.get("blockers", [])
    )
    ref = {
        "ref_type": "PortfolioReadinessRef.v1",
        "readiness": readiness_payload,
        "current_clearance": bool(current_clearance),
        "empirical_layer_status": empirical.get("status", "UNKNOWN"),
        "upstream_blockers": sorted(set(
            list(structural.get("blockers", [])) + list(decision.get("blockers", []))
        )),
        "return_series_consumed": False,
    }
    ref["ref_hash"] = _hash(ref)
    return ref


def _protocol_ref(value: Any) -> Dict[str, Any]:
    if isinstance(value, str):
        _require(_known_string(value), "protocol ref is not known")
        return {"kind": "opaque-protocol-ref", "value": value, "ref_hash": _hash(value)}
    _require(isinstance(value, Mapping), "protocol ref must be a known string or mapping")
    payload = deepcopy(dict(value))
    _require(not _deep_forbidden_keys(payload), "protocol ref contains outcome-bearing fields")
    return {"kind": "protocol-metadata", "value": payload, "ref_hash": _hash(payload)}


def create_shadow_contract(
    structural_identity: Mapping[str, Any],
    portfolio_diagnostics: Mapping[str, Any],
    *,
    protocol_ref: Any,
    review_policy: Optional[Mapping[str, Any]] = None,
    predecessor_contract_id: Optional[str] = None,
    lifecycle_version: int = 1,
    replacement_reason_ref: Optional[str] = None,
) -> Dict[str, Any]:
    """Create one immutable, authority-closed shadow/prospective contract."""
    _require(type(lifecycle_version) is int and lifecycle_version >= 1, "lifecycle_version must be a positive integer")
    identity_ref = build_economic_identity_ref(structural_identity)
    portfolio_ref = build_portfolio_readiness_ref(portfolio_diagnostics)
    protocol = _protocol_ref(protocol_ref)
    policy = _normalize_review_policy(review_policy)
    lineage_seed = {
        "predecessor_contract_id": predecessor_contract_id,
        "replacement_reason_ref": replacement_reason_ref,
    }
    seed = {
        "kernel": "economic-lifecycle.v1",
        "economic_identity_ref_hash": identity_ref["ref_hash"],
        "portfolio_readiness_ref_hash": portfolio_ref["ref_hash"],
        "protocol_ref_hash": protocol["ref_hash"],
        "review_policy_hash": _hash(policy),
        "lifecycle_version": lifecycle_version,
        "lineage_seed": lineage_seed,
    }
    contract_id = f"ECON-LC-{_hash(seed)[:24]}"
    observation_identity = {
        "identity_type": "ProspectiveObservationIdentity.v1",
        "lifecycle_contract_id": contract_id,
        "economic_identity_ref_hash": identity_ref["ref_hash"],
        "portfolio_readiness_ref_hash": portfolio_ref["ref_hash"],
        "protocol_ref_hash": protocol["ref_hash"],
        "lifecycle_version": lifecycle_version,
        "start_boundary": "UNBOUND_UNTIL_EXTERNAL_AUTHORITY",
        "activation_receipt_ref": None,
        "observation_started": False,
        "future_outcomes_consumed": 0,
    }
    observation_identity["identity_hash"] = _hash(observation_identity)
    state = (
        "READY_AWAITING_OWNER_AUTHORITY"
        if portfolio_ref["current_clearance"]
        else "BLOCKED_BY_UPSTREAM_READINESS"
    )
    contract = {
        "kernel": "economic-lifecycle.v1",
        "contract_id": contract_id,
        "lifecycle_version": lifecycle_version,
        "state": state,
        "status_class": "READY" if state == "READY_AWAITING_OWNER_AUTHORITY" else "BLOCKED",
        "economic_identity_ref": identity_ref,
        "portfolio_readiness_ref": portfolio_ref,
        "protocol_ref": protocol,
        "review_policy": policy,
        "prospective_observation_identity": observation_identity,
        "authority": deepcopy(AUTHORITY_CLOSED),
        "authority_source": "EXTERNAL_OWNER_ONLY",
        "builder_self_authorization_path": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "prospective_evidence_status": "NOT_OBSERVED",
        "review_history": [],
        "negative_knowledge": [],
        "lineage": {
            "predecessor_contract_id": predecessor_contract_id,
            "successor_contract_id": None,
            "replacement_reason_ref": replacement_reason_ref,
            "superseded": False,
        },
        "semantic_guards": {
            "blocked_is_failed": False,
            "unexecuted_is_negative": False,
            "ready_is_profitable": False,
            "structural_overlap_is_empirical_correlation": False,
            "unknown_preserved": True,
            "negative_knowledge_global_by_default": False,
        },
    }
    contract["contract_hash"] = _hash({k: v for k, v in contract.items() if k != "contract_hash"})
    assert_contract_invariants(contract)
    return contract


def assert_contract_invariants(contract: Mapping[str, Any]) -> None:
    _require(isinstance(contract, Mapping), "lifecycle contract must be a mapping")
    _require(contract.get("state") in LIFECYCLE_STATES, "unknown lifecycle state")
    authority = contract.get("authority")
    _require(isinstance(authority, Mapping), "authority membrane missing")
    for key, expected in AUTHORITY_CLOSED.items():
        _require(authority.get(key) is expected, f"authority invariant violated: {key}")
    _require(contract.get("builder_self_authorization_path") is False, "builder self-authorization path opened")
    _require(contract.get("outcome_accessed") is False, "D0 outcome access is forbidden")
    _require(contract.get("economic_result") == "NOT_OBSERVED", "D0 cannot carry an economic result")
    observation = contract.get("prospective_observation_identity")
    _require(isinstance(observation, Mapping), "prospective observation identity missing")
    _require(observation.get("observation_started") is False, "D0 cannot start prospective observation")
    _require(observation.get("future_outcomes_consumed") == 0, "D0 cannot consume future outcomes")
    _require(observation.get("activation_receipt_ref") is None, "D0 cannot mint an activation receipt")
    _require(observation.get("start_boundary") == "UNBOUND_UNTIL_EXTERNAL_AUTHORITY",
             "D0 cannot bind an observation start boundary")
    _require(contract.get("review_policy", {}).get("scheduler_owned") is False, "D0 cannot own review scheduling")
    _require(contract.get("review_policy", {}).get("automatic_wake_authorized") is False,
             "D0 cannot authorize automatic wake")


def request_self_authorization(contract: Mapping[str, Any], *_: Any, **__: Any) -> None:
    """Explicit negative capability: Builder/D0 can never grant authority."""
    assert_contract_invariants(contract)
    raise PermissionError("OWNER_AUTHORITY_REQUIRED:D0_SELF_AUTHORIZATION_FORBIDDEN")


def classify_decay_evidence(contract: Mapping[str, Any], evidence_ref: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Validate an outcome-blind evidence reference for lifecycle review."""
    assert_contract_invariants(contract)
    if evidence_ref is None:
        return {
            "status": "UNKNOWN",
            "reason": "NO_ADMISSIBLE_EVIDENCE_REF",
            "outcome_accessed": False,
            "decay_conclusion": "UNKNOWN",
        }
    if not isinstance(evidence_ref, Mapping):
        return {
            "status": "BLOCKED",
            "reason": "EVIDENCE_REF_NOT_A_MAPPING",
            "outcome_accessed": False,
            "decay_conclusion": "UNKNOWN",
        }
    evidence = deepcopy(dict(evidence_ref))
    forbidden = _deep_forbidden_keys(evidence)
    if forbidden:
        return {
            "status": "BLOCKED",
            "reason": "RAW_OUTCOME_PAYLOAD_FORBIDDEN",
            "forbidden_keys": forbidden,
            "outcome_accessed": False,
            "decay_conclusion": "UNKNOWN",
        }

    reasons: List[str] = []
    if evidence.get("lifecycle_contract_id") != contract.get("contract_id"):
        reasons.append("LIFECYCLE_CONTRACT_BINDING_MISMATCH")
    observation = contract["prospective_observation_identity"]
    if evidence.get("prospective_identity_hash") != observation.get("identity_hash"):
        reasons.append("PROSPECTIVE_IDENTITY_BINDING_MISMATCH")
    if evidence.get("evidence_class") not in EVIDENCE_CLASSES:
        reasons.append("EVIDENCE_CLASS_INVALID")
    if evidence.get("scientific_disposition") not in REVIEW_DISPOSITIONS:
        reasons.append("SCIENTIFIC_DISPOSITION_INVALID")
    if evidence.get("observed_under_authority") is not True:
        reasons.append("EXTERNAL_OBSERVATION_AUTHORITY_NOT_PROVEN")
    if not _known_string(evidence.get("authority_receipt_ref")):
        reasons.append("AUTHORITY_RECEIPT_REF_MISSING")
    if not _known_string(evidence.get("evidence_id")):
        reasons.append("EVIDENCE_ID_MISSING")
    if not _known_string(evidence.get("evidence_hash")):
        reasons.append("EVIDENCE_HASH_MISSING")
    source_refs = evidence.get("source_refs")
    if not isinstance(source_refs, list) or not source_refs or not all(_known_string(x) for x in source_refs):
        reasons.append("SOURCE_REFS_MISSING")
    if evidence.get("outcome_payload_included") is not False:
        reasons.append("OUTCOME_PAYLOAD_MUST_BE_ABSENT")

    negative = evidence.get("negative_knowledge", [])
    if not isinstance(negative, list):
        reasons.append("NEGATIVE_KNOWLEDGE_MUST_BE_LIST")
    else:
        for item in negative:
            if not isinstance(item, Mapping):
                reasons.append("NEGATIVE_KNOWLEDGE_ENTRY_INVALID")
                continue
            if item.get("scope_kind") not in REPLACEMENT_DISTINCTIONS - {"UNKNOWN"}:
                reasons.append("NEGATIVE_KNOWLEDGE_SCOPE_INVALID")
            if not _known_string(item.get("knowledge_id")):
                reasons.append("NEGATIVE_KNOWLEDGE_ID_MISSING")
            if item.get("global", False) is not False:
                reasons.append("GLOBAL_NEGATIVE_KNOWLEDGE_FORBIDDEN")

    if reasons:
        return {
            "status": "BLOCKED",
            "reason": "EVIDENCE_REF_NOT_ADMISSIBLE",
            "blockers": sorted(set(reasons)),
            "outcome_accessed": False,
            "decay_conclusion": "UNKNOWN",
        }
    return {
        "status": "ADMISSIBLE_REFERENCE_ONLY",
        "evidence_id": evidence["evidence_id"],
        "evidence_hash": evidence["evidence_hash"],
        "evidence_class": evidence["evidence_class"],
        "scientific_disposition": evidence["scientific_disposition"],
        "source_refs": sorted(set(evidence["source_refs"])),
        "authority_receipt_ref": evidence["authority_receipt_ref"],
        "negative_knowledge": deepcopy(negative),
        "outcome_accessed": False,
        "decay_conclusion": "NOT_COMPUTED_BY_D0",
    }


def apply_review(contract: Mapping[str, Any], evidence_ref: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Apply one bounded lifecycle disposition from an admissible evidence ref."""
    assert_contract_invariants(contract)
    before = deepcopy(dict(contract))
    classified = classify_decay_evidence(before, evidence_ref)
    result = deepcopy(before)

    if classified["status"] == "UNKNOWN":
        result["state"] = "REVIEW_REQUIRED" if before["state"] not in {"RETIRED", "SUPERSEDED"} else before["state"]
        result["status_class"] = "BLOCKED" if result["state"] == "REVIEW_REQUIRED" else before["status_class"]
        review = {
            "review_status": "UNKNOWN",
            "evidence_status": classified["status"],
            "reason": classified["reason"],
            "state_before": before["state"],
            "state_after": result["state"],
            "outcome_accessed": False,
        }
    elif classified["status"] == "BLOCKED":
        result["state"] = "REVIEW_REQUIRED" if before["state"] not in {"RETIRED", "SUPERSEDED"} else before["state"]
        result["status_class"] = "BLOCKED" if result["state"] == "REVIEW_REQUIRED" else before["status_class"]
        review = {
            "review_status": "BLOCKED",
            "evidence_status": classified["status"],
            "reason": classified["reason"],
            "blockers": deepcopy(classified.get("blockers", [])),
            "state_before": before["state"],
            "state_after": result["state"],
            "outcome_accessed": False,
        }
    else:
        disposition = classified["scientific_disposition"]
        if before["state"] in {"RETIRED", "SUPERSEDED"}:
            raise EconomicLifecycleError(f"terminal lifecycle state cannot be reviewed: {before['state']}")
        target = {
            "CONTINUE": "READY_AWAITING_OWNER_AUTHORITY",
            "RESIZE": "RESIZE_ELIGIBLE",
            "PARK": "PARKED",
            "RETIRE": "RETIRED",
            "REPLACE": "REPLACEMENT_REQUIRED",
            "INCONCLUSIVE": "REVIEW_REQUIRED",
        }[disposition]
        if disposition in {"CONTINUE", "RESIZE"} and not result["portfolio_readiness_ref"]["current_clearance"]:
            target = "BLOCKED_BY_UPSTREAM_READINESS"
        result["state"] = target
        result["status_class"] = "READY" if target in {"READY_AWAITING_OWNER_AUTHORITY", "RESIZE_ELIGIBLE"} else "BLOCKED"
        for item in classified.get("negative_knowledge", []):
            if item not in result["negative_knowledge"]:
                result["negative_knowledge"].append(deepcopy(item))
        review = {
            "review_status": "APPLIED",
            "evidence_status": classified["status"],
            "evidence_id": classified["evidence_id"],
            "evidence_hash": classified["evidence_hash"],
            "evidence_class": classified["evidence_class"],
            "scientific_disposition": disposition,
            "state_before": before["state"],
            "state_after": target,
            "outcome_accessed": False,
            "resize_is_authority": False,
        }
    result["review_history"] = list(result.get("review_history", [])) + [review]
    result["contract_hash"] = _hash({k: v for k, v in result.items() if k != "contract_hash"})
    assert_contract_invariants(result)
    return result


def _transferrable_negative_knowledge(records: Sequence[Mapping[str, Any]], distinction: str) -> Dict[str, Any]:
    transferred: List[Dict[str, Any]] = []
    withheld: List[str] = []
    for record in records:
        knowledge_id = str(record.get("knowledge_id", "UNKNOWN"))
        scope = record.get("scope_kind")
        global_flag = record.get("global", False)
        if global_flag is False and scope in {distinction, "MIXED"}:
            transferred.append(deepcopy(dict(record)))
        else:
            withheld.append(knowledge_id)
    return {"transferred": transferred, "withheld_ids": sorted(set(withheld))}


def supersede_with_replacement(
    predecessor: Mapping[str, Any],
    successor_structural_identity: Mapping[str, Any],
    successor_portfolio_diagnostics: Mapping[str, Any],
    *,
    successor_protocol_ref: Any,
    reason_ref: str,
    distinction: str,
    trigger_evidence_ref: Mapping[str, Any],
    review_policy: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a successor while preserving explicit, scoped ancestry."""
    assert_contract_invariants(predecessor)
    _require(predecessor.get("state") == "REPLACEMENT_REQUIRED",
             "replacement requires predecessor state REPLACEMENT_REQUIRED")
    _require(_known_string(reason_ref), "replacement reason_ref is required")
    _require(distinction in REPLACEMENT_DISTINCTIONS, "replacement distinction is invalid")
    classified = classify_decay_evidence(predecessor, trigger_evidence_ref)
    _require(classified.get("status") == "ADMISSIBLE_REFERENCE_ONLY", "replacement trigger evidence is not admissible")
    _require(classified.get("scientific_disposition") == "REPLACE", "replacement trigger must carry REPLACE disposition")

    successor = create_shadow_contract(
        successor_structural_identity,
        successor_portfolio_diagnostics,
        protocol_ref=successor_protocol_ref,
        review_policy=review_policy or predecessor.get("review_policy"),
        predecessor_contract_id=predecessor["contract_id"],
        lifecycle_version=predecessor.get("lifecycle_version", 1) + 1,
        replacement_reason_ref=reason_ref,
    )
    unchanged_identity = successor["economic_identity_ref"]["ref_hash"] == predecessor["economic_identity_ref"]["ref_hash"]
    unchanged_protocol = successor["protocol_ref"]["ref_hash"] == predecessor["protocol_ref"]["ref_hash"]
    _require(not (unchanged_identity and unchanged_protocol),
             "replacement must change economic identity or protocol implementation")
    _require(
        successor["prospective_observation_identity"]["identity_hash"]
        != predecessor["prospective_observation_identity"]["identity_hash"],
        "replacement cannot reuse predecessor prospective identity",
    )

    transfer = _transferrable_negative_knowledge(predecessor.get("negative_knowledge", []), distinction)
    successor["negative_knowledge"] = transfer["transferred"]
    predecessor_update = deepcopy(dict(predecessor))
    predecessor_update["state"] = "SUPERSEDED"
    predecessor_update["status_class"] = "BLOCKED"
    predecessor_update["lineage"] = deepcopy(predecessor_update.get("lineage", {}))
    predecessor_update["lineage"].update({
        "successor_contract_id": successor["contract_id"],
        "replacement_reason_ref": reason_ref,
        "superseded": True,
    })
    predecessor_update["contract_hash"] = _hash({k: v for k, v in predecessor_update.items() if k != "contract_hash"})

    lineage = {
        "lineage_type": "EconomicLifecycleReplacementLineage.v1",
        "predecessor_contract_id": predecessor["contract_id"],
        "successor_contract_id": successor["contract_id"],
        "reason_ref": reason_ref,
        "trigger_evidence_id": classified["evidence_id"],
        "trigger_evidence_class": classified["evidence_class"],
        "mechanism_wrapper_implementation_distinction": distinction,
        "transferred_negative_knowledge_ids": sorted(
            record["knowledge_id"] for record in transfer["transferred"]
        ),
        "withheld_negative_knowledge_ids": transfer["withheld_ids"],
        "global_negative_knowledge_transfer": False,
        "outcome_accessed": False,
    }
    lineage["lineage_hash"] = _hash(lineage)
    successor["lineage"] = {
        "predecessor_contract_id": predecessor["contract_id"],
        "successor_contract_id": None,
        "replacement_reason_ref": reason_ref,
        "replacement_lineage_hash": lineage["lineage_hash"],
        "superseded": False,
    }
    successor["contract_hash"] = _hash({k: v for k, v in successor.items() if k != "contract_hash"})
    assert_contract_invariants(predecessor_update)
    assert_contract_invariants(successor)
    return {
        "predecessor": predecessor_update,
        "successor": successor,
        "lineage": lineage,
        "outcome_accessed": False,
        "authority": deepcopy(AUTHORITY_CLOSED),
    }


def rebind_material_change(
    contract: Mapping[str, Any],
    *,
    protocol_ref: Any,
    change_class: str,
    reason_ref: str,
) -> Dict[str, Any]:
    """Material changes always receive a fresh version/observation identity."""
    assert_contract_invariants(contract)
    _require(change_class in {"WRAPPER", "IMPLEMENTATION", "MECHANISM", "MIXED"}, "material change class invalid")
    _require(_known_string(reason_ref), "material change reason_ref is required")

    identity_ref = contract["economic_identity_ref"]
    compact_identity = {
        "hypothesis_id": identity_ref["hypothesis_id"],
        "generation_id": identity_ref["generation_id"],
        "identity_hash": identity_ref["identity_hash"],
        "candidate_binding": {"status": "BOUND", "candidate_hash": identity_ref["candidate_hash"]},
        "identity_readiness": deepcopy(identity_ref.get("identity_readiness", {})),
    }
    readiness_ref = contract["portfolio_readiness_ref"]
    compact_portfolio = {"portfolio_readiness": deepcopy(readiness_ref["readiness"])}
    successor = create_shadow_contract(
        compact_identity,
        compact_portfolio,
        protocol_ref=protocol_ref,
        review_policy=contract.get("review_policy"),
        predecessor_contract_id=contract["contract_id"],
        lifecycle_version=contract.get("lifecycle_version", 1) + 1,
        replacement_reason_ref=reason_ref,
    )
    _require(successor["protocol_ref"]["ref_hash"] != contract["protocol_ref"]["ref_hash"],
             "material change requires a changed protocol ref")
    _require(
        successor["prospective_observation_identity"]["identity_hash"]
        != contract["prospective_observation_identity"]["identity_hash"],
        "material change failed to create a fresh prospective identity",
    )
    return {
        "predecessor_contract_id": contract["contract_id"],
        "successor": successor,
        "change_class": change_class,
        "reason_ref": reason_ref,
        "old_prospective_identity_hash": contract["prospective_observation_identity"]["identity_hash"],
        "new_prospective_identity_hash": successor["prospective_observation_identity"]["identity_hash"],
        "outcome_accessed": False,
    }
