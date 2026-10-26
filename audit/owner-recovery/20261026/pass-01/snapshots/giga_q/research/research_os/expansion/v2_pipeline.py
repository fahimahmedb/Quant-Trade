from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from .v2_core import (
    CLOSED_AUTHORITY,
    V2ContractError,
    assert_authority_closed,
    assert_epoch_blinding,
    assert_validator_candidate_binding,
    build_candidate,
    build_epoch_manifest,
    build_evaluation_ingest_receipt,
    build_frozen_export_intent,
    build_negative_memory,
    build_priority_decision,
    build_research_trial,
    build_validator_result,
    canonical_hash,
    classify_model_pit,
    qualify_v2_core,
    validate_multidimensional_status,
    validate_reverse_message,
)

_FORBIDDEN_RESEARCH_KEYS = {
    "return", "returns", "pnl", "profit", "loss", "outcome", "outcomes",
    "evaluation_result", "economic_result", "portfolio_contribution",
}


def _reject_outcome_payload(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in _FORBIDDEN_RESEARCH_KEYS:
                raise V2ContractError(f"OUTCOME_DATA_VISIBLE_TO_RESEARCH:{path}.{key}")
            _reject_outcome_payload(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_outcome_payload(child, f"{path}[{index}]")


def run_pre_outcome_pipeline(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Execute a deterministic V2 Core qualification path without outcomes.

    This adapter deliberately consumes only pre-outcome objects. It does not
    fetch market results, prospective observations, positions, orders, or any
    Evaluation-side outcome store.
    """
    _reject_outcome_payload(bundle)
    authority = deepcopy(bundle.get("authority", CLOSED_AUTHORITY))
    assert_authority_closed(authority)

    epoch = build_epoch_manifest(bundle["epoch"])
    trial = build_research_trial(bundle["trial"])
    candidate = build_candidate(bundle["candidate"])
    validator = build_validator_result(bundle["validator"])
    if "validator_hash" in bundle["validator"] and bundle["validator"]["validator_hash"] != validator["validator_hash"]:
        raise V2ContractError("VALIDATOR_HASH_MISMATCH")
    validate_multidimensional_status(bundle["status"])

    if trial["research_epoch_id"] != epoch["research_epoch_id"]:
        raise V2ContractError("TRIAL_EPOCH_BINDING_MISMATCH")
    if candidate["research_epoch_id"] != epoch["research_epoch_id"]:
        raise V2ContractError("CANDIDATE_EPOCH_BINDING_MISMATCH")
    if candidate["research_trial_id"] != trial["research_trial_id"]:
        raise V2ContractError("CANDIDATE_TRIAL_BINDING_MISMATCH")
    assert_validator_candidate_binding(candidate, validator)
    if validator["execution_state"] != "COMPLETE" or validator.get("scientific_decision") != "PASS":
        raise V2ContractError("EXPORT_REQUIRES_COMPLETED_VALIDATOR_PASS")
    if bundle["status"]["scientific_maturity"] != "VALIDATED":
        raise V2ContractError("EXPORT_REQUIRES_VALIDATED_SCIENTIFIC_STATUS")
    if bundle["status"]["experiment_readiness"] != "READY":
        raise V2ContractError("EXPORT_REQUIRES_READY_EXPERIMENT_STATUS")
    if bundle["status"]["authority"] != "CLOSED":
        raise V2ContractError("V2_CORE_STATUS_AUTHORITY_MUST_REMAIN_CLOSED")

    leakage = bundle.get("leakage_classification")
    if not isinstance(leakage, Mapping) or leakage.get("source_pit") not in ("PASS", "FAIL"):
        raise V2ContractError("INVALID_LEAKAGE_CLASSIFICATION")
    expected_leakage = classify_model_pit(
        source_pit=leakage["source_pit"] == "PASS",
        model_knowledge_cutoff_status=leakage.get("model_pit"),
    )
    if any(leakage.get(key) != value for key, value in expected_leakage.items()):
        raise V2ContractError("INVALID_LEAKAGE_CLASSIFICATION")
    if expected_leakage["source_pit"] != "PASS":
        raise V2ContractError("EXPORT_REQUIRES_SOURCE_PIT_PASS")

    blinding = assert_epoch_blinding(
        epoch,
        owner_status=bundle["blinding"]["owner_status"],
        supervisor_status=bundle["blinding"]["supervisor_status"],
    )

    priority = build_priority_decision(
        policy_version=bundle["priority_policy_version"],
        eligible=bundle["priority_eligible"],
    )
    negative = build_negative_memory(bundle["negative_memory"])

    expected_trial_history_hash = canonical_hash([trial["trial_hash"]])
    export_payload = deepcopy(bundle["export"])
    expected_bindings = {
        "candidate_hash": candidate["candidate_hash"],
        "research_trial_history_hash": expected_trial_history_hash,
        "research_epoch_id": epoch["research_epoch_id"],
        "epoch_manifest_hash": epoch["epoch_manifest_hash"],
        "validator_artifact_hash": validator["validator_hash"],
        "universe": candidate["universe"],
        "clock": candidate["clock"],
        "horizon": candidate["horizon"],
        "economic_expression": candidate["economic_expression"],
    }
    for key, expected in expected_bindings.items():
        supplied = export_payload.get(key)
        if supplied in (None, "AUTO"):
            export_payload[key] = expected
        elif supplied != expected:
            raise V2ContractError("EXPORT_BINDING_MISMATCH:" + key)

    export = build_frozen_export_intent(export_payload)
    ingest = build_evaluation_ingest_receipt(export_bundle_hash=export["export_bundle_hash"])
    validate_reverse_message(ingest, expected_export_bundle_hash=export["export_bundle_hash"])

    proof = {
        "authority": authority,
        "epoch_contract_qualified": True,
        "ideation_trial_accounting_qualified": trial["proposal_count"] >= 1,
        "leakage_classification_qualified": True,
        "candidate_contract_qualified": True,
        "validator_independence_qualified": bundle.get("validator_independence_qualified"),
        "evaluation_membrane_qualified": ingest["message"] == "EXPORT_ACCEPTED",
        "feedback_lineage_qualified": bundle.get("feedback_lineage_qualified"),
        "priority_policy_qualified": bool(priority["selected_task"]),
        "negative_memory_qualified": bool(negative["negative_knowledge_hash"]),
        "multidimensional_status_qualified": True,
        "bounded_orchestration_qualified": bundle.get("bounded_orchestration_qualified"),
    }
    qualification = qualify_v2_core(proof)
    if qualification["status"] != "AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED":
        raise V2ContractError("V2_QUALIFICATION_BLOCKED:" + ",".join(qualification["missing_gates"]))

    receipt = {
        "schema_version": "oracle-v2-core-pre-outcome-receipt-v1",
        "status": "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY",
        "system_qualification": qualification["status"],
        "research_epoch_id": epoch["research_epoch_id"],
        "epoch_manifest_hash": epoch["epoch_manifest_hash"],
        "research_trial_id": trial["research_trial_id"],
        "trial_hash": trial["trial_hash"],
        "candidate_hash": candidate["candidate_hash"],
        "validator_hash": validator["validator_hash"],
        "export_bundle_hash": export["export_bundle_hash"],
        "evaluation_ingest_receipt_hash": ingest["receipt_hash"],
        "priority_decision_hash": priority["decision_hash"],
        "negative_knowledge_hash": negative["negative_knowledge_hash"],
        "blinding": blinding,
        "authority": deepcopy(CLOSED_AUTHORITY),
        "outcome_accessed": False,
        "economic_claim_authorized": False,
    }
    receipt["receipt_hash"] = canonical_hash(receipt)
    return receipt
