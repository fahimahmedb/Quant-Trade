#!/usr/bin/env python3
"""Run one bounded passive public market-data capture."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.recorders import AtomicCaptureStore, ForwardRecorder, binance_public_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="One-shot credential-free forward market recorder")
    parser.add_argument("--root", default="runtime/forward_market_recorder", help="capture root; no repo secret storage")
    parser.add_argument("--symbols", default="BTCUSDT,ETHUSDT", help="initial scope subset: BTCUSDT,ETHUSDT")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--max-endpoints", type=int, default=0, help="0 = all; positive values bound a short proof run")
    parser.add_argument("--dry-plan", action="store_true", help="print public GET plan without network access")
    args = parser.parse_args()

    symbols = tuple(item.strip().upper() for item in args.symbols.split(",") if item.strip())
    plan = binance_public_plan(symbols)
    if args.max_endpoints < 0:
        parser.error("--max-endpoints must be >= 0")
    if args.max_endpoints:
        plan = plan[: args.max_endpoints]
    if args.dry_plan:
        print(json.dumps([spec.__dict__ for spec in plan], indent=2, sort_keys=True))
        return 0

    summary = ForwardRecorder(AtomicCaptureStore(args.root)).run_once(plan, timeout_seconds=args.timeout)
    print(json.dumps(summary.__dict__, sort_keys=True))
    return 0 if summary.successful > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
