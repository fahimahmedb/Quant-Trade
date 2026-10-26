"""Wave-2 canonical thin binding: C0 -> W1 Economic -> MEGA D0.

This module owns no scientific verdict, economic fingerprint, portfolio decision,
lifecycle state machine, outcome evaluation, scheduler, runtime, sizing, capital,
or trading authority. It only proves exact identity continuity across already-owned
contracts and lets D0 create its pre-outcome shadow/lifecycle contract.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.scientific_adjudication import validate_adjudication
from research.research_os.expansion.economic_lifecycle import (
    WAVE2_IMMUTABLE_BASE_SHA,
    authority_state,
    create_shadow_contract,
    validate_economic_identity_ref,
    validate_portfolio_readiness_ref,
    validate_shadow_contract,
)

SCHEMA_VERSION = "wave2-scientific-economic-handoff-v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _rehash(record: Mapping[str, Any], key: str) -> str:
    payload = deepcopy(dict(record))
    payload.pop(key, None)
    return sha256_json(payload)


def bind_scientific_economic_handoff(
    adjudication: Mapping[str, Any],
    economic_identity_ref: Mapping[str, Any],
    portfolio_readiness_ref: Mapping[str, Any],
) -> Dict[str, Any]:
    """Bind a favorable C0 verdict to independently-created W1 ECON refs.

    C0 never creates Economic Identity. This function therefore requires the
    W1 ECON / D0 references as inputs and only checks that they are the exact
    continuation of the scientifically adjudicated candidate generation.
    """
    validate_adjudication(adjudication)
    validate_economic_identity_ref(economic_identity_ref)
    validate_portfolio_readiness_ref(portfolio_readiness_ref, economic_identity_ref)

    _require(adjudication.get("verdict") == "PROMOTE", "scientific verdict is not promotable")
    _require(
        adjudication.get("scientific_posture") == "QUALIFIED_WITH_CLAIM_CEILING",
        "scientific posture is not qualified with an explicit claim ceiling",
    )
    _require(adjudication.get("promotion_target") == "ECONOMIC_IDENTITY", "scientific promotion target mismatch")
    _require(adjudication.get("economic_identity_created") is False, "C0 must not create Economic Identity")
    _require(adjudication.get("raw_outcomes_consumed") == 0, "C0 handoff must remain pre-outcome")

    identity = adjudication.get("identity")
    _require(isinstance(identity, Mapping), "scientific adjudication identity is missing")
    for key in ("hypothesis_id", "generation_id", "candidate_hash"):
        _require(
            identity.get(key) == economic_identity_ref.get(key),
            f"scientific/economic {key} binding mismatch",
        )
    _require(
        adjudication.get("evaluation_binding", {}).get("candidate_hash") == economic_identity_ref.get("candidate_hash"),
        "scientific evaluation binding candidate hash mismatch",
    )
    _require(
        economic_identity_ref.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA
        and portfolio_readiness_ref.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA,
        "economic refs do not bind the canonical Wave2 base",
    )

    ref = {
        "schema_version": SCHEMA_VERSION,
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
        "hypothesis_id": identity["hypothesis_id"],
        "generation_id": identity["generation_id"],
        "candidate_hash": identity["candidate_hash"],
        "scientific_adjudication_identity": adjudication["adjudication_identity"],
        "scientific_adjudication_hash": adjudication["adjudication_hash"],
        "scientific_posture": adjudication["scientific_posture"],
        "claim_ceiling": adjudication["claim_ceiling"],
        "economic_identity_ref_hash": economic_identity_ref["ref_hash"],
        "economic_identity_hash": economic_identity_ref["identity_hash"],
        "portfolio_readiness_ref_hash": portfolio_readiness_ref["ref_hash"],
        "portfolio_structural_mapping_status": portfolio_readiness_ref["structural_mapping_status"],
        "portfolio_pre_outcome_decision_status": portfolio_readiness_ref["pre_outcome_decision_status"],
        "downstream_target": "ECONOMIC_LIFECYCLE_D0",
        "scientific_result_is_profitability": False,
        "economic_readiness_is_profitability": False,
        "raw_outcomes_consumed": 0,
        "scheduler_owned": False,
        "runtime_owned": False,
        "position_sizing_authorized": False,
        "capital_allocation_authorized": False,
        **authority_state(),
    }
    ref["handoff_hash"] = sha256_json(ref)
    validate_scientific_economic_handoff(
        ref, adjudication, economic_identity_ref, portfolio_readiness_ref
    )
    return ref


def validate_scientific_economic_handoff(
    ref: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    economic_identity_ref: Mapping[str, Any],
    portfolio_readiness_ref: Mapping[str, Any],
) -> None:
    validate_adjudication(adjudication)
    validate_economic_identity_ref(economic_identity_ref)
    validate_portfolio_readiness_ref(portfolio_readiness_ref, economic_identity_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == SCHEMA_VERSION, "unsupported scientific/economic handoff schema")
    _require(ref.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA, "handoff Wave2 base mismatch")
    identity = adjudication.get("identity") or {}
    expected = {
        "hypothesis_id": identity.get("hypothesis_id"),
        "generation_id": identity.get("generation_id"),
        "candidate_hash": identity.get("candidate_hash"),
        "scientific_adjudication_identity": adjudication.get("adjudication_identity"),
        "scientific_adjudication_hash": adjudication.get("adjudication_hash"),
        "economic_identity_ref_hash": economic_identity_ref.get("ref_hash"),
        "economic_identity_hash": economic_identity_ref.get("identity_hash"),
        "portfolio_readiness_ref_hash": portfolio_readiness_ref.get("ref_hash"),
    }
    for key, value in expected.items():
        _require(ref.get(key) == value, f"handoff {key} mismatch")
    _require(ref.get("scientific_posture") == "QUALIFIED_WITH_CLAIM_CEILING", "handoff scientific posture mismatch")
    _require(ref.get("claim_ceiling") not in (None, "", "UNKNOWN"), "handoff claim ceiling is unresolved")
    _require(ref.get("downstream_target") == "ECONOMIC_LIFECYCLE_D0", "handoff downstream target mismatch")
    _require(ref.get("raw_outcomes_consumed") == 0, "handoff may not consume outcomes")
    _require(ref.get("scientific_result_is_profitability") is False, "scientific result may not imply profitability")
    _require(ref.get("economic_readiness_is_profitability") is False, "economic readiness may not imply profitability")
    for key, value in authority_state().items():
        _require(ref.get(key) is value, f"handoff {key} authority drift")
    for key in ("scheduler_owned", "runtime_owned", "position_sizing_authorized", "capital_allocation_authorized"):
        _require(ref.get(key) is False, f"handoff {key} must remain false")
    _require(_rehash(ref, "handoff_hash") == ref.get("handoff_hash"), "scientific/economic handoff hash mismatch")


def create_d0_shadow_from_scientific_handoff(
    handoff_ref: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    economic_identity_ref: Mapping[str, Any],
    portfolio_readiness_ref: Mapping[str, Any],
    *,
    prospective_start_boundary: str,
    implementation_version: str,
    review_policy: Mapping[str, Any],
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Create only the existing D0 pre-outcome shadow contract with exact C0 lineage."""
    validate_scientific_economic_handoff(
        handoff_ref, adjudication, economic_identity_ref, portfolio_readiness_ref
    )
    lineage = {
        "scientific_adjudication_identity": adjudication["adjudication_identity"],
        "scientific_adjudication_hash": adjudication["adjudication_hash"],
        "scientific_economic_handoff_hash": handoff_ref["handoff_hash"],
        "scientific_claim_ceiling": handoff_ref["claim_ceiling"],
    }
    extra = deepcopy(dict(metadata or {}))
    for key in lineage:
        _require(key not in extra, f"metadata may not override canonical lineage field {key}")
    extra.update(lineage)
    contract = create_shadow_contract(
        economic_identity_ref,
        portfolio_readiness_ref,
        prospective_start_boundary=prospective_start_boundary,
        implementation_version=implementation_version,
        review_policy=review_policy,
        metadata=extra,
    )
    validate_shadow_contract(contract)
    _require(contract.get("outcome_accessed") is False, "D0 shadow unexpectedly accessed outcomes")
    _require(contract.get("profitability_status") == "UNKNOWN", "D0 shadow inferred profitability")
    return contract
