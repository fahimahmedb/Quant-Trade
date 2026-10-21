"""Canonical Wave-2 C2 scientific adjudication surface.

This module is an INTERNAL_ADAPT of the qualified historical MEGA C0 kernel.
The qualified source is preserved bit-for-bit in `_scientific_adjudication_c0`.
C2 rebinds campaign identity to the repaired immutable Wave-2 base and adds
fail-closed scientific membranes required by the canonical campaign:

* comprehensive cross-examination axes;
* exact frozen-identity and independence checks for Validator / Red Team;
* immutable external provenance for a qualified negative disposition;
* provenance/claim-ceiling/uncertainty preserving final scientific posture.

It does not create outcomes, economic identity, portfolio facts, runtime work,
or any trading/capital authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional, Sequence

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion import _scientific_adjudication_c0 as _impl


WAVE2_IMMUTABLE_BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"
HISTORICAL_C0_BASE_SHA = "97165db2faa3300cef1f23de0045ed93d25eb9cb"
QUALIFIED_HISTORICAL_C0_SOURCE_BLOB = "3f0e1b7bae53e9513f0061cabcfae2505a6795f3"
W1_FACTORY_FINAL_SHA = _impl.W1_FACTORY_FINAL_SHA
VERDICTS = _impl.VERDICTS
PROMOTION_TARGET = _impl.PROMOTION_TARGET
AUTHORITY_STATE = _impl.AUTHORITY_STATE
ScientificAdjudicationError = _impl.ScientificAdjudicationError

# Canonical C2 examination is intentionally broader than the historical C0
# lane. UNKNOWN remains UNKNOWN/PARK; it is never promoted to a negative fact.
CROSS_EXAMINATION_AXES = (
    "identity_ambiguity",
    "timing_ambiguity",
    "source_ambiguity",
    "pit_integrity",
    "implementation_assumptions",
    "duplicate_expression",
    "universe_selection",
    "trial_accounting",
    "factor_beta_exposure",
    "negative_knowledge_scope",
    "causal_payer_actor",
    "cost_capacity",
    "falsifiability",
    "evidence_contradictions",
)
CROSS_AXIS_STATES = _impl.CROSS_AXIS_STATES
INDEPENDENCE_AXES = _impl.INDEPENDENCE_AXES
SCIENTIFIC_POSTURES = {
    "REJECT",
    "INCONCLUSIVE",
    "BLOCKED",
    "QUALIFIED_WITH_CLAIM_CEILING",
}

# Rebind only campaign identity and the cross-examination contract inside the
# preserved implementation. All other historical code stays byte-identical.
_impl.WAVE2_IMMUTABLE_BASE_SHA = WAVE2_IMMUTABLE_BASE_SHA
_impl.CROSS_EXAMINATION_AXES = CROSS_EXAMINATION_AXES

_original_bind_factory_ref = _impl.bind_factory_ref
_original_validate_factory_ref = _impl.validate_factory_ref
_original_bind_validator_ref = _impl.bind_validator_ref
_original_validate_validator_ref = _impl.validate_validator_ref
_original_bind_red_team_ref = _impl.bind_red_team_ref
_original_validate_red_team_ref = _impl.validate_red_team_ref
_original_bind_qualified_negative_ref = _impl.bind_qualified_negative_ref
_original_validate_qualified_negative_ref = _impl.validate_qualified_negative_ref
_original_adjudicate = _impl.adjudicate_scientific_candidate
_original_validate_adjudication = _impl.validate_adjudication


def authority_state() -> Dict[str, bool]:
    return _impl.authority_state()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ScientificAdjudicationError(message)


def _text(value: Any, name: str) -> str:
    _require(isinstance(value, str) and bool(value.strip()), f"{name} must be a non-empty string")
    return value.strip()


def _git_commit_sha(value: Any, name: str) -> str:
    value = _text(value, name)
    _require(len(value) == 40 and value.lower() == value, f"{name} must be a 40-char lowercase git SHA")
    try:
        int(value, 16)
    except ValueError as error:
        raise ScientificAdjudicationError(f"{name} must be a 40-char lowercase git SHA") from error
    return value


def _rehash(record: Mapping[str, Any], hash_key: str) -> str:
    payload = deepcopy(dict(record))
    payload.pop(hash_key, None)
    return sha256_json(payload)


def _candidate_scientific_context(candidate: Mapping[str, Any]) -> Dict[str, Any]:
    discovery = candidate.get("discovery") if isinstance(candidate.get("discovery"), Mapping) else {}
    provenance = candidate.get("provenance")
    if provenance is None:
        provenance = discovery.get("provenance")
    ancestry = candidate.get("ancestry")
    if ancestry is None:
        ancestry = discovery.get("ancestry")
    expression = candidate.get("expression_identity")
    if expression is None:
        expression = discovery.get("expression_identity")
    claim_ceiling = candidate.get("claim_ceiling")
    if claim_ceiling in (None, ""):
        claim_ceiling = discovery.get("claim_ceiling", "UNKNOWN")
    trial_id = candidate.get("trial_id", "UNKNOWN")
    experiment_epoch = candidate.get("experiment_epoch", candidate.get("epoch", "UNKNOWN"))
    return {
        "trial_id": trial_id if trial_id not in (None, "") else "UNKNOWN",
        "experiment_epoch": experiment_epoch if experiment_epoch not in (None, "") else "UNKNOWN",
        "frozen_expression_hash": sha256_json(expression) if expression is not None else "UNKNOWN",
        "provenance_hash": sha256_json(provenance) if provenance is not None else "UNKNOWN",
        "ancestry_hash": sha256_json(ancestry) if ancestry is not None else "UNKNOWN",
        "claim_ceiling": str(claim_ceiling) if claim_ceiling not in (None, "") else "UNKNOWN",
        "falsifiers_hash": sha256_json(
            candidate.get("falsifiers", candidate.get("falsification_scope", []))
        ),
        "evidence_gaps_hash": sha256_json(
            candidate.get("evidence_gaps", discovery.get("evidence_gaps", []))
        ),
    }


def bind_factory_ref(candidate: Mapping[str, Any], infrastructure: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind exact W1 Factory law and preserve scientific context without rebuilding it."""
    ref = _original_bind_factory_ref(candidate, infrastructure)
    ref["scientific_context"] = _candidate_scientific_context(candidate)
    ref["canonical_wave2_rebind_from"] = HISTORICAL_C0_BASE_SHA
    ref["qualified_historical_source_blob"] = QUALIFIED_HISTORICAL_C0_SOURCE_BLOB
    ref["ref_hash"] = _rehash(ref, "ref_hash")
    validate_factory_ref(ref)
    return ref


def validate_factory_ref(ref: Mapping[str, Any]) -> None:
    _original_validate_factory_ref(ref)
    _require(ref.get("wave2_base_sha") == WAVE2_IMMUTABLE_BASE_SHA, "FactoryRef canonical Wave2 base mismatch")
    context = ref.get("scientific_context")
    _require(isinstance(context, Mapping), "FactoryRef scientific context is missing")
    for key in (
        "trial_id", "experiment_epoch", "frozen_expression_hash", "provenance_hash",
        "ancestry_hash", "claim_ceiling", "falsifiers_hash", "evidence_gaps_hash",
    ):
        _require(key in context, f"FactoryRef scientific context missing {key}")
    _require(ref.get("qualified_historical_source_blob") == QUALIFIED_HISTORICAL_C0_SOURCE_BLOB,
             "FactoryRef qualified historical source identity mismatch")


# Install the stricter factory validator for all preserved downstream helpers.
_impl.validate_factory_ref = validate_factory_ref


def build_cross_examination_ref(
    factory_ref: Mapping[str, Any],
    axes: Mapping[str, Mapping[str, Any]],
    *,
    examiner_id: str,
    provenance_refs: Sequence[str],
) -> Dict[str, Any]:
    return _impl.build_cross_examination_ref(
        factory_ref, axes, examiner_id=examiner_id, provenance_refs=provenance_refs
    )


def validate_cross_examination_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    _impl.validate_cross_examination_ref(ref, factory_ref)
    _require(set(ref.get("axes", {})) == set(CROSS_EXAMINATION_AXES),
             "CrossExaminationRef does not cover the canonical C2 axes")


def bind_validator_ref(factory_ref: Mapping[str, Any], receipt: Mapping[str, Any]) -> Dict[str, Any]:
    """Bind an independent Validator receipt to the exact frozen identity."""
    validate_factory_ref(factory_ref)
    _require(isinstance(receipt, Mapping), "validator receipt must be a mapping")
    validator_id = _text(receipt.get("validator"), "validator_receipt.validator")
    producer_id = _text(receipt.get("producer_id"), "validator_receipt.producer_id")
    _require(validator_id != producer_id, "validator may not self-validate the producer")
    _require(receipt.get("validator_independent") is True, "validator independence is not proven")
    _require(receipt.get("self_validation") is False, "self-validation must be explicitly false")
    _require(receipt.get("frozen_protocol_hash") == factory_ref["frozen_protocol_hash"],
             "validator receipt frozen protocol hash mismatch")
    _require(receipt.get("outcome_accessed") is False, "validator may not access outcomes in C0")
    _require(receipt.get("post_outcome_mutation") is False, "validator receipt records post-outcome mutation")
    ref = _original_bind_validator_ref(factory_ref, receipt)
    ref.update({
        "producer_id": producer_id,
        "validator_independent": True,
        "self_validation": False,
        "frozen_identity_verified": True,
        "post_outcome_mutation": False,
    })
    ref["ref_hash"] = _rehash(ref, "ref_hash")
    validate_validator_ref(ref, factory_ref)
    return ref


def validate_validator_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    _original_validate_validator_ref(ref, factory_ref)
    _require(ref.get("validator_independent") is True, "ValidatorRef independence not proven")
    _require(ref.get("self_validation") is False, "ValidatorRef self-validation is forbidden")
    _require(ref.get("frozen_identity_verified") is True, "ValidatorRef frozen identity is not verified")
    _require(ref.get("post_outcome_mutation") is False, "ValidatorRef contains post-outcome mutation")
    _require(ref.get("validator_id") != ref.get("producer_id"), "ValidatorRef validator equals producer")


_impl.validate_validator_ref = validate_validator_ref


def bind_red_team_ref(
    factory_ref: Mapping[str, Any], validator_ref: Mapping[str, Any], receipt: Mapping[str, Any]
) -> Dict[str, Any]:
    """Bind Red Team to exact frozen identity and keep it independent of Validator."""
    validate_validator_ref(validator_ref, factory_ref)
    _require(isinstance(receipt, Mapping), "Red Team receipt must be a mapping")
    red_team_id = _text(receipt.get("red_team"), "red_team_receipt.red_team")
    _require(red_team_id != validator_ref.get("validator_id"), "Red Team may not be the Validator")
    _require(receipt.get("red_team_independent") is True, "Red Team independence is not proven")
    _require(receipt.get("self_red_team") is False, "self Red-Team review must be explicitly false")
    for key in ("candidate_hash", "protocol_hash", "frozen_protocol_hash"):
        _require(receipt.get(key) == factory_ref[key], f"Red Team exact {key} mismatch")
    _require(receipt.get("outcome_accessed") is False, "Red Team may not access outcomes in C0")
    _require(receipt.get("post_outcome_mutation") is False, "Red Team receipt records post-outcome mutation")
    ref = _original_bind_red_team_ref(factory_ref, validator_ref, receipt)
    ref.update({
        "red_team_independent": True,
        "self_red_team": False,
        "frozen_identity_verified": True,
        "post_outcome_mutation": False,
        "scientific_posture": (
            "QUALIFIED_WITH_CLAIM_CEILING" if ref["status"] == "PASS" else "BLOCKED"
        ),
    })
    ref["ref_hash"] = _rehash(ref, "ref_hash")
    validate_red_team_ref(ref, factory_ref, validator_ref)
    return ref


def validate_red_team_ref(
    ref: Mapping[str, Any], factory_ref: Mapping[str, Any], validator_ref: Mapping[str, Any]
) -> None:
    _original_validate_red_team_ref(ref, factory_ref, validator_ref)
    _require(ref.get("red_team_independent") is True, "RedTeamRef independence not proven")
    _require(ref.get("self_red_team") is False, "RedTeamRef self-review is forbidden")
    _require(ref.get("frozen_identity_verified") is True, "RedTeamRef frozen identity is not verified")
    _require(ref.get("post_outcome_mutation") is False, "RedTeamRef contains post-outcome mutation")
    _require(ref.get("scientific_posture") in {"QUALIFIED_WITH_CLAIM_CEILING", "BLOCKED"},
             "RedTeamRef scientific posture invalid")


_impl.validate_red_team_ref = validate_red_team_ref


def bind_independence_ref(factory_ref: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    return _impl.bind_independence_ref(factory_ref, record)


def validate_independence_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    _impl.validate_independence_ref(ref, factory_ref)


def bind_qualified_negative_ref(factory_ref: Mapping[str, Any], record: Mapping[str, Any]) -> Dict[str, Any]:
    """Accept only externally issued, immutable, scoped negative scientific evidence."""
    validate_factory_ref(factory_ref)
    _require(isinstance(record, Mapping), "qualified negative record must be a mapping")
    evaluator_id = _text(record.get("evaluator_id"), "qualified negative evaluator_id")
    _require(evaluator_id.casefold() not in {"c0", "mega-c0", "scientific-adjudication-c0"},
             "C0 may not act as the external negative evaluator")
    _require(record.get("evaluator_authority_kind") == "GIT_COMMIT_PATH",
             "qualified negative evidence requires immutable evaluator authority")
    authority_commit = _git_commit_sha(
        record.get("evaluator_authority_commit_sha"), "qualified negative evaluator authority commit"
    )
    authority_path = _text(
        record.get("evaluator_authority_path"), "qualified negative evaluator authority path"
    )
    ref = _original_bind_qualified_negative_ref(factory_ref, record)
    ref.update({
        "evaluator_authority_kind": "GIT_COMMIT_PATH",
        "evaluator_authority_commit_sha": authority_commit,
        "evaluator_authority_path": authority_path,
        "evaluator_authority_hash": sha256_json({
            "kind": "GIT_COMMIT_PATH",
            "commit_sha": authority_commit,
            "path": authority_path,
            "evaluator_id": evaluator_id,
        }),
        "outcome_accessed_by_c0": False,
    })
    ref["ref_hash"] = _rehash(ref, "ref_hash")
    validate_qualified_negative_ref(ref, factory_ref)
    return ref


def validate_qualified_negative_ref(ref: Mapping[str, Any], factory_ref: Mapping[str, Any]) -> None:
    _original_validate_qualified_negative_ref(ref, factory_ref)
    _require(ref.get("evaluator_authority_kind") == "GIT_COMMIT_PATH",
             "QualifiedNegativeRef lacks immutable evaluator authority")
    commit_sha = _git_commit_sha(
        ref.get("evaluator_authority_commit_sha"), "QualifiedNegativeRef evaluator authority commit"
    )
    path = _text(ref.get("evaluator_authority_path"), "QualifiedNegativeRef evaluator authority path")
    expected = sha256_json({
        "kind": "GIT_COMMIT_PATH",
        "commit_sha": commit_sha,
        "path": path,
        "evaluator_id": ref.get("evaluator_id"),
    })
    _require(ref.get("evaluator_authority_hash") == expected,
             "QualifiedNegativeRef evaluator authority hash mismatch")
    _require(ref.get("outcome_accessed_by_c0") is False, "QualifiedNegativeRef records C0 outcome access")


_impl.validate_qualified_negative_ref = validate_qualified_negative_ref


def _posture_for(verdict: str) -> str:
    return {
        "PROMOTE": "QUALIFIED_WITH_CLAIM_CEILING",
        "PARK": "INCONCLUSIVE",
        "BLOCK": "BLOCKED",
        "KILL": "REJECT",
    }[verdict]


def adjudicate_scientific_candidate(
    factory_ref: Mapping[str, Any],
    *,
    cross_examination_ref: Optional[Mapping[str, Any]] = None,
    validator_ref: Optional[Mapping[str, Any]] = None,
    red_team_ref: Optional[Mapping[str, Any]] = None,
    independence_ref: Optional[Mapping[str, Any]] = None,
    qualified_negative_ref: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Compose exact pre-economic state into a provenance-preserving posture."""
    validate_factory_ref(factory_ref)
    if cross_examination_ref is not None and validator_ref is not None:
        _require(cross_examination_ref.get("examiner_id") != validator_ref.get("validator_id"),
                 "cross-examiner and Validator must be distinct")

    result = _original_adjudicate(
        factory_ref,
        cross_examination_ref=cross_examination_ref,
        validator_ref=validator_ref,
        red_team_ref=red_team_ref,
        independence_ref=independence_ref,
        qualified_negative_ref=qualified_negative_ref,
    )

    context = deepcopy(dict(factory_ref["scientific_context"]))
    # A favorable scientific disposition without an explicit claim ceiling is
    # not promotable. UNKNOWN remains unresolved rather than being guessed.
    if result["verdict"] == "PROMOTE" and context.get("claim_ceiling") == "UNKNOWN":
        result["verdict"] = "PARK"
        result["reason_codes"] = ["CLAIM_CEILING_UNRESOLVED"]
        result["promotion_target"] = None
        result["scientific_negative_claim"] = False

    identity = deepcopy(dict(result["identity"]))
    identity["scientific_context"] = context
    result["identity"] = identity
    result["adjudication_identity"] = sha256_json(identity)
    result["scientific_posture"] = _posture_for(result["verdict"])
    result["claim_ceiling"] = context["claim_ceiling"]
    result["uncertainty_state"] = {
        "cross_examination_uncertainties": sorted(
            cross_examination_ref.get("bounded_uncertainties", []) if cross_examination_ref else []
        ),
        "unknown_preserved": True,
        "blocked_is_failed": False,
        "unexecuted_is_negative": False,
    }
    result["evaluation_binding"] = {
        "candidate_hash": factory_ref["candidate_hash"],
        "protocol_hash": factory_ref["protocol_hash"],
        "frozen_protocol_hash": factory_ref["frozen_protocol_hash"],
        "factory_ref_hash": factory_ref["ref_hash"],
        "trial_id": context["trial_id"],
        "experiment_epoch": context["experiment_epoch"],
        "frozen_expression_hash": context["frozen_expression_hash"],
        "provenance_hash": context["provenance_hash"],
    }
    result["downstream_binding_required"] = [
        "ECONOMIC_IDENTITY_REF",
        "PORTFOLIO_READINESS_REF",
        "ECONOMIC_LIFECYCLE_D0",
    ]
    result["negative_knowledge_scope"] = (
        qualified_negative_ref.get("negative_knowledge_scope")
        if result["verdict"] == "KILL" and qualified_negative_ref is not None
        else None
    )
    result["adjudication_hash"] = _rehash(result, "adjudication_hash")
    validate_adjudication(result)
    return result


def validate_adjudication(result: Mapping[str, Any]) -> None:
    _original_validate_adjudication(result)
    posture = result.get("scientific_posture")
    _require(posture in SCIENTIFIC_POSTURES, "invalid canonical scientific posture")
    _require(posture == _posture_for(result["verdict"]), "scientific posture/verdict mismatch")
    identity = result.get("identity")
    context = identity.get("scientific_context") if isinstance(identity, Mapping) else None
    _require(isinstance(context, Mapping), "adjudication scientific context missing")
    _require(result.get("claim_ceiling") == context.get("claim_ceiling"),
             "adjudication claim ceiling drift")
    if posture == "QUALIFIED_WITH_CLAIM_CEILING":
        _require(result.get("claim_ceiling") not in (None, "", "UNKNOWN"),
                 "qualified scientific posture requires explicit claim ceiling")
    uncertainty = result.get("uncertainty_state")
    _require(isinstance(uncertainty, Mapping) and uncertainty.get("unknown_preserved") is True,
             "adjudication must preserve UNKNOWN uncertainty")
    _require(result.get("economic_identity_created") is False, "C0 may not create Economic Identity")
    _require(result.get("economic_result") == "NOT_OBSERVED", "C0 may not create economic results")
    _require(result.get("profitability_status") == "UNKNOWN", "C0 may not infer profitability")
    _require(result.get("raw_outcomes_consumed") == 0, "C0 may not consume outcomes")
    _require(result.get("downstream_binding_required") == [
        "ECONOMIC_IDENTITY_REF", "PORTFOLIO_READINESS_REF", "ECONOMIC_LIFECYCLE_D0"
    ], "C0 downstream ownership boundary drift")


# Expose the preserved historical primitives that remain canonical after the
# campaign rebind. Their global validators now point at the hardened C2 checks.
bind_independence_ref = bind_independence_ref
validate_independence_ref = validate_independence_ref
