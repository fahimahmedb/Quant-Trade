from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping

from research.research_os.engines.protocol import validate_engine_output

from .v2_core import V2ContractError, build_candidate, build_validator_result, canonical_hash


_FAMILY_MAP = {
    "FUNDAMENTAL": "fundamental",
    "EVENT_DOCUMENT": "event",
    "INSTITUTIONAL_FLOW": "forced_flow",
    "QUANT_MECHANISM": "quant",
}


def _documentary_packet(engine_output: Mapping[str, Any]) -> Dict[str, Any]:
    evidence = (engine_output.get("candidate") or {}).get("documentary_evidence") or {}
    packet = evidence.get("packet") or {}
    return deepcopy(packet) if isinstance(packet, dict) else {}


def adapt_engine_output_to_v2_candidate(
    engine_output: Mapping[str, Any],
    *,
    research_trial_id: str,
    research_epoch_id: str,
    producer_identity: Mapping[str, Any],
    disconfirmation_manifest: Mapping[str, Any],
) -> Dict[str, Any]:
    """Project an existing qualified producer output into CandidateCore V2.

    The bridge never invents outcome evidence. Unknown family-specific concepts
    remain explicit semantic nulls rather than being filled with causal prose.
    """
    raw = deepcopy(dict(engine_output))
    validate_engine_output(raw)
    engine_family = raw["engine_family"]
    if engine_family not in _FAMILY_MAP:
        raise V2ContractError("UNSUPPORTED_V1_ENGINE_FAMILY_FOR_V2_BRIDGE")
    candidate = raw["candidate"]
    packet = _documentary_packet(raw)
    source_refs = deepcopy(raw.get("source_refs") or [])
    if not source_refs:
        raise V2ContractError("V2_BRIDGE_REQUIRES_SOURCE_REFS")

    issuer = packet.get("issuer_id", "UNKNOWN")
    instrument = packet.get("instrument", "UNKNOWN")
    evidence_manifest = {
        "engine_id": raw["engine_id"],
        "engine_family": engine_family,
        "synthetic_only": raw["synthetic_only"],
        "source_refs": source_refs,
        "documentary_packet_hash": packet.get("content_hash", "NOT_APPLICABLE"),
        "evidence_class": packet.get("evidence_class", "UNKNOWN"),
    }
    clock = packet.get("available_at", candidate.get("evidence_timing", "UNRESOLVED"))
    horizon = candidate.get("horizon", packet.get("horizon", "UNRESOLVED"))
    economic_expression = {
        "instrument": instrument,
        "direction": "NOT_YET_MEASURABLE",
        "implementation_status": "NOT_YET_MEASURABLE",
    }

    family = _FAMILY_MAP[engine_family]
    if family == "fundamental":
        extension = {
            "type": "FundamentalExtension",
            "issuer": issuer,
            "business_driver": sorted(candidate.get("economic_tags") or []) or ["UNKNOWN"],
            "valuation_transmission": candidate["mechanism"],
        }
    elif family == "event":
        extension = {
            "type": "EventExtension",
            "event": packet.get("event_kind", "UNRESOLVED"),
            "availability_time": packet.get("available_at", "UNKNOWN"),
            "event_clock": clock,
            "reaction_channel": "UNRESOLVED",
            "revision_policy": packet.get("revision_status", "UNKNOWN"),
        }
    elif family == "forced_flow":
        extension = {
            "type": "ForcedFlowExtension",
            "forced_constrained_actor": packet.get("actor", "UNKNOWN"),
            "binding_constraint": packet.get("constraint", "UNRESOLVED"),
            "payer": "UNKNOWN",
            "instrument": instrument,
            "timing": packet.get("horizon", horizon),
        }
    else:
        extension = {
            "type": "QuantExtension",
            "signal_definition": candidate["mechanism"],
            "observation_clock": "UNRESOLVED",
            "decision_clock": "UNRESOLVED",
            "execution_clock": "UNRESOLVED",
            "data_route": source_refs,
            "multiplicity_family": raw["engine_id"],
        }

    v2 = {
        "hypothesis_id": candidate["hypothesis_id"],
        "generation_id": candidate["generation_id"],
        "research_trial_id": research_trial_id,
        "research_epoch_id": research_epoch_id,
        "family": family,
        "claim": candidate["claim"],
        "mechanism_statement": candidate["mechanism"],
        "universe": [issuer] if issuer != "UNKNOWN" else ["UNRESOLVED"],
        "clock": clock,
        "horizon": horizon,
        "economic_expression": economic_expression,
        "evidence_manifest": evidence_manifest,
        "falsification_scope": candidate["falsification_scope"],
        "decision_map": deepcopy(candidate["decision_map"]),
        "known_confounders": [],
        "disconfirmation_manifest": deepcopy(dict(disconfirmation_manifest)),
        "producer_identity": deepcopy(dict(producer_identity)),
        "extension": extension,
    }
    return build_candidate(v2)


def adapt_existing_validation_to_v2(
    *,
    v2_candidate: Mapping[str, Any],
    existing_validation: Mapping[str, Any],
    validator_identity: str,
    validator_version: str,
    validator_model: str,
    validator_prompt_hash: str,
    validator_context_hash: str,
    validator_retrieval_manifest_hash: str,
    producer_identity_hash: str,
    validator_state_identity_hash: str,
) -> Dict[str, Any]:
    """Bind an existing independent validation result to the V2 state model.

    Different identity hashes are required so a mere worker-name difference
    cannot masquerade as state isolation.
    """
    if producer_identity_hash == validator_state_identity_hash:
        raise V2ContractError("VALIDATOR_STATE_ISOLATION_NOT_PROVEN")
    status = existing_validation.get("status")
    if status not in {"PASS", "BLOCK"}:
        raise V2ContractError("EXISTING_VALIDATION_HAS_NO_SCIENTIFIC_DECISION")
    failures = list(existing_validation.get("failures") or existing_validation.get("critical_failures") or [])
    payload = {
        "hypothesis_id": v2_candidate["hypothesis_id"],
        "generation_id": v2_candidate["generation_id"],
        "validator_identity": validator_identity,
        "validator_version": validator_version,
        "validator_model": validator_model,
        "validator_prompt_hash": validator_prompt_hash,
        "validator_context_hash": validator_context_hash,
        "validator_retrieval_manifest_hash": validator_retrieval_manifest_hash,
        "execution_state": "COMPLETE",
        "scientific_decision": status,
        "epistemic_blockers": failures,
        "producer_identity_hash": producer_identity_hash,
        "validator_state_identity_hash": validator_state_identity_hash,
        "source_validation_hash": canonical_hash(existing_validation),
    }
    return build_validator_result(payload)
