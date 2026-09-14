#!/usr/bin/env python3
"""Acquire official SEC ownership data and build the V2-A deterministic Form-4 census."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.sec_form4 import (  # noqa: E402
    PARSER_VERSION,
    SEC_USER_AGENT,
    SessionCalendar,
    SourceRecord,
    _http_get,
    _sha256_bytes,
    build_census,
    candidate_to_dict,
    build_mapping_ledger,
    census_summary,
    event_to_dict,
    jsonl_bytes,
    loss_to_dict,
    observation_to_dict,
    probe_yahoo_symbols,
    quarter_specs,
    resolve_event_times,
    source_url,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def acquire(raw_dir: Path, expected_manifest: dict[str, dict[str, object]] | None = None) -> tuple[list[tuple[str, bytes]], list[SourceRecord]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    payloads: list[tuple[str, bytes]] = []
    records: list[SourceRecord] = []
    for year, quarter in quarter_specs():
        period = f"{year}Q{quarter}"
        path = raw_dir / f"{year}q{quarter}_form345.zip"
        url = source_url(year, quarter)
        if path.exists():
            data = path.read_bytes()
        else:
            print(f"download {period}: {url}", flush=True)
            data = _http_get(url, user_agent=os.environ.get("SEC_USER_AGENT", SEC_USER_AGENT), delay=0.2)
            path.write_bytes(data)
        digest = _sha256_bytes(data)
        expected = (expected_manifest or {}).get(period)
        if expected is not None and digest != expected.get("sha256"):
            raise SystemExit(f"source drift for {period}: expected {expected.get('sha256')} got {digest}")
        records.append(SourceRecord(
            period=period,
            source_url=url,
            sha256=digest,
            bytes=len(data),
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            local_path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        ))
        payloads.append((period, data))
    return payloads, records


def generate_calendar(path: Path) -> None:
    try:
        import exchange_calendars as xcals
    except ImportError as exc:
        raise SystemExit("exchange_calendars is required to generate the pinned XNYS calendar") from exc
    cal = xcals.get_calendar("XNYS")
    sessions = cal.sessions_in_range("2019-12-01", "2026-07-31")
    version = getattr(sys.modules.get("exchange_calendars"), "__version__", "unknown")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write("session,source,version\n")
        for ts in sessions:
            handle.write(f"{ts.date().isoformat()},exchange_calendars:XNYS,{version}\n")


def run(args: argparse.Namespace) -> None:
    raw_dir = ROOT / args.raw_dir
    out_dir = ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    calendar_path = ROOT / args.calendar
    if args.generate_calendar or not calendar_path.exists():
        generate_calendar(calendar_path)
    calendar = SessionCalendar.from_csv(calendar_path)

    expected_manifest = None
    manifest_path = out_dir / "provenance_manifest.json"
    if args.verify_source_hashes and manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_manifest = {row["period"]: row for row in old["sources"]}

    payloads, sources = acquire(raw_dir, expected_manifest=expected_manifest)
    build = build_census(payloads, calendar)
    events, losses, acceptance = resolve_event_times(build, cache_dir=raw_dir / "acceptance_headers")
    build.events = events
    build.losses = losses
    build.waterfall["event_time_resolved_formations"] = sum(e.event_time_status == "RESOLVED" for e in events)
    build.waterfall["event_time_unresolved_formations"] = sum(e.event_time_status != "RESOLVED" for e in events)

    price_status = None
    price_snapshot_path = out_dir / "price_coverage_snapshot.json"
    if args.verify_source_hashes and price_snapshot_path.exists():
        price_status = json.loads(price_snapshot_path.read_text(encoding="utf-8"))["symbols"]
    elif args.probe_price_coverage:
        provisional = build_mapping_ledger(build, events, None)
        symbol_events: dict[str, list[str]] = {}
        for row in provisional:
            if row["selected_symbol"] and not row["reason_codes"]:
                symbol_events.setdefault(row["selected_symbol"], []).append(row["formation_transaction_date"])
        price_status = probe_yahoo_symbols(symbol_events)
        write_json(price_snapshot_path, {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "purpose": "mapping coverage only; price arrays are never read or persisted",
            "symbols": price_status,
        })
    mapping = build_mapping_ledger(build, events, price_status)
    build.waterfall["mappable_events"] = sum(r["mapping_status"] == "MAPPABLE" for r in mapping)
    build.waterfall["unmappable_events"] = len(mapping) - build.waterfall["mappable_events"]
    from quant.dataplane.sec_form4 import LossLedgerRecord, _stable_hash
    for row in mapping:
        codes = tuple(sorted(set(row["reason_codes"])))
        if codes:
            losses.append(LossLedgerRecord(
                record_id=_stable_hash(["mapping", row["event_id"], codes], "LOSS-"),
                event_id=row["event_id"], accession=None, issuer_cik=row["issuer_cik"], owner_cik=None,
                status="UNRESOLVED", reason_codes=codes, detail=f"security/price-path mapping unresolved for {row.get('selected_symbol') or row.get('as_filed_symbols')}",
            ))
        if row["diagnostic_codes"]:
            losses.append(LossLedgerRecord(
                record_id=_stable_hash(["mapping-diagnostic", row["event_id"], row["diagnostic_codes"]], "LOSS-"),
                event_id=row["event_id"], accession=None, issuer_cik=row["issuer_cik"], owner_cik=None,
                status="DIAGNOSTIC", reason_codes=tuple(row["diagnostic_codes"]), detail="temporal ticker history diagnostic; event remains in census",
            ))

    deterministic_files = {
        "normalized_candidates.jsonl": jsonl_bytes(candidate_to_dict(x) for x in sorted(build.normalized_candidates, key=lambda x: (x.accession, x.row_id))),
        "normalized_purchase_observations.jsonl": jsonl_bytes(observation_to_dict(o) for o in build.observations),
        "events.jsonl": jsonl_bytes(event_to_dict(e) for e in events),
        "loss_ledger.jsonl": jsonl_bytes(loss_to_dict(x) for x in sorted(losses, key=lambda x: x.record_id)),
        "mapping_ledger.jsonl": jsonl_bytes(sorted(mapping, key=lambda x: x["event_id"])),
    }
    for name, data in deterministic_files.items():
        (out_dir / name).write_bytes(data)

    summary = census_summary(build, events, mapping)
    write_json(out_dir / "census_summary.json", summary)
    write_json(out_dir / "waterfall.json", build.waterfall)
    write_json(out_dir / "acceptance_manifest.json", acceptance)
    provenance = {
        "parser_version": PARSER_VERSION,
        "period": ["2020Q1", "2026Q2"],
        "calendar": {
            "path": str(calendar_path.relative_to(ROOT)),
            "sha256": _sha256_bytes(calendar_path.read_bytes()),
            "source": calendar.source,
            "version": calendar.version,
        },
        "sources": [asdict(x) for x in sources],
        "deterministic_outputs": {name: _sha256_bytes(data) for name, data in deterministic_files.items()},
    }
    write_json(manifest_path, provenance)
    run_meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_cache": str(raw_dir),
        "price_probe_enabled": bool(args.probe_price_coverage),
    }
    write_json(out_dir / "run_metadata.json", run_meta)
    loss_counts = {}
    for item in losses:
        for code in item.reason_codes:
            loss_counts[code] = loss_counts.get(code, 0) + 1
    top = sorted(summary["issuer_event_distribution"].items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    report = [
        "# SEC Form-4 deterministic census (V2-A)", "",
        "This report is generated from the machine-readable census. It contains no return, P&L, Sharpe, alpha, hit-rate or performance analysis.", "",
        f"- period: 2020-01-01 through 2026-06-30 inclusive (2026 H1)",
        f"- official SEC quarterly sources: {len(sources)}",
        f"- economic 2-insider / 10-session formations: **{summary['formations']}**",
        f"- event-time resolved: **{summary['event_time_resolved']}**; unresolved: **{summary['event_time_unresolved']}**",
        f"- event issuers: **{summary['distinct_event_issuers']}**; event insiders: **{summary['distinct_event_insiders']}**",
        f"- top-10 issuer share: **{summary['top_10_issuer_share']:.4%}**; issuer HHI: **{summary['issuer_hhi']:.6f}**",
        f"- mappable events: **{summary['mappable_events']}**; unmappable: **{summary['unmappable_events']}**", "",
        "## Annual formations", "",
    ]
    report.extend(f"- {year}: {count}" for year, count in summary["annual_formations"].items())
    report.extend(["", "## Top issuers by formation count", ""])
    report.extend(f"- {cik}: {count}" for cik, count in top)
    report.extend(["", "## Waterfall", ""])
    report.extend(f"- {key}: {value}" for key, value in sorted(build.waterfall.items()))
    report.extend(["", "## Unresolved / diagnostic reason counts", ""])
    report.extend(f"- {key}: {value}" for key, value in sorted(loss_counts.items()))
    report.extend(["", "## Calendar", "", f"- source: {calendar.source}", f"- version: {calendar.version}", f"- semantics: {build.diagnostics['calendar_semantics']}", "", "## Design-level sample-size sensitivity", ""])
    report.extend(f"- intracluster rho {rho}: N_effective {value}" for rho, value in summary["design_n_effective_by_intracluster_rho"].items())
    (out_dir / "CENSUS_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="var/sec_form4_raw")
    parser.add_argument("--output-dir", default="artifacts/sec_form4_census")
    parser.add_argument("--calendar", default="data/calendars/xnys_sessions_2019_2026.csv")
    parser.add_argument("--generate-calendar", action="store_true")
    parser.add_argument("--probe-price-coverage", action="store_true")
    parser.add_argument("--verify-source-hashes", action="store_true")
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
