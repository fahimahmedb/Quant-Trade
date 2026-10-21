"""Dataset definitions and the ingestion entry point.

Ingestion is deliberately separate from research: it writes a normalized,
fingerprinted snapshot into the repository so every later result is
reproducible without network access, and so a reviewer can re-derive any
number the system reports. New ingestion also binds the normalized dataset to
recoverable exact source bytes in the shared ``EvidenceStore``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..events import EventLog
from ..paths import QuantPaths
from ..state import read_json, utc_now, write_json
from .adapters import DataUnavailable, fetch_yahoo_daily, load_local_tsv
from .evidence import EvidenceStore
from .panel import PricePanel
from .registry import DatasetRecord, DatasetRegistry, fingerprint_file
from .validation import validate_panel


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
EVIDENCE_STORE_PATH = "var/evidence"


def metadata_path(root: Path, record: DatasetRecord) -> Path:
    return (root / record.path).with_suffix(".meta.json")


def _register(registry: DatasetRegistry, record: DatasetRecord, panel: PricePanel,
              expected: list[str], root: Path) -> DatasetRecord:
    target = root / record.path
    panel.write(target)
    validation = validate_panel(panel, expected)
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
    # re-read the prices but not what they are or where they came from. The raw
    # evidence objects themselves stay in the EvidenceStore; the sidecar carries
    # only immutable content/receipt identities plus source/product declarations.
    write_json(metadata_path(root, record),
               record.to_dict() | {"expected_symbols": expected})
    return registry.register(record)


def _record_from_provenance(
    *,
    dataset_id: str,
    adapter: str,
    path: str,
    provenance: dict[str, Any],
    point_in_time: dict[str, Any],
    license_note: str,
) -> DatasetRecord:
    """Build the common evidence-bound portion of an ingestion record."""
    return DatasetRecord(
        dataset_id=dataset_id,
        source=provenance["source"],
        adapter=adapter,
        path=path,
        point_in_time=point_in_time,
        caveats=provenance["caveats"],
        license_note=license_note,
        source_identity=provenance.get("source_identity"),
        source_product_identity=provenance.get("source_product_identity"),
        evidence_required=True,
        evidence_store_path=EVIDENCE_STORE_PATH,
        evidence=list(provenance.get("evidence", [])),
    )


def register_committed_snapshots(paths: QuantPaths, registry: DatasetRegistry,
                                 log: EventLog) -> list[str]:
    """Re-register datasets already committed to the repository, without network.

    A snapshot carrying the new evidence contract is usable only while its raw
    source objects + acquisition receipts remain recoverable. Legacy sidecars
    without ``evidence_required`` retain their historical semantics; they are a
    compatibility surface, not proof that raw-source qualification existed.
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
        panel = PricePanel.load(target)
        record.fingerprint = fingerprint_file(target)
        record.validation = validate_panel(panel, expected or record.symbols)
        record.availability = "AVAILABLE" if record.validation["passed"] else "INVALID"
        record.refreshed_at = utc_now()
        registered_record = registry.register(record)
        registered.append(record.dataset_id)
        log.emit("DATA", "DATA", "snapshot_registered", record.dataset_id,
                 rows=record.rows, fingerprint=record.fingerprint,
                 availability=registered_record.availability,
                 evidence_required=record.evidence_required)
    return registered


def ingest_sector_panel(paths: QuantPaths, registry: DatasetRegistry, log: EventLog,
                        range_: str = "10y") -> DatasetRecord:
    """Ingest the multi-asset panel the blocked research lanes were waiting on."""
    symbols = SECTOR_UNIVERSE + [BENCHMARK] + CONTEXT
    evidence_store = EvidenceStore(paths.root / EVIDENCE_STORE_PATH)
    panel, provenance = fetch_yahoo_daily(
        symbols, range_=range_, evidence_store=evidence_store)
    record = _record_from_provenance(
        dataset_id=SECTOR_DATASET,
        adapter="yahoo_daily",
        path=f"data/datasets/{SECTOR_DATASET}.csv",
        provenance=provenance,
        point_in_time={
            "timestamp_semantics": provenance["timestamp_semantics"],
            "information_available_at": "the close of the dated session",
            "minimum_decision_lag_days": 1,
            "retrieved_at": provenance["retrieved_at"],
            "requested_range": range_},
        license_note="public endpoint, personal research use; not redistributed as a data product",
    )
    registered = _register(registry, record, panel, symbols, paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", SECTOR_DATASET,
             severity="INFO" if registered.availability == "AVAILABLE" else "WARN",
             rows=registered.rows, symbols=len(registered.symbols),
             first_date=registered.first_date, last_date=registered.last_date,
             fingerprint=registered.fingerprint, availability=registered.availability,
             evidence_objects=len(registered.evidence),
             problems=registered.validation.get("problems", []))
    return registered


def ingest_index(paths: QuantPaths, registry: DatasetRegistry, log: EventLog) -> DatasetRecord:
    """Register the historical index export already committed to the repository."""
    evidence_store = EvidenceStore(paths.root / EVIDENCE_STORE_PATH)
    panel, provenance = load_local_tsv(
        paths.data / "nasdaq_composite_daily.txt", "NDXCOMP", evidence_store=evidence_store)
    record = _record_from_provenance(
        dataset_id=INDEX_DATASET,
        adapter="local_tsv",
        path=f"data/datasets/{INDEX_DATASET}.csv",
        provenance=provenance,
        point_in_time={"timestamp_semantics": provenance["timestamp_semantics"],
                       "information_available_at": "the close of the dated session",
                       "minimum_decision_lag_days": 1,
                       "retrieved_at": provenance["retrieved_at"]},
        license_note="operator-supplied export already committed to this repository",
    )
    registered = _register(registry, record, panel, ["NDXCOMP"], paths.root)
    log.emit("DATA", "DATA", "dataset_ingested", INDEX_DATASET, rows=registered.rows,
             first_date=registered.first_date, last_date=registered.last_date,
             fingerprint=registered.fingerprint, availability=registered.availability,
             evidence_objects=len(registered.evidence))
    return registered


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
    # Evidence-bound sidecars still pass through the registry evidence gate.
    missing = registry.missing_for([SECTOR_DATASET, INDEX_DATASET])
    if missing:
        outcome["from_snapshot"] = register_committed_snapshots(paths, registry, log)
        outcome["blocked"] = [item for item in outcome["blocked"]
                              if item["dataset_id"] not in outcome["from_snapshot"]]
    return outcome