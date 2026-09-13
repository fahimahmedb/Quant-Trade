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
        """Re-read the registry from disk and return newly seen dataset ids.

        Ingestion runs in its own process, so a long-running Clock that only
        consults the copy it loaded at boot can never notice a dataset that
        arrived while it was idle.
        """
        payload = read_json(self.path, {"version": 1, "datasets": {}}) or {}
        stored = payload.get("datasets", {})
        added = [key for key in stored if key not in self.records]
        for key, value in stored.items():
            if key not in self.records:
                self.records[key] = DatasetRecord(**value)
        return added

    def refresh_availability(self) -> list[DatasetRecord]:
        """Re-check every registered dataset against the filesystem.

        A dataset whose bytes changed is re-fingerprinted, which is the event
        that makes previously completed work eligible to run again.
        """
        changed = []
        for record in self.records.values():
            path = self.root / record.path
            if not path.exists():
                if record.availability != "MISSING":
                    record.availability = "MISSING"
                    changed.append(record)
                continue
            current = fingerprint_file(path)
            if current != record.fingerprint:
                record.fingerprint = current
                record.refreshed_at = utc_now()
                record.availability = "AVAILABLE"
                changed.append(record)
            elif record.availability == "MISSING":
                record.availability = "AVAILABLE"
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
