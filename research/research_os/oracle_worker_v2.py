"""Oracle V2 Core worker entrypoint.

This module deliberately reuses the V1-qualified ResearchOSWorker for fresh
GitHub snapshots, claims, leases, atomic publication and recovery. The only
behavioral substitution is the stage executor, selected explicitly by a
`research_contract_version = v2-core` worker config.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .github_state import GitHubStateStore, PREFIX, StateConflict
from .model_backend import BackendUnavailable
from .oracle_worker import AUTHORITY, ResearchOSWorker, backend_from_config, timestamp
from .queue_replenisher import derive_refill_task
from .worker_preflight import canonical_hash, run_worker_preflight
from .expansion.v2_stage_executor import V2StageExecutor
from .expansion.v2_state import V2ModelAudit, V2StateStore


def _require_v2_config(config):
    if config.get("research_contract_version") != "v2-core":
        raise ValueError("V2_WORKER_REQUIRES_EXPLICIT_V2_CORE_CONTRACT")
    if config.get("economic_experiment_authorized", False) is not False:
        raise ValueError("V2_WORKER_ECONOMIC_AUTHORITY_MUST_REMAIN_FALSE")
    if config.get("prospective_observation_authorized", False) is not False:
        raise ValueError("V2_WORKER_PROSPECTIVE_AUTHORITY_MUST_REMAIN_FALSE")
    if config.get("real_capital_authorized", False) is not False:
        raise ValueError("V2_WORKER_REAL_CAPITAL_AUTHORITY_MUST_REMAIN_FALSE")
    if config.get("live_trading_authorized", False) is not False:
        raise ValueError("V2_WORKER_LIVE_AUTHORITY_MUST_REMAIN_FALSE")


class V2ResearchOSWorker(ResearchOSWorker):
    @staticmethod
    def _source_catalog(snapshot):
        catalog = {}
        prefix = PREFIX + "sources/"
        for path, blob_sha in sorted(snapshot.blobs.items()):
            if not path.startswith(prefix) or not path.endswith(".json"):
                continue
            try:
                record = snapshot.read(path)
            except (KeyError, ValueError, TypeError):
                continue
            if isinstance(record, dict):
                catalog[path] = {"record": record, "blob_sha": blob_sha}
        return catalog

    @staticmethod
    def _verify_bound_source(snapshot, task):
        inputs = task.get("inputs") or {}
        path = inputs.get("documentary_source")
        if not path:
            return
        if not isinstance(path, str) or not path.startswith(PREFIX + "sources/"):
            raise StateConflict("V2_DERIVED_SOURCE_PATH_INVALID")
        if path not in snapshot.blobs:
            raise StateConflict("V2_DERIVED_SOURCE_MISSING")
        expected_blob = inputs.get("documentary_source_blob")
        if expected_blob and snapshot.blobs[path] != expected_blob:
            raise StateConflict("V2_DERIVED_SOURCE_BLOB_CHANGED")
        record = snapshot.read(path)
        expected_record = inputs.get("documentary_source_record_hash")
        if expected_record and canonical_hash(record) != expected_record:
            raise StateConflict("V2_DERIVED_SOURCE_RECORD_CHANGED")
        packet = record.get("documentary_packet") or {}
        expected_packet = inputs.get("documentary_source_packet_hash")
        if expected_packet and packet.get("content_hash") != expected_packet:
            raise StateConflict("V2_DERIVED_SOURCE_PACKET_CHANGED")

    def _select(self, snapshot):
        task, lane = super()._select(snapshot)
        if task is not None:
            self._verify_bound_source(snapshot, task)
        return task, lane

    def _verify_lease(self, snapshot, task_id, generation, session, lane):
        task, preflight = super()._verify_lease(snapshot, task_id, generation, session, lane)
        self._verify_bound_source(snapshot, task)
        return task, preflight

    def _refill_or_idle(self, snapshot, base_receipt):
        if self.expected_task_id:
            return self._idle(snapshot, base_receipt, "CANARY_TARGET_TERMINAL", persist=False)
        if self.lane not in ("auto", "integrator_portfolio"):
            return self._idle(snapshot, base_receipt, "NO_ADMISSIBLE_LANE_TASK")

        derived = derive_refill_task(
            frontier=snapshot.read(PREFIX + "runtime/RESEARCH_FRONTIER.json"),
            tasks=snapshot.tasks(),
            created_at=timestamp(self.now()),
            source_catalog=self._source_catalog(snapshot),
        )
        task = derived["task"]
        if task is None:
            return self._idle(snapshot, base_receipt, derived["status"])

        original_head = snapshot.head
        # Reacquire both queue and documentary source identities before publish.
        with self.store.snapshot() as fresh:
            if fresh.head != original_head:
                raise StateConflict("QUEUE_CHANGED_BEFORE_REFILL")
            run_worker_preflight(fresh.base)
            confirmed = derive_refill_task(
                frontier=fresh.read(PREFIX + "runtime/RESEARCH_FRONTIER.json"),
                tasks=fresh.tasks(),
                created_at=task["created_at"],
                source_catalog=self._source_catalog(fresh),
            )
            if confirmed != derived:
                raise StateConflict("FRONTIER_DERIVATION_CHANGED")
            task_path = PREFIX + f"tasks/{task['task_id']}.json"
            key = derived["derivation_key"]
            receipt_path = PREFIX + f"receipts/queue-refill/{key}.json"
            event_path = PREFIX + f"events/queue-refill/{key}.json"
            event = {
                "event_id": key,
                "session_id": key,
                "worker_id": self.worker_id + ".integrator_portfolio",
                "action_id": task["task_id"],
                "event_type": "ACTION_COMPLETED",
                "event_seq": 1,
                "generation": 1,
                "emitted_at": timestamp(self.now()),
                "payload": {
                    "result": "DERIVED_ONE_READY_TASK",
                    "queue_state": "QUEUED",
                    "ready_count": 1,
                    "next_task_id": task["task_id"],
                    "next_lane": task["derivation"]["target_lane"],
                    "source_bound": bool((task.get("inputs") or {}).get("documentary_source")),
                },
            }
            receipt = dict(base_receipt, derivation=derived, producer_execution_same_wake=False)
            writes = {task_path: task, receipt_path: receipt, event_path: event}
            commit = self.store.commit(
                fresh,
                writes,
                create_only=list(writes),
                message="Research OS canonical source-aware queue refill " + key,
            )
            return dict(
                base_receipt,
                status="DERIVED_ONE_READY_TASK",
                task_id=task["task_id"],
                output_commit=commit,
            )


def build_v2_worker(config, *, store=None, backend=None):
    _require_v2_config(config)
    backend = backend if backend is not None else backend_from_config(config)
    if backend is not None and hasattr(backend, "model") and hasattr(backend, "budget"):
        backend = V2ModelAudit(backend)
    store = store or GitHubStateStore(
        cache=Path(config["cache"]), repository=config["repository"], branch=config["branch"]
    )
    store = V2StateStore(store, (config.get("model_backend") or {}).get("model", "DETERMINISTIC_ENGINE"),
                         backend if isinstance(backend, V2ModelAudit) else None, config.get("lane", "auto"))
    return V2ResearchOSWorker(
        store,
        lane=config.get("lane", "auto"),
        worker_id=config["worker_id"],
        release_sha=config["release_sha"],
        executor=V2StageExecutor(backend),
        lease_seconds=config.get("lease_seconds", 600), expected_task_id=config.get("canary_task_id"),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=["run", "dry-run", "noop"], default="run")
    parser.add_argument("--healthcheck", action="store_true")
    args = parser.parse_args(argv)

    config = json.loads(Path(args.config).read_text())
    _require_v2_config(config)
    backend = backend_from_config(config)
    if args.healthcheck:
        if backend is None:
            raise BackendUnavailable("LOCAL_MODEL_NOT_CONFIGURED")
        health = backend.healthcheck()
        health["research_contract_version"] = "v2-core"
        print(json.dumps(health, sort_keys=True))
        return 0

    if args.mode == "run":
        from deploy.oracle_release_install import _validate_release_receipt

        release_root = Path(__file__).resolve().parents[2]
        receipt = json.loads((release_root / ".quant_release_receipt.json").read_text())
        _validate_release_receipt(receipt, config["release_sha"])
        if Path(receipt["path"]).resolve() != release_root:
            raise ValueError("EXECUTABLE_RELEASE_PATH_MISMATCH")

    worker = build_v2_worker(config, backend=backend)
    result = worker.wake(mode=args.mode)
    result["research_contract_version"] = "v2-core"
    result["v2_preflight"] = worker.store.last_preflight
    print(json.dumps(result, sort_keys=True))
    if args.mode == "run":
        worker.store.compact_if_due()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StateConflict as exc:
        print(json.dumps({
            "status": "RETRY_FRESH_STATE_NEXT_WAKE",
            "reason": str(exc),
            "research_contract_version": "v2-core",
            "authority": AUTHORITY,
        }))
        raise SystemExit(0)
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        print(json.dumps({
            "status": "BLOCKED",
            "reason": str(exc),
            "research_contract_version": "v2-core",
            "authority": AUTHORITY,
        }))
        raise SystemExit(1)
