from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Sequence

AUTHORITY_KEYS = (
    "economic_experiment_authorized",
    "prospective_observation_authorized",
    "real_capital_authorized",
    "live_trading_authorized",
)
CLOSED_AUTHORITY = {key: False for key in AUTHORITY_KEYS}

SEMANTIC_NULLS = {"UNKNOWN", "NOT_APPLICABLE", "NOT_YET_MEASURABLE", "UNRESOLVED"}
EPOCH_CLOSE_POLICIES = {"TIME_BOUND", "N_EXPORTS", "PREDECLARED_COMPOSITE"}
EXECUTION_STATES = {
    "PENDING", "RUNNING", "COMPLETE", "RETRYABLE_ERROR", "PERMANENT_ERROR", "INTERRUPTED"
}
SCIENTIFIC_DECISIONS = {"PASS", "BLOCK"}
SCIENTIFIC_MATURITY = {
    "IDEA", "EVIDENCE_BOUND", "DISCONFIRMATION_ATTEMPTED", "FROZEN", "VALIDATED"
}
EXPERIMENT_READINESS = {"INCOMPLETE", "READY"}
PORTFOLIO_RELATIONSHIPS = {
    "UNKNOWN", "DISTINCT", "VARIANT", "REPLICATION", "DUPLICATE", "COMPLEMENTARY"
}
AUTHORITY_STATES = {"CLOSED", "OWNER_AUTHORIZED"}
ALLOWED_REVERSE_MESSAGES = {
    "EXPORT_ACCEPTED", "EXPORT_REJECTED_FOR_SCHEMA_ERROR", "INTEGRITY_FAILURE"
}
FORBIDDEN_OUTCOME_KEYS = {
    "return", "returns", "pnl", "profit", "loss", "outcome", "outcomes", "metric", "metrics",
    "rank", "score_after_outcome", "portfolio_contribution", "economic_result", "evaluation_result",
}
PRIMARY_EXTENSIONS = {
    "fundamental": "FundamentalExtension",
    "event": "EventExtension",
    "forced_flow": "ForcedFlowExtension",
    "quant": "QuantExtension",
}
FAMILY_REQUIRED = {
    "FundamentalExtension": {"issuer", "business_driver", "valuation_transmission"},
    "EventExtension": {"event", "availability_time", "event_clock", "reaction_channel", "revision_policy"},
    "ForcedFlowExtension": {"forced_constrained_actor", "binding_constraint", "payer", "instrument", "timing"},
    "QuantExtension": {"signal_definition", "observation_clock", "decision_clock", "execution_clock", "data_route", "multiplicity_family"},
}


class V2ContractError(ValueError):
    pass


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _require(mapping: Mapping[str, Any], keys: Iterable[str], label: str) -> None:
    missing = sorted(key for key in keys if key not in mapping)
    if missing:
        raise V2ContractError(f"{label}_MISSING:" + ",".join(missing))


def _require_identifiers(mapping: Mapping[str, Any], keys: Iterable[str], label: str) -> None:
    invalid = sorted(key for key in keys if not isinstance(mapping[key], str)
                     or not mapping[key].strip() or mapping[key].strip().upper() in SEMANTIC_NULLS)
    if invalid:
        raise V2ContractError(f"{label}_INVALID_IDENTIFIER:" + ",".join(invalid))


def _parse_time(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise V2ContractError("INVALID_TIMESTAMP")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise V2ContractError("TIMESTAMP_WITHOUT_TIMEZONE")
    return parsed.astimezone(timezone.utc)


def assert_authority_closed(authority: Mapping[str, Any]) -> None:
    _require(authority, AUTHORITY_KEYS, "AUTHORITY")
    if any(authority[key] is not False for key in AUTHORITY_KEYS):
        raise V2ContractError("V2_CORE_AUTHORITY_OPEN")


def classify_model_pit(*, source_pit: bool, model_knowledge_cutoff_status: str) -> Dict[str, str]:
    if not isinstance(model_knowledge_cutoff_status, str) or model_knowledge_cutoff_status not in {
        "PROVABLY_BEFORE_CUTOFF", "NOT_PROVABLE", "AFTER_CUTOFF"
    }:
        raise V2ContractError("INVALID_MODEL_PIT_STATUS")
    if type(source_pit) is not bool:
        raise V2ContractError("INVALID_SOURCE_PIT_STATUS")
    if not source_pit:
        status = "SOURCE_NOT_PIT"
    elif model_knowledge_cutoff_status == "PROVABLY_BEFORE_CUTOFF":
        status = "SOURCE_AND_MODEL_PIT"
    elif model_knowledge_cutoff_status == "NOT_PROVABLE":
        status = "HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT"
    else:
        status = "MODEL_KNOWLEDGE_AFTER_CUTOFF"
    return {
        "source_pit": "PASS" if source_pit else "FAIL",
        "model_pit": model_knowledge_cutoff_status,
        "historical_generation_status": status,
    }


def build_epoch_manifest(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "research_epoch_id", "parent_epoch_id", "opened_at", "knowledge_cutoff", "research_window",
        "export_cutoff", "close_policy", "feedback_release_policy", "research_policy_hash",
        "model_routing_policy_hash", "allowed_model_set", "allowed_model_change_policy",
        "source_policy_hash", "retrieval_policy_hash", "validator_policy_hash",
        "max_candidate_exports", "scheduled_close_at", "epoch_knowledge_parent",
        "epoch_feedback_dependencies", "contamination_status",
    }
    _require(payload, required, "EPOCH")
    _require_identifiers(payload, ("research_epoch_id",), "EPOCH")
    if payload["close_policy"] not in EPOCH_CLOSE_POLICIES:
        raise V2ContractError("INVALID_CLOSE_POLICY")
    if not isinstance(payload["allowed_model_set"], list) or not payload["allowed_model_set"]:
        raise V2ContractError("EMPTY_ALLOWED_MODEL_SET")
    if not isinstance(payload["epoch_feedback_dependencies"], list):
        raise V2ContractError("INVALID_FEEDBACK_DEPENDENCIES")
    if type(payload["max_candidate_exports"]) is not int or payload["max_candidate_exports"] < 1:
        raise V2ContractError("INVALID_MAX_CANDIDATE_EXPORTS")
    opened = _parse_time(payload["opened_at"])
    cutoff = _parse_time(payload["knowledge_cutoff"])
    export_cutoff = _parse_time(payload["export_cutoff"])
    scheduled_close = _parse_time(payload["scheduled_close_at"])
    if cutoff > opened:
        raise V2ContractError("KNOWLEDGE_CUTOFF_AFTER_OPEN")
    if export_cutoff > scheduled_close:
        raise V2ContractError("EXPORT_CUTOFF_AFTER_CLOSE")
    manifest = deepcopy(dict(payload))
    manifest["close_policy_hash"] = canonical_hash({"close_policy": payload["close_policy"],
                                                    "max_candidate_exports": payload["max_candidate_exports"],
                                                    "scheduled_close_at": payload["scheduled_close_at"]})
    manifest["feedback_release_policy_hash"] = canonical_hash(payload["feedback_release_policy"])
    manifest["epoch_manifest_hash"] = canonical_hash(manifest)
    return manifest


def assert_epoch_update(previous: Mapping[str, Any], current: Mapping[str, Any], *, first_export_accepted: bool) -> None:
    if previous.get("research_epoch_id") != current.get("research_epoch_id"):
        raise V2ContractError("EPOCH_ID_CHANGED")
    if first_export_accepted:
        immutable = {
            "knowledge_cutoff", "export_cutoff", "close_policy", "close_policy_hash",
            "feedback_release_policy", "feedback_release_policy_hash", "research_policy_hash",
            "model_routing_policy_hash", "allowed_model_set", "allowed_model_change_policy",
            "source_policy_hash", "retrieval_policy_hash", "validator_policy_hash",
            "max_candidate_exports", "scheduled_close_at",
        }
        changed = sorted(key for key in immutable if previous.get(key) != current.get(key))
        if changed:
            raise V2ContractError("POST_EXPORT_EPOCH_MUTATION:" + ",".join(changed))


def assert_model_allowed(epoch: Mapping[str, Any], model_identity: str) -> None:
    if model_identity not in epoch.get("allowed_model_set", []):
        raise V2ContractError("MODEL_OUTSIDE_EPOCH_POLICY")


def build_research_trial(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "research_trial_id", "research_epoch_id", "trial_type", "model_identity", "prompt_hash",
        "context_hash", "retrieval_manifest_hash", "source_packet_hash", "generated_at",
        "sampling_parameters", "generated_proposals", "discarded_proposals", "retry_count",
    }
    _require(payload, required, "TRIAL")
    _require_identifiers(payload, ("research_trial_id", "research_epoch_id"), "TRIAL")
    if payload["trial_type"] != "RESEARCH_GENERATION_TRIAL":
        raise V2ContractError("INVALID_RESEARCH_TRIAL_TYPE")
    if type(payload["retry_count"]) is not int or payload["retry_count"] < 0:
        raise V2ContractError("INVALID_RETRY_COUNT")
    if not isinstance(payload["generated_proposals"], list) or not payload["generated_proposals"]:
        raise V2ContractError("TRIAL_WITHOUT_GENERATED_PROPOSALS")
    if not isinstance(payload["discarded_proposals"], list):
        raise V2ContractError("INVALID_DISCARDED_PROPOSALS")
    trial = deepcopy(dict(payload))
    trial["proposal_count"] = len(trial["generated_proposals"])
    trial["discard_count"] = len(trial["discarded_proposals"])
    trial["trial_hash"] = canonical_hash(trial)
    return trial


def build_candidate(payload: Mapping[str, Any]) -> Dict[str, Any]:
    core_required = {
        "hypothesis_id", "generation_id", "research_trial_id", "research_epoch_id", "family", "claim",
        "mechanism_statement", "universe", "clock", "horizon", "economic_expression",
        "evidence_manifest", "falsification_scope", "decision_map", "known_confounders",
        "disconfirmation_manifest", "producer_identity", "extension",
    }
    _require(payload, core_required, "CANDIDATE")
    _require_identifiers(payload, ("hypothesis_id", "generation_id", "research_trial_id", "research_epoch_id"),
                         "CANDIDATE")
    family = payload["family"]
    if family not in PRIMARY_EXTENSIONS:
        raise V2ContractError("UNSUPPORTED_CANDIDATE_FAMILY")
    extension = payload["extension"]
    if not isinstance(extension, Mapping):
        raise V2ContractError("INVALID_FAMILY_EXTENSION")
    expected = PRIMARY_EXTENSIONS[family]
    if extension.get("type") != expected:
        raise V2ContractError("FAMILY_EXTENSION_MISMATCH")
    _require(extension, FAMILY_REQUIRED[expected], expected.upper())
    if not payload["falsification_scope"] or not payload["decision_map"]:
        raise V2ContractError("CANDIDATE_WITHOUT_FALSIFICATION_OR_DECISION_MAP")
    candidate = deepcopy(dict(payload))
    candidate.pop("candidate_hash", None)
    candidate["candidate_hash"] = canonical_hash(candidate)
    return candidate


def build_validator_result(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "hypothesis_id", "generation_id", "validator_identity", "validator_version",
        "validator_model", "validator_prompt_hash", "validator_context_hash",
        "validator_retrieval_manifest_hash", "execution_state", "epistemic_blockers",
    }
    _require(payload, required, "VALIDATOR")
    _require_identifiers(payload, ("hypothesis_id", "generation_id", "validator_identity"), "VALIDATOR")
    execution = payload["execution_state"]
    if execution not in EXECUTION_STATES:
        raise V2ContractError("INVALID_VALIDATOR_EXECUTION_STATE")
    result = deepcopy(dict(payload))
    decision = result.get("scientific_decision")
    if execution == "COMPLETE":
        if decision not in SCIENTIFIC_DECISIONS:
            raise V2ContractError("COMPLETE_VALIDATOR_REQUIRES_PASS_OR_BLOCK")
    elif decision is not None:
        raise V2ContractError("NONCOMPLETE_VALIDATOR_CANNOT_DECIDE")
    if not isinstance(result["epistemic_blockers"], list):
        raise V2ContractError("INVALID_EPISTEMIC_BLOCKERS")
    if decision == "PASS" and result["epistemic_blockers"]:
        raise V2ContractError("VALIDATOR_PASS_WITH_EPISTEMIC_BLOCKERS")
    result["validator_hash"] = canonical_hash({k: v for k, v in result.items() if k != "validator_hash"})
    return result


def validate_multidimensional_status(status: Mapping[str, str]) -> None:
    if status.get("scientific_maturity") not in SCIENTIFIC_MATURITY:
        raise V2ContractError("INVALID_SCIENTIFIC_MATURITY")
    if status.get("experiment_readiness") not in EXPERIMENT_READINESS:
        raise V2ContractError("INVALID_EXPERIMENT_READINESS")
    if status.get("portfolio_relationship") not in PORTFOLIO_RELATIONSHIPS:
        raise V2ContractError("INVALID_PORTFOLIO_RELATIONSHIP")
    if status.get("authority") not in AUTHORITY_STATES:
        raise V2ContractError("INVALID_AUTHORITY_STATE")


def assert_validator_candidate_binding(candidate: Mapping[str, Any], validator: Mapping[str, Any]) -> None:
    """Require the complete Validator artifact to refer to this exact Candidate."""
    if any(validator.get(key) != candidate[key] for key in ("hypothesis_id", "generation_id", "candidate_hash")):
        raise V2ContractError("VALIDATOR_CANDIDATE_BINDING_MISMATCH")
    if validator.get("validator_hash") != build_validator_result(validator)["validator_hash"]:
        raise V2ContractError("VALIDATOR_HASH_MISMATCH")


def assert_trial_proposal_binding(candidate: Mapping[str, Any], trial: Mapping[str, Any]) -> None:
    """Join a generated proposal to its exact subject, not merely its trial ID.

    Native producer trials reference the original source Candidate; generic V2
    trials reference the V2 Candidate itself. These hashes are not interchangeable.
    """
    _require_identifiers(candidate, ("hypothesis_id", "generation_id"), "TRIAL_CANDIDATE")
    manifest = candidate.get("evidence_manifest")
    if not isinstance(manifest, Mapping):
        raise V2ContractError("TRIAL_PROPOSAL_BINDING_MISMATCH")
    reference = candidate.get("candidate_hash")
    if "source_candidate_hash" in manifest or "documentary_packet_hash" in manifest:
        reference = manifest.get("source_candidate_hash")
        packet_hash = manifest.get("documentary_packet_hash")
        if not _is_sha256(packet_hash) or trial.get("source_packet_hash") != packet_hash:
            raise V2ContractError("TRIAL_SOURCE_PACKET_BINDING_MISMATCH")
    if not _is_sha256(reference):
        raise V2ContractError("TRIAL_PROPOSAL_BINDING_MISMATCH")
    expected = {"hypothesis_id": candidate.get("hypothesis_id"),
                "generation_id": candidate.get("generation_id"), "candidate_hash": reference}
    if not any(isinstance(proposal, Mapping) and all(proposal.get(k) == v for k, v in expected.items())
               for proposal in trial["generated_proposals"]):
        raise V2ContractError("TRIAL_PROPOSAL_BINDING_MISMATCH")


def build_priority_decision(*, policy_version: str, eligible: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    if not policy_version or not eligible:
        raise V2ContractError("PRIORITY_REQUIRES_POLICY_AND_ELIGIBLE_SET")
    normalized: List[Dict[str, Any]] = []
    for item in eligible:
        _require(item, {"task_id", "priority", "reason_codes", "resource_cost", "starvation_factor"}, "PRIORITY_ITEM")
        if "high_value" in item or "expected_return" in item or "economic_score" in item:
            raise V2ContractError("OUTCOME_LIKE_PRIORITY_SIGNAL_FORBIDDEN")
        normalized.append(deepcopy(dict(item)))
    ordered = sorted(
        normalized,
        key=lambda x: (-int(x["priority"]), -float(x["starvation_factor"]), float(x["resource_cost"]), x["task_id"]),
    )
    return {
        "policy_version": policy_version,
        "eligible_set": [x["task_id"] for x in ordered],
        "criteria": ["priority_desc", "starvation_desc", "resource_cost_asc", "task_id_asc"],
        "selected_task": ordered[0]["task_id"],
        "selected_reason_codes": ordered[0]["reason_codes"],
        "decision_hash": canonical_hash({"policy_version": policy_version, "eligible": ordered}),
    }


def build_negative_memory(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "negative_knowledge_id", "failure_scope", "assumptions", "regime_context", "source_context",
        "failure_reason", "revisit_conditions", "revisit_policy",
    }
    _require(payload, required, "NEGATIVE_MEMORY")
    if payload.get("failure_reason") == "IDEA_FALSE_FOREVER" and not payload.get("logical_proof"):
        raise V2ContractError("UNSCOPED_PERMANENT_NEGATIVE_CLAIM")
    record = deepcopy(dict(payload))
    record["negative_knowledge_hash"] = canonical_hash(record)
    return record


def _scan_forbidden_outcome_keys(value: Any, path: str = "$") -> List[str]:
    hits: List[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_norm = str(key).lower()
            if key_norm in FORBIDDEN_OUTCOME_KEYS:
                hits.append(f"{path}.{key}")
            hits.extend(_scan_forbidden_outcome_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            hits.extend(_scan_forbidden_outcome_keys(child, f"{path}[{idx}]"))
    return hits


def build_frozen_export_intent(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {
        "candidate_hash", "research_trial_history_hash", "research_epoch_id", "epoch_manifest_hash",
        "protocol_hash", "source_snapshot_hashes", "pit_manifest_hash", "universe", "clock", "horizon",
        "economic_expression", "cost_model_declaration", "capacity_declaration",
        "multiplicity_declaration", "validator_artifact_hash", "research_head",
    }
    _require(payload, required, "EXPORT")
    hits = _scan_forbidden_outcome_keys(payload)
    if hits:
        raise V2ContractError("OUTCOME_DATA_IN_RESEARCH_EXPORT:" + ",".join(hits))
    export = deepcopy(dict(payload))
    export["event_type"] = "FROZEN_EXPORT_INTENT"
    export["export_bundle_hash"] = canonical_hash(export)
    return export


def build_evaluation_ingest_receipt(*, export_bundle_hash: str, message: str = "EXPORT_ACCEPTED") -> Dict[str, Any]:
    if not isinstance(message, str) or message not in ALLOWED_REVERSE_MESSAGES:
        raise V2ContractError("FORBIDDEN_EVALUATION_REVERSE_MESSAGE")
    if not _is_sha256(export_bundle_hash):
        raise V2ContractError("INVALID_EXPORT_BUNDLE_HASH")
    receipt = {
        "event_type": "EVALUATION_INGEST_RECEIPT",
        "message": message,
        "export_bundle_hash": export_bundle_hash,
    }
    if _scan_forbidden_outcome_keys(receipt):
        raise V2ContractError("OUTCOME_DATA_IN_INGEST_RECEIPT")
    receipt["receipt_hash"] = canonical_hash(receipt)
    return receipt


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def validate_reverse_message(message: Mapping[str, Any], *, expected_export_bundle_hash: str = None) -> None:
    """Validate technical receipt metadata, optionally bound to a known export.

    This does not authenticate an evaluator or prove transport isolation.
    """
    if not isinstance(message, Mapping):
        raise V2ContractError("INVALID_EVALUATION_REVERSE_MESSAGE")
    if not isinstance(message.get("message"), str) or message["message"] not in ALLOWED_REVERSE_MESSAGES:
        raise V2ContractError("FORBIDDEN_EVALUATION_REVERSE_MESSAGE")
    hits = _scan_forbidden_outcome_keys(message)
    if hits:
        raise V2ContractError("OUTCOME_DATA_IN_REVERSE_MESSAGE:" + ",".join(hits))
    required = {"event_type", "message", "export_bundle_hash", "receipt_hash"}
    _require(message, required, "EVALUATION_RECEIPT")
    if set(message) != required:
        raise V2ContractError("UNEXPECTED_EVALUATION_REVERSE_FIELDS")
    if message["event_type"] != "EVALUATION_INGEST_RECEIPT":
        raise V2ContractError("INVALID_EVALUATION_RECEIPT_EVENT")
    if not _is_sha256(message["export_bundle_hash"]):
        raise V2ContractError("INVALID_EXPORT_BUNDLE_HASH")
    if expected_export_bundle_hash is not None:
        if not _is_sha256(expected_export_bundle_hash):
            raise V2ContractError("INVALID_EXPECTED_EXPORT_BUNDLE_HASH")
        if message["export_bundle_hash"] != expected_export_bundle_hash:
            raise V2ContractError("EVALUATION_RECEIPT_EXPORT_BINDING_MISMATCH")
    expected_receipt_hash = canonical_hash({key: value for key, value in message.items() if key != "receipt_hash"})
    if message["receipt_hash"] != expected_receipt_hash:
        raise V2ContractError("EVALUATION_RECEIPT_HASH_MISMATCH")


def blinding_integrity(*, owner_status: str, supervisor_status: str) -> Dict[str, str]:
    allowed = {"BLINDED", "OUTCOME_VIEWED"}
    if owner_status not in allowed or supervisor_status not in allowed:
        raise V2ContractError("INVALID_BLINDING_STATUS")
    integrity = "BROKEN" if "OUTCOME_VIEWED" in {owner_status, supervisor_status} else "PASS"
    return {
        "owner_outcome_blinding_status": owner_status,
        "supervisor_outcome_blinding_status": supervisor_status,
        "epoch_blinding_integrity": integrity,
    }


def assert_epoch_blinding(epoch: Mapping[str, Any], *, owner_status: str,
                          supervisor_status: str) -> Dict[str, str]:
    """Admit only a CLEAN epoch with explicit blinding of both influencing actors."""
    if epoch.get("contamination_status") != "CLEAN":
        raise V2ContractError("EPOCH_CONTAMINATED")
    integrity = blinding_integrity(owner_status=owner_status, supervisor_status=supervisor_status)
    if integrity["epoch_blinding_integrity"] != "PASS":
        raise V2ContractError("BLINDING_INTEGRITY_BROKEN")
    return integrity


def release_feedback(*, source_epoch_id: str, successor_epoch_id: str,
                     source_epoch_closed: bool, policy_allows_release: bool,
                     feedback_hash: str) -> Dict[str, Any]:
    if source_epoch_closed is not True:
        raise V2ContractError("FEEDBACK_BEFORE_EPOCH_CLOSE")
    if policy_allows_release is not True:
        raise V2ContractError("FEEDBACK_RELEASE_NOT_AUTHORIZED_BY_POLICY")
    if not source_epoch_id or not successor_epoch_id or source_epoch_id == successor_epoch_id:
        raise V2ContractError("FEEDBACK_REQUIRES_SUCCESSOR_EPOCH")
    _require_identifiers({"source_epoch_id": source_epoch_id, "successor_epoch_id": successor_epoch_id},
                         ("source_epoch_id", "successor_epoch_id"), "FEEDBACK")
    if not isinstance(feedback_hash, str) or not feedback_hash.strip():
        raise V2ContractError("FEEDBACK_HASH_REQUIRED")
    event = {
        "event_type": "ECONOMIC_FEEDBACK_RELEASED",
        "source_epoch_id": source_epoch_id,
        "successor_epoch_id": successor_epoch_id,
        "feedback_hash": feedback_hash,
    }
    event["event_hash"] = canonical_hash(event)
    return event


def qualify_v2_core(proof: Mapping[str, Any]) -> Dict[str, Any]:
    assert_authority_closed(proof.get("authority", {}))
    required_true = {
        "epoch_contract_qualified",
        "ideation_trial_accounting_qualified",
        "leakage_classification_qualified",
        "candidate_contract_qualified",
        "validator_independence_qualified",
        "evaluation_membrane_qualified",
        "feedback_lineage_qualified",
        "priority_policy_qualified",
        "negative_memory_qualified",
        "multidimensional_status_qualified",
        "bounded_orchestration_qualified",
    }
    missing = sorted(key for key in required_true if proof.get(key) is not True)
    status = "BLOCK" if missing else "AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED"
    return {
        "status": status,
        "missing_gates": missing,
        "authority": deepcopy(CLOSED_AUTHORITY),
        "economic_claim_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }
