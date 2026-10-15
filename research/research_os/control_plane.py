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

    if task_selection.get("invent_work_when_empty") is not False:
        errors.append("invent_work_when_empty")
    if task_selection.get("max_lineages_per_wake") != 1:
        errors.append("max_lineages_per_wake_not_one")
    if task_selection.get("multi_stage_same_lineage") is not True:
        errors.append("multi_stage_same_lineage_not_enabled")
    if not isinstance(task_selection.get("max_stages_per_lineage_per_wake"), int) or task_selection["max_stages_per_lineage_per_wake"] < 1:
        errors.append("invalid_max_stages_per_lineage_per_wake")
    if independence.get("discovery_lane_may_not_validate_own_hypothesis") is not True:
        errors.append("self_validation_not_forbidden")
    if independence.get("challenge_lane_may_not_generate_or_repair_signal") is not True:
        errors.append("challenge_signal_repair_not_forbidden")
    if independence.get("integrator_lane_may_not_override_red_team_blocker") is not True:
        errors.append("integrator_red_team_override_not_forbidden")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "mode": control.get("mode"),
        "workflow_model": control.get("workflow_model"),
        "capabilities": sorted(capabilities),
        "lanes": sorted(lanes),
        "routing": control.get("routing", []),
        "global_authority": authorities,
    }
