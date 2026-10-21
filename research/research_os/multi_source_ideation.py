"""Passive Wave-2 multi-source ideation intake.

Hard boundary: this module may qualify proposals for Discovery, but it never creates
READY tasks, Candidates, experiments, producers, scheduler work, Oracle work, or
scientific/economic outcomes.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

BASE_SHA = "2b99d8aeb8a342f1ef32544247d366cb8a26037e"
POLICIES = ("SYSTEMATIC_COVERAGE", "INFORMATION_VALUE", "DIVERGENT_EXPLORATION")
TERMINAL_STATES = {
    "PROPOSAL_EMITTED", "SEED_EMITTED", "NO_PROPOSAL", "NO_ADMISSIBLE_NOVEL_SOURCE",
    "FRONTIER_EXHAUSTED", "BLOCKED", "SOURCE_UNAVAILABLE", "SOURCE_FAILED",
    "INVALID_INPUT", "NO_ACTION",
}
ARTIFACT_KINDS = {"IDEATION_SEED", "IDEA_PROPOSAL"}
MEMORY_CLASSES = {
    "KNOWN_EXACT_NEGATIVE", "KNOWN_FAMILY_CONDITIONAL_NEGATIVE", "BLOCKED_DATA",
    "INVALID_PROTOCOL", "UNEXECUTED", "SUPERSEDED", "RELATED_NOT_DISPOSITIVE",
    "NO_QUALIFIED_MATCH", "UNKNOWN",
}
DUPLICATE_CLASSES = {
    "EXACT_DUPLICATE", "ANCESTRY_MATCH", "LIKELY_SEMANTIC_DUPLICATE",
    "POSSIBLE_EXPRESSION_EQUIVALENCE", "DISTINCT", "UNKNOWN", "REVIEW_REQUIRED",
}
OUTCOME_BEARING_KEYS = {
    "pnl", "pnl_series", "profit", "profitability", "return", "returns",
    "return_series", "realized_return", "realized_return_series", "sharpe", "sortino",
    "alpha", "covariance", "correlation", "empirical_correlation", "realized_pnl",
    "unrealized_pnl", "price", "prices", "price_series", "fill", "fills",
    "equity_curve", "win_rate", "hit_rate", "outcome", "outcomes", "economic_result",
}


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _reject_outcome_fields(value: Any, path: str = "payload") -> None:
    """Keep ideation pre-outcome even when an external model/source is untrusted."""
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in OUTCOME_BEARING_KEYS:
                raise ValueError(f"outcome-bearing ideation field forbidden: {path}.{key}")
            _reject_outcome_fields(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _reject_outcome_fields(nested, f"{path}[{index}]")


def build_context_snapshot(*, ideation_cycle_id: str, created_at: str, refs: Mapping[str, Any], relevant_schema_versions: Mapping[str, str]) -> dict:
    required = (
        "memory_snapshot_ref", "ancestry_snapshot_ref", "frontier_snapshot_ref",
        "evidence_snapshot_ref", "source_catalog_snapshot_ref", "capability_snapshot_ref",
        "authority_snapshot_ref", "active_work_snapshot_ref",
    )
    missing = [k for k in required if not refs.get(k)]
    if missing:
        raise ValueError(f"incomplete ideation context: {missing}")
    body = {
        "schema_version": "multi-source-ideation-context-v2",
        "ideation_cycle_id": ideation_cycle_id,
        "created_at": created_at,
        **{k: deepcopy(refs[k]) for k in required},
        "relevant_schema_versions": deepcopy(dict(relevant_schema_versions)),
        "outcome_accessed": False,
    }
    body["context_snapshot_hash"] = _hash(body)
    return body


def validate_policy_input(snapshot: Mapping[str, Any]) -> None:
    if snapshot.get("outcome_accessed") is not False:
        raise ValueError("OUTCOME_ACCESSED must remain false")
    expected = dict(snapshot)
    supplied = expected.pop("context_snapshot_hash", None)
    if not supplied or _hash(expected) != supplied:
        raise ValueError("context snapshot hash mismatch")


def raw_artifact(*, policy_kind: str, status: str, context_snapshot_hash: str, artifact_kind: str | None = None, payload: Mapping[str, Any] | None = None, reason: str | None = None) -> dict:
    if policy_kind not in POLICIES or status not in TERMINAL_STATES:
        raise ValueError("invalid policy/status")
    if artifact_kind is not None and artifact_kind not in ARTIFACT_KINDS:
        raise ValueError("invalid artifact kind")
    if status == "PROPOSAL_EMITTED" and artifact_kind != "IDEA_PROPOSAL":
        raise ValueError("proposal terminal requires IDEA_PROPOSAL")
    if status == "SEED_EMITTED" and artifact_kind != "IDEATION_SEED":
        raise ValueError("seed terminal requires IDEATION_SEED")
    if status in {"SOURCE_UNAVAILABLE", "SOURCE_FAILED", "BLOCKED", "NO_ACTION", "NO_PROPOSAL", "NO_ADMISSIBLE_NOVEL_SOURCE", "FRONTIER_EXHAUSTED", "INVALID_INPUT"} and artifact_kind is not None:
        raise ValueError("non-emission terminal cannot carry proposal")
    bounded_payload = deepcopy(dict(payload or {}))
    _reject_outcome_fields(bounded_payload)
    return {
        "policy_kind": policy_kind, "status": status, "context_snapshot_hash": context_snapshot_hash,
        "artifact_kind": artifact_kind, "payload": bounded_payload, "reason": reason,
    }


def barrier(artifacts: Sequence[Mapping[str, Any]], context_snapshot_hash: str) -> dict:
    by_policy = {}
    for item in artifacts:
        if item.get("context_snapshot_hash") != context_snapshot_hash:
            raise ValueError("cross-context policy artifact")
        policy = item.get("policy_kind")
        if policy in by_policy:
            raise ValueError("duplicate policy terminal")
        if item.get("status") not in TERMINAL_STATES:
            raise ValueError("policy not terminal")
        by_policy[policy] = deepcopy(dict(item))
    missing = set(POLICIES) - set(by_policy)
    if missing:
        return {"status": "WAITING_FOR_TERMINAL_STATES", "missing": sorted(missing), "intake_allowed": False}
    return {"status": "BARRIER_COMPLETE", "artifacts": by_policy, "intake_allowed": True}


def policy_a(*, snapshot: Mapping[str, Any], frontier_decision: Mapping[str, Any], source_plan: Mapping[str, Any] | None) -> dict:
    validate_policy_input(snapshot)
    h = snapshot["context_snapshot_hash"]
    if frontier_decision.get("action") != "GENERATE_MECHANISM" or frontier_decision.get("executable") is not True:
        state = "FRONTIER_EXHAUSTED" if frontier_decision.get("frontier_state") == "SCIENTIFICALLY_EXHAUSTED" else "BLOCKED"
        return raw_artifact(policy_kind=POLICIES[0], status=state, context_snapshot_hash=h, reason="FRONTIER_NOT_ACTIONABLE")
    if not source_plan or source_plan.get("status") != "SOURCE_SELECTED" or not source_plan.get("source_identity"):
        return raw_artifact(policy_kind=POLICIES[0], status="NO_ADMISSIBLE_NOVEL_SOURCE", context_snapshot_hash=h, reason="QUALIFIED_UNUSED_DOCUMENTARY_SOURCE_REQUIRED")
    payload = {
        "source_identity": source_plan["source_identity"],
        "direction": frontier_decision.get("uncertainty_resolved", "UNKNOWN"),
        "needs_discovery_synthesis": True,
    }
    return raw_artifact(policy_kind=POLICIES[0], status="SEED_EMITTED", context_snapshot_hash=h, artifact_kind="IDEATION_SEED", payload=payload)


def policy_b(*, snapshot: Mapping[str, Any], research_decision: Mapping[str, Any]) -> dict:
    validate_policy_input(snapshot)
    h = snapshot["context_snapshot_hash"]
    action = str(research_decision.get("action") or "NO_ACTION")
    if action in {"NO_ACTION", "NO_BUILD", "PARK", "REPAIR_PROTOCOL", "ESCALATE_VALIDATION"}:
        return raw_artifact(policy_kind=POLICIES[1], status="NO_ACTION", context_snapshot_hash=h, reason=action)
    if action not in {"GENERATE_MECHANISM", "RUN_PRODUCER", "ACQUIRE_EVIDENCE_INTENT"}:
        return raw_artifact(policy_kind=POLICIES[1], status="INVALID_INPUT", context_snapshot_hash=h, reason="UNSUPPORTED_RESEARCH_DECISION")
    payload = {"research_action": action, "decision_ref": research_decision.get("decision_id"), "needs_discovery_synthesis": True}
    return raw_artifact(policy_kind=POLICIES[1], status="SEED_EMITTED", context_snapshot_hash=h, artifact_kind="IDEATION_SEED", payload=payload)


class ModelBackend(Protocol):
    backend_identity: str
    model_identity: str
    def generate(self, mandate: Mapping[str, Any]) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class DeterministicFakeBackend:
    response: Mapping[str, Any]
    backend_identity: str = "deterministic-fake"
    model_identity: str = "fixture-v1"
    def generate(self, mandate: Mapping[str, Any]) -> Mapping[str, Any]:
        del mandate
        return deepcopy(dict(self.response))


def policy_c(*, snapshot: Mapping[str, Any], backend: ModelBackend | None, mandate: Mapping[str, Any]) -> tuple[dict, dict | None]:
    validate_policy_input(snapshot)
    h = snapshot["context_snapshot_hash"]
    if backend is None:
        return raw_artifact(policy_kind=POLICIES[2], status="SOURCE_UNAVAILABLE", context_snapshot_hash=h, reason="EXTERNAL_RUNTIME_MISSING"), None
    if mandate.get("outcome_accessed") not in (None, False):
        raise ValueError("divergent model may not receive outcome-bearing context")
    _reject_outcome_fields(mandate, "mandate")
    response = backend.generate(deepcopy(dict(mandate)))
    if not isinstance(response, Mapping):
        return raw_artifact(policy_kind=POLICIES[2], status="SOURCE_FAILED", context_snapshot_hash=h, reason="MALFORMED_MODEL_OUTPUT"), None
    try:
        _reject_outcome_fields(response, "model_response")
    except ValueError:
        return raw_artifact(policy_kind=POLICIES[2], status="BLOCKED", context_snapshot_hash=h, reason="OUTCOME_BEARING_MODEL_OUTPUT_FORBIDDEN"), None
    alternatives = response.get("alternatives")
    selected = response.get("selected_alternative_index")
    if not isinstance(alternatives, list) or not 1 <= len(alternatives) <= 5 or not isinstance(selected, int) or selected < 0 or selected >= len(alternatives):
        return raw_artifact(policy_kind=POLICIES[2], status="SOURCE_FAILED", context_snapshot_hash=h, reason="MALFORMED_MODEL_OUTPUT"), None
    chosen = alternatives[selected]
    if not isinstance(chosen, Mapping):
        return raw_artifact(policy_kind=POLICIES[2], status="SOURCE_FAILED", context_snapshot_hash=h, reason="MALFORMED_SELECTED_ALTERNATIVE"), None
    receipt = {
        "alternative_count": len(alternatives),
        "alternative_summaries": [str(x.get("summary", "UNKNOWN")) if isinstance(x, Mapping) else "INVALID" for x in alternatives],
        "selection_criteria": response.get("selection_criteria", "UNKNOWN"),
        "selected_alternative_index": selected,
        "selected_proposal": deepcopy(dict(chosen)),
        "raw_response_hash": _hash(response),
        "backend_identity": backend.backend_identity,
        "model_identity": backend.model_identity,
        "prompt_contract_version": str(mandate.get("prompt_contract_version", "UNKNOWN")),
        "context_snapshot_hash": h,
        "semantic_retry_count": int(response.get("semantic_retry_count", 0)),
    }
    if receipt["semantic_retry_count"] != 0:
        return raw_artifact(policy_kind=POLICIES[2], status="BLOCKED", context_snapshot_hash=h, reason="HIDDEN_SEMANTIC_RETRY_FORBIDDEN"), receipt
    complete = all(chosen.get(k) not in (None, "", "UNKNOWN") for k in ("mechanism", "payer", "actor", "clock", "universe", "falsifier"))
    kind = "IDEA_PROPOSAL" if complete else "IDEATION_SEED"
    status = "PROPOSAL_EMITTED" if complete else "SEED_EMITTED"
    payload = deepcopy(dict(chosen)); payload["needs_discovery_synthesis"] = not complete
    return raw_artifact(policy_kind=POLICIES[2], status=status, context_snapshot_hash=h, artifact_kind=kind, payload=payload), receipt


def source_claim(*, source_identity: str, context_snapshot_hash: str, policy_kind: str) -> dict:
    if policy_kind not in POLICIES:
        raise ValueError("invalid policy")
    identity = _hash({"source_identity": source_identity, "context_snapshot_hash": context_snapshot_hash, "policy_kind": policy_kind})
    return {"claim_id": identity, "source_identity": source_identity, "context_snapshot_hash": context_snapshot_hash, "policy_kind": policy_kind, "state": "HELD", "scientifically_consumed": False}


def transition_claim(claim: Mapping[str, Any], target: str) -> dict:
    if claim.get("state") != "HELD" or target not in {"RELEASED", "TRANSFERRED"}:
        raise ValueError("only HELD -> RELEASED/TRANSFERRED allowed")
    out = deepcopy(dict(claim)); out["state"] = target; out["scientifically_consumed"] = False
    return out


def memory_lineage_check(relation: Mapping[str, Any]) -> dict:
    disposition = str(relation.get("scientific_disposition") or "UNKNOWN")
    if relation.get("qualified") is not True:
        classification = "UNKNOWN"
    elif disposition == "BLOCKED":
        classification = "BLOCKED_DATA"
    elif disposition in {"UNEXECUTED", "NOT_RUN"}:
        classification = "UNEXECUTED"
    elif disposition in {"INVALIDATED_PROTOCOL", "INVALID_PROTOCOL"}:
        classification = "INVALID_PROTOCOL"
    elif disposition == "NEGATIVE" and relation.get("same_semantic_family") is True:
        classification = "KNOWN_EXACT_NEGATIVE" if relation.get("same_evidence") is True else "KNOWN_FAMILY_CONDITIONAL_NEGATIVE"
    elif relation.get("same_semantic_family") is True:
        classification = "RELATED_NOT_DISPOSITIVE"
    else:
        classification = "NO_QUALIFIED_MATCH"
    assert classification in MEMORY_CLASSES
    return {"classification": classification, "relation": deepcopy(dict(relation))}


def duplicate_check(proposal: Mapping[str, Any], known: Sequence[Mapping[str, Any]]) -> dict:
    identity = proposal.get("identity") or {}
    if not identity:
        return {"classification": "UNKNOWN"}
    normalized = {str(k): str(v).strip().lower() for k, v in identity.items() if v not in (None, "", "UNKNOWN")}
    if not normalized:
        return {"classification": "UNKNOWN"}
    for row in known:
        other = row.get("identity") or {}
        other_norm = {str(k): str(v).strip().lower() for k, v in other.items() if v not in (None, "", "UNKNOWN")}
        if normalized == other_norm:
            return {"classification": "EXACT_DUPLICATE", "match_id": row.get("proposal_id")}
        core = ("mechanism", "payer", "actor", "clock", "universe")
        if all(normalized.get(k) and normalized.get(k) == other_norm.get(k) for k in core):
            return {"classification": "POSSIBLE_EXPRESSION_EQUIVALENCE", "match_id": row.get("proposal_id")}
    return {"classification": "DISTINCT"}


def light_implementability(payload: Mapping[str, Any]) -> dict:
    required = ("mechanism", "falsifier", "universe")
    missing = [k for k in required if payload.get(k) in (None, "", "UNKNOWN")]
    contradictions = [k for k in ("actor", "clock") if payload.get(k) == "CONTRADICTED"]
    return {"admissible": not missing and not contradictions, "missing": missing, "contradictions": contradictions}


def intake(*, artifact: Mapping[str, Any], memory_check: Mapping[str, Any], duplicate: Mapping[str, Any], implementability: Mapping[str, Any], current_context_hash: str) -> dict:
    if artifact.get("context_snapshot_hash") != current_context_hash:
        return {"decision": "STALE_REQUALIFICATION_REQUIRED", "eligible_for_discovery": False}
    if artifact.get("artifact_kind") != "IDEA_PROPOSAL":
        return {"decision": "NEEDS_DISCOVERY_SYNTHESIS", "eligible_for_discovery": artifact.get("artifact_kind") == "IDEATION_SEED"}
    if memory_check.get("classification") == "KNOWN_EXACT_NEGATIVE" or duplicate.get("classification") == "EXACT_DUPLICATE" or implementability.get("admissible") is not True:
        return {"decision": "NOT_ELIGIBLE", "eligible_for_discovery": False}
    return {"decision": "ELIGIBLE_FOR_DISCOVERY", "eligible_for_discovery": True}


class ProposalLedger:
    """Passive idempotent ledger; deliberately has no READY/LEASE/RUN semantics."""
    def __init__(self) -> None:
        self._rows: dict[str, dict] = {}
    def persist(self, record: Mapping[str, Any]) -> str:
        forbidden = {"READY", "LEASED", "RUNNING", "RETRY", "WORKER_OWNER", "heartbeat"}
        if forbidden.intersection(record.keys()) or str(record.get("status")) in forbidden:
            raise ValueError("operational queue semantics forbidden")
        rid = _hash(record)
        prior = self._rows.get(rid)
        row = deepcopy(dict(record))
        if prior is not None and prior != row:
            raise ValueError("immutable ledger collision")
        self._rows[rid] = row
        return rid
    def rows(self) -> list[dict]:
        return [deepcopy(v) for _, v in sorted(self._rows.items())]


def side_effect_zeroes() -> dict:
    return {
        "READY_TASKS_CREATED": 0, "CONTROL_PLANE_MUTATIONS": 0, "PRODUCERS_EXECUTED": 0,
        "ORACLE_MUTATIONS": 0, "SCHEDULER_MUTATIONS": 0, "CANDIDATES_CREATED": 0,
    }
