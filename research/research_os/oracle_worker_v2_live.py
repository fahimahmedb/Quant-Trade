"""Oracle V2 entrypoint with non-authoritative Live Lab local projection.

Scientific behavior is identical to oracle_worker_v2. The only addition is a
post-commit local outbox mirror consumed by an independent Site emitter.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .github_state import StateConflict
from .live_lab_bridge import DEFAULT_OUTBOX, LiveLabProjectionStore, attach_live_lab_projection
from .model_backend import BackendUnavailable
from .oracle_worker import AUTHORITY, backend_from_config
from .oracle_worker_v2 import _require_v2_config, build_v2_worker


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--mode", choices=["run", "dry-run", "noop"], default="run")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument("--outbox", default=str(DEFAULT_OUTBOX))
    args = parser.parse_args(argv)

    config = json.loads(Path(args.config).read_text())
    _require_v2_config(config)
    backend = backend_from_config(config)
    if args.healthcheck:
        if backend is None:
            raise BackendUnavailable("LOCAL_MODEL_NOT_CONFIGURED")
        health = backend.healthcheck()
        health["research_contract_version"] = "v2-core"
        health["live_lab_projection"] = "LOCAL_OUTBOX_ONLY"
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
    attach_error = None
    try:
        attach_live_lab_projection(worker, Path(args.outbox))
    except (OSError, ValueError, RuntimeError) as exc:
        # Site projection is deliberately subordinate to research execution.
        attach_error = f"{type(exc).__name__}:{exc}"

    result = worker.wake(mode=args.mode)
    result["research_contract_version"] = "v2-core"
    result["v2_preflight"] = worker.store.last_preflight
    projection_store = worker.store if isinstance(worker.store, LiveLabProjectionStore) else None
    projection_error = attach_error or (projection_store.last_projection_error if projection_store else None)
    result["live_lab_projection"] = {
        "mode": "LOCAL_OUTBOX_ONLY" if projection_store else "DISABLED_DEGRADED",
        "outbox": str(Path(args.outbox)),
        "degraded": projection_error is not None,
        "error": projection_error,
    }
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
