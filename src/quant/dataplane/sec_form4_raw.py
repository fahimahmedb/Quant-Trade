"""Durable raw evidence primitives for SEC/Form-4 capture.

The store is intentionally parser-independent: it preserves exact HTTP response
body bytes, local acquisition envelopes, source-version conflicts and restart
reconciliation. Scientific visibility/admissibility remain explicitly false.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from ..paths import QuantPaths
from ..state import append_jsonl, read_jsonl, utc_now

CAPTURED = "CAPTURED"
NOT_VISIBLE = "NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL"
NOT_ADMISSIBLE = "NOT_ADMISSIBLE_FOR_CONFIRMATION"


@dataclass(frozen=True)
class SecAttemptRecord:
    attempt_id: str
    attempt_kind: str
    phase: str
    source_locator: str
    request_attempted_at_utc: str
    response_received_at_utc: str | None
    result_state: str
    http_status: int | None
    raw_object_sha256: str | None
    byte_length: int | None
    collector_version: str
    git_commit: str
    endpoint_class: str
    media_type: str | None = None
    error_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SecRawObjectRecord:
    sha256: str
    byte_length: int
    first_received_at_utc: str
    media_type: str | None
    endpoint_class: str
    capture_state: str = CAPTURED
    visibility_state: str = NOT_VISIBLE
    admissibility_state: str = NOT_ADMISSIBLE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SecSourceVersionRecord:
    source_identity: str
    source_locator: str
    raw_object_sha256: str
    observed_at_utc: str
    conflict: bool
    prior_sha256: str | None
    package_state: str = "RAW_RESPONSE_COMPLETE"
    capture_state: str = CAPTURED
    visibility_state: str = NOT_VISIBLE
    admissibility_state: str = NOT_ADMISSIBLE

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SecCaptureStore:
    """Content-addressed raw bytes + append-only acquisition evidence."""

    def __init__(self, paths: QuantPaths, fault_hook: Callable[[str], None] | None = None):
        self.paths = paths
        self.raw_root = paths.sec_form4_raw
        self.pending_root = paths.sec_form4_pending
        self.attempts_path = paths.sec_form4_attempts
        self.manifest_path = paths.sec_form4_manifest
        self.source_versions_path = paths.sec_form4_source_versions
        self.reconciliation_path = paths.sec_form4_reconciliation
        self.fault_hook = fault_hook
        self.raw_root.mkdir(parents=True, exist_ok=True)
        self.pending_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _fsync_dir(path: Path) -> None:
        try:
            fd = os.open(path, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def digest(body: bytes) -> str:
        return "sha256:" + hashlib.sha256(body).hexdigest()

    def object_path(self, digest: str) -> Path:
        if not digest.startswith("sha256:") or len(digest) != 71:
            raise ValueError(f"invalid sha256 object id: {digest}")
        hexdigest = digest[7:]
        return self.raw_root / hexdigest[:2] / f"{hexdigest}.bin"

    def read_raw(self, digest: str) -> bytes:
        body = self.object_path(digest).read_bytes()
        actual = self.digest(body)
        if actual != digest:
            raise IOError(f"raw object corruption: expected {digest}, got {actual}")
        return body

    def append_attempt(self, record: SecAttemptRecord) -> None:
        append_jsonl(self.attempts_path, record.to_dict())

    def terminal_attempt_ids(self) -> set[str]:
        return {
            row["attempt_id"] for row in read_jsonl(self.attempts_path)
            if row.get("phase") == "COMPLETED"
        }

    def _record_reconciliation(self, kind: str, subject: str, **detail: Any) -> None:
        seed = json.dumps([kind, subject, detail], sort_keys=True)
        reconciliation_id = hashlib.sha256(seed.encode()).hexdigest()[:24]
        existing = {row.get("reconciliation_id") for row in read_jsonl(self.reconciliation_path)}
        if reconciliation_id in existing:
            return
        append_jsonl(self.reconciliation_path, {
            "reconciliation_id": reconciliation_id,
            "kind": kind,
            "subject": subject,
            "recorded_at_utc": utc_now(),
            "detail": detail,
        })

    def _stage_response(
        self,
        terminal: SecAttemptRecord,
        body: bytes,
        source_identity: str | None,
    ) -> Path:
        if terminal.raw_object_sha256 != self.digest(body) or terminal.byte_length != len(body):
            raise ValueError("terminal envelope does not match response bytes")
        temp = self.pending_root / f".{terminal.attempt_id}.{uuid.uuid4().hex}.tmp"
        temp.mkdir(parents=True, exist_ok=False)
        with (temp / "raw.bin").open("xb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        receipt = {"terminal": terminal.to_dict(), "source_identity": source_identity}
        with (temp / "receipt.json").open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        self._fsync_dir(temp)
        stage = self.pending_root / terminal.attempt_id
        if stage.exists():
            shutil.rmtree(temp, ignore_errors=True)
            raise FileExistsError(f"staged response already exists: {terminal.attempt_id}")
        os.rename(temp, stage)
        self._fsync_dir(self.pending_root)
        if self.fault_hook:
            self.fault_hook("after_stage_commit")
        return stage

    def _manifest_hashes(self) -> set[str]:
        return {row["sha256"] for row in read_jsonl(self.manifest_path) if row.get("sha256")}

    def _publish_raw(self, body: bytes, terminal: SecAttemptRecord) -> SecRawObjectRecord:
        digest = terminal.raw_object_sha256
        if digest is None:
            raise ValueError("raw response requires a sha256")
        destination = self.object_path(digest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            temp = destination.parent / f".{destination.name}.{uuid.uuid4().hex}.tmp"
            with temp.open("xb") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temp, destination)
                self._fsync_dir(destination.parent)
            except FileExistsError:
                pass
            finally:
                temp.unlink(missing_ok=True)
        existing = destination.read_bytes()
        if existing != body or self.digest(existing) != digest:
            raise IOError(f"immutable raw object mismatch for {digest}")
        if self.fault_hook:
            self.fault_hook("after_raw_object_commit")
        record = SecRawObjectRecord(
            sha256=digest,
            byte_length=len(body),
            first_received_at_utc=(terminal.response_received_at_utc
                                   or terminal.request_attempted_at_utc),
            media_type=terminal.media_type,
            endpoint_class=terminal.endpoint_class,
        )
        if digest not in self._manifest_hashes():
            append_jsonl(self.manifest_path, record.to_dict())
        return record

    def _record_source_version(self, source_identity: str | None,
                               terminal: SecAttemptRecord) -> bool:
        if not source_identity or terminal.raw_object_sha256 is None:
            return False
        versions = [row for row in read_jsonl(self.source_versions_path)
                    if row.get("source_identity") == source_identity]
        duplicate = [row for row in versions
                     if row.get("raw_object_sha256") == terminal.raw_object_sha256]
        if duplicate:
            return any(bool(row.get("conflict")) for row in duplicate)
        prior = versions[-1]["raw_object_sha256"] if versions else None
        conflict = prior is not None and prior != terminal.raw_object_sha256
        append_jsonl(self.source_versions_path, SecSourceVersionRecord(
            source_identity=source_identity,
            source_locator=terminal.source_locator,
            raw_object_sha256=terminal.raw_object_sha256,
            observed_at_utc=(terminal.response_received_at_utc
                             or terminal.request_attempted_at_utc),
            conflict=conflict,
            prior_sha256=prior,
        ).to_dict())
        if conflict:
            self._record_reconciliation(
                "SOURCE_IDENTITY_CONFLICT", source_identity,
                prior_sha256=prior, new_sha256=terminal.raw_object_sha256)
        return conflict

    def _commit_stage(self, stage: Path) -> tuple[SecRawObjectRecord, bool]:
        payload = json.loads((stage / "receipt.json").read_text(encoding="utf-8"))
        terminal = SecAttemptRecord(**payload["terminal"])
        body = (stage / "raw.bin").read_bytes()
        if self.digest(body) != terminal.raw_object_sha256 or len(body) != terminal.byte_length:
            raise IOError(f"staged response integrity failure: {terminal.attempt_id}")
        raw = self._publish_raw(body, terminal)
        if terminal.attempt_id not in self.terminal_attempt_ids():
            self.append_attempt(terminal)
        conflict = self._record_source_version(payload.get("source_identity"), terminal)
        shutil.rmtree(stage)
        self._fsync_dir(self.pending_root)
        return raw, conflict

    def capture_response(self, terminal: SecAttemptRecord, body: bytes,
                         source_identity: str | None = None) -> tuple[SecRawObjectRecord, bool]:
        """Commit bytes + receipt as one restart-recoverable evidence transaction."""
        return self._commit_stage(self._stage_response(terminal, body, source_identity))

    def recover_pending(self) -> list[str]:
        recovered: list[str] = []
        for stage in sorted(self.pending_root.iterdir()):
            if not stage.is_dir():
                continue
            if stage.name.startswith("."):
                shutil.rmtree(stage, ignore_errors=True)
                continue
            try:
                self._commit_stage(stage)
                recovered.append(stage.name)
                self._record_reconciliation("RECOVERED_STAGED_RESPONSE", stage.name,
                                            status="replayed")
            except Exception as exc:
                self._record_reconciliation("STAGED_RESPONSE_RECOVERY_FAILED", stage.name,
                                            error_class=type(exc).__name__)
                raise
        return recovered

    def reconcile(self) -> dict[str, Any]:
        recovered = self.recover_pending()
        terminals = self.terminal_attempt_ids()
        for row in read_jsonl(self.attempts_path):
            if row.get("phase") == "STARTED" and row.get("attempt_id") not in terminals:
                self._record_reconciliation(
                    "INCOMPLETE_ATTEMPT", row["attempt_id"],
                    attempt_kind=row.get("attempt_kind"),
                    endpoint_class=row.get("endpoint_class"),
                    request_attempted_at_utc=row.get("request_attempted_at_utc"))
        storage_health = "HEALTHY"
        for row in read_jsonl(self.manifest_path):
            digest = row.get("sha256")
            if not digest:
                continue
            try:
                body = self.read_raw(digest)
                if len(body) != row.get("byte_length"):
                    raise IOError("byte length mismatch")
            except Exception as exc:
                storage_health = "DEGRADED"
                self._record_reconciliation("RAW_OBJECT_MISSING_OR_CORRUPT", digest,
                                            error_class=type(exc).__name__)
        return {"recovered": recovered, "storage_health": storage_health}

    def rebuild_manifest(self) -> None:
        """Rebuild the manifest from immutable bytes + completed receipt envelopes."""
        completed = [row for row in read_jsonl(self.attempts_path)
                     if row.get("phase") == "COMPLETED" and row.get("raw_object_sha256")]
        first: dict[str, dict[str, Any]] = {}
        for row in completed:
            digest = row["raw_object_sha256"]
            stamp = row.get("response_received_at_utc") or row["request_attempted_at_utc"]
            if digest not in first or stamp < first[digest]["stamp"]:
                first[digest] = {"stamp": stamp, "row": row}
        records: list[dict[str, Any]] = []
        for path in sorted(self.raw_root.glob("*/*.bin")):
            body = path.read_bytes()
            digest = self.digest(body)
            if path != self.object_path(digest):
                raise IOError(f"misaddressed raw object: {path}")
            if digest not in first:
                raise IOError(f"raw object lacks receipt envelope: {digest}")
            info = first[digest]
            row = info["row"]
            records.append(SecRawObjectRecord(
                sha256=digest, byte_length=len(body),
                first_received_at_utc=info["stamp"],
                media_type=row.get("media_type"), endpoint_class=row["endpoint_class"],
            ).to_dict())
        temp = self.manifest_path.with_suffix(".jsonl.tmp")
        temp.parent.mkdir(parents=True, exist_ok=True)
        with temp.open("w", encoding="utf-8") as handle:
            for record in sorted(records, key=lambda item: item["sha256"]):
                handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, self.manifest_path)
        self._fsync_dir(self.manifest_path.parent)

    def attempt_history_digest(self) -> str:
        body = self.attempts_path.read_bytes() if self.attempts_path.exists() else b""
        return "sha256:" + hashlib.sha256(body).hexdigest()
