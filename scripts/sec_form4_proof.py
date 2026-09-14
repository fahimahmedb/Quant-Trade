#!/usr/bin/env python3
"""Artifact freshness/reconciliation checks for the SEC Form-4 census mission."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "sec_form4_census"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    required = [
        "provenance_manifest.json", "census_summary.json", "waterfall.json",
        "normalized_candidates.jsonl", "normalized_purchase_observations.jsonl", "events.jsonl", "loss_ledger.jsonl",
        "mapping_ledger.jsonl", "acceptance_manifest.json",
    ]
    missing = [name for name in required if not (ART / name).exists()]
    if missing:
        print("missing SEC census artifacts: " + ", ".join(missing))
        return 1
    manifest = json.loads((ART / "provenance_manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["deterministic_outputs"].items():
        actual = sha(ART / name)
        if actual != expected:
            print(f"stale artifact {name}: expected {expected}, got {actual}")
            return 1
    events = load_jsonl(ART / "events.jsonl")
    mapping = load_jsonl(ART / "mapping_ledger.jsonl")
    losses = load_jsonl(ART / "loss_ledger.jsonl")
    summary = json.loads((ART / "census_summary.json").read_text(encoding="utf-8"))
    if len(events) != summary["formations"]:
        print("event count does not reconcile to census summary")
        return 1
    if len(mapping) != len(events):
        print("mapping ledger must contain exactly one row for every event")
        return 1
    if {r["event_id"] for r in mapping} != {e["event_id"] for e in events}:
        print("mapping ledger event IDs do not reconcile")
        return 1
    unresolved = sum(e["event_time_status"] != "RESOLVED" for e in events)
    if unresolved != summary["event_time_unresolved"]:
        print("event-time unresolved count mismatch")
        return 1
    forbidden = ("forward_return", "total_return", "pnl", "sharpe", "alpha", "hit_rate", "return_t")
    for path in [ART / x for x in required if x.endswith((".json", ".jsonl"))]:
        text = path.read_text(encoding="utf-8").lower()
        # `design_n_effective` is allowed; performance vocabulary is not expected in mission outputs.
        if any(token in text for token in forbidden):
            print(f"forbidden performance field/token present in {path.name}")
            return 1
    print(f"SEC census artifacts reconcile: {len(events)} formations, {len(mapping)} mapping rows, {len(losses)} loss/diagnostic rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
