"""Opt-in Oracle worker variant that emits explicit Live Lab UI metadata.

The canonical ResearchOSWorker remains unchanged. This wrapper only enriches its
existing durable worker-event payloads. It does not add a network transport and
it does not change scientific authority, queueing, leases, receipts or results.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .github_state import GitHubStateStore, StateConflict
from .live_lab_contract import assert_live_ui_contract, live_ui_metadata
from .model_backend import BackendUnavailable
from .oracle_worker import AUTHORITY, ResearchOSWorker, backend_from_config, next_stage
from .worker_stages import CanonicalStageExecutor


class LiveLabResearchOSWorker(ResearchOSWorker):
    """Canonical worker with truth-preserving, explicit UI annotations."""

    def _event(self, task, session, lane, seq, kind, payload):
        event = super()._event(task, session, lane, seq, kind, payload)
        stage = payload.get("stage") if isinstance(payload, dict) else None
        if kind == "ACTION_STARTED":
            stage = next_stage(task, lane)
        if stage:
            event["payload"].update(live_ui_metadata(lane, stage))
        return event


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=["run", "dry-run", "noop"], default="run")
    parser.add_argument("--healthcheck", action="store_true")
    args = parser.parse_args(argv)

    assert_live_ui_contract()
    config = json.loads(Path(args.config).read_text())
    backend = backend_from_config(config)
    if args.healthcheck:
        if backend is None:
            raise BackendUnavailable("LOCAL_MODEL_NOT_CONFIGURED")
        print(json.dumps(backend.healthcheck(), sort_keys=True))
        return 0

    if args.mode == "run":
        from deploy.oracle_release_install import _validate_release_receipt
        release_root = Path(__file__).resolve().parents[2]
        receipt = json.loads((release_root / ".quant_release_receipt.json").read_text())
        _validate_release_receipt(receipt, config["release_sha"])
        if Path(receipt["path"]).resolve() != release_root:
            raise ValueError("EXECUTABLE_RELEASE_PATH_MISMATCH")

    store = GitHubStateStore(cache=Path(config["cache"]), repository=config["repository"], branch=config["branch"])
    worker = LiveLabResearchOSWorker(
        store,
        lane=config.get("lane", "auto"),
        worker_id=config["worker_id"],
        release_sha=config["release_sha"],
        executor=CanonicalStageExecutor(backend),
    )
    print(json.dumps(worker.wake(mode=args.mode), sort_keys=True))
    if args.mode == "run":
        store.compact_if_due()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StateConflict as exc:
        print(json.dumps({"status": "RETRY_FRESH_STATE_NEXT_WAKE", "reason": str(exc), "authority": AUTHORITY}))
        raise SystemExit(0)
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc), "authority": AUTHORITY}))
        raise SystemExit(1)
