"""Pure Research Intelligence preflight for deterministic frontier refill.

This module does not create tasks, select workers, execute producers, acquire data,
or mutate scientific memory.  It translates Owner-governed *generation mandates*
into explainable pre-outcome decisions that the existing queue replenisher may
consume.  A frontier mandate is intentionally not treated as a candidate economic
identity: UNKNOWN identity is not novelty.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional, Sequence

from .research_intelligence import capability_route_status, classify_frontier


STATE_TO_NOOP_STATUS = {
    "DUPLICATE_ONLY": "NOOP_DUPLICATE_ONLY",
    "SOURCE_MISSING": "NOOP_SOURCE_MISSING",
    "CAPABILITY_MISSING": "NOOP_CAPABILITY_MISSING",
    "BUDGET_BLOCKED": "NOOP_BUDGET_BLOCKED",
    "EXTERNAL_ACCESS_BLOCKED": "NOOP_EXTERNAL_ACCESS_BLOCKED",
    "AUTHORITY_SEALED": "NOOP_AUTHORITY_SEALED",
    "TEMPORARILY_PARKED": "NOOP_TEMPORARILY_PARKED",
    "SCIENTIFICALLY_EXHAUSTED": "NOOP_FRONTIER_SCIENTIFICALLY_EXHAUSTED",
    "SEARCH_SPACE_INCOMPLETE": "NOOP_SEARCH_SPACE_INCOMPLETE",
    "ACTIVE_QUEUE": "NOOP_QUEUE_NOT_EMPTY",
}


def _identity_unknown() -> Dict[str, Any]:
    missing = [
        "mechanism",
        "payer",
        "constrained_actor",
        "timing_clock",
        "universe",
        "economic_exposure",
    ]
    return {
        "resolved": False,
        "missing_core_dimensions": missing,
        "mechanism_key": None,
        "evidence_key": None,
        "dimensions": {field: "UNKNOWN" for field in (
            "mechanism", "payer", "constrained_actor", "timing_clock", "universe",
            "economic_exposure", "instrument", "source_family", "evidence_identity",
        )},
    }


def _generation_decision(
    entry: Mapping[str, Any],
    *,
    capability_registry: Mapping[str, Any],
    workflow_lanes: Mapping[str, Any],
    source_plan: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Evaluate one frontier generation mandate without claiming candidate novelty."""
    frontier_id = str(entry.get("frontier_id") or "UNKNOWN")
    capability = capability_route_status(
        entry.get("required_capability"),
        entry.get("target_lane"),
        capability_registry,
        workflow_lanes,
    )
    blockers = []
    reasons = [
        "FRONTIER_IS_GENERATION_MANDATE_NOT_CANDIDATE",
        "UNKNOWN_IDENTITY_IS_NOT_NOVELTY",
        "SCIENTIFIC_MEMORY_MATCH_DEFERRED_UNTIL_IDENTITY_RESOLVED",
    ]

    if not capability["available"]:
        blockers.append(capability["state"])
        reasons.append("CAPABILITY_OR_ROUTE_BLOCKED")

    if source_plan is not None:
        if source_plan.get("status") != "SOURCE_SELECTED":
            blockers.append("SOURCE_MISSING")
            reasons.append(str(source_plan.get("status") or "SOURCE_PLAN_UNKNOWN"))
        else:
            reasons.append("QUALIFIED_UNUSED_SOURCE_BOUND")

    selected_action = {
        "action": "GENERATE_MECHANISM",
        "cost_units": 0,
        "depth": "WIDE",
        "is_falsifier": False,
        "falsification_power": "NOT_APPLICABLE_BEFORE_IDENTITY",
        "uncertainty_resolved": "candidate semantic identity and mechanism definition",
        "required_capability": entry.get("required_capability"),
        "target_lane": entry.get("target_lane"),
        "requires_authority": [],
    }
    executable = not blockers
    if executable:
        reasons.extend([
            "CAPABILITY_AND_ROUTE_ACTIVE",
            "ZERO_COST_RESEARCH_ACTION_NO_BUDGET_AUTHORITY_REQUIRED",
        ])
    return {
        "candidate_id": frontier_id,
        "frontier_id": frontier_id,
        "action": "GENERATE_MECHANISM" if executable else "PARK",
        "executable": executable,
        "reason_codes": reasons,
        "identity": _identity_unknown(),
        "novelty_status": "UNRESOLVED_NOT_CLAIMED",
        "memory_applicability": "DEFERRED_UNTIL_CANDIDATE_IDENTITY",
        "memory_influence": [],
        "blockers": blockers,
        "uncertainty_resolved": selected_action["uncertainty_resolved"] if executable else None,
        "selected_action": selected_action if executable else None,
        "capability": deepcopy(capability),
        "source_plan_status": source_plan.get("status") if source_plan is not None else "NOT_EVALUATED",
        "selection_trace": [
            "frontier mandate does not establish semantic novelty",
            "validate capability and route before scheduling generation",
            "require qualified unused source when source planning is active",
            "defer family/evidence memory matching until candidate identity exists",
        ],
        "scheduler_mutation": False,
    }


def evaluate_frontier_mandates(
    entries: Sequence[Mapping[str, Any]],
    *,
    capability_registry: Mapping[str, Any],
    workflow_lanes: Mapping[str, Any],
    source_plans: Optional[Mapping[str, Mapping[str, Any]]] = None,
    queue_active_count: int = 0,
    search_space_complete: bool = False,
    archaeology_complete: bool = False,
) -> Dict[str, Any]:
    """Return an explainable preflight receipt; never schedule work itself."""
    plans = source_plans or {}
    decisions = [
        _generation_decision(
            entry,
            capability_registry=capability_registry,
            workflow_lanes=workflow_lanes,
            source_plan=plans.get(str(entry.get("frontier_id"))),
        )
        for entry in entries
    ]
    frontier_state = classify_frontier(
        decisions,
        queue_active_count=queue_active_count,
        search_space_complete=search_space_complete,
        archaeology_complete=archaeology_complete,
    )
    admissible_ids = [
        str(item["frontier_id"])
        for item in decisions
        if item.get("executable") is True and item.get("action") == "GENERATE_MECHANISM"
    ]
    state = str(frontier_state["state"])
    return {
        "schema_version": "research-refill-policy-v1",
        "frontier_state": frontier_state,
        "decisions": decisions,
        "admissible_frontier_ids": admissible_ids,
        "noop_status": None if admissible_ids else STATE_TO_NOOP_STATUS.get(state, "NOOP_RESEARCH_POLICY_BLOCKED"),
        "scheduler_mutation": False,
        "scientific_claims": {
            "novelty_claimed": False,
            "economic_outcome_accessed": False,
            "alpha_claimed": False,
            "empirical_correlation_claimed": False,
        },
    }
