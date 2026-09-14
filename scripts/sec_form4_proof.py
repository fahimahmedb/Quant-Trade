#!/usr/bin/env python3
"""Artifact freshness/reconciliation checks for the SEC Form-4 census mission."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.sec_form4 import REASON_CODES  # noqa: E402

ART = ROOT / "artifacts" / "sec_form4_census"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    if path.suffix == ".gz":
        text = gzip.decompress(path.read_bytes()).decode("utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def fail(message: str) -> int:
    print(message)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    required = [
        "provenance_manifest.json", "census_summary.json", "waterfall.json",
        "normalized_candidates.jsonl.gz", "normalized_purchase_observations.jsonl.gz",
        "events.jsonl", "loss_ledger.jsonl.gz", "mapping_ledger.jsonl",
        "acceptance_manifest.json", "price_coverage_snapshot.json", "CENSUS_REPORT.md",
    ]
    missing = [name for name in required if not (ART / name).exists()]
    if missing:
        return fail("missing SEC census artifacts: " + ", ".join(missing))

    manifest = json.loads((ART / "provenance_manifest.json").read_text(encoding="utf-8"))
    for name, expected in manifest["deterministic_outputs"].items():
        actual = sha(ART / name)
        if actual != expected:
            return fail(f"stale artifact {name}: expected {expected}, got {actual}")

    price_snapshot = json.loads((ART / "price_coverage_snapshot.json").read_text(encoding="utf-8"))
    price_symbols_hash = canonical_sha(price_snapshot.get("symbols", {}))
    expected_price_hash = manifest.get("mapping_input", {}).get("price_coverage_symbols_sha256")
    if price_symbols_hash != expected_price_hash:
        return fail(f"price coverage snapshot drift: expected {expected_price_hash}, got {price_symbols_hash}")

    events = load_jsonl(ART / "events.jsonl")
    observations = load_jsonl(ART / "normalized_purchase_observations.jsonl.gz")
    candidates = load_jsonl(ART / "normalized_candidates.jsonl.gz")
    mapping = load_jsonl(ART / "mapping_ledger.jsonl")
    losses = load_jsonl(ART / "loss_ledger.jsonl.gz")
    summary = json.loads((ART / "census_summary.json").read_text(encoding="utf-8"))
    waterfall = json.loads((ART / "waterfall.json").read_text(encoding="utf-8"))
    acceptance = json.loads((ART / "acceptance_manifest.json").read_text(encoding="utf-8"))

    if len(events) != summary["formations"] or len(events) != waterfall.get("economic_formations"):
        return fail("event count does not reconcile to census summary/waterfall")
    if len({e["event_id"] for e in events}) != len(events):
        return fail("event IDs are not unique")
    if sum(summary.get("annual_formations", {}).values()) != len(events):
        return fail("annual formation distribution does not reconcile")
    if sum(summary.get("issuer_event_distribution", {}).values()) != len(events):
        return fail("issuer formation distribution does not reconcile")
    if len(mapping) != len(events):
        return fail("mapping ledger must contain exactly one row for every event")
    if {r["event_id"] for r in mapping} != {e["event_id"] for e in events}:
        return fail("mapping ledger event IDs do not reconcile")
    mappable = sum(r["mapping_status"] == "MAPPABLE" for r in mapping)
    if mappable != summary["mappable_events"] or len(events) - mappable != summary["unmappable_events"]:
        return fail("mapping coverage does not reconcile to event population")
    if sum(v["events"] for v in summary.get("mapping_coverage_by_year", {}).values()) != len(events):
        return fail("mapping coverage by year does not reconcile")
    unresolved = sum(e["event_time_status"] != "RESOLVED" for e in events)
    if unresolved != summary["event_time_unresolved"]:
        return fail("event-time unresolved count mismatch")

    obs_by_id = {o["observation_id"]: o for o in observations}
    for event in events:
        owners = set(event["owner_ciks"])
        if len(owners) < 2:
            return fail(f"event {event['event_id']} has fewer than two distinct owners")
        if int(event["session_distance"]) > 10:
            return fail(f"event {event['event_id']} exceeds frozen 10-session rule")
        if not event["constituent_observation_ids"] or any(oid not in obs_by_id for oid in event["constituent_observation_ids"]):
            return fail(f"event {event['event_id']} has broken observation lineage")
        if event["event_time_status"] == "RESOLVED":
            # Reconstruct each owner's earliest public acceptance from exact event
            # accession lineage.  event_time must be the second-earliest distinct
            # owner observation, i.e. the first instant two owners are public.
            owner_times: list[str] = []
            for owner in owners:
                times: list[str] = []
                for oid in event["constituent_observation_ids"]:
                    obs = obs_by_id[oid]
                    if obs["owner_cik"] != owner:
                        continue
                    for acc in obs["accessions"]:
                        if acc in acceptance:
                            times.append(acceptance[acc]["acceptance_time"])
                if times:
                    owner_times.append(min(times))
            if len(owner_times) < 2 or sorted(owner_times)[1] != event["event_time"]:
                return fail(f"event {event['event_id']} event_time is not the causal second-owner public time")
            exact_pairs = sorted((a, acceptance[a]["acceptance_time"]) for a in event["accessions"] if a in acceptance)
            if exact_pairs != [tuple(x) for x in event.get("acceptance_timestamps", [])]:
                return fail(f"event {event['event_id']} acceptance timestamp lineage drift")

    for row in candidates:
        if row["status"] == "QUALIFYING":
            if row["document_type"] != "4" or row["transaction_code"] != "P" or row["acquired_disposed_code"] != "A":
                return fail("qualifying candidate violates frozen original-Form4 P/acquired semantics")
            if not row.get("issuer_cik") or not row.get("owner_cik"):
                return fail("qualifying candidate has unresolved issuer/owner identity")
            if row.get("unresolved_owner_cik_rows", 0) != 0 or len(row.get("reporting_owner_ciks", [])) != 1:
                return fail("qualifying candidate is not unambiguous single-owner identity")
            if not (row.get("is_director") or row.get("is_officer")):
                return fail("qualifying candidate is not officer/director")
    expected_candidates = waterfall.get("original_form4_p_acquired_rows", 0) + waterfall.get("form4a_p_acquired_rows", 0)
    if len(candidates) != expected_candidates:
        return fail("normalized P/acquired candidate table does not reconcile to Form4 + Form4/A candidate rows")

    if len({row["record_id"] for row in losses}) != len(losses):
        return fail("loss/unresolved ledger record IDs are not unique")
    unknown_reasons = sorted({code for row in losses for code in row.get("reason_codes", []) if code not in REASON_CODES})
    if unknown_reasons:
        return fail("unknown loss-ledger reason codes: " + ", ".join(unknown_reasons))

    forbidden = ("forward_return", "total_return", "pnl", "sharpe", "alpha", "hit_rate", "return_t")

    def reject_forbidden_keys(value: object, where: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                lowered = str(key).lower()
                if any(token in lowered for token in forbidden):
                    raise ValueError(f"forbidden performance field {key!r} present in {where}")
                reject_forbidden_keys(nested, where)
        elif isinstance(value, list):
            for nested in value:
                reject_forbidden_keys(nested, where)

    structured: list[tuple[str, object]] = [
        ("census_summary.json", summary), ("waterfall.json", waterfall),
        ("acceptance_manifest.json", acceptance), ("price_coverage_snapshot.json", price_snapshot),
        ("events.jsonl", events), ("mapping_ledger.jsonl", mapping),
        ("loss_ledger.jsonl.gz", losses), ("normalized_candidates.jsonl.gz", candidates),
        ("normalized_purchase_observations.jsonl.gz", observations),
    ]
    try:
        for name, payload in structured:
            reject_forbidden_keys(payload, name)
    except ValueError as exc:
        return fail(str(exc))

    print(
        f"SEC census artifacts reconcile: {len(events)} formations, {len(mapping)} mapping rows, "
        f"{len(losses)} loss/diagnostic rows; frozen semantics and causal timing checks pass"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
