"""Immutable raw evidence store and append-only acquisition journals.

This is the Day-1 irreversible layer. Everything above it - discovery, coverage,
parsing, science - can be rebuilt later from the bytes preserved here. The bytes
themselves cannot be rebuilt, so this module is deliberately boring and strict.

Rules it enforces, each of them tested:

* the stored object is the exact bytes received, hashed with SHA-256 over those
  bytes, addressed by that hash;
* an existing object is never overwritten; an identical re-capture is a
  deduplication, and differing bytes under the same source identity are an
  explicit conflict version rather than a replacement;
* a truncated transfer is preserved as *incomplete* evidence in a separate
  namespace and can never be promoted to a valid raw capture;
* an acquisition is acknowledged only after the raw object and then its
  envelope are durably on disk, so every crash boundary is replayable;
* identifying source strings live only in the restricted journals, so the
  firewall-safe journals a status surface may read cannot leak content.
"""

from __future__ import annotations

import errno
import hashlib
import os
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

from ...paths import QuantPaths
from ...state import append_jsonl, read_jsonl, write_json, read_json
from .version import COLLECTOR_VERSION, git_commit


#: The three independent states of section 7 of the reclassification.
CAPTURED = "CAPTURED"
NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL = "NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL"
NOT_ADMISSIBLE_FOR_CONFIRMATION = "NOT_ADMISSIBLE_FOR_CONFIRMATION"

#: Attempt result states. ``NO_NEW_DATA`` is reserved for a proven discovery.
NO_NEW_DATA = "NO_NEW_DATA"
NEW_ITEMS = "NEW_ITEMS"
CAPTURED_OK = "CAPTURED"
DEDUPLICATED = "DEDUPLICATED"
REQUEST_FAILED = "REQUEST_FAILED"
DISCOVERY_INVALID = "DISCOVERY_INVALID"
RATE_LIMITED = "RATE_LIMITED"
ACCESS_FORBIDDEN = "ACCESS_FORBIDDEN"
PERMANENT_CLIENT_ERROR = "PERMANENT_CLIENT_ERROR"
SERVER_ERROR = "SERVER_ERROR"
INCOMPLETE_TRANSFER = "INCOMPLETE_TRANSFER"
STORAGE_FAILED = "STORAGE_FAILED"
COOLDOWN_SUPPRESSED = "COOLDOWN_SUPPRESSED"
HUNG_REQUEST = "HUNG_REQUEST"

#: Result states that mean the collector asked and the source answered usefully.
SUCCESSFUL_RESULTS = frozenset({NO_NEW_DATA, NEW_ITEMS, CAPTURED_OK, DEDUPLICATED})


class SecStorageFailure(RuntimeError):
    """Durable evidence could not be written. Nothing may be acknowledged."""


class RawObjectConflict(RuntimeError):
    """Content addressing was violated: stored bytes do not match their hash."""


def digest_bytes(body: bytes) -> str:
    return "sha256:" + hashlib.sha256(body).hexdigest()


def digest_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _is_disk_full(exc: OSError) -> bool:
    return exc.errno in (errno.ENOSPC, errno.EDQUOT, errno.EFBIG)


@dataclass
class SecAttemptRecord:
    """Firewall-safe liveness record. One per request attempt, always written.

    Carries no locator, no accession and no title: the locator appears only as
    an opaque digest, resolvable through the restricted journal.
    """

    attempt_id: str
    attempt_kind: str
    endpoint_class: str
    source_locator_digest: str
    request_attempted_at_utc: str
    result_state: str
    collector_version: str
    git_commit: str
    response_received_at_utc: str | None = None
    http_status: int | None = None
    raw_object_sha256: str | None = None
    byte_length: int | None = None
    incomplete_object_sha256: str | None = None
    content_encoding: str | None = None
    declared_content_length: int | None = None
    transfer_outcome: str | None = None
    media_type: str | None = None
    error_class: str | None = None
    retry_after_seconds: float | None = None
    limiter_waited_seconds: float | None = None
    poll_id: str | None = None
    #: Discovery page offset. An offset is not a filing count.
    page_start: int | None = None
    duration_seconds: float | None = None
    #: Exact scheduler obligation this network attempt was emitted to satisfy.
    obligation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecRawObjectRecord:
    """Firewall-safe manifest entry: identity, size, timing, states."""

    raw_object_sha256: str
    byte_length: int
    first_received_at_utc: str
    endpoint_class: str
    media_type: str | None = None
    content_encoding: str | None = None
    declared_content_length: int | None = None
    transfer_outcome: str = "COMPLETE"
    capture_state: str = CAPTURED
    visibility_state: str = NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL
    admissibility_state: str = NOT_ADMISSIBLE_FOR_CONFIRMATION
    collector_version: str = COLLECTOR_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecAcquisitionEnvelope:
    """Restricted tier: binds one source identity to one immutable object.

    This is the commit record. A discovered task is acknowledged only once its
    envelope is durable, which is what makes every crash boundary replayable.
    """

    envelope_id: str
    attempt_id: str
    source_identity: str
    source_locator: str
    endpoint_class: str
    request_attempted_at_utc: str
    response_received_at_utc: str
    http_status: int
    raw_object_sha256: str
    byte_length: int
    collector_version: str
    git_commit: str
    content_encoding: str | None = None
    declared_content_length: int | None = None
    transfer_outcome: str = "COMPLETE"
    media_type: str | None = None
    #: Source-published/acceptance time, when the source supplied one. A
    #: distinct field: it is never substituted for the local receipt time above.
    source_published_at_utc: str | None = None
    #: The discovery object/page this task came from, per the coverage rule.
    discovery_object_sha256: str | None = None
    poll_id: str | None = None
    deduplicated: bool = False
    capture_state: str = CAPTURED
    visibility_state: str = NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL
    admissibility_state: str = NOT_ADMISSIBLE_FOR_CONFIRMATION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SecSourceVersionRecord:
    """Restricted tier: every observation of a source identity's bytes."""

    source_identity: str
    raw_object_sha256: str
    observed_at_utc: str
    version: int
    conflict: bool = False
    prior_sha256: str | None = None
    attempt_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RawWriteResult:
    raw_object_sha256: str
    byte_length: int
    deduplicated: bool
    path: Path = field(repr=False, default_factory=Path)


class SecCaptureStore:
    """Content-addressed raw bytes plus the append-only journals around them."""

    def __init__(self, paths: QuantPaths, root: Path | None = None):
        self.paths = paths.ensure_sec()
        self.git_commit = git_commit(root or paths.root)
        self.collector_version = COLLECTOR_VERSION

    # --- raw objects -------------------------------------------------------
    def object_path(self, object_id: str) -> Path:
        if not object_id.startswith("sha256:") or len(object_id) != 71:
            raise ValueError("raw object id must be a sha256: digest")
        hexdigest = object_id[7:]
        if any(character not in "0123456789abcdef" for character in hexdigest):
            raise ValueError("raw object id contains non-hex characters")
        return self.paths.sec_raw_objects / hexdigest[:2] / f"{hexdigest}.bin"

    def incomplete_path(self, object_id: str) -> Path:
        if not object_id.startswith("sha256:") or len(object_id) != 71:
            raise ValueError("incomplete object id must be a sha256: digest")
        hexdigest = object_id[7:]
        if any(character not in "0123456789abcdef" for character in hexdigest):
            raise ValueError("incomplete object id contains non-hex characters")
        return self.paths.sec_incomplete_objects / hexdigest[:2] / f"{hexdigest}.partial"

    def has_object(self, object_id: str) -> bool:
        return self.object_path(object_id).exists()

    def read_object(self, object_id: str) -> bytes:
        body = self.object_path(object_id).read_bytes()
        actual = digest_bytes(body)
        if actual != object_id:
            raise RawObjectConflict(
                f"stored object does not match its address: {object_id} holds {actual}")
        return body

    def put_object(self, body: bytes, *, incomplete: bool = False) -> RawWriteResult:
        """Write bytes immutably. An existing object is verified, never replaced."""
        object_id = digest_bytes(body)
        target = self.incomplete_path(object_id) if incomplete else self.object_path(object_id)
        if target.exists():
            existing = target.read_bytes()
            if existing != body:
                raise RawObjectConflict(
                    f"content address collision at {object_id}: stored bytes differ")
            return RawWriteResult(object_id, len(body), True, target)
        self._link_into_place(body, target)
        return RawWriteResult(object_id, len(body), False, target)

    def _link_into_place(self, body: bytes, target: Path) -> None:
        staging = self.paths.sec_staging / f"{uuid.uuid4().hex}.part"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            handle = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                written = 0
                while written < len(body):
                    written += os.write(handle, body[written:])
                os.fsync(handle)
            finally:
                os.close(handle)
            os.chmod(staging, 0o444)
            try:
                # link, not rename: it cannot clobber an existing object even
                # under a race, so immutability does not rely on a prior check.
                os.link(staging, target)
            except FileExistsError:
                existing = target.read_bytes()
                if existing != body:
                    raise RawObjectConflict(
                        "content address collision detected while linking") from None
            self._fsync_dir(target.parent)
        except OSError as exc:
            if _is_disk_full(exc):
                raise SecStorageFailure(f"raw object write failed: {errno.errorcode.get(exc.errno, exc.errno)}") from exc
            raise SecStorageFailure(f"raw object write failed: {type(exc).__name__}") from exc
        finally:
            try:
                staging.unlink()
            except OSError:
                pass

    @staticmethod
    def _fsync_dir(path: Path) -> None:
        """Evidence publication is not durable if directory fsync fails."""
        try:
            handle = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(handle)
            finally:
                os.close(handle)
        except OSError as exc:
            raise SecStorageFailure(
                f"directory fsync failed: {type(exc).__name__}") from exc

    # --- journals ----------------------------------------------------------
    def _append(self, path: Path, record: dict[str, Any]) -> None:
        try:
            append_jsonl(path, record)
        except OSError as exc:
            raise SecStorageFailure(
                f"journal append failed for {path.name}: {type(exc).__name__}") from exc

    def record_attempt(self, record: SecAttemptRecord) -> SecAttemptRecord:
        self._append(self.paths.sec_attempts, record.to_dict())
        return record

    def record_raw_object(self, record: SecRawObjectRecord) -> SecRawObjectRecord:
        self._append(self.paths.sec_raw_manifest, record.to_dict())
        return record

    def record_locator(self, *, locator: str, source_identity: str | None,
                       endpoint_class: str, observed_at_utc: str,
                       poll_id: str | None = None,
                       source_published_at_utc: str | None = None) -> str:
        """Restricted: the only place a plaintext locator is written."""
        locator_digest = digest_text(locator)
        self._append(self.paths.sec_locators, {
            "source_locator_digest": locator_digest, "source_locator": locator,
            "source_identity": source_identity,
            "source_identity_digest": digest_text(source_identity) if source_identity else None,
            "endpoint_class": endpoint_class, "observed_at_utc": observed_at_utc,
            "poll_id": poll_id, "source_published_at_utc": source_published_at_utc})
        return locator_digest

    def record_envelope(self, envelope: SecAcquisitionEnvelope) -> SecAcquisitionEnvelope:
        """ACK only bytes that are still present, address-correct and complete."""
        try:
            body = self.read_object(envelope.raw_object_sha256)
        except (OSError, RawObjectConflict, ValueError) as exc:
            raise SecStorageFailure("envelope raw object is not reconstructible") from exc
        if len(body) != envelope.byte_length:
            raise SecStorageFailure("envelope byte length does not match raw object")
        self._append(self.paths.sec_envelopes, envelope.to_dict())
        return envelope

    def record_source_version(self, *, source_identity: str, raw_object_sha256: str,
                              observed_at_utc: str,
                              attempt_id: str | None = None) -> SecSourceVersionRecord:
        """Append an observation, flagging a conflict rather than replacing."""
        history = self.source_versions(source_identity)
        prior = history[-1]["raw_object_sha256"] if history else None
        conflict = prior is not None and prior != raw_object_sha256
        record = SecSourceVersionRecord(
            source_identity=source_identity, raw_object_sha256=raw_object_sha256,
            observed_at_utc=observed_at_utc, version=len(history) + 1, conflict=conflict,
            prior_sha256=prior, attempt_id=attempt_id)
        self._append(self.paths.sec_source_versions, record.to_dict())
        return record

    # --- reads -------------------------------------------------------------
    def attempts(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.paths.sec_attempts))

    def raw_manifest(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.paths.sec_raw_manifest))

    def envelopes(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.paths.sec_envelopes))

    def source_versions(self, source_identity: str | None = None) -> list[dict[str, Any]]:
        records = read_jsonl(self.paths.sec_source_versions)
        if source_identity is None:
            return list(records)
        return [record for record in records if record["source_identity"] == source_identity]

    def locators(self) -> list[dict[str, Any]]:
        return list(read_jsonl(self.paths.sec_locators))

    def resolve_locator(self, locator_digest: str) -> dict[str, Any] | None:
        """Restricted lookup used for replay and point-in-time reconstruction."""
        for record in self.locators():
            if record["source_locator_digest"] == locator_digest:
                return record
        return None

    def committed_identities(self) -> dict[str, str]:
        """Source identities whose envelope is durable: the acknowledged set.

        This is what makes acknowledgement crash-safe. A task whose bytes were
        written but whose envelope was not is absent here and will be replayed.
        """
        committed: dict[str, str] = {}
        for record in self.envelopes():
            try:
                body = self.read_object(record["raw_object_sha256"])
            except (OSError, RawObjectConflict, ValueError, KeyError) as exc:
                raise SecStorageFailure(
                    "acknowledged envelope references non-reconstructible bytes") from exc
            if len(body) != record.get("byte_length"):
                raise SecStorageFailure(
                    "acknowledged envelope byte length no longer matches raw object")
            committed[record["source_identity"]] = record["raw_object_sha256"]
        return committed

    def conflicts(self) -> list[dict[str, Any]]:
        return [record for record in self.source_versions() if record.get("conflict")]

    def storage_health(self) -> dict[str, Any]:
        """Firewall-safe storage telemetry: sizes and integrity, never content."""
        objects = 0
        stored_bytes = 0
        for path in self.paths.sec_raw_objects.rglob("*.bin"):
            objects += 1
            stored_bytes += path.stat().st_size
        incomplete = sum(1 for _ in self.paths.sec_incomplete_objects.rglob("*.partial"))
        uncommitted_staging = sum(1 for _ in self.paths.sec_staging.glob("*.part"))
        return {"raw_objects": objects, "raw_bytes": stored_bytes,
                "incomplete_objects": incomplete,
                "uncommitted_staging_files": uncommitted_staging,
                "append_only": True, "content_addressed": True,
                "capture_state": CAPTURED,
                "visibility_state": NOT_VISIBLE_FOR_SCIENTIFIC_PROTOCOL,
                "admissibility_state": NOT_ADMISSIBLE_FOR_CONFIRMATION}

    def verify_objects(self) -> list[str]:
        """Re-hash every object. Returns the addresses whose bytes disagree."""
        broken: list[str] = []
        for path in sorted(self.paths.sec_raw_objects.rglob("*.bin")):
            object_id = "sha256:" + path.stem
            try:
                if digest_bytes(path.read_bytes()) != object_id:
                    broken.append(object_id)
            except OSError:
                broken.append(object_id)
        return broken

    def new_attempt_id(self) -> str:
        return uuid.uuid4().hex
