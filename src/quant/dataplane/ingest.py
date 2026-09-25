"""Dataset definitions and the ingestion entry point.

Ingestion is deliberately separate from research: it writes a normalized,
fingerprinted snapshot into the repository so every later result is
reproducible without network access, and so a reviewer can re-derive any
number the system reports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..events import EventLog
from ..paths import QuantPaths
from ..state import read_json, utc_now, write_json
from .adapters import DataUnavailable, fetch_yahoo_daily, load_local_tsv
from .futures import (BROAD_START, FUTURES_BENCHMARK, FUTURES_BROAD_DATASET,
                      FUTURES_DATASET, FUTURES_UNIVERSE, build_futures_panel, fetch_source,
                      select_broad_universe)
from .panel import PricePanel
from .registry import DatasetRecord, DatasetRegistry, fingerprint_file
from .validation import validate_panel, validation_policy


#: Cross-sectional relative-value universe. Nine SPDR sector funds share one
#: broad equity beta, which is what lets a dollar-neutral spread isolate a
#: residual rather than re-express market direction.
SECTOR_UNIVERSE = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY"]
#: Benchmark used only for beta attribution, never traded by research strategies.
BENCHMARK = "SPY"
#: Other liquid assets carried for market-state context and future lanes.
CONTEXT = ["TLT", "GLD"]

SECTOR_DATASET = "us_sector_etf_daily"
INDEX_DATASET = "nasdaq_composite_daily"


def metadata_path(root: Path, record: DatasetRecord) -> Path:
    return (root / record.path).with_suffix(".meta.json")


def _register(registry: DatasetRegistry, record: DatasetRecord, panel: PricePanel,
              expected: list[str], root: Path) -> DatasetRecord:
    target = root / record.path
    panel.write(target)
    policy = validation_policy(record)
    validation = validate_panel(panel, policy["required"] or expected, policy["min_rows"])
    record.rows = len(panel.bars)
    record.symbols = panel.symbols
    record.first_date = panel.dates[0] if panel.dates else None
    record.last_date = panel.dates[-1] if panel.dates else None
    record.fingerprint = fingerprint_file(target)
    record.validation = validation
    record.availability = "AVAILABLE" if validation["passed"] else "INVALID"
    record.refreshed_at = utc_now()
    # Provenance is committed next to the data. The live registry lives in var/,
    # which is not in the repository, so without this sidecar a reviewer could
    # re-read the prices but not what they are or where they came from.
    write_json(metadata_path(root, record),
               record.to_dict() | {"expected_symbols": expected})
    return registry.register(record)


def register_committed_snapshots(paths: QuantPaths, registry: DatasetRegistry,
                                 log: EventLog) -> list[str]:
    """Re-register datasets already committed to the repository, without network.

    This is what makes every published result reproducible offline: the bytes,
    the fingerprint and the provenance are all in the repository.
    """
    registered = []
    for sidecar in sorted(paths.datasets.glob("*.meta.json")):
        payload = read_json(sidecar) or {}
        expected = payload.pop("expected_symbols", [])
        payload.pop("availability", None)
        record = DatasetRecord(**payload)
        target = paths.root / record.path
        if not target.exists():
            continue
        declared = payload.get("fingerprint")
        panel = PricePanel.load(target)
        record.fingerprint = fingerprint_file(target)
        policy = validation_policy(record)
        record.validation = validate_panel(panel, policy["required"] or expected or record.symbols,
                                           policy["min_rows"])
        if declared:
            record.validation["sidecar_fingerprint"] = declared
        if declared and declared != record.fingerprint:
            # The sidecar is the committed provenance of these bytes. Bytes that
            # no longer match it are unprovenanced and must not become research.
            record.validation["passed"] = False
            record.validation.setdefault("problems", []).append(
                f"bytes {record.fingerprint} do not match the committed sidecar "
                f"fingerprint {declared}")
            log.emit("DATA", "DATA", "snapshot_fingerprint_mismatch", record.dataset_id,
                     severity="FAULT", declared=declared, actual=record.fingerprint)
        record.availability = "AVAILABLE" if record.validation["passed"] else "INVALID"
        record.refreshed_at = utc_now()
        registry.register(record)
        registered.append(record.dataset_id)
        log.emit("DATA", "DATA", "snapshot_registered", record.dataset_id,
                 rows=record.rows, fingerprint=record.fingerprint,
                 availability=record.availability)
    return registered


def ingest_sector_panel(paths: QuantPaths, registry: DatasetRegistry, log: EventLog,
                        range_: str = "10y") -> DatasetRecord:
    """Ingest the multi-asset panel the blocked research lanes were waiting on."""
    symbols = SECTOR_UNIVERSE + [BENCHMARK] + CONTEXT
    panel, provenance = fetch_yahoo_daily(symbols, range_=range_)
    record = DatasetRecord(
        dataset_id=SECTOR_DATASET, source=provenance["source"], adapter="yahoo_daily",
        path=f"data/datasets/{SECTOR_DATASET}.csv",
        point_in_time={
            "timestamp_semantics": provenance["timestamp_semantics"],
            "information_available_at": "the close of the dated session",
            "minimum_decision_lag_days": 1,
            "retrieved_at": provenance["retrieved_at"],
            "requested_range": range_},
        caveats=provenance["caveats"],
        license_note="public endpoint, personal research use; not redistributed as a data product")
    registered = _register(registry, record, panel, symbols, paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", SECTOR_DATASET,
             severity="INFO" if registered.availability == "AVAILABLE" else "WARN",
             rows=registered.rows, symbols=len(registered.symbols),
             first_date=registered.first_date, last_date=registered.last_date,
             fingerprint=registered.fingerprint, availability=registered.availability,
             problems=registered.validation.get("problems", []))
    return registered


def ingest_index(paths: QuantPaths, registry: DatasetRegistry, log: EventLog) -> DatasetRecord:
    """Register the historical index export already committed to the repository."""
    panel, provenance = load_local_tsv(paths.data / "nasdaq_composite_daily.txt", "NDXCOMP")
    record = DatasetRecord(
        dataset_id=INDEX_DATASET, source=provenance["source"], adapter="local_tsv",
        path=f"data/datasets/{INDEX_DATASET}.csv",
        point_in_time={"timestamp_semantics": provenance["timestamp_semantics"],
                       "information_available_at": "the close of the dated session",
                       "minimum_decision_lag_days": 1},
        caveats=provenance["caveats"],
        license_note="operator-supplied export already committed to this repository")
    registered = _register(registry, record, panel, ["NDXCOMP"], paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", INDEX_DATASET, rows=registered.rows,
             first_date=registered.first_date, last_date=registered.last_date,
             fingerprint=registered.fingerprint, availability=registered.availability)
    return registered


def ingest_futures_panel(paths: QuantPaths, registry: DatasetRegistry, log: EventLog,
                         checkout: Path | None = None, broad: bool = False) -> DatasetRecord:
    """Derive and register a futures excess-return panel.

    ``checkout`` is a local pysystemtrade clone; without one the pinned commit
    is fetched through git into ``var/sources``. ``broad`` selects the
    staggered-entry panel (``select_broad_universe``) instead of the 31
    aligned contracts.
    """
    if checkout is None:
        try:
            checkout = fetch_source(paths.var / "sources" / "pysystemtrade")
        except Exception as exc:  # network or git unavailable
            raise DataUnavailable(f"pysystemtrade source unavailable: {exc}") from exc
    if broad:
        dataset_id, universe = FUTURES_BROAD_DATASET, select_broad_universe(checkout)
        panel, provenance = build_futures_panel(checkout, universe, start=BROAD_START,
                                                calendar_symbol=FUTURES_BENCHMARK,
                                                cost_feature=True)
    else:
        dataset_id, universe = FUTURES_DATASET, FUTURES_UNIVERSE
        panel, provenance = build_futures_panel(checkout, cost_feature=True)
    record = DatasetRecord(
        dataset_id=dataset_id, source=provenance["source"],
        adapter="pysystemtrade_futures_excess_return",
        path=f"data/datasets/{dataset_id}.csv.gz",
        point_in_time={
            "timestamp_semantics": provenance["timestamp_semantics"],
            "information_available_at": "the close of the dated session",
            "minimum_decision_lag_days": 1,
            "derivation": provenance["derivation"],
            "source_commit": provenance["source_commit"],
            "source_input_digest": provenance["source_input_digest"],
            "stale_bars_carried_forward": provenance["stale_bars_carried_forward"],
            **({"excluded_for_data_quality": provenance["excluded_for_data_quality"]}
               if provenance.get("excluded_for_data_quality") else {})},
        caveats=provenance["caveats"],
        license_note="derived from data files in a GPL-3.0 open-source repository whose "
                     "prices originate from commercial vendors; private research use only, "
                     "not redistributed as a data product")
    universe = provenance["universe"]
    registered = _register(registry, record, panel, universe, paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", dataset_id,
             severity="INFO" if registered.availability == "AVAILABLE" else "WARN",
             rows=registered.rows, symbols=len(registered.symbols),
             first_date=registered.first_date, last_date=registered.last_date,
             fingerprint=registered.fingerprint, availability=registered.availability,
             problems=registered.validation.get("problems", []))
    return registered


def ingest_calendar_panel(paths: QuantPaths, registry: DatasetRegistry,
                          log: EventLog) -> DatasetRecord:
    """Derive the calendar-legs panel from the committed ETF snapshot."""
    from .calendar_legs import (CALENDAR_BASE, CALENDAR_DATASET, OVERNIGHT_SUFFIX,
                                build_calendar_panel, load_fomc_days)
    source_path = paths.datasets / f"{SECTOR_DATASET}.csv"
    if not source_path.exists():
        raise DataUnavailable(f"{SECTOR_DATASET} snapshot missing")
    fomc = load_fomc_days(paths.root)
    panel, provenance = build_calendar_panel(PricePanel.load(source_path), CALENDAR_BASE, fomc)
    symbols = CALENDAR_BASE + [symbol + OVERNIGHT_SUFFIX for symbol in CALENDAR_BASE]
    record = DatasetRecord(
        dataset_id=CALENDAR_DATASET,
        source=f"derived from {SECTOR_DATASET} ({fingerprint_file(source_path)}) and the "
               f"scheduled FOMC calendar ({len(fomc)} decision days)",
        adapter="calendar_legs_derivation", path=f"data/datasets/{CALENDAR_DATASET}.csv.gz",
        point_in_time={"information_available_at": "the close of the dated session",
                       "minimum_decision_lag_days": 1, "derivation": provenance["derivation"],
                       "calendar_features": "sessions_left_in_month and fomc_in_sessions are "
                                            "computed from the NYSE holiday rules and the "
                                            "published FOMC schedule, both known in advance"},
        caveats=provenance["caveats"] + ["inherits every caveat of the source ETF snapshot"],
        license_note="derived research dataset")
    registered = _register(registry, record, panel, symbols, paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", CALENDAR_DATASET, rows=registered.rows,
             fingerprint=registered.fingerprint, availability=registered.availability)
    return registered


def _committed_record(paths: QuantPaths, dataset_id: str,
                      suffix: str) -> tuple[DatasetRecord, list[str]]:
    data_path = paths.datasets / f"{dataset_id}{suffix}"
    payload = dict(read_json(data_path.with_suffix(".meta.json")) or {})
    expected = payload.pop("expected_symbols", [])
    payload.pop("availability", None)
    return DatasetRecord(**payload), expected


def _append_if_valid(registry: DatasetRegistry, record: DatasetRecord, panel: PricePanel,
                     rows: list[dict[str, Any]], expected: list[str], root: Path,
                     next_expected: str) -> dict[str, Any]:
    """Append forward rows only if they start at the next session and the
    extended panel validates; otherwise write nothing and report why."""
    from .feeds import extend_panel
    first = min(row["date"] for row in rows)
    if first != next_expected:
        return {"blocked": f"gap: first new session {first} but the next expected is "
                           f"{next_expected}; nothing appended"}
    candidate = extend_panel(panel, rows)
    policy = validation_policy(record)
    verdict = validate_panel(candidate, policy["required"] or expected, policy["min_rows"])
    if not verdict["passed"]:
        return {"blocked": "extended panel fails validation; nothing appended",
                "problems": verdict["problems"]}
    registered = _register(registry, record, candidate, expected, root)
    return {"appended_bars": len(rows), "last_date": registered.last_date,
            "availability": registered.availability}


def sync_feeds(paths: QuantPaths, registry: DatasetRegistry, log: EventLog,
               feeds: Path) -> dict[str, Any]:
    """Append forward sessions from collected feeds; never rewrite history."""
    from datetime import date, timedelta
    from .calendar_legs import FOMC_FILE, load_fomc_days, next_sessions
    from .feeds import (daily_funding, daily_marks, etf_forward_rows, merged_fomc_days,
                        perp_forward_rows, read_latest, write_fomc_days)
    report: dict[str, Any] = {}
    etf_path = paths.datasets / f"{SECTOR_DATASET}.csv"
    changed_calendar = False
    if etf_path.exists():
        record, expected = _committed_record(paths, SECTOR_DATASET, ".csv")
        panel = PricePanel.load(etf_path)
        symbols = expected or panel.symbols
        rows, info = etf_forward_rows(panel, read_latest(feeds / "yahoo" / "daily_bars.jsonl"),
                                      symbols)
        outcome: dict[str, Any] = dict(info)
        if rows:
            record.caveats = list(dict.fromkeys(list(record.caveats) + [
                "sessions after the original snapshot were appended from data/feeds (Yahoo "
                "chart API via the data-feeds workflow), adj_close rebased at the seam"]))
            outcome.update(_append_if_valid(registry, record, panel, rows, symbols, paths.root,
                                            next_sessions(panel.dates[-1], 1)[0]))
            changed_calendar = "appended_bars" in outcome
        report[SECTOR_DATASET] = outcome or {"appended_bars": 0}
    fomc_feed = read_latest(feeds / "fomc" / "scheduled.jsonl")
    if fomc_feed:
        committed = load_fomc_days(paths.root)
        merged = merged_fomc_days(committed, fomc_feed)
        if merged != committed:
            write_fomc_days(paths.root / FOMC_FILE, merged)
            changed_calendar = True
            report["fomc_schedule"] = {"added": sorted(set(merged) - set(committed)),
                                       "removed": sorted(set(committed) - set(merged))}
    if changed_calendar and (paths.datasets / "us_calendar_legs_daily.csv.meta.json").exists():
        registered = ingest_calendar_panel(paths, registry, log)
        report["us_calendar_legs_daily"] = {"rebuilt": True, "last_date": registered.last_date}
    perp_path = paths.datasets / "perp_funding_pairs_daily.csv.gz"
    if perp_path.exists():
        record, expected = _committed_record(paths, "perp_funding_pairs_daily", ".csv.gz")
        panel = PricePanel.load(perp_path)
        rows = perp_forward_rows(
            panel, daily_funding(read_latest(feeds / "funding" / "rates.jsonl").values()),
            daily_marks(read_latest(feeds / "hyperliquid" / "universe.jsonl").items()))
        if rows:
            following = (date.fromisoformat(panel.dates[-1]) + timedelta(days=1)).isoformat()
            report["perp_funding_pairs_daily"] = _append_if_valid(
                registry, record, panel, rows, expected, paths.root, following)
        else:
            report["perp_funding_pairs_daily"] = {"appended_bars": 0}
    log.emit("DATA", "DATA", "feeds_synced", "data/feeds",
             severity="WARN" if any("blocked" in str(value) for value in report.values())
             else "INFO", report=report)
    return report


def ingest_all(paths: QuantPaths, registry: DatasetRegistry, log: EventLog,
               range_: str = "10y", network: bool = True) -> dict[str, Any]:
    """Ingest everything available. A blocked source never stops the others."""
    outcome: dict[str, Any] = {"ingested": [], "blocked": [], "from_snapshot": []}
    try:
        record = ingest_index(paths, registry, log)
        outcome["ingested"].append(record.dataset_id)
    except DataUnavailable as exc:
        outcome["blocked"].append({"dataset_id": INDEX_DATASET, "reason": str(exc)})
        log.emit("DATA", "DATA", "dataset_blocked", INDEX_DATASET, severity="WARN", reason=str(exc))
    if network:
        try:
            record = ingest_sector_panel(paths, registry, log, range_=range_)
            outcome["ingested"].append(record.dataset_id)
        except DataUnavailable as exc:
            outcome["blocked"].append({"dataset_id": SECTOR_DATASET, "reason": str(exc)})
            log.emit("DATA", "DATA", "dataset_blocked", SECTOR_DATASET, severity="WARN",
                     reason=str(exc))
    # A source being unreachable must not make a dataset already committed to the
    # repository unusable, so the snapshot is always registered as a fallback.
    missing = registry.missing_for([SECTOR_DATASET, INDEX_DATASET])
    if missing:
        outcome["from_snapshot"] = register_committed_snapshots(paths, registry, log)
        outcome["blocked"] = [item for item in outcome["blocked"]
                              if item["dataset_id"] not in outcome["from_snapshot"]]
    return outcome
