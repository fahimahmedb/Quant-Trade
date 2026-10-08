#!/usr/bin/env python3
"""Scientifically gated rerun of the frozen Polymarket neg-risk parity screen.

This runner changes measurement only. Economic universe, route arithmetic, fees,
depth logic, threshold, persistence rule, snapshot count and interval remain frozen.
The CLOB book `timestamp` is retained as state-version provenance; it is not used
as an HTTP acquisition timestamp. A single batch request is gated by its measured
client request/response span using the same 1000 ms numeric synchrony bound.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

SNAPSHOTS = 60
INTERVAL_S = 10.0
MAX_EVENTS = 10
MAX_ACQUISITION_SPAN_MS = 1000.0
THRESHOLD_USDC = Decimal("0.10")
THRESHOLD_RATE = Decimal("0.001")
PINNED_ECONOMIC_COLLECTOR_BLOB = "faffb23fc0c0fce0ad498b05681e2608d0f5b347"
SOURCE_RUN_ID = 37815709390
SOURCE_ARTIFACT = "polymarket-neg-risk-readonly-screen"
SOURCE_SELECTED_EVENT_IDS = (
    "106981", "233140", "237722", "250181", "250182",
    "250183", "256576", "256577", "256578", "259108",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n")
    os.replace(tmp, path)


def import_collector():
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    import neg_risk_collector as nr  # type: ignore
    return nr


def event_key(s):
    return (0, int(s.event_id)) if s.event_id.isdigit() else (1, s.event_id)


def fee_obj(f) -> dict[str, str]:
    return {"rate": str(f.rate), "exponent": str(f.exponent)}


def require_book_contract(nr, books: dict[str, dict[str, Any]]) -> None:
    for b in books.values():
        for k in ("bids", "asks", "timestamp", "hash", "min_order_size", "tick_size", "neg_risk"):
            if k not in b:
                raise nr.DataContractError(f"book missing required field {k}")
        if not isinstance(b["bids"], list) or not isinstance(b["asks"], list):
            raise nr.DataContractError("book bids/asks are not lists")
        nr.dec(b["tick_size"], "tick_size")
        if not str(b["hash"]):
            raise nr.DataContractError("empty book hash")


def depth_for_route(nr, event, books, source_market_id: str) -> dict[str, Any]:
    src = next(m for m in event.markets if m.market_id == source_market_id)
    buy_avail = sum(nr.dec(x["size"], "size") for x in books[src.no_token].get("asks", []))
    sells: dict[str, str] = {}
    for m in event.markets:
        if m.market_id != source_market_id:
            sells[m.market_id] = str(sum(nr.dec(x["size"], "size") for x in books[m.yes_token].get("bids", [])))
    return {"buy_no_available_shares": str(buy_avail), "sell_yes_available_shares": sells}


def evaluate_routes_same_economics(nr, event, books_payload: Any):
    """Exact frozen route arithmetic, with only the invalid state-timestamp gate removed."""
    books = nr.index_books(books_payload, event.token_ids)
    results = []
    for src in event.markets:
        no_book = books[src.no_token]
        leg_books = [books[m.yes_token] for m in event.markets if m.market_id != src.market_id]
        q = max([nr.dec(no_book["min_order_size"], "min_order_size")] +
                [nr.dec(b["min_order_size"], "min_order_size") for b in leg_books])
        buy = nr.walk_book(no_book.get("asks"), q, True, src.fee)
        if buy is None:
            continue
        sell_gross = nr.D0
        sell_fees = nr.D0
        ok = True
        for m in event.markets:
            if m.market_id == src.market_id:
                continue
            f = nr.walk_book(books[m.yes_token].get("bids"), q, False, m.fee)
            if f is None:
                ok = False
                break
            sell_gross += f.gross
            sell_fees += f.fee
        if not ok:
            continue
        all_fees = buy.fee + sell_fees
        gap = sell_gross - sell_fees - buy.gross - buy.fee
        gross_notional = buy.gross + sell_gross
        threshold = max(THRESHOLD_USDC, gross_notional * THRESHOLD_RATE)
        results.append(nr.RouteResult(
            event.event_id, src.market_id, q, buy.gross, sell_gross,
            all_fees, gap, gross_notional, threshold, gap >= threshold,
        ))
    return results


def timed_snapshot(nr, event):
    started_utc = now_utc()
    start_ns = time.monotonic_ns()
    raw, payload = nr.snapshot_event(event)
    elapsed_ms = (time.monotonic_ns() - start_ns) / 1_000_000.0
    ended_utc = now_utc()
    return started_utc, ended_utc, elapsed_ms, raw, payload


def discover_frozen_universe(nr):
    raw_probe, probe = nr._request("GET", f"{nr.GAMMA}/events?closed=false&order=id&ascending=true&limit=1&offset=0")
    if not isinstance(probe, list):
        raise nr.DataContractError("Gamma preflight events response is not a list")
    events_payload = nr.list_open_events()
    eligible = []
    rejects = defaultdict(int)
    for e in events_payload:
        try:
            s = nr.normalize_standard_neg_risk_event(e)
            if len(s.markets) != 3:
                rejects["component_count_not_exactly_3"] += 1
                continue
            eligible.append(s)
        except nr.DataContractError as ex:
            rejects[str(ex)] += 1
    eligible.sort(key=event_key)
    selected0 = eligible[:MAX_EVENTS]
    if tuple(s.event_id for s in selected0) != SOURCE_SELECTED_EVENT_IDS:
        raise nr.DataContractError(
            "deterministic selected event set drifted from source failed screen; refuse non-identical rerun"
        )
    selected = []
    for first in selected0:
        current = nr.refetch_event(first.event_id)
        if len(current.markets) != 3:
            raise nr.DataContractError(f"event component count changed from exactly 3: {first.event_id}")
        if {m.condition_id for m in current.markets} != {m.condition_id for m in first.markets}:
            raise nr.DataContractError(f"event component set changed during completeness refetch: {first.event_id}")
        selected.append(current)
    return raw_probe, events_payload, eligible, selected, dict(sorted(rejects.items()))


def blocked_summary(error: str) -> dict[str, Any]:
    return {
        "prior_kill_verdict": "INVALIDATED_BY_DATA_QUALITY_GATE",
        "timestamp_root_cause": "API_TIMESTAMP_SEMANTICS_MISUNDERSTOOD",
        "measurement_correction": "single batch request-response acquisition span; state timestamps diagnostic only",
        "economic_spec_changed": False,
        "runtime_gate": "FAIL",
        "data_quality_gate": "BLOCKED",
        "scientific_execution_gate": "BLOCKED",
        "same_frozen_test_reexecutable": True,
        "routes_evaluated": 0,
        "primary_statistic_computable": False,
        "economic_verdict": None,
        "terminal_state": "BLOCKED_DATA_QUALITY",
        "error": error,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "finished_utc": now_utc(),
    }


def run(mode: str, out_dir: Path, simulate_failure: bool = False) -> int:
    out_dir.mkdir(parents=True, exist_ok=False)
    diagnostic = {
        "mode": mode,
        "started_utc": now_utc(),
        "runtime_gate": "STARTED",
        "real_capital_authorized": False,
        "live_trading_authorized": False,
        "wallet_used": False,
        "orders_used": False,
        "conversion_used": False,
        "settlement_outcomes_used": False,
    }
    atomic_json(out_dir / "diagnostic.json", diagnostic)
    try:
        if simulate_failure:
            raise RuntimeError("SIMULATED_ENTRYPOINT_FAILURE_FOR_DIAGNOSTIC_TEST")
        nr = import_collector()
        diagnostic["runtime_gate"] = "IMPORT_PASS"
        atomic_json(out_dir / "diagnostic.json", diagnostic)

        raw_probe, events_payload, eligible, selected, rejects = discover_frozen_universe(nr)
        if not selected:
            raise nr.DataContractError("no selected frozen events")

        s0, e0, elapsed0, pre_raw, pre_payload = timed_snapshot(nr, selected[0])
        pre_books = nr.index_books(pre_payload, selected[0].token_ids)
        require_book_contract(nr, pre_books)
        pre_state_skew = max(nr.timestamp_ms(b) for b in pre_books.values()) - min(nr.timestamp_ms(b) for b in pre_books.values())
        preflight = {
            "gamma_preflight_sha256": hashlib.sha256(raw_probe).hexdigest(),
            "gamma_discovery_sha256": hashlib.sha256(json.dumps(events_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "events_eligible": len(eligible),
            "events_sampled": len(selected),
            "selected_event_ids": [e.event_id for e in selected],
            "rejection_counts": rejects,
            "clob_preflight_event_id": selected[0].event_id,
            "clob_preflight_raw_sha256": hashlib.sha256(pre_raw).hexdigest(),
            "clob_request_started_utc": s0,
            "clob_request_ended_utc": e0,
            "clob_batch_acquisition_span_ms": elapsed0,
            "book_state_timestamp_skew_ms_diagnostic_only": pre_state_skew,
            "measurement_gate": f"batch acquisition span <= {MAX_ACQUISITION_SPAN_MS} ms",
        }
        atomic_json(out_dir / "preflight.json", preflight)
        if elapsed0 > MAX_ACQUISITION_SPAN_MS:
            raise nr.DataContractError("preflight batch acquisition span exceeds frozen 1000 ms synchrony bound")

        if mode == "smoke":
            diagnostic.update({"runtime_gate": "PASS", "finished_utc": now_utc(), "status": "SMOKE_PASS"})
            atomic_json(out_dir / "diagnostic.json", diagnostic)
            return 0

        manifest = {
            "source_run_id": SOURCE_RUN_ID,
            "source_artifact": SOURCE_ARTIFACT,
            "prior_kill_verdict": "INVALIDATED_BY_DATA_QUALITY_GATE",
            "timestamp_root_cause": "API_TIMESTAMP_SEMANTICS_MISUNDERSTOOD",
            "same_frozen_test_reexecutable": True,
            "economic_spec_changed": False,
            "snapshots_requested": SNAPSHOTS,
            "interval_s": INTERVAL_S,
            "max_events": MAX_EVENTS,
            "max_acquisition_span_ms": MAX_ACQUISITION_SPAN_MS,
            "threshold_rule": "max(0.10 pUSD, 10 bp * total traded gross notional)",
            "persistence_rule": "same route >=3 non-adjacent snapshots OR exceedance in >=2 distinct events",
            "selected_event_ids": [e.event_id for e in selected],
            "events_eligible": len(eligible),
            "events_sampled": len(selected),
            "measurement_correction": "book timestamp retained as state-version provenance; simultaneity measured by one POST /books request-response span",
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        }
        atomic_json(out_dir / "manifest.json", manifest)

        audit_rows = []
        route_rows = []
        data_contract_error = None
        for n in range(SNAPSHOTS):
            cycle_start = time.monotonic()
            events_valid = 0
            for event in selected:
                try:
                    rs, re, elapsed_ms, raw, payload = timed_snapshot(nr, event)
                    books = nr.index_books(payload, event.token_ids)
                    require_book_contract(nr, books)
                    state_ts = {t: nr.timestamp_ms(b) for t, b in books.items()}
                    state_skew = max(state_ts.values()) - min(state_ts.values())
                    base = {
                        "snapshot_n": n,
                        "event_id": event.event_id,
                        "request_started_utc": rs,
                        "request_ended_utc": re,
                        "batch_acquisition_span_ms": elapsed_ms,
                        "token_ids": list(event.token_ids),
                        "raw_sha256": hashlib.sha256(raw).hexdigest(),
                        "book_state_timestamps_ms": state_ts,
                        "book_hashes": {t: str(b["hash"]) for t, b in books.items()},
                        "book_state_timestamp_skew_ms_diagnostic_only": state_skew,
                        "fee_schedules": {m.market_id: fee_obj(m.fee) for m in event.markets},
                    }
                    if elapsed_ms > MAX_ACQUISITION_SPAN_MS:
                        base.update({"valid": False, "invalid_reason": "BATCH_ACQUISITION_SPAN_GT_1000MS"})
                        audit_rows.append(base)
                        continue
                    routes = evaluate_routes_same_economics(nr, event, payload)
                    events_valid += 1
                    ros = []
                    for r in routes:
                        rbps = (r.gap / r.gross_traded_notional * Decimal("10000")) if r.gross_traded_notional else None
                        row = {
                            "snapshot_n": n,
                            "event_id": r.event_id,
                            "source_market": r.source_market_id,
                            "q": str(r.q),
                            "buy_cost": str(r.buy_cost),
                            "sell_proceeds": str(r.sell_proceeds),
                            "taker_fees": str(r.taker_fees),
                            "net_gap": str(r.gap),
                            "gross_traded_notional": str(r.gross_traded_notional),
                            "net_gap_bps": str(rbps) if rbps is not None else None,
                            "threshold": str(r.threshold),
                            "threshold_exceeded": bool(r.violation),
                            "batch_acquisition_span_ms": elapsed_ms,
                            "depth": depth_for_route(nr, event, books, r.source_market_id),
                        }
                        ros.append(row)
                        route_rows.append(row)
                    base.update({"valid": True, "routes": ros})
                    audit_rows.append(base)
                except nr.DataContractError as ex:
                    data_contract_error = f"DATA_CONTRACT_ERROR: {ex}"
                    audit_rows.append({"snapshot_n": n, "event_id": event.event_id, "valid": False, "fatal_data_contract_error": str(ex)})
                    raise
            audit_rows.append({"snapshot_n": n, "cycle_summary": True, "events_valid": events_valid, "events_sampled": len(selected)})
            if n + 1 < SNAPSHOTS:
                time.sleep(max(0.0, INTERVAL_S - (time.monotonic() - cycle_start)))

        by_route = defaultdict(list)
        exceedance_events = set()
        for row in route_rows:
            key = (row["event_id"], row["source_market"])
            by_route[key].append(row)
            if row["threshold_exceeded"]:
                exceedance_events.add(row["event_id"])

        persistence = {}
        persistent_routes = []
        for key, rows in by_route.items():
            idx = sorted({int(r["snapshot_n"]) for r in rows if r["threshold_exceeded"]})
            chosen = []
            last = -10**9
            for i in idx:
                if i - last >= 2:
                    chosen.append(i)
                    last = i
            persistence[key] = len(chosen)
            if len(chosen) >= 3:
                persistent_routes.append(key)

        structural = bool(persistent_routes or len(exceedance_events) >= 2)
        valid_event_snapshots = sum(1 for r in audit_rows if r.get("valid") is True)
        valid_rounds = sum(1 for r in audit_rows if r.get("cycle_summary") and r["events_valid"] == r["events_sampled"] and r["events_sampled"] > 0)
        routes_evaluated = len(route_rows)
        primary_statistic_computable = routes_evaluated > 0
        data_quality_gate = "PASS" if data_contract_error is None and valid_event_snapshots > 0 else "BLOCKED"
        scientific_execution_gate = "PASS" if primary_statistic_computable else "BLOCKED"

        if data_quality_gate != "PASS" or scientific_execution_gate != "PASS":
            economic_verdict = None
            terminal_state = "BLOCKED_DATA_QUALITY"
        elif structural:
            economic_verdict = "PROMOTE_TO_CONVERSION_COST_LATENCY_VALIDATION"
            terminal_state = "VALID_ECONOMIC_VERDICT"
        else:
            economic_verdict = "KILL"
            terminal_state = "VALID_ECONOMIC_VERDICT"

        best = max(route_rows, key=lambda r: Decimal(r["net_gap"])) if route_rows else None
        if best is not None:
            best = dict(best)
            best["persistence_count"] = persistence.get((best["event_id"], best["source_market"]), 0)

        summary = {
            "prior_kill_verdict": "INVALIDATED_BY_DATA_QUALITY_GATE",
            "timestamp_root_cause": "API_TIMESTAMP_SEMANTICS_MISUNDERSTOOD",
            "measurement_correction": "single batch request-response acquisition span; state timestamps diagnostic only",
            "economic_spec_changed": False,
            "runtime_gate": "PASS",
            "data_quality_gate": data_quality_gate,
            "scientific_execution_gate": scientific_execution_gate,
            "same_frozen_test_reexecutable": True,
            "events_eligible": len(eligible),
            "events_sampled": len(selected),
            "snapshots_requested": SNAPSHOTS,
            "snapshot_rounds_valid": valid_rounds,
            "valid_event_snapshots": valid_event_snapshots,
            "routes_evaluated": routes_evaluated,
            "primary_statistic_computable": primary_statistic_computable,
            "threshold_exceedances": sum(1 for r in route_rows if r["threshold_exceeded"]),
            "persistent_routes": len(persistent_routes),
            "events_with_exceedance": sorted(exceedance_events),
            "structural_violation": structural if primary_statistic_computable else None,
            "best_route": best,
            "economic_verdict": economic_verdict,
            "terminal_state": terminal_state,
            "data_contract_error": data_contract_error,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
            "finished_utc": now_utc(),
        }
        atomic_json(out_dir / "summary.json", summary)
        with (out_dir / "snapshot_audit.jsonl").open("w") as f:
            for row in audit_rows:
                f.write(json.dumps(row, sort_keys=True, default=str, separators=(",", ":")) + "\n")
        diagnostic.update({"runtime_gate": "PASS", "status": "RUN_COMPLETE", "finished_utc": now_utc()})
        atomic_json(out_dir / "diagnostic.json", diagnostic)
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return 0
    except Exception as ex:
        diagnostic.update({
            "runtime_gate": "FAIL",
            "status": "FAILED",
            "error_type": type(ex).__name__,
            "error": str(ex),
            "traceback": traceback.format_exc(),
            "finished_utc": now_utc(),
        })
        atomic_json(out_dir / "diagnostic.json", diagnostic)
        if mode == "run":
            atomic_json(out_dir / "summary.json", blocked_summary(f"{type(ex).__name__}: {ex}"))
        print(json.dumps(diagnostic, indent=2, sort_keys=True), file=sys.stderr)
        return 2


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("smoke", "run"), required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--simulate-failure", action="store_true")
    args = ap.parse_args()
    raise SystemExit(run(args.mode, Path(args.out_dir), args.simulate_failure))


if __name__ == "__main__":
    main()
