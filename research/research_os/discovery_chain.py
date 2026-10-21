"""Thin MEGA B binding from qualified Research Intelligence to Discovery.

This module executes only an already-qualified RUN_PRODUCER action. Sources are
injected by the caller; there is no network acquisition, task creation, lease,
queue, scheduler, or Control Plane mutation here.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Mapping, Optional

from .discovery_engine import AUTHORITY, DISCOVERY_VERSION, build_discovery_handoff
from .engines.builtin import ENGINE_REGISTRY
from .engines.protocol import EngineContext
from .expansion.engine_dossiers_v1 import build_engine_dossier

ENGINE_ROUTES = {
    "quant": ("QUANT_MECHANISM", "quant_mechanisms"),
    "event_document": ("EVENT_DOCUMENT", "event_document"),
    "fundamental": ("FUNDAMENTAL", "fundamental"),
    "institutional_flow": ("INSTITUTIONAL_FLOW", "institutional_flows"),
}


def _blocked(reason: str) -> Dict[str, Any]:
    return {
        "version": DISCOVERY_VERSION,
        "status": "BLOCKED_BEFORE_PRODUCER",
        "producer_executed": False,
        "blockers": [reason],
        "scheduler_mutation": False,
        "control_plane_mutation": False,
        "scientific_memory_mutation": False,
        "outcome_accessed": False,
        "authority": deepcopy(AUTHORITY),
    }


def run_discovery_chain(
    research_decision: Mapping[str, Any],
    *,
    engine_key: str,
    source: Mapping[str, Any],
    run_id: str,
    synthetic_only: bool,
    discovery_facts: Mapping[str, Any],
    dossier_detail: Optional[Mapping[str, Any]] = None,
    prior_candidates: Iterable[Mapping[str, Any]] = (),
) -> Dict[str, Any]:
    """Execute producer -> common Candidate -> implementability -> Factory handoff.

    The Research Intelligence decision must already authorize RUN_PRODUCER and
    must carry the exact capability routed to the selected producer family.
    """
    if (
        research_decision.get("action") != "RUN_PRODUCER"
        or research_decision.get("executable") is not True
        or research_decision.get("scheduler_mutation") is not False
    ):
        return _blocked("RESEARCH_INTELLIGENCE_NOT_QUALIFIED_FOR_PRODUCER")

    route = ENGINE_ROUTES.get(str(engine_key))
    if route is None or engine_key not in ENGINE_REGISTRY:
        return _blocked("UNSUPPORTED_PRODUCER_ROUTE")
    family, expected_capability = route

    selected = research_decision.get("selected_action")
    selected = selected if isinstance(selected, Mapping) else {}
    if selected.get("required_capability") != expected_capability:
        return _blocked("RESEARCH_INTELLIGENCE_PRODUCER_CAPABILITY_MISSING_OR_MISMATCH")
    if type(synthetic_only) is not bool:
        return _blocked("EVIDENCE_MODE_NOT_EXPLICIT")

    output = ENGINE_REGISTRY[engine_key].run(
        dict(source), EngineContext(run_id=run_id, synthetic_only=synthetic_only)
    )
    if output.get("engine_family") != family:
        result = _blocked("PRODUCER_ROUTE_FAMILY_MISMATCH")
        result["status"] = "BLOCKED_DISCOVERY"
        result["producer_executed"] = True
        return result

    dossier = build_engine_dossier(
        output,
        dict(dossier_detail) if isinstance(dossier_detail, Mapping) else None,
    )
    result = build_discovery_handoff(
        research_decision,
        output,
        dossier=dossier,
        discovery_facts=discovery_facts,
        prior_candidates=prior_candidates,
    )
    result["producer_executed"] = True
    result["producer_execution_mode"] = "DIRECT_QUALIFIED_ACTION_NO_SCHEDULER"
    result["producer_route"] = {
        "engine_key": engine_key,
        "engine_family": family,
        "required_capability": expected_capability,
    }
    return result
