"""Atomic, restart-safe persistence for raw forward captures and ledgers."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .models import CaptureRecord, GapRecord, RecorderState


class AtomicCaptureStore:
    """Content-address raw bytes; persist metadata/state through atomic rename.

    Raw responses are never overwritten. Rotation is by UTC date/source directory.
    No automatic deletion is implemented: retention remains indefinite until Blue Team
    explicitly validates cost, retention, and applicable terms.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.raw_root = self.root / "raw"
        self.capture_root = self.root / "captures"
        self.gap_root = self.root / "gaps"
        self.state_path = self.root / "state" / "recorder_state.json"
        for directory in (self.raw_root, self.capture_root, self.gap_root, self.state_path.parent):
            directory.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> RecorderState:
        if not self.state_path.exists():
            return RecorderState()
        value = json.loads(self.state_path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("recorder state must be a JSON object")
        return RecorderState.from_dict(value)

    def save_state(self, state: RecorderState) -> None:
        self._atomic_json(self.state_path, state.to_dict())

    def persist_raw(self, *, utc_date: str, source_id: str, raw: bytes) -> tuple[str, str, bool]:
        digest = hashlib.sha256(raw).hexdigest()
        destination = self.raw_root / source_id / f"{digest}.bin"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            existing = destination.read_bytes()
            if hashlib.sha256(existing).hexdigest() != digest:
                raise IOError("content-addressed raw collision")
            return digest, str(destination.relative_to(self.root)), True
        self._atomic_bytes(destination, raw)
        return digest, str(destination.relative_to(self.root)), False

    def persist_capture(self, record: CaptureRecord) -> Path:
        utc_date = record.retrieval_completed_utc[:10]
        destination = self.capture_root / utc_date / record.source_id / f"{record.capture_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            existing = json.loads(destination.read_text(encoding="utf-8"))
            if existing != record.to_dict():
                raise IOError(f"capture replay conflict: {record.capture_id}")
            return destination
        self._atomic_json(destination, record.to_dict())
        return destination

    def persist_gap(self, record: GapRecord) -> Path:
        utc_date = record.detected_utc[:10]
        destination = self.gap_root / utc_date / record.source_id / f"{record.gap_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            existing = json.loads(destination.read_text(encoding="utf-8"))
            if existing != record.to_dict():
                raise IOError(f"gap replay conflict: {record.gap_id}")
            return destination
        self._atomic_json(destination, record.to_dict())
        return destination

    @staticmethod
    def _atomic_json(destination: Path, value: dict[str, Any]) -> None:
        payload = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
        AtomicCaptureStore._atomic_bytes(destination, payload)

    @staticmethod
    def _atomic_bytes(destination: Path, payload: bytes) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, destination)
            dir_fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            if temp.exists():
                temp.unlink()
