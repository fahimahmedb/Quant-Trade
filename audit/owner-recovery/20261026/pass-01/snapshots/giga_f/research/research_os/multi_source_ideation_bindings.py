"""Thin bindings from canonical Wave-2 Research OS contracts into passive ideation.

No reverse dependency is introduced: existing refill/source-planner/Research Intelligence
remain authoritative and unmodified.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .multi_source_ideation import POLICIES, raw_artifact, validate_policy_input


def canonical_source_identity(source: Mapping[str, Any]) -> str | None:
    """Use content identity, not path labels, for ideation source claims."""
    for key in ("packet_hash", "blob_sha", "record_hash"):
        value = source.get(key)
        if value:
            return f"{key}:{value}"
    return None


def systematic_coverage_from_frontier(*, snapshot: Mapping[str, Any], frontier_decision: Mapping[str, Any], source_plan: Mapping[str, Any] | None) -> dict:
    """Policy A adapter for frontier_source_planner_v2 output."""
    validate_policy_input(snapshot)
    h = snapshot["context_snapshot_hash"]
    if frontier_decision.get("action") != "GENERATE_MECHANISM" or frontier_decision.get("executable") is not True:
        exhausted = frontier_decision.get("frontier_state") == "SCIENTIFICALLY_EXHAUSTED"
        return raw_artifact(policy_kind=POLICIES[0], status="FRONTIER_EXHAUSTED" if exhausted else "BLOCKED", context_snapshot_hash=h, reason="FRONTIER_NOT_ACTIONABLE")
    if not source_plan:
        return raw_artifact(policy_kind=POLICIES[0], status="NO_ADMISSIBLE_NOVEL_SOURCE", context_snapshot_hash=h, reason="SOURCE_PLAN_REQUIRED")
    status = source_plan.get("status")
    if status in {"NO_ADMISSIBLE_DOCUMENTARY_SOURCE", "NO_UNUSED_ADMISSIBLE_SOURCE"}:
        return raw_artifact(policy_kind=POLICIES[0], status="NO_ADMISSIBLE_NOVEL_SOURCE", context_snapshot_hash=h, reason=str(status))
    if status != "SOURCE_SELECTED":
        return raw_artifact(policy_kind=POLICIES[0], status="INVALID_INPUT", context_snapshot_hash=h, reason="UNRECOGNIZED_SOURCE_PLAN_STATUS")
    source = source_plan.get("source") or {}
    identity = canonical_source_identity(source)
    if not identity:
        return raw_artifact(policy_kind=POLICIES[0], status="BLOCKED", context_snapshot_hash=h, reason="SOURCE_CONTENT_IDENTITY_MISSING")
    payload = {
        "source_identity": identity,
        "source_provenance": {
            "path": source.get("path"), "packet_hash": source.get("packet_hash"),
            "blob_sha": source.get("blob_sha"), "record_hash": source.get("record_hash"),
            "source_ref": source.get("source_ref"), "available_at": source.get("available_at"),
        },
        "frontier_id": source_plan.get("frontier_id"),
        "family": source_plan.get("family"),
        "direction": frontier_decision.get("uncertainty_resolved", "UNKNOWN"),
        "needs_discovery_synthesis": True,
    }
    return raw_artifact(policy_kind=POLICIES[0], status="SEED_EMITTED", context_snapshot_hash=h, artifact_kind="IDEATION_SEED", payload=payload)


def information_value_from_research_intelligence(*, snapshot: Mapping[str, Any], decision: Mapping[str, Any]) -> dict:
    """Policy B consumes Research Intelligence; it never re-ranks the decision."""
    validate_policy_input(snapshot)
    h = snapshot["context_snapshot_hash"]
    action = str(decision.get("action") or "NO_ACTION")
    executable = decision.get("executable") is True
    if not executable or action in {"NO_ACTION", "NO_BUILD", "PARK", "REPAIR_PROTOCOL", "ESCALATE_VALIDATION"}:
        return raw_artifact(policy_kind=POLICIES[1], status="NO_ACTION", context_snapshot_hash=h, reason=action)
    if action not in {"GENERATE_MECHANISM", "RUN_PRODUCER", "ACQUIRE_EVIDENCE_INTENT", "REUSE_EXISTING_EVIDENCE", "ARCHAEOLOGY_LOOKUP"}:
        return raw_artifact(policy_kind=POLICIES[1], status="INVALID_INPUT", context_snapshot_hash=h, reason="UNSUPPORTED_RESEARCH_DECISION")
    payload = {
        "research_action": action,
        "candidate_id": decision.get("candidate_id"),
        "reason_codes": deepcopy(list(decision.get("reason_codes") or [])),
        "uncertainty_resolved": decision.get("uncertainty_resolved"),
        "selected_action": deepcopy(decision.get("selected_action")),
        "needs_discovery_synthesis": True,
        "ranking_authority": "RESEARCH_INTELLIGENCE_REUSED_NOT_REIMPLEMENTED",
    }
    return raw_artifact(policy_kind=POLICIES[1], status="SEED_EMITTED", context_snapshot_hash=h, artifact_kind="IDEATION_SEED", payload=payload)
