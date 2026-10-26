"""Explainable next-research-action planning without task creation.

The planner consumes an already-qualified Scientific Memory screen and current
Control Plane capability/route contracts.  It returns a durable recommendation
only.  It has no queue, task creation, execution, acquisition or scientific-truth
authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Optional

from .research_intelligence import UNKNOWN, capability_route_status


def _route(capability: str, lane: str, context: Mapping[str, Any]) -> Dict[str, Any]:
    registry = context.get("capability_registry") or {"capabilities": []}
    lanes = context.get("workflow_lanes") or {"lanes": []}
    return capability_route_status(capability, lane, registry, lanes)


def _control_limits(context: Mapping[str, Any]) -> Dict[str, Any]:
    cp = context.get("control_plane") or {}
    selection = cp.get("task_selection") or {}
    refill = cp.get("queue_replenishment") or {}
    return {
        "follow_up_task_requires_explicit_current_task_authority": selection.get(
            "follow_up_task_creation_authorized_only_when_current_task_explicitly_allows"
        ) is True,
        "free_form_task_invention_forbidden": refill.get("free_form_task_invention_forbidden") is True,
    }


def plan_research_action(
    feedback: Mapping[str, Any],
    context: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Translate Scientific Memory feedback into a non-executing action receipt."""
    context = context or {}
    action = str(feedback.get("action") or "PARK")
    missing = list((feedback.get("identity") or {}).get("missing_core_dimensions") or [])
    limits = _control_limits(context)

    base = {
        "schema_version": "research-action-receipt-v1",
        "source_decision": action,
        "scheduler_mutation": False,
        "task_created": False,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "expected_return": UNKNOWN,
        "empirical_correlation": UNKNOWN,
        "budget_units": UNKNOWN,
        "control_limits": limits,
    }

    if action == "NO_BUILD":
        return {
            **base,
            "next_action": "NO_BUILD",
            "why": "qualified Scientific Memory identifies the same semantic family as a known negative",
            "uncertainty_to_resolve": None,
            "requires_new_task": False,
            "decision_enactable_in_current_screen": True,
            "blockers": [],
            "cheapest_candidate_action": "NO_BUILD",
        }

    if action == "PARK":
        return {
            **base,
            "next_action": "PARK",
            "why": "historical blocker remains unresolved and is not evidence of failure",
            "uncertainty_to_resolve": "historical blocker closure",
            "requires_new_task": False,
            "decision_enactable_in_current_screen": True,
            "blockers": ["HISTORICAL_BLOCKER_UNRESOLVED"],
            "cheapest_candidate_action": "PARK_UNTIL_BLOCKER_CHANGES",
        }

    if action == "NO_ACTION":
        return {
            **base,
            "next_action": "NO_ACTION",
            "why": "qualified memory supplies no suppression or forced escalation",
            "uncertainty_to_resolve": None,
            "requires_new_task": False,
            "decision_enactable_in_current_screen": True,
            "blockers": [],
            "cheapest_candidate_action": "CONTINUE_EXISTING_LINEAGE",
        }

    if action == "ARCHAEOLOGY_LOOKUP":
        archaeology = _route("legacy_recovery", "evidence_data", context)
        identity = _route("economic_identity", "integrator_portfolio", context)
        blockers = []
        if not archaeology.get("available"):
            blockers.append("ARCHAEOLOGY_CAPABILITY_OR_ROUTE_UNAVAILABLE:" + str(archaeology.get("state")))
        # The current CP allows follow-up creation only when the current task explicitly
        # grants it. A candidate screen alone cannot prove that grant and may not invent it.
        blockers.append("FOLLOW_UP_TASK_AUTHORITY_NOT_PROVEN_BY_SCREEN")
        return {
            **base,
            "next_action": "ARCHAEOLOGY_LOOKUP",
            "why": "semantic identity is incomplete; UNKNOWN identity cannot be counted as novelty",
            "uncertainty_to_resolve": {
                "missing_semantic_dimensions": missing,
                "goal": "resolve candidate identity before duplicate/novelty judgement",
            },
            "requires_new_task": True,
            "decision_enactable_in_current_screen": False,
            "required_capability": "legacy_recovery",
            "target_lane": "evidence_data",
            "capability_route": deepcopy(archaeology),
            "cheapest_candidate_action": {
                "action": "ARCHAEOLOGY_LOOKUP",
                "relative_depth": "WIDE_CHEAP_FIRST",
                "cost_units": UNKNOWN,
                "falsification_power": "IDENTITY_RESOLUTION_NOT_ECONOMIC_FALSIFICATION",
            },
            "deep_escalation_if_still_unresolved": {
                "action": "REUSE_EXISTING_EVIDENCE",
                "required_capability": "economic_identity",
                "target_lane": "integrator_portfolio",
                "capability_route": deepcopy(identity),
                "relative_depth": "DEEPER_AFTER_ARCHAEOLOGY",
                "requires_authorized_handoff": True,
            },
            "blockers": blockers,
        }

    if action == "REPAIR_PROTOCOL":
        return {
            **base,
            "next_action": "REPAIR_PROTOCOL",
            "why": "same semantic family has an invalidated protocol; unchanged rerun is inadmissible",
            "uncertainty_to_resolve": "whether a materially repaired protocol removes the invalidation",
            "requires_new_task": True,
            "decision_enactable_in_current_screen": False,
            "required_capability": "CURRENT_PRODUCER_FAMILY",
            "target_lane": UNKNOWN,
            "cheapest_candidate_action": "REPAIR_PROTOCOL_BEFORE_ANY_RERUN",
            "blockers": ["PRODUCER_FAMILY_AND_FOLLOW_UP_AUTHORITY_MUST_BE_REACQUIRED"],
        }

    if action == "ESCALATE_VALIDATION":
        validation = _route("validator", "independent_challenge", context)
        blockers = []
        if not validation.get("available"):
            blockers.append("VALIDATOR_CAPABILITY_OR_ROUTE_UNAVAILABLE:" + str(validation.get("state")))
        blockers.append("FROZEN_HYPOTHESIS_REQUIRED_BEFORE_VALIDATION_HANDOFF")
        return {
            **base,
            "next_action": "ESCALATE_VALIDATION",
            "why": "historical evidence is positive but insufficient and cannot be promoted by Search",
            "uncertainty_to_resolve": "independent evidence sufficiency and claim restriction",
            "requires_new_task": True,
            "decision_enactable_in_current_screen": False,
            "required_capability": "validator",
            "target_lane": "independent_challenge",
            "capability_route": deepcopy(validation),
            "cheapest_candidate_action": "FREEZE_ONLY_AFTER_CURRENT_SCIENTIFIC_BLOCKERS_CLEAR",
            "blockers": blockers,
        }

    return {
        **base,
        "next_action": "PARK",
        "why": "research action is not recognized by the bounded planner",
        "uncertainty_to_resolve": UNKNOWN,
        "requires_new_task": False,
        "decision_enactable_in_current_screen": True,
        "blockers": ["UNSUPPORTED_RESEARCH_ACTION:" + action],
        "cheapest_candidate_action": "PARK",
    }
