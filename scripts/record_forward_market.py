#!/usr/bin/env python3
"""Run one bounded passive public market-data capture."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.recorders import AtomicCaptureStore, ForwardRecorder, binance_public_plan


def _verify_live_provenance(root: Path, plan, *, prior_sequences: dict[str, int] | None = None) -> dict[str, object]:
    """Fail closed unless the just-completed full plan is durably verifiable.

    Verification is deliberately independent of parsed market values: it checks only
    public-source provenance, HTTP success, exact raw bytes, hashes, parser version,
    and UTC/monotonic retrieval metadata. When prior_sequences is supplied, every
    source must have advanced during the current run so stale captures cannot satisfy
    a failed proof attempt.
    """
    store = AtomicCaptureStore(root)
    state = store.recover_state()
    prior_sequences = prior_sequences or {}
    verified: list[dict[str, object]] = []
    failures: list[str] = []

    for spec in plan:
        cursor = state.last_by_source.get(spec.source_id)
        if not isinstance(cursor, dict):
            failures.append(f"{spec.source_id}: missing durable cursor")
            continue
        try:
            current_sequence = int(cursor.get("sequence", 0))
        except (TypeError, ValueError):
            failures.append(f"{spec.source_id}: invalid durable sequence")
            continue
        if current_sequence <= int(prior_sequences.get(spec.source_id, 0)):
            failures.append(f"{spec.source_id}: no fresh capture committed by this proof run")
            continue
        capture_id = str(cursor.get("capture_id", ""))
        matches = list((root / "captures").glob(f"**/{capture_id}.json"))
        if len(matches) != 1:
            failures.append(f"{spec.source_id}: expected one capture metadata file, found {len(matches)}")
            continue
        metadata = json.loads(matches[0].read_text(encoding="utf-8"))
        raw_path = root / str(metadata.get("raw_path", ""))
        if not raw_path.is_file():
            failures.append(f"{spec.source_id}: raw bytes missing")
            continue
        raw = raw_path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        checks = {
            "sequence": metadata.get("sequence") == current_sequence,
            "endpoint": metadata.get("endpoint") == spec.endpoint,
            "parser_version": metadata.get("parser_version") == spec.parser_version,
            "http_2xx": isinstance(metadata.get("http_status"), int) and 200 <= metadata["http_status"] < 300,
            "sha256": metadata.get("raw_sha256") == digest,
            "raw_bytes": metadata.get("raw_bytes") == len(raw),
            "utc_started": str(metadata.get("retrieval_started_utc", "")).endswith("Z"),
            "utc_completed": str(metadata.get("retrieval_completed_utc", "")).endswith("Z"),
            "monotonic": isinstance(metadata.get("monotonic_started_ns"), int)
            and isinstance(metadata.get("monotonic_completed_ns"), int)
            and metadata["monotonic_completed_ns"] >= metadata["monotonic_started_ns"],
        }
        failed_checks = sorted(name for name, ok in checks.items() if not ok)
        if failed_checks:
            failures.append(f"{spec.source_id}: failed provenance checks {failed_checks}")
            continue
        verified.append(
            {
                "source_id": spec.source_id,
                "capture_id": capture_id,
                "sequence": current_sequence,
                "http_status": metadata["http_status"],
                "raw_bytes": len(raw),
                "raw_sha256": digest,
            }
        )

    return {
        "proof": "PASS" if not failures and len(verified) == len(plan) else "FAIL",
        "planned_sources": len(plan),
        "verified_sources": len(verified),
        "captures": verified,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="One-shot credential-free forward market recorder")
    parser.add_argument("--root", default="runtime/forward_market_recorder", help="capture root; no repo secret storage")
    parser.add_argument("--symbols", default="BTCUSDT,ETHUSDT", help="initial scope subset: BTCUSDT,ETHUSDT")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-endpoints", type=int, default=0, help="0 = all; positive values bound a short diagnostic run")
    parser.add_argument("--dry-plan", action="store_true", help="print public GET plan without network access")
    parser.add_argument(
        "--proof",
        action="store_true",
        help="run the complete BTCUSDT+ETHUSDT public plan once and verify fresh persisted provenance/raw hashes",
    )
    args = parser.parse_args()

    symbols = tuple(item.strip().upper() for item in args.symbols.split(",") if item.strip())
    plan = binance_public_plan(symbols)
    if args.max_endpoints < 0:
        parser.error("--max-endpoints must be >= 0")
    if args.proof and (symbols != ("BTCUSDT", "ETHUSDT") or args.max_endpoints or args.dry_plan):
        parser.error("--proof requires the complete default BTCUSDT,ETHUSDT plan and cannot be combined with --max-endpoints/--dry-plan")
    if args.max_endpoints:
        plan = plan[: args.max_endpoints]
    if args.dry_plan:
        print(json.dumps([spec.__dict__ for spec in plan], indent=2, sort_keys=True))
        return 0

    root = Path(args.root)
    store = AtomicCaptureStore(root)
    prior_sequences: dict[str, int] = {}
    if args.proof:
        before = store.recover_state()
        for source_id, cursor in before.last_by_source.items():
            if isinstance(cursor, dict):
                try:
                    prior_sequences[source_id] = int(cursor.get("sequence", 0))
                except (TypeError, ValueError):
                    prior_sequences[source_id] = 0
    summary = ForwardRecorder(store).run_once(plan, timeout_seconds=args.timeout)
    print(json.dumps({"run": summary.__dict__}, sort_keys=True))
    if args.proof:
        proof = _verify_live_provenance(root, plan, prior_sequences=prior_sequences)
        print(json.dumps({"live_provenance_proof": proof}, sort_keys=True))
        return 0 if proof["proof"] == "PASS" else 3
    return 0 if summary.successful > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
