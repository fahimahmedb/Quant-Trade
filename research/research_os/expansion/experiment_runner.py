from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List
import hashlib
import sys
from pathlib import Path

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
        if plan.get("status") != "READY_FOR_REPRODUCIBLE_DRY_RUN":
            raise ValueError("blocked execution plan cannot be replayed")
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

    @staticmethod
    def execution_code_hash() -> str:
        root = Path(__file__).resolve().parents[1]
        paths = [Path(__file__), root / 'expansion/engine_dossiers_v1.py',
                 root / 'engines/builtin.py', root / 'engines/protocol.py',
                 root / 'expansion/archaeology.py', root / 'expansion/persistent_state.py',
                 root / 'scientific_store.py']
        return sha256_json({str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    @staticmethod
    def execution_environment_hash() -> str:
        import decimal
        return sha256_json({"python": sys.version, "decimal_precision": decimal.getcontext().prec,
                            "decimal_rounding": decimal.getcontext().rounding})

    def execute(self, plan: Dict[str, Any], inputs: List[Dict[str, Any]], checkpoint_dir: Path) -> Dict[str, Any]:
        """Execute only pinned synthetic documentary transforms; never a backtest.

        PREPARED survives interruption before COMPLETED. Replay recomputes the
        transform and must match the immutable completed result byte-for-byte.
        """
        from research.research_os.engines.builtin import ENGINE_REGISTRY
        from research.research_os.engines.protocol import EngineContext
        from .archaeology import EdgeArchaeologyEngine
        from .persistent_state import write_immutable_json

        self.replay(plan)
        payload = plan['plan']
        if payload.get('declared_metrics') != ['DOCUMENTARY_FACTS_V1']:
            raise ValueError('execution supports only DOCUMENTARY_FACTS_V1')
        if not inputs or sha256_json(inputs) != payload.get('dataset_manifest_hash'):
            raise ValueError('execution input hash mismatch')
        if payload.get('code_hash') != self.execution_code_hash():
            raise ValueError('execution code hash mismatch')
        if payload.get('environment_hash') != self.execution_environment_hash():
            raise ValueError('execution environment hash mismatch')
        binding = {"execution_plan_hash": plan['execution_plan_hash'],
                   "input_hash": sha256_json(inputs), "state": "PREPARED"}
        key = plan['execution_plan_hash']
        write_immutable_json(Path(checkpoint_dir) / f'{key}.prepared.json', binding)
        records = []
        for item in inputs:
            if set(item) != {'engine_key', 'source'} or 'documentary_packet' not in item['source']:
                raise ValueError('execution requires structured documentary inputs')
            engine = EdgeArchaeologyEngine() if item['engine_key'] == 'archaeology' else ENGINE_REGISTRY[item['engine_key']]
            output = engine.run(item['source'], EngineContext('DOCUMENTARY_FACTS_V1'))
            records.append(output)
        result = {"experiment_id": plan['experiment_id'], "execution_plan_hash": key,
                  "input_hash": binding['input_hash'], "state": "EXECUTED_DRY_RUN",
                  "records": records, "evidence_class": "SYNTHETIC",
                  "outcome_accessed": False, "economic_result": "NOT_OBSERVED"}
        result['execution_receipt_hash'] = sha256_json(result)
        write_immutable_json(Path(checkpoint_dir) / f'{key}.completed.json', result)
        return result


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
