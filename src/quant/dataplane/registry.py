"""Dataset registry: provenance, fingerprints, validation and availability.

``QUANT_NORTH_STAR.md``: "No research or capital decision may silently assume
data that the system cannot trace." A dataset is therefore usable only when it
is registered, fingerprinted and ``AVAILABLE``; anything else blocks the work
that depends on it instead of degrading quietly.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ..state import read_json, utc_now, write_json


AVAILABILITY = ("AVAILABLE", "STALE", "INVALID", "MISSING")


def fingerprint_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class DatasetRecord:
    dataset_id: str
    source: str
    adapter: str
    path: str
    kind: str = "daily_bars"
    symbols: list[str] = field(default_factory=list)
    rows: int = 0
    first_date: str | None = None
    last_date: str | None = None
    fingerprint: str | None = None
    ingested_at: str = field(default_factory=utc_now)
    refreshed_at: str | None = None
    availability: str = "MISSING"
    validation: dict[str, Any] = field(default_factory=dict)
    point_in_time: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)
    license_note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def version_key(self) -> str:
        return f"{self.dataset_id}@{self.fingerprint or 'none'}"


class DatasetRegistry:
    """Persistent registry. Availability changes are what unblock dependent work."""

    def __init__(self, path: Path, root: Path):
        self.path = path
        self.root = root
        payload = read_json(path, {"version": 1, "datasets": {}}) or {"version": 1, "datasets": {}}
        self.records: dict[str, DatasetRecord] = {
            key: DatasetRecord(**value) for key, value in payload["datasets"].items()}

    def save(self) -> None:
        write_json(self.path, {"version": 1,
                               "datasets": {key: record.to_dict()
                                            for key, record in sorted(self.records.items())}})

    def register(self, record: DatasetRecord) -> DatasetRecord:
        self.records[record.dataset_id] = record
        self.save()
        return record

    def get(self, dataset_id: str) -> DatasetRecord | None:
        return self.records.get(dataset_id)

    def resolve(self, dataset_id: str) -> Path:
        record = self.records[dataset_id]
        return self.root / record.path

    def reload(self) -> list[str]:
        """Re-read records written by another ingestion process.

        Existing ids are replaced when the persisted document changed.  A
        reloaded AVAILABLE verdict is still checked against the validation
        fingerprint in ``refresh_availability`` before it can be trusted.
        """
        payload = read_json(self.path, {"version": 1, "datasets": {}}) or {}
        stored = payload.get("datasets", {})
        changed: list[str] = []
        for key, value in stored.items():
            incoming = DatasetRecord(**value)
            current = self.records.get(key)
            if current is None or current.to_dict() != incoming.to_dict():
                self.records[key] = incoming
                changed.append(key)
        return changed

    def _revalidate(self, record: DatasetRecord, path: Path) -> None:
        """Refresh structural metadata and bind validation to the actual bytes."""
        # Local imports keep the registry primitive free of an import cycle.
        from .panel import PricePanel
        from .validation import validate_panel

        before = fingerprint_file(path)
        try:
            panel = PricePanel.load(path)
            expected = list(record.symbols) or list(panel.symbols)
            validation = validate_panel(panel, expected)
            after = fingerprint_file(path)
            record.fingerprint = after
            record.rows = len(panel.bars)
            record.symbols = list(panel.symbols)
            record.first_date = panel.dates[0] if panel.dates else None
            record.last_date = panel.dates[-1] if panel.dates else None
            declared = (record.validation or {}).get("sidecar_fingerprint")
            sidecar = path.with_suffix(".meta.json")
            if declared and sidecar.exists():
                # The committed sidecar is the authority, not the copy cached in
                # var/: a legitimately re-committed snapshot must become valid.
                from ..state import read_json
                declared = (read_json(sidecar) or {}).get("fingerprint") or declared
            if declared:
                validation["sidecar_fingerprint"] = declared
                if declared != after:
                    validation["passed"] = False
                    validation.setdefault("problems", []).append(
                        f"bytes {after} do not match the committed sidecar fingerprint "
                        f"{declared}")
            if after != before:
                validation = {"passed": False,
                              "problems": ["dataset bytes changed during validation"],
                              "warnings": validation.get("warnings", []),
                              "fingerprint": after}
                record.availability = "STALE"
            else:
                validation["fingerprint"] = after
                record.availability = "AVAILABLE" if validation["passed"] else "INVALID"
            record.validation = validation
        except Exception as exc:
            current = fingerprint_file(path) if path.exists() else None
            record.fingerprint = current
            record.validation = {"passed": False,
                                 "problems": [f"validation failed: {type(exc).__name__}: {exc}"],
                                 "warnings": [], "fingerprint": current}
            record.availability = "INVALID"

    def refresh_availability(self) -> list[DatasetRecord]:
        """Re-check every registered dataset against the filesystem.

        A byte change is never promoted directly to AVAILABLE.  The validation
        verdict itself carries the exact byte fingerprint it describes, so a
        second process cannot publish new bytes/new fingerprint while leaving a
        stale AVAILABLE verdict behind.
        """
        changed: list[DatasetRecord] = []
        for record in self.records.values():
            path = self.root / record.path
            if not path.exists():
                if record.availability != "MISSING":
                    record.availability = "MISSING"
                    record.refreshed_at = utc_now()
                    changed.append(record)
                continue
            current = fingerprint_file(path)
            bytes_changed = current != record.fingerprint
            validation_fingerprint = record.validation.get("fingerprint")
            needs_recheck = (bytes_changed
                             or record.availability in {"MISSING", "STALE"}
                             or validation_fingerprint != current)
            if needs_recheck:
                record.refreshed_at = utc_now()
                self._revalidate(record, path)
                changed.append(record)
        if changed:
            self.save()
        return changed

    def available(self) -> list[DatasetRecord]:
        return [record for record in self.records.values() if record.availability == "AVAILABLE"]

    def missing_for(self, required: list[str]) -> list[str]:
        """Dataset ids a task needs that are not currently usable."""
        return [dataset_id for dataset_id in required
                if (record := self.records.get(dataset_id)) is None
                or record.availability != "AVAILABLE"]

    def health(self) -> dict[str, Any]:
        counts: dict[str, int] = {name: 0 for name in AVAILABILITY}
        for record in self.records.values():
            counts[record.availability] = counts.get(record.availability, 0) + 1
        return {"datasets": len(self.records), "by_availability": counts,
                "healthy": counts["AVAILABLE"] == len(self.records) and bool(self.records)}
