"""MEGA C0 scientific adjudication kernel.

C0 is a downstream composition layer. It binds the qualified Candidate/Factory
identity to cross-examination, Validator, Red Team and independence receipts and
emits a deterministic North-Star verdict: PROMOTE / PARK / KILL / BLOCK.

It does not rebuild Factory, Validator, Red Team, discovery, Economic Identity,
runtime, or outcome evaluation. Raw outcomes and authority escalation are
forbidden at this boundary.
"""
from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Sequence

from research.research_os.scientific_store import sha256_json


WAVE2_IMMUTABLE_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
W1_FACTORY_FINAL_SHA = "dfaf0bd7be04926a2b16dc585ccb82699c6dd0e4"
VERDICTS = {"PROMOTE", "PARK", "KILL", "BLOCK"}
PROMOTION_TARGET = "ECONOMIC_IDENTITY"

AUTHORITY_STATE = MappingProxyType({
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
    "outcome_accessed": False,
})

CROSS_EXAMINATION_AXES = (
    "identity_ambiguity",
    "timing_ambiguity",
    "source_ambiguity",
    "pit_integrity",
    "implementation_assumptions",
    "duplicate_expression",
)
CROSS_AXIS_STATES = {"PASS", "UNKNOWN", "CONFLICTED", "BLOCK"}

INDEPENDENCE_AXES = (
    "information_isolation",
    "retrieval_independence",
    "cognitive_independence",
    "state_isolation",
)

_ALLOWED_RED_TEAM_BLOCKERS = {
    "BLOCK_DATA", "BLOCK_LEAKAGE", "BLOCK_CLOCK", "BLOCK_PIT",
    "BLOCK_MULTIPLICITY", "BLOCK_TRIAL_ACCOUNTING", "BLOCK_IMPLEMENTABILITY",
    "BLOCK_COST_MODEL", "BLOCK_CAPACITY", "BLOCK_CLAIM_LEVEL",
    "BLOCK_REPRODUCIBILITY", "BLOCK_ECONOMIC_IDENTITY",
    "BLOCK_PORTFOLIO_DUPLICATION",
}

_FORBIDDEN_OUTCOME_KEYS = {
    "pnl", "pnl_series", "profit", "profitability", "return", "returns",
    "return_series", "realized_return", "realized_return_series", "sharpe",
    "sortino", "alpha", "drawdown", "covariance", "empirical_correlation",
    "price", "prices", "price_series", "fill", "fills", "equity_curve",
    "realized_pnl", "unrealized_pnl", "hit_rate", "win_rate", "outcome",
    "outcomes", "raw_outcomes", "observed_outcomes",
}


class ScientificAdjudicationError(ValueError):
    """Raised when an input violates C0 identity/provenance/authority law."""


def authority_state() -> Dict[str, bool]:
    return dict(AUTHORITY_STATE)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ScientificAdjudicationError(message)


def _text(value: Any, name: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{name} must be a non-empty string")
    return value.strip()


def _hash_value(value: Any, name: str, lengths: Sequence[int] = (64,)) -> str:
    _require(isinstance(value, str), f"{name} must be a hash string")
    _require(len(value) in lengths, f"{name} must have length {tuple(lengths)}")
    _require(value.lower() == value, f"{name} must be lowercase hex")
    try:
        int(value, 16)
    except ValueError as error:
        raise ScientificAdjudicationError(f"{name} must be lowercase hex") from error
    return value


def _reject_outcomes(value: Any, path: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().casefold()
            if normalized in _FORBIDDEN_OUTCOME_KEYS:
                raise ScientificAdjudicationError(f"{path}.{key} is outcome-bearing and forbidden in C0")
            _reject_outcomes(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_outcomes(item, f"{path}[{index}]")


def _assert_authority_closed(mapping: Mapping[str, Any], prefix: str) -> None:
    for key, required in AUTHORITY_STATE.items():
        if key in mapping:
            _require(mapping.get(key) is required, f"{prefix}.{key} must remain {required}")
    for key in (
        "economic_test_authorized", "economic_claim_authorized",
        "outcome_access_authorized", "capital_authorized",
        "capital_allocation_authorized", "position_sizing_authorized",
        "orders_authorized", "outcomes_opened",
    ):
        if key in mapping:
            _require(mapping.get(key) is False, f"{prefix}.{key} must remain False")


def _record_hash(record: Mapping[str, Any], hash_key: str) -> str:
    payload = deepcopy(dict(record))
    payload.pop(hash_key, None)
    return sha256_json(payload)


def _validate_self_hash(record: Mapping[str, Any], hash_key: str, label: str) -> None:
    supplied = _hash_value(record.get(hash_key), f"{label}.{hash_key}")
    _require(_record_hash(record, hash_key) == supplied, f"{label} hash mismatch")


def bind_factory_ref(candidate: Mapping[str, Any], infrastructure: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind exact W1 Factory identity without recreating registry/freeze semantics."""
    _require(isinstance(candidate, Mapping), "candidate must be a mapping")
    _require(isinstance(infrastructure, Mapping), "experiment infrastructure must be a mapping")
    _reject_outcomes(candidate, "candidate")
    _reject_outcomes(infrastructure, "experiment_infrastructure")
    _assert_authority_closed(infrastructure, "experiment_infrastructure")

    hypothesis_id = _text(candidate.get("hypothesis_id"), "candidate.hypothesis_id")
    generation_id = _text(candidate.get("generation_id"), "candidate.generation_id")
    candidate_hash = sha256_json(dict(candidate))

    _require(infrastructure.get("status") == "PASS", "Factory experiment infrastructure is not PASS")
    _require(infrastructure.get("blockers") in ([], ()), "Factory experiment infrastructure has blockers")
    _require(infrastructure.get("outcome_accessed") is False, "Factory infrastructure accessed outcomes")
    _require(infrastructure.get("economic_result") == "NOT_OBSERVED", "Factory infrastructure carries an economic result")

    registry = infrastructure.get("registry")
    frozen_registry = infrastructure.get("frozen_registry")
    frozen_protocol = infrastructure.get("frozen_protocol")
    _require(all(isinstance(item, Mapping) for item in (registry, frozen_registry, frozen_protocol)),
             "Factory registry/frozen registry/frozen protocol are required")

    protocol_hash = _hash_value(frozen_protocol.get("protocol_hash"), "frozen_protocol.protocol_hash")
    _require(frozen_protocol.get("candidate_hash") == candidate_hash,
             "Factory frozen protocol candidate hash mismatch")
    frozen_protocol_hash = sha256_json(dict(frozen_protocol))

    for name, entry in (("registry", registry), ("frozen_registry", frozen_registry)):
        _require(entry.get("candidate_hash") == candidate_hash, f"Factory {name} candidate hash mismatch")
        _require(entry.get("protocol_hash") == protocol_hash, f"Factory {name} protocol hash mismatch")
        _require(entry.get("frozen_protocol_hash") == frozen_protocol_hash,
                 f"Factory {name} frozen protocol hash mismatch")
    _require(registry.get("registry_id") == frozen_registry.get("registry_id"),
             "Factory registry identity changed across freeze")

    infrastructure_hash = infrastructure.get("infrastructure_hash")
    if infrastructure_hash is not None:
        _hash_value(infrastructure_hash, "experiment_infrastructure.infrastructure_hash")
        _require(_record_hash(infrastructure, "infrastructure_hash") == infrastructure_hash,
                 "Factory infrastructure hash mismatch")
    else:
        infrastructure_hash = sha256_json(dict(infrastructure))

    ref = {
        "schema_version": "scientific-adjudication-factory-ref-v1",
        "hypothesis_id": hypothesis_id,
        "generation_id": generation_id,
        "candidate_hash": candidate_hash,
        "protocol_hash": protocol_hash,
        "frozen_protocol_hash": frozen_protocol_hash,
        "registry_id": _text(registry.get("registry_id"), "registry.registry_id"),
        "infrastructure_hash": infrastructure_hash,
        "w1_factory_final_sha": W1_FACTORY_FINAL_SHA,
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
        "economic_result": "NOT_OBSERVED",
        **authority_state(),
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_factory_ref(ref: Mapping[str, Any]) -> None:
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-adjudication-factory-ref-v1",
             "unsupported FactoryRef schema")
    for key in ("candidate_hash", "protocol_hash", "frozen_protocol_hash", "infrastructure_hash", "ref_hash"):
        _hash_value(ref.get(key), f"FactoryRef.{key}")
    _text(ref.get("hypothesis_id"), "FactoryRef.hypothesis_id")
    _text(ref.get("generation_id"), "FactoryRef.generation_id")
    _text(ref.get("registry_id"), "FactoryRef.registry_id")
    _require(ref.get("w1_factory_final_sha") == W1_FACTORY_FINAL_SHA, "FactoryRef W1 Factory SHA mismatch")
    _require(ref.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA, "FactoryRef Wave2 base mismatch")
    _require(ref.get("economic_result") == "NOT_OBSERVED", "FactoryRef economic result must be NOT_OBSERVED")
    _assert_authority_closed(ref, "FactoryRef")
    _validate_self_hash(ref, "ref_hash", "FactoryRef")


def build_cross_examination_ref(
    factory_ref: Mapping[str, Any],
    axes: Mapping[str, Mapping[str, Any]],
    *,
    examiner_id: str,
    provenance_refs: Sequence[str],
) -> Dict[str, Any]:
    """Build a bounded adversarial examination; UNKNOWN/CONFLICTED never become negative evidence."""
    validate_factory_ref(factory_ref)
    _require(isinstance(axes, Mapping), "cross-examination axes must be a mapping")
    _require(set(axes) == set(CROSS_EXAMINATION_AXES), "cross-examination axes are incomplete or contain extras")
    _require(isinstance(provenance_refs, (list, tuple)) and provenance_refs,
             "cross-examination requires provenance refs")
    normalized: Dict[str, Dict[str, Any]] = {}
    for axis in CROSS_EXAMINATION_AXES:
        record = axes[axis]
        _require(isinstance(record, Mapping), f"cross-examination axis {axis} must be a mapping")
        _reject_outcomes(record, f"cross_examination.{axis}")
        status = record.get("status")
        _require(status in CROSS_AXIS_STATES, f"invalid cross-examination state for {axis}")
        reason_codes = record.get("reason_codes", [])
        _require(isinstance(reason_codes, list) and all(isinstance(item, str) and item for item in reason_codes),
                 f"cross-examination {axis} reason_codes must be strings")
        normalized[axis] = {
            "status": status,
            "reason_codes": sorted(set(reason_codes)),
            "detail_ref": record.get("detail_ref"),
        }

    states = [record["status"] for record in normalized.values()]
    if any(state in {"BLOCK", "CONFLICTED"} for state in states):
        overall = "BLOCK"
    elif any(state == "UNKNOWN" for state in states):
        overall = "PARK"
    else:
        overall = "PASS"

    ref = {
        "schema_version": "scientific-cross-examination-ref-v1",
        "factory_ref_hash": factory_ref["ref_hash"],
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "examiner_id": _text(examiner_id, "examiner_id"),
        "axes": normalized,
        "status": overall,
        "material_blockers": sorted(
            axis for axis, record in normalized.items() if record["status"] in {"BLOCK", "CONFLICTED"}
        ),
        "bounded_uncertainties": sorted(
            axis for axis, record in normalized.items() if record["status"] == "UNKNOWN"
        ),
        "provenance_refs": sorted(set(_text(item, "provenance_ref") for item in provenance_refs)),
        "negative_claim_supported": False,
        "candidate_mutated": False,
        **authority_state(),
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_cross_examination_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    validate_factory_ref(factory_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-cross-examination-ref-v1",
             "unsupported CrossExaminationRef schema")
    _require(ref.get("factory_ref_hash") == factory_ref["ref_hash"], "cross-examination FactoryRef binding mismatch")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(ref.get(key) == factory_ref[key], f"cross-examination {key} mismatch")
    _require(ref.get("status") in {"PASS", "PARK", "BLOCK"}, "invalid cross-examination overall status")
    _require(ref.get("negative_claim_supported") is False, "cross-examination alone cannot support a negative claim")
    _require(ref.get("candidate_mutated") is False, "cross-examination mutated candidate")
    _assert_authority_closed(ref, "CrossExaminationRef")
    _reject_outcomes(ref.get("axes", {}), "CrossExaminationRef.axes")
    _validate_self_hash(ref, "ref_hash", "CrossExaminationRef")


def bind_validator_ref(factory_ref: Mapping[str, Any], receipt: Mapping[str, Any]) -> Dict[str, Any]:
    validate_factory_ref(factory_ref)
    _require(isinstance(receipt, Mapping), "validator receipt must be a mapping")
    _reject_outcomes(receipt, "validator_receipt")
    _assert_authority_closed(receipt, "validator_receipt")
    _require(receipt.get("status") in {"READY_FOR_AUTHORIZED_ECONOMIC_TEST", "BLOCK"},
             "validator receipt status is outside canonical readiness contract")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash"):
        _require(receipt.get(key) == factory_ref[key], f"validator receipt {key} mismatch")
    _require(receipt.get("candidate_mutated") is False, "validator mutated candidate")
    _require(receipt.get("economic_test_authorized") is False, "validator opened economic-test authority")
    _require(receipt.get("economic_claim_authorized") is False, "validator opened economic-claim authority")
    _require(receipt.get("outcome_access_authorized") is False, "validator opened outcome authority")

    ref = {
        "schema_version": "scientific-validator-ref-v1",
        "factory_ref_hash": factory_ref["ref_hash"],
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "validator_id": _text(receipt.get("validator"), "validator_receipt.validator"),
        "status": receipt["status"],
        "block_reasons": deepcopy(receipt.get("block_reasons", [])),
        "checks_hash": sha256_json(receipt.get("checks", {})),
        "receipt_hash": sha256_json(dict(receipt)),
        "ready_for_authorized_economic_test": receipt.get("ready_for_authorized_economic_test") is True,
        "candidate_mutated": False,
        **authority_state(),
    }
    if ref["status"] == "READY_FOR_AUTHORIZED_ECONOMIC_TEST":
        _require(ref["ready_for_authorized_economic_test"] is True, "validator READY status/readiness flag mismatch")
        _require(not ref["block_reasons"], "validator READY receipt carries block reasons")
    else:
        _require(ref["ready_for_authorized_economic_test"] is False, "validator BLOCK status/readiness flag mismatch")
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_validator_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    validate_factory_ref(factory_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-validator-ref-v1",
             "unsupported ValidatorRef schema")
    _require(ref.get("factory_ref_hash") == factory_ref["ref_hash"], "ValidatorRef FactoryRef binding mismatch")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(ref.get(key) == factory_ref[key], f"ValidatorRef {key} mismatch")
    _require(ref.get("status") in {"READY_FOR_AUTHORIZED_ECONOMIC_TEST", "BLOCK"}, "invalid ValidatorRef status")
    _require(ref.get("candidate_mutated") is False, "ValidatorRef records candidate mutation")
    _assert_authority_closed(ref, "ValidatorRef")
    _validate_self_hash(ref, "ref_hash", "ValidatorRef")


def bind_red_team_ref(
    factory_ref: Mapping[str, Any], validator_ref: Mapping[str, Any], receipt: Mapping[str, Any]
) -> Dict[str, Any]:
    validate_validator_ref(validator_ref, factory_ref)
    _require(isinstance(receipt, Mapping), "Red Team receipt must be a mapping")
    _reject_outcomes(receipt, "red_team_receipt")
    _assert_authority_closed(receipt, "red_team_receipt")
    _require(receipt.get("status") in {"PASS", "BLOCK"}, "Red Team status must be PASS or BLOCK")
    for key in ("hypothesis_id", "generation_id"):
        _require(receipt.get(key) == factory_ref[key], f"Red Team {key} mismatch")
    rights = receipt.get("negative_rights", [])
    _require(isinstance(rights, list) and set(rights) <= _ALLOWED_RED_TEAM_BLOCKERS,
             "Red Team emitted blocker outside negative-rights contract")
    _require(receipt.get("repair_attempted") is False, "Red Team attempted repair")
    _require(receipt.get("signal_repair_attempted") is False, "Red Team attempted signal repair")
    _require(receipt.get("candidate_mutated") is False, "Red Team mutated candidate")
    _require(receipt.get("validator_receipt_mutated") is False, "Red Team mutated validator receipt")
    _require(receipt.get("parameters_optimized") is False, "Red Team optimized parameters")
    _require(receipt.get("retuned_until_profitable") is False, "Red Team retuned until profitable")
    _require(receipt.get("outcomes_opened") is False, "Red Team opened outcomes")
    if receipt["status"] == "PASS":
        _require(not rights, "Red Team PASS receipt carries negative rights")
    else:
        _require(bool(rights), "Red Team BLOCK receipt has no blocker")

    ref = {
        "schema_version": "scientific-red-team-ref-v1",
        "factory_ref_hash": factory_ref["ref_hash"],
        "validator_ref_hash": validator_ref["ref_hash"],
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "red_team_id": _text(receipt.get("red_team"), "red_team_receipt.red_team"),
        "status": receipt["status"],
        "negative_rights": sorted(set(rights)),
        "receipt_hash": sha256_json(dict(receipt)),
        "negative_claim_supported": False,
        **authority_state(),
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_red_team_ref(
    ref: Mapping[str, Any], factory_ref: Mapping[str, Any], validator_ref: Mapping[str, Any]
) -> None:
    validate_validator_ref(validator_ref, factory_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-red-team-ref-v1",
             "unsupported RedTeamRef schema")
    _require(ref.get("factory_ref_hash") == factory_ref["ref_hash"], "RedTeamRef FactoryRef binding mismatch")
    _require(ref.get("validator_ref_hash") == validator_ref["ref_hash"], "RedTeamRef ValidatorRef binding mismatch")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(ref.get(key) == factory_ref[key], f"RedTeamRef {key} mismatch")
    _require(ref.get("status") in {"PASS", "BLOCK"}, "invalid RedTeamRef status")
    _require(ref.get("negative_claim_supported") is False, "Red Team alone cannot support a negative claim")
    _assert_authority_closed(ref, "RedTeamRef")
    _validate_self_hash(ref, "ref_hash", "RedTeamRef")


def bind_independence_ref(factory_ref: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind existing independence proof; duplicate/commentary support never increases independence."""
    validate_factory_ref(factory_ref)
    _require(isinstance(record, Mapping), "independence record must be a mapping")
    _reject_outcomes(record, "independence_record")
    _assert_authority_closed(record, "independence_record")
    axis_values = {axis: record.get(axis) is True for axis in INDEPENDENCE_AXES}
    structural_proven = all(axis_values.values()) and record.get("outcome_accessed") is False
    retrieval = record.get("retrieval") if isinstance(record.get("retrieval"), Mapping) else {}
    reconstructed_hash = retrieval.get("reconstructed_v2_candidate_hash") or retrieval.get("reconstructed_candidate_hash")
    if reconstructed_hash is not None:
        _hash_value(reconstructed_hash, "independence reconstructed candidate hash")
    support_relation = record.get("support_relation", "PRIMARY_SOURCE_RECONSTRUCTION")
    _require(support_relation in {"PRIMARY_SOURCE_RECONSTRUCTION", "DUPLICATE", "WRAPPER_EQUIVALENT", "UNKNOWN"},
             "invalid independence support relation")
    semantic_diverse_review = record.get("semantic_diverse_review", "NOT_PROVEN")
    semantic_review_proven = semantic_diverse_review == "PROVEN_INDEPENDENT_SEMANTIC_REVIEW"
    independent_confirmation = (
        structural_proven
        and support_relation == "PRIMARY_SOURCE_RECONSTRUCTION"
        and semantic_review_proven
    )
    ref = {
        "schema_version": "scientific-independence-ref-v1",
        "factory_ref_hash": factory_ref["ref_hash"],
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "axes": axis_values,
        "structural_independence_proven": structural_proven,
        "support_relation": support_relation,
        "independent_confirmation_count": 1 if independent_confirmation else 0,
        "semantic_diverse_review": semantic_diverse_review,
        "semantic_independent_confirmation_proven": semantic_review_proven,
        "information_scope": record.get("information_scope"),
        "cognitive_scope": record.get("cognitive_scope"),
        "record_hash": sha256_json(dict(record)),
        **authority_state(),
    }
    ref["status"] = "PASS" if structural_proven else "BLOCK"
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_independence_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    validate_factory_ref(factory_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-independence-ref-v1",
             "unsupported IndependenceRef schema")
    _require(ref.get("factory_ref_hash") == factory_ref["ref_hash"], "IndependenceRef FactoryRef binding mismatch")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(ref.get(key) == factory_ref[key], f"IndependenceRef {key} mismatch")
    _require(ref.get("status") in {"PASS", "BLOCK"}, "invalid IndependenceRef status")
    if ref.get("support_relation") in {"DUPLICATE", "WRAPPER_EQUIVALENT", "UNKNOWN"}:
        _require(ref.get("independent_confirmation_count") == 0,
                 "duplicate/wrapper/unknown support cannot count as independent confirmation")
    if ref.get("semantic_independent_confirmation_proven") is not True:
        _require(ref.get("independent_confirmation_count") == 0,
                 "unproven semantic review cannot count as independent confirmation")
    _assert_authority_closed(ref, "IndependenceRef")
    _validate_self_hash(ref, "ref_hash", "IndependenceRef")


def bind_qualified_negative_ref(factory_ref: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind a qualified external negative disposition without accepting raw outcomes.

    This is the *only* path that can support KILL. It is deliberately external to
    C0 and carries only an opaque evidence hash plus scoped disposition metadata.
    """
    validate_factory_ref(factory_ref)
    _require(isinstance(record, Mapping), "qualified negative record must be a mapping")
    _reject_outcomes(record, "qualified_negative_record")
    _assert_authority_closed(record, "qualified_negative_record")
    _require(record.get("status") == "QUALIFIED_NEGATIVE", "negative record is not qualified")
    _require(record.get("disposition") == "KILL", "qualified negative disposition must be KILL")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(record.get(key) == factory_ref[key], f"qualified negative {key} mismatch")
    _require(record.get("issued_by_c0") is False, "C0 may not self-issue qualified negative evidence")
    _require(record.get("raw_outcomes_included") is False, "raw outcomes cannot cross C0 negative-evidence boundary")
    _require(record.get("outcome_accessed_by_c0") is False, "C0 may not access outcomes")
    _require(record.get("negative_knowledge_global") is False, "negative knowledge may not be global by default")
    scope = _text(record.get("negative_knowledge_scope"), "negative_knowledge_scope")
    _require(scope.upper() != "GLOBAL", "negative knowledge scope must be bounded")
    evidence_hash = _hash_value(record.get("evidence_hash"), "qualified negative evidence_hash")
    evaluator_id = _text(record.get("evaluator_id"), "qualified negative evaluator_id")

    ref = {
        "schema_version": "scientific-qualified-negative-ref-v1",
        "factory_ref_hash": factory_ref["ref_hash"],
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "status": "QUALIFIED_NEGATIVE",
        "disposition": "KILL",
        "evidence_hash": evidence_hash,
        "evaluator_id": evaluator_id,
        "negative_knowledge_scope": scope,
        "negative_knowledge_global": False,
        "raw_outcomes_included": False,
        "issued_by_c0": False,
        **authority_state(),
    }
    ref["ref_hash"] = sha256_json(ref)
    return ref


def validate_qualified_negative_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    validate_factory_ref(factory_ref)
    _require(isinstance(ref, Mapping) and ref.get("schema_version") == "scientific-qualified-negative-ref-v1",
             "unsupported QualifiedNegativeRef schema")
    _require(ref.get("factory_ref_hash") == factory_ref["ref_hash"], "QualifiedNegativeRef FactoryRef binding mismatch")
    for key in ("hypothesis_id", "generation_id", "candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(ref.get(key) == factory_ref[key], f"QualifiedNegativeRef {key} mismatch")
    _require(ref.get("status") == "QUALIFIED_NEGATIVE" and ref.get("disposition") == "KILL",
             "QualifiedNegativeRef disposition invalid")
    _require(ref.get("negative_knowledge_global") is False, "QualifiedNegativeRef globalized negative knowledge")
    _require(ref.get("raw_outcomes_included") is False, "QualifiedNegativeRef contains raw outcomes")
    _require(ref.get("issued_by_c0") is False, "QualifiedNegativeRef was self-issued by C0")
    _assert_authority_closed(ref, "QualifiedNegativeRef")
    _validate_self_hash(ref, "ref_hash", "QualifiedNegativeRef")


def adjudicate_scientific_candidate(
    factory_ref: Mapping[str, Any],
    *,
    cross_examination_ref: Optional[Mapping[str, Any]] = None,
    validator_ref: Optional[Mapping[str, Any]] = None,
    red_team_ref: Optional[Mapping[str, Any]] = None,
    independence_ref: Optional[Mapping[str, Any]] = None,
    qualified_negative_ref: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Compose exact pre-economic scientific state into one canonical verdict."""
    validate_factory_ref(factory_ref)
    missing = []
    if cross_examination_ref is None:
        missing.append("CROSS_EXAMINATION_UNEXECUTED")
    if validator_ref is None:
        missing.append("VALIDATOR_UNEXECUTED")
    if red_team_ref is None:
        missing.append("RED_TEAM_UNEXECUTED")
    if independence_ref is None:
        missing.append("INDEPENDENCE_UNPROVEN")

    if cross_examination_ref is not None:
        validate_cross_examination_ref(cross_examination_ref, factory_ref)
    if validator_ref is not None:
        validate_validator_ref(validator_ref, factory_ref)
    if red_team_ref is not None:
        _require(validator_ref is not None, "RedTeamRef cannot be validated without ValidatorRef")
        validate_red_team_ref(red_team_ref, factory_ref, validator_ref)
    if independence_ref is not None:
        validate_independence_ref(independence_ref, factory_ref)
    if qualified_negative_ref is not None:
        validate_qualified_negative_ref(qualified_negative_ref, factory_ref)

    blockers = list(missing)
    park_reasons = []
    if cross_examination_ref is not None:
        if cross_examination_ref["status"] == "BLOCK":
            blockers.extend(f"CROSS_EXAM_{item}" for item in cross_examination_ref["material_blockers"])
        elif cross_examination_ref["status"] == "PARK":
            park_reasons.extend(f"CROSS_EXAM_UNKNOWN_{item}" for item in cross_examination_ref["bounded_uncertainties"])
    if validator_ref is not None and validator_ref["status"] != "READY_FOR_AUTHORIZED_ECONOMIC_TEST":
        blockers.append("VALIDATOR_BLOCK")
    if red_team_ref is not None and red_team_ref["status"] != "PASS":
        blockers.extend(f"RED_TEAM_{item}" for item in red_team_ref["negative_rights"])
    if independence_ref is not None and independence_ref["status"] != "PASS":
        blockers.append("VALIDATOR_INDEPENDENCE_NOT_PROVEN")

    structurally_clear = not blockers and not park_reasons
    if qualified_negative_ref is not None and structurally_clear:
        verdict = "KILL"
        reasons = ["QUALIFIED_SCOPED_NEGATIVE_SCIENTIFIC_DISPOSITION"]
    elif blockers:
        verdict = "BLOCK"
        reasons = sorted(set(blockers))
    elif park_reasons:
        verdict = "PARK"
        reasons = sorted(set(park_reasons))
    else:
        verdict = "PROMOTE"
        reasons = ["SCIENTIFIC_ADJUDICATION_COMPLETE"]

    components = {
        "factory_ref_hash": factory_ref["ref_hash"],
        "cross_examination_ref_hash": cross_examination_ref.get("ref_hash") if cross_examination_ref else None,
        "validator_ref_hash": validator_ref.get("ref_hash") if validator_ref else None,
        "red_team_ref_hash": red_team_ref.get("ref_hash") if red_team_ref else None,
        "independence_ref_hash": independence_ref.get("ref_hash") if independence_ref else None,
        "qualified_negative_ref_hash": qualified_negative_ref.get("ref_hash") if qualified_negative_ref else None,
    }
    identity_payload = {
        "schema_version": "scientific-adjudication-identity-v1",
        "wave2_base_sha": WAVE2_IMMUTABLE_BASE_SHA,
        "hypothesis_id": factory_ref["hypothesis_id"],
        "generation_id": factory_ref["generation_id"],
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "components": components,
    }
    adjudication_identity = sha256_json(identity_payload)
    result = {
        "schema_version": "scientific-adjudication-v1",
        "adjudication_identity": adjudication_identity,
        "identity": identity_payload,
        "verdict": verdict,
        "reason_codes": reasons,
        "promotion_target": PROMOTION_TARGET if verdict == "PROMOTE" else None,
        "economic_identity_created": False,
        "economic_result": "NOT_OBSERVED",
        "profitability_status": "UNKNOWN",
        "ready_is_profitable": False,
        "unexecuted_is_negative": False,
        "blocked_is_failed": False,
        "negative_knowledge_global": False,
        "independent_confirmation_count": (
            independence_ref.get("independent_confirmation_count", 0) if independence_ref else 0
        ),
        "semantic_independent_confirmation_proven": (
            independence_ref.get("semantic_independent_confirmation_proven", False)
            if independence_ref else False
        ),
        "scientific_negative_claim": verdict == "KILL",
        "raw_outcomes_consumed": 0,
        "candidate_mutated": False,
        "protocol_mutated": False,
        **authority_state(),
    }
    result["adjudication_hash"] = sha256_json(result)
    validate_adjudication(result)
    return result


def validate_adjudication(result: Mapping[str, Any]) -> None:
    _require(isinstance(result, Mapping) and result.get("schema_version") == "scientific-adjudication-v1",
             "unsupported scientific adjudication schema")
    _require(result.get("verdict") in VERDICTS, "invalid scientific verdict")
    identity = result.get("identity")
    _require(isinstance(identity, Mapping), "adjudication identity payload missing")
    _require(identity.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA, "adjudication Wave2 base mismatch")
    _require(result.get("adjudication_identity") == sha256_json(dict(identity)), "adjudication identity mismatch")
    if result["verdict"] == "PROMOTE":
        _require(result.get("promotion_target") == PROMOTION_TARGET, "PROMOTE target must be Economic Identity")
        components = identity.get("components") or {}
        _require(all(components.get(key) is not None for key in (
            "cross_examination_ref_hash", "validator_ref_hash", "red_team_ref_hash", "independence_ref_hash"
        )), "PROMOTE requires all scientific components")
    else:
        _require(result.get("promotion_target") is None, "non-PROMOTE verdict cannot carry a promotion target")
    _require(result.get("economic_identity_created") is False, "C0 may not create Economic Identity")
    _require(result.get("economic_result") == "NOT_OBSERVED", "C0 may not carry economic results")
    _require(result.get("profitability_status") == "UNKNOWN", "C0 may not infer profitability")
    _require(result.get("raw_outcomes_consumed") == 0, "C0 may not consume raw outcomes")
    _require(result.get("candidate_mutated") is False and result.get("protocol_mutated") is False,
             "C0 may not mutate candidate/protocol state")
    _assert_authority_closed(result, "adjudication")
    _validate_self_hash(result, "adjudication_hash", "adjudication")
