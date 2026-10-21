"""Pre-outcome economic lifecycle contracts for MEGA D0.

This module starts strictly downstream of the qualified W1 Economic boundary.
It consumes references to canonical Economic Identity and Portfolio Readiness
products, never rebuilds their semantics, and never grants authority.

Future evidence may enter only as an opaque, externally qualified reference.
D0 never reads PnL, returns, alpha, Sharpe, empirical correlation, or any
outcome-bearing payload.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.portfolio_v2 import structural_identity


WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
W1_ECON_CODE_QUALIFIED_SHA = "73f99bf7ec504b217463f5435700887994e5ec5f"
W1_ECON_DOCUMENTARY_FINAL_SHA = "83bb495104acf7de8617593bc737a8a204c99b32"

AUTHORITY_STATE = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
}

LIFECYCLE_STATES = {
    "BOUND_PRE_OUTCOME",
    "BLOCKED_BY_UPSTREAM_READINESS",
    "SHADOW_READY_AWAITING_AUTHORITY",
    "PARKED",
    "RETIRED",
    "SUPERSEDED",
}
REVIEW_DISPOSITIONS = {"HOLD", "RESIZE_ELIGIBLE", "PARK", "RETIRE", "REPLACE"}
DECAY_EVIDENCE_KINDS = {
    "REGIME_MISMATCH",
    "IMPLEMENTATION_DEGRADATION",
    "COST_CAPACITY_DETERIORATION",
    "EDGE_DECAY",
}
EVIDENCE_ADMISSIBILITY = {"INSUFFICIENT", "CONFLICTED", "ADMISSIBLE_EXTERNAL_EVALUATOR"}
REPLACEMENT_KINDS = {"NEW_MECHANISM", "NEW_WRAPPER", "IMPLEMENTATION_REVISION"}
NEGATIVE_KNOWLEDGE_SCOPES = {
    "NOT_TRANSFERRED",
    "PREDECESSOR_IDENTITY_ONLY",
    "EXPLICIT_MECHANISM_SCOPE",
    "EXPLICIT_IMPLEMENTATION_SCOPE",
}
FORBIDDEN_OUTCOME_KEYS = {
    "pnl", "profit", "profitability", "return", "returns", "sharpe", "alpha",
    "covariance", "empirical_correlation", "realized_pnl", "realized_return",
    "outcome", "outcomes",
}


def authority_state() -> Dict[str, bool]:
    return dict(AUTHORITY_STATE)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _require_nonempty(value: Any, name: str) -> str:
    if not _nonempty(value):
        raise ValueError(f"{name} must be a non-empty string")
    return str(value).strip()


def _is_hex(value: Any, length: int) -> bool:
    if not isinstance(value, str) or len(value) != length:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return value.lower() == value


def _require_hash(value: Any, name: str, lengths: Sequence[int] = (64,)) -> str:
    if any(_is_hex(value, length) for length in lengths):
        return str(value)
    raise ValueError(f"{name} must be lowercase hex of length {tuple(lengths)}")


def _validate_authority_closed(mapping: Mapping[str, Any], *, prefix: str = "") -> None:
    closed = {
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "outcome_accessed": False,
        "return_series_consumed": False,
        "capital_allocation_authorized": False,
        "position_sizing_authorized": False,
        "orders_authorized": False,
        "portfolio_optimization_authorized": False,
    }
    for key, required in closed.items():
        if key in mapping and mapping[key] is not required:
            raise ValueError(f"{prefix}{key} must remain {required}")


def _reject_outcome_payload(value: Any, *, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).strip().lower() in FORBIDDEN_OUTCOME_KEYS:
                raise ValueError(f"{path}.{key} is outcome-bearing and forbidden in D0")
            _reject_outcome_payload(item, path=f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_outcome_payload(item, path=f"{path}[{index}]")


def bind_economic_identity_ref(identity: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind W1 ECON's canonical structural identity; do not reproduce it."""
    if not isinstance(identity, Mapping):
        raise ValueError("economic identity input must be a mapping")
    projection = structural_identity(deepcopy(dict(identity)))
    binding = projection.get("candidate_binding") or {}
    if binding.get("status") != "BOUND":
        raise ValueError("economic identity must have a verified candidate binding")

    ref = {
        "schema_version": "economic-identity-ref-v1",
        "hypothesis_id": _require_nonempty(projection.get("hypothesis_id"), "hypothesis_id"),
        "generation_id": _require_nonempty(projection.get("generation_id"), "generation_id"),
        "candidate_hash": _require_hash(binding.get("candidate_hash"), "candidate_hash"),
        "identity_hash": _require_hash(projection.get("identity_hash"), "identity_hash"),
        "identity_readiness_status": projection["identity_readiness"]["status"],
        "identity_readiness_blockers": deepcopy(projection["identity_readiness"]["blockers"]),
        "upstream_contract": "research.research_os.expansion.portfolio_v2.structural_identity",
        "w1_econ_code_qualified_sha": W1_ECON_CODE_QUALIFIED_SHA,
        "w1_econ_documentary_final_sha": W1_ECON_DOCUMENTARY_FINAL_SHA,
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
        "empirical_return_data_consumed": False,
        "outcome_accessed": False,
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_economic_identity_ref(ref: Mapping[str, Any]) -> None:
    if not isinstance(ref, Mapping) or ref.get("schema_version") != "economic-identity-ref-v1":
        raise ValueError("unsupported EconomicIdentityRef schema")
    _require_nonempty(ref.get("hypothesis_id"), "hypothesis_id")
    _require_nonempty(ref.get("generation_id"), "generation_id")
    _require_hash(ref.get("candidate_hash"), "candidate_hash")
    _require_hash(ref.get("identity_hash"), "identity_hash")
    _require_hash(ref.get("ref_hash"), "ref_hash")
    if ref.get("w1_econ_code_qualified_sha") != W1_ECON_CODE_QUALIFIED_SHA:
        raise ValueError("EconomicIdentityRef does not point to qualified W1 ECON code")
    if ref.get("wave2_base_sha") != WAVE2_IMMUTABLE_BASE_SHA:
        raise ValueError("EconomicIdentityRef does not point to the immutable Wave2 base")
    _validate_authority_closed(ref, prefix="EconomicIdentityRef.")
    payload = deepcopy(dict(ref))
    declared = payload.pop("ref_hash")
    if sha256_json(payload) != declared:
        raise ValueError("EconomicIdentityRef hash mismatch")


def bind_portfolio_readiness_ref(
    diagnostics: Mapping[str, Any], economic_identity_ref: Mapping[str, Any]
) -> Dict[str, Any]:
    """Bind W1 ECON readiness without reproducing its portfolio logic."""
    validate_economic_identity_ref(economic_identity_ref)
    if not isinstance(diagnostics, Mapping) or diagnostics.get("portfolio_engine") != "portfolio-diagnostics.v2":
        raise ValueError("PortfolioReadinessRef requires canonical portfolio-diagnostics.v2")
    _validate_authority_closed(diagnostics, prefix="portfolio.")
    if diagnostics.get("return_series_consumed") is not False:
        raise ValueError("portfolio readiness consumed return series")
    readiness = diagnostics.get("portfolio_readiness")
    if not isinstance(readiness, Mapping):
        raise ValueError("portfolio diagnostics missing portfolio_readiness")
    empirical = readiness.get("empirical_layer")
    if not isinstance(empirical, Mapping) or empirical.get("status") != "SEALED_BY_AUTHORITY":
        raise ValueError("portfolio empirical layer must remain SEALED_BY_AUTHORITY")
    if empirical.get("requirements_do_not_grant_authority") is not True:
        raise ValueError("portfolio empirical requirements must not grant authority")

    matching = [
        item for item in diagnostics.get("structural_identities", [])
        if item.get("hypothesis_id") == economic_identity_ref["hypothesis_id"]
        and item.get("generation_id") == economic_identity_ref["generation_id"]
    ]
    if len(matching) != 1:
        raise ValueError("portfolio readiness must contain exactly one matching structural identity")
    projection = matching[0]
    if projection.get("identity_hash") != economic_identity_ref["identity_hash"]:
        raise ValueError("portfolio readiness identity hash mismatch")
    if (projection.get("candidate_binding") or {}).get("candidate_hash") != economic_identity_ref["candidate_hash"]:
        raise ValueError("portfolio readiness candidate hash mismatch")

    ref = {
        "schema_version": "portfolio-readiness-ref-v1",
        "hypothesis_id": economic_identity_ref["hypothesis_id"],
        "generation_id": economic_identity_ref["generation_id"],
        "economic_identity_ref_hash": economic_identity_ref["ref_hash"],
        "identity_hash": economic_identity_ref["identity_hash"],
        "candidate_hash": economic_identity_ref["candidate_hash"],
        "structural_mapping_status": readiness["structural_mapping"]["status"],
        "structural_mapping_blockers": deepcopy(readiness["structural_mapping"]["blockers"]),
        "pre_outcome_decision_status": readiness["pre_outcome_decision"]["status"],
        "pre_outcome_decision_blockers": deepcopy(readiness["pre_outcome_decision"]["blockers"]),
        "empirical_layer_status": empirical["status"],
        "portfolio_readiness_hash": sha256_json(readiness),
        "upstream_contract": "research.research_os.expansion.portfolio_v2.portfolio_diagnostics_v2",
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
        "return_series_consumed": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "outcome_accessed": False,
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_portfolio_readiness_ref(ref: Mapping[str, Any], economic_identity_ref: Mapping[str, Any]) -> None:
    validate_economic_identity_ref(economic_identity_ref)
    if not isinstance(ref, Mapping) or ref.get("schema_version") != "portfolio-readiness-ref-v1":
        raise ValueError("unsupported PortfolioReadinessRef schema")
    if ref.get("economic_identity_ref_hash") != economic_identity_ref["ref_hash"]:
        raise ValueError("PortfolioReadinessRef economic identity binding mismatch")
    for key in ("hypothesis_id", "generation_id", "identity_hash", "candidate_hash"):
        if ref.get(key) != economic_identity_ref[key]:
            raise ValueError(f"PortfolioReadinessRef {key} mismatch")
    if ref.get("empirical_layer_status") != "SEALED_BY_AUTHORITY":
        raise ValueError("PortfolioReadinessRef empirical layer must remain sealed")
    if ref.get("wave2_base_sha") != WAVE2_IMMUTABLE_BASE_SHA:
        raise ValueError("PortfolioReadinessRef does not point to immutable Wave2 base")
    _validate_authority_closed(ref, prefix="PortfolioReadinessRef.")
    _require_hash(ref.get("portfolio_readiness_hash"), "portfolio_readiness_hash")
    payload = deepcopy(dict(ref))
    declared = payload.pop("ref_hash", None)
    _require_hash(declared, "ref_hash")
    if sha256_json(payload) != declared:
        raise ValueError("PortfolioReadinessRef hash mismatch")


def normalize_review_policy(policy: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(policy, Mapping):
        raise ValueError("review policy must be a mapping")
    allowed = {
        "policy_id", "policy_version", "cadence_kind", "review_interval",
        "minimum_admissible_observations", "minimum_distinct_review_windows",
        "regime_context_required", "implementation_context_required",
        "cost_capacity_context_required", "scheduler_owned_by_d0", "policy_hash",
    }
    extra = sorted(set(policy) - allowed)
    if extra:
        raise ValueError(f"unsupported review policy fields: {', '.join(extra)}")
    cadence_kind = policy.get("cadence_kind")
    if cadence_kind not in {"CALENDAR", "OBSERVATION_COUNT", "HYBRID"}:
        raise ValueError("invalid review cadence_kind")
    review_interval = policy.get("review_interval")
    minimum = policy.get("minimum_admissible_observations")
    windows = policy.get("minimum_distinct_review_windows", 1)
    for name, value in (
        ("review_interval", review_interval),
        ("minimum_admissible_observations", minimum),
        ("minimum_distinct_review_windows", windows),
    ):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    normalized = {
        "policy_id": _require_nonempty(policy.get("policy_id"), "policy_id"),
        "policy_version": _require_nonempty(policy.get("policy_version"), "policy_version"),
        "cadence_kind": cadence_kind,
        "review_interval": review_interval,
        "minimum_admissible_observations": minimum,
        "minimum_distinct_review_windows": windows,
        "regime_context_required": policy.get("regime_context_required") is not False,
        "implementation_context_required": policy.get("implementation_context_required") is not False,
        "cost_capacity_context_required": policy.get("cost_capacity_context_required") is not False,
        "scheduler_owned_by_d0": False,
    }
    expected_hash = sha256_json(normalized)
    declared_hash = policy.get("policy_hash")
    if declared_hash is not None and declared_hash != expected_hash:
        raise ValueError("review policy hash mismatch")
    if "scheduler_owned_by_d0" in policy and policy.get("scheduler_owned_by_d0") is not False:
        raise ValueError("review policy must not grant scheduler ownership to D0")
    normalized["policy_hash"] = expected_hash
    return normalized


def decay_evidence_contract(review_policy: Mapping[str, Any]) -> Dict[str, Any]:
    policy = normalize_review_policy(review_policy)
    return {
        "schema_version": "decay-evidence-contract-v1",
        "review_policy_hash": policy["policy_hash"],
        "minimum_admissible_observations": policy["minimum_admissible_observations"],
        "minimum_distinct_review_windows": policy["minimum_distinct_review_windows"],
        "required_context": {
            "regime": policy["regime_context_required"],
            "implementation": policy["implementation_context_required"],
            "cost_capacity": policy["cost_capacity_context_required"],
        },
        "accepted_evidence_kinds": sorted(DECAY_EVIDENCE_KINDS),
        "external_evaluator_required": True,
        "raw_outcomes_accepted_by_d0": False,
        "insufficient_evidence_is_negative": False,
        "regime_mismatch_is_decay": False,
        "implementation_degradation_is_edge_decay": False,
        "cost_capacity_deterioration_is_edge_decay": False,
        "outcome_accessed": False,
    }


def create_shadow_contract(
    economic_identity_ref: Mapping[str, Any],
    portfolio_readiness_ref: Mapping[str, Any],
    *,
    prospective_start_boundary: str,
    implementation_version: str,
    review_policy: Mapping[str, Any],
    contract_version: str = "economic-lifecycle-v1",
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an immutable contract, never a book of positions/orders/PnL."""
    validate_economic_identity_ref(economic_identity_ref)
    validate_portfolio_readiness_ref(portfolio_readiness_ref, economic_identity_ref)
    start = _require_nonempty(prospective_start_boundary, "prospective_start_boundary")
    implementation = _require_nonempty(implementation_version, "implementation_version")
    version = _require_nonempty(contract_version, "contract_version")
    user_metadata = deepcopy(dict(metadata or {}))
    _reject_outcome_payload(user_metadata, path="metadata")
    policy = normalize_review_policy(review_policy)
    evidence_contract = decay_evidence_contract(policy)

    upstream_ready = (
        economic_identity_ref["identity_readiness_status"] == "QUALIFIED_CURRENT"
        and portfolio_readiness_ref["structural_mapping_status"] == "QUALIFIED_CURRENT"
        and portfolio_readiness_ref["pre_outcome_decision_status"] == "QUALIFIED_CURRENT"
    )
    initial_state = "SHADOW_READY_AWAITING_AUTHORITY" if upstream_ready else "BLOCKED_BY_UPSTREAM_READINESS"
    immutable_core = {
        "contract_version": version,
        "economic_identity_ref": deepcopy(dict(economic_identity_ref)),
        "portfolio_readiness_ref": deepcopy(dict(portfolio_readiness_ref)),
        "prospective_start_boundary": start,
        "implementation_version": implementation,
        "review_policy": policy,
        "decay_evidence_contract": evidence_contract,
        "metadata": user_metadata,
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
    }
    contract_id = "SHADOW-" + sha256_json(immutable_core)[:24]
    observation_identity_payload = {
        "contract_id": contract_id,
        "economic_identity_ref_hash": economic_identity_ref["ref_hash"],
        "portfolio_readiness_ref_hash": portfolio_readiness_ref["ref_hash"],
        "prospective_start_boundary": start,
        "implementation_version": implementation,
        "review_policy_hash": policy["policy_hash"],
        "contract_version": version,
    }
    contract = {
        "schema_version": "shadow-prospective-contract-v1",
        "contract_id": contract_id,
        "immutable_core": immutable_core,
        "immutable_core_hash": sha256_json(immutable_core),
        "observation_identity": sha256_json(observation_identity_payload),
        "initial_lifecycle_state": initial_state,
        "readiness": "READY_AWAITING_EXTERNAL_AUTHORITY" if upstream_ready else "BLOCKED_BY_UPSTREAM_READINESS",
        "shadow_status_implies_profitability": False,
        "profitability_status": "UNKNOWN",
        "material_change_requires_new_contract": True,
        "retrospective_rewrite_permitted": False,
        "future_evaluation_must_bind_observation_identity": True,
        "scheduler_owned_by_d0": False,
        "runtime_owned_by_d0": False,
        "real_trading_owned_by_d0": False,
        "observation_started": False,
        "future_observations_consumed": 0,
        **authority_state(),
    }
    contract["contract_hash"] = sha256_json(contract)
    return contract


def validate_shadow_contract(contract: Mapping[str, Any]) -> None:
    if not isinstance(contract, Mapping) or contract.get("schema_version") != "shadow-prospective-contract-v1":
        raise ValueError("unsupported shadow contract schema")
    if contract.get("initial_lifecycle_state") not in LIFECYCLE_STATES:
        raise ValueError("invalid initial lifecycle state")
    if contract.get("shadow_status_implies_profitability") is not False:
        raise ValueError("shadow status must never imply profitability")
    if contract.get("profitability_status") != "UNKNOWN":
        raise ValueError("pre-outcome profitability must remain UNKNOWN")
    if contract.get("retrospective_rewrite_permitted") is not False:
        raise ValueError("retrospective rewriting is forbidden")
    if contract.get("material_change_requires_new_contract") is not True:
        raise ValueError("material changes must require a new contract")
    if contract.get("observation_started") is not False or contract.get("future_observations_consumed") != 0:
        raise ValueError("D0 may not start or consume prospective observations")
    _validate_authority_closed(contract, prefix="shadow.")
    core = contract.get("immutable_core")
    if not isinstance(core, Mapping) or sha256_json(core) != contract.get("immutable_core_hash"):
        raise ValueError("shadow immutable core hash mismatch")
    identity_ref = core.get("economic_identity_ref")
    readiness_ref = core.get("portfolio_readiness_ref")
    validate_economic_identity_ref(identity_ref)
    validate_portfolio_readiness_ref(readiness_ref, identity_ref)
    policy = normalize_review_policy(core.get("review_policy", {}))
    if policy != core.get("review_policy"):
        raise ValueError("review policy is not canonical")
    _reject_outcome_payload(core.get("metadata", {}), path="metadata")
    observation_payload = {
        "contract_id": contract.get("contract_id"),
        "economic_identity_ref_hash": identity_ref["ref_hash"],
        "portfolio_readiness_ref_hash": readiness_ref["ref_hash"],
        "prospective_start_boundary": core.get("prospective_start_boundary"),
        "implementation_version": core.get("implementation_version"),
        "review_policy_hash": policy["policy_hash"],
        "contract_version": core.get("contract_version"),
    }
    if sha256_json(observation_payload) != contract.get("observation_identity"):
        raise ValueError("observation identity mismatch")
    payload = deepcopy(dict(contract))
    declared = payload.pop("contract_hash", None)
    _require_hash(declared, "contract_hash")
    if sha256_json(payload) != declared:
        raise ValueError("shadow contract hash mismatch")


def initial_lifecycle_state(contract: Mapping[str, Any]) -> Dict[str, Any]:
    validate_shadow_contract(contract)
    state = {
        "schema_version": "economic-lifecycle-state-v1",
        "contract_id": contract["contract_id"],
        "contract_hash": contract["contract_hash"],
        "observation_identity": contract["observation_identity"],
        "current_state": contract["initial_lifecycle_state"],
        "transition_history": [],
        "last_event_hash": None,
        "review_disposition": "HOLD",
        "decay_claim_status": "UNEXECUTED",
        "profitability_status": "UNKNOWN",
        "observation_started": False,
        "future_observations_consumed": 0,
        **authority_state(),
    }
    state["state_hash"] = sha256_json(state)
    return state


def validate_lifecycle_state(state: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    validate_shadow_contract(contract)
    if not isinstance(state, Mapping) or state.get("schema_version") != "economic-lifecycle-state-v1":
        raise ValueError("unsupported lifecycle state schema")
    if state.get("contract_id") != contract["contract_id"] or state.get("contract_hash") != contract["contract_hash"]:
        raise ValueError("lifecycle state contract binding mismatch")
    if state.get("observation_identity") != contract["observation_identity"]:
        raise ValueError("lifecycle state observation identity mismatch")
    if state.get("current_state") not in LIFECYCLE_STATES:
        raise ValueError("invalid lifecycle state")
    if state.get("review_disposition") not in REVIEW_DISPOSITIONS:
        raise ValueError("invalid lifecycle review disposition")
    if state.get("profitability_status") != "UNKNOWN":
        raise ValueError("lifecycle state may not infer profitability")
    if state.get("observation_started") is not False or state.get("future_observations_consumed") != 0:
        raise ValueError("D0 lifecycle may not start or consume observations")
    _validate_authority_closed(state, prefix="lifecycle.")
    history = state.get("transition_history")
    if not isinstance(history, list):
        raise ValueError("transition_history must be a list")
    previous = None
    for event in history:
        if event.get("previous_event_hash") != previous:
            raise ValueError("transition history hash chain broken")
        payload = deepcopy(dict(event))
        declared = payload.pop("event_hash", None)
        if sha256_json(payload) != declared:
            raise ValueError("transition event hash mismatch")
        previous = declared
    if state.get("last_event_hash") != previous:
        raise ValueError("last_event_hash mismatch")
    payload = deepcopy(dict(state))
    declared = payload.pop("state_hash", None)
    _require_hash(declared, "state_hash")
    if sha256_json(payload) != declared:
        raise ValueError("lifecycle state hash mismatch")


def validate_decay_evidence_ref(evidence_ref: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    """Validate an opaque ref; underlying outcome payload is never accepted."""
    validate_shadow_contract(contract)
    if not isinstance(evidence_ref, Mapping):
        raise ValueError("decay evidence ref must be a mapping")
    allowed = {
        "schema_version", "evidence_ref_id", "evidence_kind", "admissibility",
        "observation_identity", "evaluation_protocol_hash", "evidence_hash",
        "review_window_count", "admissible_observation_count", "reason_codes",
        "scope", "outcome_accessed_by_d0", "raw_outcomes_included", "ref_hash",
    }
    extra = sorted(set(evidence_ref) - allowed)
    if extra:
        raise ValueError(f"unsupported decay evidence ref fields: {', '.join(extra)}")
    if evidence_ref.get("schema_version") != "qualified-decay-evidence-ref-v1":
        raise ValueError("unsupported decay evidence ref schema")
    _require_nonempty(evidence_ref.get("evidence_ref_id"), "evidence_ref_id")
    if evidence_ref.get("evidence_kind") not in DECAY_EVIDENCE_KINDS:
        raise ValueError("invalid decay evidence kind")
    if evidence_ref.get("admissibility") not in EVIDENCE_ADMISSIBILITY:
        raise ValueError("invalid evidence admissibility")
    if evidence_ref.get("observation_identity") != contract["observation_identity"]:
        raise ValueError("decay evidence does not bind exact observation identity")
    _require_hash(evidence_ref.get("evaluation_protocol_hash"), "evaluation_protocol_hash")
    _require_hash(evidence_ref.get("evidence_hash"), "evidence_hash")
    if evidence_ref.get("outcome_accessed_by_d0") is not False:
        raise ValueError("D0 must remain outcome-blind")
    if evidence_ref.get("raw_outcomes_included") is not False:
        raise ValueError("raw outcomes are forbidden in D0 evidence refs")
    for name in ("review_window_count", "admissible_observation_count"):
        value = evidence_ref.get(name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    reasons = evidence_ref.get("reason_codes")
    if not isinstance(reasons, list) or not all(_nonempty(item) for item in reasons):
        raise ValueError("reason_codes must be a list of non-empty strings")
    _require_nonempty(evidence_ref.get("scope"), "scope")
    payload = deepcopy(dict(evidence_ref))
    declared = payload.pop("ref_hash", None)
    _require_hash(declared, "ref_hash")
    if sha256_json(payload) != declared:
        raise ValueError("decay evidence ref hash mismatch")


def classify_review_evidence(
    contract: Mapping[str, Any], evidence_ref: Optional[Mapping[str, Any]] = None
) -> Dict[str, Any]:
    validate_shadow_contract(contract)
    policy = contract["immutable_core"]["review_policy"]
    if evidence_ref is None:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "evidence_kind": "NONE",
            "decay_claim_supported": False,
            "negative_claim_supported": False,
            "eligible_actions": ["HOLD", "PARK"],
            "reason_codes": ["NO_QUALIFIED_FUTURE_EVIDENCE_REF"],
            "outcome_accessed": False,
        }
    validate_decay_evidence_ref(evidence_ref, contract)
    sufficient = (
        evidence_ref["admissible_observation_count"] >= policy["minimum_admissible_observations"]
        and evidence_ref["review_window_count"] >= policy["minimum_distinct_review_windows"]
    )
    admissible = evidence_ref["admissibility"] == "ADMISSIBLE_EXTERNAL_EVALUATOR" and sufficient
    kind = evidence_ref["evidence_kind"]
    if not admissible:
        reasons = list(evidence_ref["reason_codes"])
        if not sufficient:
            reasons.append("REVIEW_EVIDENCE_MINIMUM_NOT_MET")
        return {
            "status": "INSUFFICIENT_EVIDENCE", "evidence_kind": kind,
            "decay_claim_supported": False, "negative_claim_supported": False,
            "eligible_actions": ["HOLD", "PARK"],
            "reason_codes": sorted(set(reasons)), "outcome_accessed": False,
        }
    if kind == "REGIME_MISMATCH":
        return {
            "status": "REGIME_MISMATCH", "evidence_kind": kind,
            "decay_claim_supported": False, "negative_claim_supported": False,
            "eligible_actions": ["HOLD", "PARK"],
            "reason_codes": list(evidence_ref["reason_codes"]), "outcome_accessed": False,
        }
    if kind in {"IMPLEMENTATION_DEGRADATION", "COST_CAPACITY_DETERIORATION"}:
        return {
            "status": kind, "evidence_kind": kind,
            "decay_claim_supported": False, "negative_claim_supported": False,
            "eligible_actions": ["HOLD", "RESIZE_ELIGIBLE", "PARK", "RETIRE", "REPLACE"],
            "reason_codes": list(evidence_ref["reason_codes"]), "outcome_accessed": False,
        }
    return {
        "status": "DECAY_EVIDENCE_ADMISSIBLE", "evidence_kind": "EDGE_DECAY",
        "decay_claim_supported": True, "negative_claim_supported": True,
        "eligible_actions": ["HOLD", "RESIZE_ELIGIBLE", "PARK", "RETIRE", "REPLACE"],
        "reason_codes": list(evidence_ref["reason_codes"]), "outcome_accessed": False,
    }


def review_decision(
    contract: Mapping[str, Any], *, requested_disposition: str,
    evidence_ref: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    validate_shadow_contract(contract)
    if requested_disposition not in REVIEW_DISPOSITIONS:
        raise ValueError("invalid requested lifecycle disposition")
    classification = classify_review_evidence(contract, evidence_ref)
    if requested_disposition not in classification["eligible_actions"]:
        raise ValueError(f"{requested_disposition} is not supported by evidence class {classification['status']}")
    decision = {
        "schema_version": "economic-lifecycle-review-decision-v1",
        "contract_id": contract["contract_id"],
        "observation_identity": contract["observation_identity"],
        "requested_disposition": requested_disposition,
        "evidence_classification": classification,
        "decay_claim": bool(classification["decay_claim_supported"]),
        "negative_claim": bool(classification["negative_claim_supported"]),
        "resize_eligibility_only": requested_disposition == "RESIZE_ELIGIBLE",
        "position_sizing_authorized": False,
        "capital_allocation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "outcome_accessed": False,
    }
    decision["decision_hash"] = sha256_json(decision)
    return decision


def apply_review_decision(
    state: Mapping[str, Any], contract: Mapping[str, Any], decision: Mapping[str, Any]
) -> Dict[str, Any]:
    """Apply administrative lifecycle state only; RESIZE_ELIGIBLE is not sizing."""
    validate_lifecycle_state(state, contract)
    if not isinstance(decision, Mapping):
        raise ValueError("review decision must be a mapping")
    if decision.get("contract_id") != contract["contract_id"] or decision.get("observation_identity") != contract["observation_identity"]:
        raise ValueError("review decision contract binding mismatch")
    payload = deepcopy(dict(decision))
    declared = payload.pop("decision_hash", None)
    _require_hash(declared, "decision_hash")
    if sha256_json(payload) != declared:
        raise ValueError("review decision hash mismatch")
    _validate_authority_closed(decision, prefix="review.")
    disposition = decision.get("requested_disposition")
    targets = {
        "HOLD": state["current_state"],
        "RESIZE_ELIGIBLE": state["current_state"],
        "PARK": "PARKED", "RETIRE": "RETIRED", "REPLACE": "SUPERSEDED",
    }
    if disposition not in targets:
        raise ValueError("invalid review disposition")
    current, target = state["current_state"], targets[disposition]
    if current in {"RETIRED", "SUPERSEDED"} and target != current:
        raise ValueError(f"terminal lifecycle state {current} cannot transition to {target}")
    event_payload = {
        "sequence": len(state["transition_history"]) + 1,
        "from_state": current,
        "to_state": target,
        "disposition": disposition,
        "decision_hash": declared,
        "evidence_status": decision["evidence_classification"]["status"],
        "decay_claim": decision["decay_claim"],
        "previous_event_hash": state["last_event_hash"],
    }
    event = dict(event_payload)
    event["event_hash"] = sha256_json(event_payload)
    updated = deepcopy(dict(state))
    updated["current_state"] = target
    updated["review_disposition"] = disposition
    updated["decay_claim_status"] = (
        "SUPPORTED_BY_EXTERNAL_ADMISSIBLE_EVIDENCE" if decision["decay_claim"] else "NOT_CLAIMED"
    )
    updated["transition_history"] = list(updated["transition_history"]) + [event]
    updated["last_event_hash"] = event["event_hash"]
    updated.pop("state_hash", None)
    updated["state_hash"] = sha256_json(updated)
    validate_lifecycle_state(updated, contract)
    return updated


def build_replacement_lineage(
    predecessor_contract: Mapping[str, Any],
    successor_economic_identity_ref: Mapping[str, Any],
    successor_portfolio_readiness_ref: Mapping[str, Any],
    *, replacement_kind: str, reason: str, blocker_or_evidence_class: str,
    negative_knowledge_scope: str = "NOT_TRANSFERRED",
    evidence_ref: Optional[Mapping[str, Any]] = None,
    predecessor_lineage: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    validate_shadow_contract(predecessor_contract)
    validate_economic_identity_ref(successor_economic_identity_ref)
    validate_portfolio_readiness_ref(successor_portfolio_readiness_ref, successor_economic_identity_ref)
    if replacement_kind not in REPLACEMENT_KINDS:
        raise ValueError("invalid replacement_kind")
    reason = _require_nonempty(reason, "replacement reason")
    blocker = _require_nonempty(blocker_or_evidence_class, "blocker_or_evidence_class")
    if negative_knowledge_scope not in NEGATIVE_KNOWLEDGE_SCOPES:
        raise ValueError("negative knowledge scope must be explicit and bounded")
    predecessor_ref = predecessor_contract["immutable_core"]["economic_identity_ref"]
    if (
        successor_economic_identity_ref["identity_hash"] == predecessor_ref["identity_hash"]
        and successor_economic_identity_ref["candidate_hash"] == predecessor_ref["candidate_hash"]
    ):
        raise ValueError("replacement successor must not be the exact predecessor identity")
    history = [deepcopy(dict(item)) for item in (predecessor_lineage or [])]
    if successor_economic_identity_ref["identity_hash"] in {
        item.get("predecessor_identity_hash") for item in history
    }:
        raise ValueError("replacement lineage would create an identity cycle")
    evidence_hash = None
    if evidence_ref is not None:
        validate_decay_evidence_ref(evidence_ref, predecessor_contract)
        evidence_hash = evidence_ref["ref_hash"]
    record = {
        "schema_version": "economic-replacement-lineage-v1",
        "predecessor_contract_id": predecessor_contract["contract_id"],
        "predecessor_contract_hash": predecessor_contract["contract_hash"],
        "predecessor_observation_identity": predecessor_contract["observation_identity"],
        "predecessor_identity_hash": predecessor_ref["identity_hash"],
        "successor_identity_ref_hash": successor_economic_identity_ref["ref_hash"],
        "successor_identity_hash": successor_economic_identity_ref["identity_hash"],
        "successor_portfolio_readiness_ref_hash": successor_portfolio_readiness_ref["ref_hash"],
        "replacement_kind": replacement_kind,
        "reason": reason,
        "blocker_or_evidence_class": blocker,
        "evidence_ref_hash": evidence_hash,
        "negative_knowledge_scope": negative_knowledge_scope,
        "negative_knowledge_global": False,
        "automatic_negative_knowledge_transfer": False,
        "ancestry_depth": len(history) + 1,
        "ancestry_record_hashes": [item.get("lineage_hash") for item in history],
        "outcome_accessed": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
    record["lineage_hash"] = sha256_json(record)
    return record


def lifecycle_contract_summary(contract: Mapping[str, Any]) -> Dict[str, Any]:
    validate_shadow_contract(contract)
    return {
        "contract_id": contract["contract_id"],
        "observation_identity": contract["observation_identity"],
        "readiness": contract["readiness"],
        "initial_lifecycle_state": contract["initial_lifecycle_state"],
        "profitability_status": "UNKNOWN",
        "shadow_status_implies_profitability": False,
        "review_policy_hash": contract["immutable_core"]["review_policy"]["policy_hash"],
        "scheduler_owned_by_d0": False,
        "runtime_owned_by_d0": False,
        "outcome_accessed": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
