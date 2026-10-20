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

from .github_state import GitHubStateStore, StateConflict
from .model_backend import BackendUnavailable
from .oracle_worker import AUTHORITY, ResearchOSWorker, backend_from_config
from .expansion.v2_stage_executor import V2StageExecutor


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


def build_v2_worker(config, *, store=None, backend=None):
    _require_v2_config(config)
    backend = backend if backend is not None else backend_from_config(config)
    store = store or GitHubStateStore(
        cache=Path(config["cache"]), repository=config["repository"], branch=config["branch"]
    )
    return ResearchOSWorker(
        store,
        lane=config.get("lane", "auto"),
        worker_id=config["worker_id"],
        release_sha=config["release_sha"],
        executor=V2StageExecutor(backend),
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
    print(json.dumps(worker.wake(mode=args.mode), sort_keys=True))
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
