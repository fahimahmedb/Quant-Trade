from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REQUIRED_CAPABILITIES = {
    "legacy_recovery",
    "quant_mechanisms",
    "fundamental",
    "event_document",
    "institutional_flows",
    "validator",
    "red_team",
    "portfolio_map",
}


def load_control_plane(base: Path) -> Dict[str, Any]:
    control = json.loads((base / "runtime" / "CONTROL_PLANE.json").read_text())
    registry = json.loads((base / "runtime" / "CAPABILITY_REGISTRY.json").read_text())

    capabilities = {item["capability_id"] for item in registry.get("capabilities", [])}
    missing = sorted(REQUIRED_CAPABILITIES - capabilities)
    authorities = control.get("global_authority", {})
    errors = []
    if missing:
        errors.append(f"missing_capabilities:{','.join(missing)}")
    if control.get("mode") != "PREPROD_SIMULATION_ONLY":
        errors.append("control_plane_not_preprod")
    if registry.get("production_worker_launch_authorized") is not False:
        errors.append("production_worker_launch_authorized")
    for key in (
        "production_worker_launch_authorized",
        "economic_experiment_authorized",
        "prospective_observation_authorized",
        "real_capital_authorized",
        "live_trading_authorized",
    ):
        if authorities.get(key) is not False:
            errors.append(f"authority_must_be_false:{key}")
    if control.get("task_selection", {}).get("invent_work_when_empty") is not False:
        errors.append("invent_work_when_empty")
    if control.get("task_selection", {}).get("max_tasks_per_wake") != 1:
        errors.append("max_tasks_per_wake_not_one")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "capabilities": sorted(capabilities),
        "routing": control.get("routing", []),
        "handoff_rules": control.get("handoff_rules", []),
        "global_authority": authorities,
    }
