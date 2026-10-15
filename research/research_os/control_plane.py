from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REQUIRED_CAPABILITIES = {
    "legacy_recovery",
    "data_provenance",
    "trial_accounting",
    "source_qualification",
    "quant_mechanisms",
    "institutional_flows",
    "fundamental",
    "event_document",
    "validator",
    "red_team",
    "economic_identity",
    "portfolio_map",
    "shadow_readiness",
    "learning_telemetry",
    "control_integrator",
}

REQUIRED_LANES = {
    "market_discovery",
    "fundamental_events",
    "evidence_data",
    "independent_challenge",
    "integrator_portfolio",
}


def load_control_plane(base: Path) -> Dict[str, Any]:
    control = json.loads((base / "runtime" / "CONTROL_PLANE.json").read_text())
    registry = json.loads((base / "runtime" / "CAPABILITY_REGISTRY.json").read_text())
    lanes_doc = json.loads((base / "runtime" / "WORKFLOW_LANES.json").read_text())

    capabilities = {item["capability_id"] for item in registry.get("capabilities", [])}
    missing = sorted(REQUIRED_CAPABILITIES - capabilities)
    lanes = {item["lane_id"] for item in lanes_doc.get("lanes", [])}
    missing_lanes = sorted(REQUIRED_LANES - lanes)
    authorities = control.get("global_authority", {})
    task_selection = control.get("task_selection", {})
    independence = control.get("independence_rules", {})
    refill = control.get("queue_replenishment", {})

    errors = []
    if missing:
        errors.append(f"missing_capabilities:{','.join(missing)}")
    if missing_lanes:
        errors.append(f"missing_lanes:{','.join(missing_lanes)}")
    if control.get("mode") != "PRODUCTION_RESEARCH_WORKERS":
        errors.append("control_plane_not_production_research_workers")
    if control.get("workflow_model") != "ONE_LINEAGE_MULTI_STAGE":
        errors.append("workflow_model_not_one_lineage_multi_stage")
    if registry.get("production_worker_launch_authorized") is not True:
        errors.append("production_worker_launch_not_authorized")
    if authorities.get("production_worker_launch_authorized") is not True:
        errors.append("control_plane_production_worker_launch_not_authorized")

    for key in (
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    ):
        if authorities.get(key) is not False:
            errors.append(f"authority_must_be_false:{key}")

    # Queue refill is not free-form work invention. The generic invention flag
    # remains hard FALSE; only the deterministic steward exception below may
    # materialize a pre-authorized frontier task.
    if task_selection.get("invent_work_when_empty") is not False:
        errors.append("invent_work_when_empty")
    if task_selection.get("max_lineages_per_wake") != 1:
        errors.append("max_lineages_per_wake_not_one")
    if task_selection.get("multi_stage_same_lineage") is not True:
        errors.append("multi_stage_same_lineage_not_enabled")
    if not isinstance(task_selection.get("max_stages_per_lineage_per_wake"), int) or task_selection["max_stages_per_lineage_per_wake"] < 1:
        errors.append("invalid_max_stages_per_lineage_per_wake")

    if refill.get("authorized") is not True:
        errors.append("queue_replenishment_not_authorized")
    if refill.get("steward_lane") != "integrator_portfolio":
        errors.append("invalid_queue_replenishment_steward")
    if refill.get("steward_capability") != "control_integrator":
        errors.append("invalid_queue_replenishment_capability")
    if refill.get("trigger") != "NO_READY_OR_CLAIMED_TASKS_GLOBAL":
        errors.append("invalid_queue_replenishment_trigger")
    if refill.get("frontier_file") != "research/research_os/runtime/RESEARCH_FRONTIER.json":
        errors.append("invalid_queue_replenishment_frontier")
    if refill.get("max_new_tasks_per_wake") != 1:
        errors.append("queue_replenishment_not_bounded_to_one")
    if refill.get("producer_execution_same_refill_wake") is not False:
        errors.append("producer_execution_same_refill_wake")
    if refill.get("recursive_refill_same_wake") is not False:
        errors.append("recursive_refill_same_wake")
    if refill.get("derivation_key_required") is not True:
        errors.append("queue_replenishment_derivation_key_not_required")
    if refill.get("duplicate_derivation_forbidden") is not True:
        errors.append("duplicate_derivation_not_forbidden")
    if refill.get("legacy_screen_required_before_candidate_freeze") is not True:
        errors.append("refill_legacy_screen_not_required")
    if refill.get("free_form_task_invention_forbidden") is not True:
        errors.append("free_form_task_invention_not_forbidden")
    for key in (
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    ):
        if refill.get(key) is not False:
            errors.append(f"queue_replenishment_authority_must_be_false:{key}")

    if independence.get("discovery_lane_may_not_validate_own_hypothesis") is not True:
        errors.append("self_validation_not_forbidden")
    if independence.get("challenge_lane_may_not_generate_or_repair_signal") is not True:
        errors.append("challenge_signal_repair_not_forbidden")
    if independence.get("integrator_lane_may_not_override_red_team_blocker") is not True:
        errors.append("integrator_red_team_override_not_forbidden")
    if independence.get("queue_steward_may_derive_but_not_execute_producer_task_same_wake") is not True:
        errors.append("queue_steward_same_wake_execution_not_forbidden")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "mode": control.get("mode"),
        "workflow_model": control.get("workflow_model"),
        "capabilities": sorted(capabilities),
        "lanes": sorted(lanes),
        "routing": control.get("routing", []),
        "queue_replenishment": refill,
        "global_authority": authorities,
    }
