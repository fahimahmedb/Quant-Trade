from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List

from research.research_os.scientific_store import sha256_json


class DryRunExperimentRunner:
    """Builds and replays deterministic execution plans without opening economic outcomes."""

    def __init__(self, runner_version: str = "dry-run-experiment-runner.v1") -> None:
        self.runner_version = runner_version

    def plan(
        self,
        envelope: Dict[str, Any],
        source_qualifications: Iterable[Dict[str, Any]],
        runner_meta: Dict[str, Any],
    ) -> Dict[str, Any]:
        qualifications = list(source_qualifications)
        blockers: List[str] = []
        if envelope.get("status") != "FROZEN_READY_NO_OUTCOME":
            blockers.append("EXPERIMENT_ENVELOPE_NOT_FROZEN")
        if not envelope.get("protocol_hash"):
            blockers.append("PROTOCOL_HASH_MISSING")
        if envelope.get("outcome_opened") is not False:
            blockers.append("OUTCOME_ALREADY_OPENED")
        if not qualifications:
            blockers.append("SOURCE_QUALIFICATION_MISSING")
        if any(item.get("status") != "PASS" for item in qualifications):
            blockers.append("SOURCE_QUALIFICATION_BLOCKED")
        if any(item.get("outcome_accessed") is not False for item in qualifications):
            blockers.append("SOURCE_OUTCOME_ACCESS_DETECTED")

        required_meta = ("dataset_manifest_hash", "code_hash", "environment_hash", "seed")
        for field in required_meta:
            if runner_meta.get(field) in (None, ""):
                blockers.append(f"RUNNER_{field.upper()}_MISSING")

        source_hashes = sorted(item.get("route_hash") for item in qualifications if item.get("route_hash"))
        plan_payload = {
            "runner_version": self.runner_version,
            "experiment_id": envelope.get("experiment_id"),
            "protocol_hash": envelope.get("protocol_hash"),
            "dataset_manifest_hash": runner_meta.get("dataset_manifest_hash"),
            "code_hash": runner_meta.get("code_hash"),
            "environment_hash": runner_meta.get("environment_hash"),
            "seed": runner_meta.get("seed"),
            "source_route_hashes": source_hashes,
            "declared_metrics": list(runner_meta.get("declared_metrics") or []),
            "execution_mode": "DRY_RUN_NO_OUTCOME",
        }
        plan_hash = sha256_json(plan_payload)
        return {
            "experiment_id": envelope.get("experiment_id"),
            "status": "READY_FOR_REPRODUCIBLE_DRY_RUN" if not blockers else "BLOCK",
            "blockers": sorted(set(blockers)),
            "runner_version": self.runner_version,
            "execution_plan_hash": plan_hash,
            "plan": plan_payload,
            "outcome_access_authorized": False,
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
            "side_effects_authorized": False,
            "reproducible_inputs_frozen": not blockers,
        }

    def replay(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        if plan.get("outcome_accessed") is not False:
            raise PermissionError("dry-run replay refuses outcome-bearing state")
        replay_hash = sha256_json(plan["plan"])
        if replay_hash != plan["execution_plan_hash"]:
            raise ValueError("execution plan mutation detected")
        return {
            "experiment_id": plan["experiment_id"],
            "status": "REPLAY_MATCH",
            "execution_plan_hash": replay_hash,
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
        }


def summarize_reproducibility(plans: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = [deepcopy(item) for item in plans]
    return {
        "runner": "dry-run-experiment-runner.v1",
        "plan_count": len(items),
        "ready_count": sum(item["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN" for item in items),
        "blocked_count": sum(item["status"] != "READY_FOR_REPRODUCIBLE_DRY_RUN" for item in items),
        "outcomes_opened": sum(bool(item.get("outcome_accessed")) for item in items),
        "all_plan_hashes_unique": len({item["execution_plan_hash"] for item in items}) == len(items),
        "economic_result_observed": False,
    }
