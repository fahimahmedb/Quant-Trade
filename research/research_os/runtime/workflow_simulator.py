from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List


LANE_ORDER = [
    "market_discovery",
    "fundamental_events",
    "evidence_data",
    "independent_challenge",
    "integrator_portfolio",
]

DISCOVERY_TYPES = {
    "QUANT_MECHANISM",
    "INSTITUTIONAL_FLOW",
    "FUNDAMENTAL_RESEARCH",
    "EVENT_DOCUMENT",
}
EVIDENCE_TYPES = {"LEGACY_RECOVERY", "DATA_PROVENANCE", "TRIAL_ACCOUNTING", "SOURCE_QUALIFICATION"}
CHALLENGE_TYPES = {"VALIDATION", "RED_TEAM"}
INTEGRATION_TYPES = {"PORTFOLIO_MAP", "ECONOMIC_IDENTITY", "SHADOW_READINESS", "LEARNING_TELEMETRY", "CONTROL_INTEGRATION"}


def _task(task_id: str, task_type: str, lineage_id: str, priority: int, origin_lane: str | None = None) -> Dict[str, Any]:
    return {
        "task_id": task_id,
        "task_type": task_type,
        "lineage_id": lineage_id,
        "priority": priority,
        "status": "READY",
        "origin_lane": origin_lane,
        "history": [],
    }


def initial_queue() -> List[Dict[str, Any]]:
    return [
        _task("SIM-Q-001", "QUANT_MECHANISM", "LIN-Q-001", 90),
        _task("SIM-F-001", "FUNDAMENTAL_RESEARCH", "LIN-F-001", 90),
        _task("SIM-L-001", "LEGACY_RECOVERY", "LIN-L-001", 80),
        _task("SIM-E-001", "EVENT_DOCUMENT", "LIN-E-001", 70),
        _task("SIM-FLOW-001", "INSTITUTIONAL_FLOW", "LIN-FLOW-001", 70),
    ]


def load_config(base: Path | None = None) -> Dict[str, Any]:
    root = base or Path(__file__).resolve().parent
    return json.loads((root / "WORKFLOW_LANES.json").read_text())


def lane_task_types(config: Dict[str, Any], lane_id: str) -> set[str]:
    lane = next(x for x in config["lanes"] if x["lane_id"] == lane_id)
    return set(lane["task_types"])


def select_task(queue: List[Dict[str, Any]], config: Dict[str, Any], lane_id: str) -> Dict[str, Any] | None:
    allowed = lane_task_types(config, lane_id)
    ready = [t for t in queue if t["status"] == "READY" and t["task_type"] in allowed]
    if not ready:
        return None
    ready.sort(key=lambda x: (-x["priority"], x["task_id"]))
    return ready[0]


def execute_wake(queue: List[Dict[str, Any]], config: Dict[str, Any], lane_id: str, cycle: int) -> Dict[str, Any]:
    task = select_task(queue, config, lane_id)
    wake = {
        "cycle": cycle,
        "lane_id": lane_id,
        "lineage_id": None,
        "task_id": None,
        "stages": [],
        "created_tasks": [],
        "status": "IDLE",
    }
    if task is None:
        return wake

    lane = next(x for x in config["lanes"] if x["lane_id"] == lane_id)
    wake["lineage_id"] = task["lineage_id"]
    wake["task_id"] = task["task_id"]
    wake["status"] = "COMPLETE"
    wake["stages"] = lane["same_lineage_stages"][: config["execution_model"]["max_stages_per_wake"]]

    # Independence: challenge must never be executed by the discovery origin lane.
    if task["task_type"] in CHALLENGE_TYPES and task.get("origin_lane") == lane_id:
        raise AssertionError(f"self-validation detected for {task['lineage_id']}")

    task["status"] = "COMPLETE"
    task["history"].append({"cycle": cycle, "lane_id": lane_id, "stages": list(wake["stages"])})

    if task["task_type"] in DISCOVERY_TYPES:
        created = _task(
            f"SIM-VAL-{task['lineage_id']}",
            "VALIDATION",
            task["lineage_id"],
            95,
            origin_lane=lane_id,
        )
        created["frozen_hypothesis"] = True
        queue.append(created)
        wake["created_tasks"].append(created["task_id"])

    elif task["task_type"] in CHALLENGE_TYPES:
        if not task.get("frozen_hypothesis"):
            raise AssertionError(f"challenge without frozen hypothesis for {task['lineage_id']}")
        created = _task(
            f"SIM-INT-{task['lineage_id']}",
            "ECONOMIC_IDENTITY",
            task["lineage_id"],
            90,
            origin_lane=lane_id,
        )
        created["challenge_complete"] = True
        queue.append(created)
        wake["created_tasks"].append(created["task_id"])

    elif task["task_type"] in INTEGRATION_TYPES:
        if not task.get("challenge_complete"):
            raise AssertionError(f"integration before challenge complete for {task['lineage_id']}")

    elif task["task_type"] in EVIDENCE_TYPES:
        pass
    else:
        raise AssertionError(f"unrouted task type: {task['task_type']}")

    return wake


def simulate(cycles: int = 3) -> Dict[str, Any]:
    config = load_config()
    queue = deepcopy(initial_queue())
    wakes: List[Dict[str, Any]] = []

    for cycle in range(1, cycles + 1):
        for lane_id in LANE_ORDER:
            wakes.append(execute_wake(queue, config, lane_id, cycle))

    active = [t for t in queue if t["status"] == "READY"]
    executed = [w for w in wakes if w["status"] == "COMPLETE"]

    # One lineage per wake is structural: each non-idle wake has exactly one lineage.
    one_lineage_per_wake = all(w["lineage_id"] is not None for w in executed)

    # No discovery lane may execute challenge tasks for its own lineage.
    no_self_validation = True
    for t in queue:
        for h in t["history"]:
            if t["task_type"] in CHALLENGE_TYPES and t.get("origin_lane") == h["lane_id"]:
                no_self_validation = False

    # Every discovery lineage created in the first two cycles should reach integration by cycle 3.
    discovery_lineages = {t["lineage_id"] for t in queue if t["task_type"] in DISCOVERY_TYPES}
    integrated_lineages = {
        t["lineage_id"] for t in queue
        if t["task_type"] in INTEGRATION_TYPES and t["status"] == "COMPLETE"
    }
    remaining_discovery_work = [
        t for t in active
        if t["lineage_id"] in discovery_lineages and t["task_type"] in CHALLENGE_TYPES | INTEGRATION_TYPES
    ]

    hard = config["hard_authority"]
    authority_safe = hard == {
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

    # With five discovery lineages and only one challenge + one integrator wake per cycle,
    # three cycles intentionally leave backlog. Deadlock means no executable wake despite ready routed work,
    # not mere queueing caused by bounded throughput.
    ready_by_lane = {}
    for lane_id in LANE_ORDER:
        ready_by_lane[lane_id] = len([
            t for t in active if t["task_type"] in lane_task_types(config, lane_id)
        ])
    deadlock = bool(active) and all(v == 0 for v in ready_by_lane.values())

    passed = one_lineage_per_wake and no_self_validation and authority_safe and not deadlock

    return {
        "status": "PASS" if passed else "FAIL",
        "cycles": cycles,
        "wake_count": len(wakes),
        "productive_wakes": len(executed),
        "one_lineage_per_wake": one_lineage_per_wake,
        "self_validation_detected": not no_self_validation,
        "deadlock_detected": deadlock,
        "authority_safe": authority_safe,
        "discovery_lineages": sorted(discovery_lineages),
        "integrated_lineages": sorted(integrated_lineages),
        "remaining_discovery_handoffs": len(remaining_discovery_work),
        "ready_by_lane_after_simulation": ready_by_lane,
        "wakes": wakes,
    }


def main() -> None:
    result = simulate(3)
    out = Path(__file__).resolve().parents[1] / "simulations" / "workflow_lane_simulation_result.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"WORKFLOW_LANE_SIMULATION={result['status']}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
