"""Immutable evidence storage and replay-safe lineage primitives.

The manifest in this module is an index, never a semantic source of truth. Raw
payloads are addressed by their own SHA-256 digest, validation assertions are
stored separately and must be revalidated from the raw bytes before they are
trusted, and derived lineage can be replayed against its declared transform.

The core deliberately depends only on the Python standard library. Adapters may
sit above it, but no data vendor is required by the evidence contracts.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


VALIDATION_STATUSES = ("VALID", "INVALID", "AMBIGUOUS")


class EvidenceError(RuntimeError):
    """Base error for evidence-store failures."""


class EvidenceCorruptionError(EvidenceError):
    """Durable bytes or committed metadata do not match their content address."""


class SemanticValidationError(EvidenceError):
    """Recorded semantic assertions cannot be reproduced from the raw bytes."""


@dataclass(frozen=True)
class ValidationOutcome:
    """Result produced directly by a parser/validator over raw bytes."""

    status: str
    identity_assertions: dict[str, Any] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in VALIDATION_STATUSES:
            raise ValueError(f"unknown validation status: {self.status}")


@dataclass(frozen=True)
class RawObject:
    """One acquisition receipt for immutable content-addressed bytes."""

    sha256: str
    size_bytes: int
    source_uri: str
    retrieved_at: str
    media_type: str
    source_type: str
    receipt_id: str


@dataclass(frozen=True)
class ValidatedObject:
    """Recorded validation result; authority requires replay from ``raw_sha256``."""

    validation_id: str
    raw_sha256: str
    parser_name: str
    parser_version: str
    validation_status: str
    identity_assertions: dict[str, Any]
    errors: tuple[str, ...]
    validated_at: str


@dataclass(frozen=True)
class DerivedArtifact:
    """Immutable transform lineage from input object hashes to an output hash."""

    artifact_id: str
    input_sha256s: tuple[str, ...]
    transform_name: str
    transform_version: str
    output_sha256: str
    parameters: dict[str, Any]
    created_at: str


Validator = Callable[[bytes], ValidationOutcome]
Transform = Callable[[tuple[bytes, ...], dict[str, Any]], bytes]
FaultHook = Callable[[str, dict[str, Any]], None]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _digest(value: str) -> str:
    prefix = "sha256:"
    if not value.startswith(prefix):
        raise ValueError(f"expected sha256 content address, got {value!r}")
    digest = value[len(prefix):]
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"invalid sha256 content address: {value!r}")
    return digest


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


def _record_id(prefix: str, payload: dict[str, Any]) -> str:
    return f"{prefix}:" + hashlib.sha256(_canonical_json(payload)).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(candidate)
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must carry timezone information: {value}")
    return parsed


def _fsync_directory(path: Path) -> None:
    """Best-effort directory fsync so a rename survives a sudden process death."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.{os.getpid()}.tmp"
    try:
        with temporary.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        if temporary.exists():
            temporary.unlink()


def _recover_torn_jsonl_tail(path: Path) -> bool:
    """Discard only an unterminated final append, never committed corruption."""
    if not path.exists() or path.stat().st_size == 0:
        return False
    with path.open("rb+") as handle:
        handle.seek(-1, os.SEEK_END)
        if handle.read(1) == b"\n":
            return False
        handle.seek(0)
        payload = handle.read()
        last_newline = payload.rfind(b"\n")
        handle.seek(0)
        handle.truncate(last_newline + 1 if last_newline >= 0 else 0)
        handle.flush()
        os.fsync(handle.fileno())
    return True


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _recover_torn_jsonl_tail(path)
    encoded = _canonical_json(record)
    with path.open("ab") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(path.parent)


def _read_jsonl_strict(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("rb") as handle:
        lines = handle.readlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            if index == len(lines) - 1 and not line.endswith(b"\n"):
                break
            raise EvidenceCorruptionError(
                f"malformed committed JSONL record at {path}:{index + 1}") from exc
    return records


class EvidenceStore:
    """Content-addressed evidence store with reconstructible manifests.

    Atomic object/record files hold durable truth. ``manifest.jsonl`` is only a
    replay/index surface and can be rebuilt from those files after deletion or a
    torn append. The optional fault hook is intentionally narrow and exists so
    tests can kill the process at durability boundaries.
    """

    def __init__(self, root: Path, fault_hook: FaultHook | None = None):
        self.root = Path(root)
        self.objects_root = self.root / "objects" / "sha256"
        self.receipts_root = self.root / "receipts"
        self.validated_root = self.root / "validated"
        self.derived_root = self.root / "derived"
        self.manifest_path = self.root / "manifest.jsonl"
        self._fault_hook = fault_hook
        self.root.mkdir(parents=True, exist_ok=True)
        _recover_torn_jsonl_tail(self.manifest_path)

    def _fault(self, stage: str, **context: Any) -> None:
        if self._fault_hook is not None:
            self._fault_hook(stage, context)

    def _append_manifest_once(self, record: dict[str, Any], identity_field: str) -> None:
        identity = record[identity_field]
        for existing in self.read_manifest():
            if existing.get("kind") == record.get("kind") and existing.get(identity_field) == identity:
                return
        _append_jsonl(self.manifest_path, record)

    def object_path(self, sha256: str) -> Path:
        digest = _digest(sha256)
        return self.objects_root / digest[:2] / digest

    def _receipt_dir(self, sha256: str) -> Path:
        return self.receipts_root / _digest(sha256)

    def _validation_path(self, raw_sha256: str, validation_id: str) -> Path:
        raw_digest = _digest(raw_sha256)
        validation_digest = validation_id.split(":", 1)[-1]
        return self.validated_root / raw_digest / f"{validation_digest}.json"

    def _derived_path(self, artifact_id: str) -> Path:
        digest = artifact_id.split(":", 1)[-1]
        return self.derived_root / f"{digest}.json"

    def put_bytes(
        self,
        payload: bytes,
        *,
        source_uri: str,
        retrieved_at: str | None = None,
        media_type: str = "application/octet-stream",
        source_type: str = "unknown",
    ) -> RawObject:
        if not isinstance(payload, bytes):
            raise TypeError("raw evidence payload must be bytes")
        if not source_uri:
            raise ValueError("source_uri is required")
        retrieved_at = retrieved_at or utc_now()
        _parse_timestamp(retrieved_at)
        sha256 = sha256_bytes(payload)
        destination = self.object_path(sha256)
        if destination.exists():
            committed = destination.read_bytes()
            if sha256_bytes(committed) != sha256:
                raise EvidenceCorruptionError(
                    f"object path {destination} does not contain its addressed bytes")
        else:
            _atomic_write(destination, payload)
            self._fault("after_object_commit", sha256=sha256, path=str(destination))
        self._append_manifest_once(
            {"kind": "raw_object", "sha256": sha256, "size_bytes": len(payload)},
            "sha256",
        )

        receipt_body = {
            "sha256": sha256,
            "size_bytes": len(payload),
            "source_uri": source_uri,
            "retrieved_at": retrieved_at,
            "media_type": media_type,
            "source_type": source_type,
        }
        receipt_id = _record_id("receipt", receipt_body)
        receipt = RawObject(**receipt_body, receipt_id=receipt_id)
        receipt_path = self._receipt_dir(sha256) / f"{receipt_id.split(':', 1)[1]}.json"
        encoded_receipt = _canonical_json(asdict(receipt))
        if receipt_path.exists():
            if receipt_path.read_bytes() != encoded_receipt:
                raise EvidenceCorruptionError(f"receipt id collision at {receipt_path}")
        else:
            _atomic_write(receipt_path, encoded_receipt)
            self._fault("after_receipt_commit", sha256=sha256, receipt_id=receipt_id)
        self._fault("before_manifest_append", kind="raw_receipt", receipt_id=receipt_id)
        self._append_manifest_once({"kind": "raw_receipt", **asdict(receipt)}, "receipt_id")
        self._fault("after_manifest_append", kind="raw_receipt", receipt_id=receipt_id)
        return receipt

    def get_bytes(self, sha256: str) -> bytes:
        path = self.object_path(sha256)
        if not path.exists():
            raise FileNotFoundError(path)
        payload = path.read_bytes()
        actual = sha256_bytes(payload)
        if actual != sha256:
            raise EvidenceCorruptionError(
                f"content address mismatch for {sha256}: found {actual}")
        return payload

    def verify_object(self, sha256: str) -> bool:
        self.get_bytes(sha256)
        return True

    def receipts(self, sha256: str) -> list[RawObject]:
        self.verify_object(sha256)
        directory = self._receipt_dir(sha256)
        if not directory.exists():
            return []
        results: list[RawObject] = []
        for path in sorted(directory.glob("*.json")):
            record = self._load_receipt_file(path)
            if record.sha256 != sha256:
                raise EvidenceCorruptionError(
                    f"receipt {path} points at {record.sha256}, expected {sha256}")
            results.append(record)
        return results

    def _load_receipt_file(self, path: Path) -> RawObject:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            record = RawObject(**payload)
        except (json.JSONDecodeError, TypeError) as exc:
            raise EvidenceCorruptionError(f"invalid receipt record: {path}") from exc
        body = asdict(record)
        body.pop("receipt_id")
        expected_id = _record_id("receipt", body)
        if expected_id != record.receipt_id or path.stem != expected_id.split(":", 1)[1]:
            raise EvidenceCorruptionError(f"receipt content address mismatch: {path}")
        _parse_timestamp(record.retrieved_at)
        return record

    def validate_object(
        self,
        raw_sha256: str,
        *,
        parser_name: str,
        parser_version: str,
        validator: Validator,
        validated_at: str | None = None,
    ) -> ValidatedObject:
        if not parser_name or not parser_version:
            raise ValueError("parser_name and parser_version are required")
        raw = self.get_bytes(raw_sha256)
        outcome = validator(raw)
        if not isinstance(outcome, ValidationOutcome):
            raise TypeError("validator must return ValidationOutcome")
        validated_at = validated_at or utc_now()
        _parse_timestamp(validated_at)
        body = {
            "raw_sha256": raw_sha256,
            "parser_name": parser_name,
            "parser_version": parser_version,
            "validation_status": outcome.status,
            "identity_assertions": outcome.identity_assertions,
            "errors": list(outcome.errors),
            "validated_at": validated_at,
        }
        validation_id = _record_id("validation", body)
        record = ValidatedObject(
            validation_id=validation_id,
            raw_sha256=raw_sha256,
            parser_name=parser_name,
            parser_version=parser_version,
            validation_status=outcome.status,
            identity_assertions=outcome.identity_assertions,
            errors=outcome.errors,
            validated_at=validated_at,
        )
        path = self._validation_path(raw_sha256, validation_id)
        encoded = _canonical_json(self._validated_to_json(record))
        if path.exists():
            if path.read_bytes() != encoded:
                raise EvidenceCorruptionError(f"validation id collision at {path}")
        else:
            _atomic_write(path, encoded)
            self._fault("after_validation_commit", validation_id=validation_id)
        self._append_manifest_once(
            {"kind": "validated_object", **self._validated_to_json(record)}, "validation_id")
        return record

    @staticmethod
    def _validated_to_json(record: ValidatedObject) -> dict[str, Any]:
        payload = asdict(record)
        payload["errors"] = list(record.errors)
        return payload

    def load_validation_record(self, validation_id: str) -> ValidatedObject:
        """Load recorded assertions without granting them semantic authority."""
        for path in self.validated_root.glob(f"*/{validation_id.split(':', 1)[-1]}.json"):
            return self._load_validation_file(path)
        raise FileNotFoundError(validation_id)

    def _load_validation_file(self, path: Path) -> ValidatedObject:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["errors"] = tuple(payload.get("errors", ()))
            record = ValidatedObject(**payload)
        except (json.JSONDecodeError, TypeError) as exc:
            raise EvidenceCorruptionError(f"invalid validation record: {path}") from exc
        if record.validation_status not in VALIDATION_STATUSES:
            raise EvidenceCorruptionError(
                f"invalid validation status {record.validation_status!r} in {path}")
        body = self._validated_to_json(record)
        body.pop("validation_id")
        expected = _record_id("validation", body)
        if expected != record.validation_id or path.stem != expected.split(":", 1)[1]:
            raise EvidenceCorruptionError(f"validation content address mismatch: {path}")
        self.verify_object(record.raw_sha256)
        _parse_timestamp(record.validated_at)
        return record

    def verified_validation(
        self,
        validation_id: str,
        *,
        parser_name: str,
        parser_version: str,
        validator: Validator,
    ) -> ValidatedObject:
        """Return a validation record only if its assertions replay from raw bytes."""
        record = self.load_validation_record(validation_id)
        if record.parser_name != parser_name or record.parser_version != parser_version:
            raise SemanticValidationError(
                "stored parser identity does not match the parser requested for revalidation")
        outcome = validator(self.get_bytes(record.raw_sha256))
        expected = ValidationOutcome(
            status=record.validation_status,
            identity_assertions=record.identity_assertions,
            errors=record.errors,
        )
        if outcome != expected:
            raise SemanticValidationError(
                f"validation {validation_id} cannot be reproduced from raw bytes")
        return record

    def derive(
        self,
        input_sha256s: Iterable[str],
        *,
        transform_name: str,
        transform_version: str,
        transform: Transform,
        parameters: dict[str, Any] | None = None,
        created_at: str | None = None,
        output_media_type: str = "application/octet-stream",
    ) -> DerivedArtifact:
        inputs = tuple(input_sha256s)
        if not inputs:
            raise ValueError("derived artifacts require at least one input object")
        if not transform_name or not transform_version:
            raise ValueError("transform_name and transform_version are required")
        raw_inputs = tuple(self.get_bytes(value) for value in inputs)
        parameters = dict(parameters or {})
        output = transform(raw_inputs, parameters)
        if not isinstance(output, bytes):
            raise TypeError("transform must return bytes")
        created_at = created_at or utc_now()
        _parse_timestamp(created_at)
        output_receipt = self.put_bytes(
            output,
            source_uri=f"derived://{transform_name}/{transform_version}",
            retrieved_at=created_at,
            media_type=output_media_type,
            source_type="derived",
        )
        body = {
            "input_sha256s": list(inputs),
            "transform_name": transform_name,
            "transform_version": transform_version,
            "output_sha256": output_receipt.sha256,
            "parameters": parameters,
            "created_at": created_at,
        }
        artifact_id = _record_id("artifact", body)
        record = DerivedArtifact(
            artifact_id=artifact_id,
            input_sha256s=inputs,
            transform_name=transform_name,
            transform_version=transform_version,
            output_sha256=output_receipt.sha256,
            parameters=parameters,
            created_at=created_at,
        )
        path = self._derived_path(artifact_id)
        encoded = _canonical_json(self._derived_to_json(record))
        if path.exists():
            if path.read_bytes() != encoded:
                raise EvidenceCorruptionError(f"derived artifact id collision at {path}")
        else:
            _atomic_write(path, encoded)
            self._fault("after_derived_commit", artifact_id=artifact_id)
        self._append_manifest_once(
            {"kind": "derived_artifact", **self._derived_to_json(record)}, "artifact_id")
        return record

    @staticmethod
    def _derived_to_json(record: DerivedArtifact) -> dict[str, Any]:
        payload = asdict(record)
        payload["input_sha256s"] = list(record.input_sha256s)
        return payload

    def load_derived_record(self, artifact_id: str) -> DerivedArtifact:
        return self._load_derived_file(self._derived_path(artifact_id))

    def _load_derived_file(self, path: Path) -> DerivedArtifact:
        if not path.exists():
            raise FileNotFoundError(path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["input_sha256s"] = tuple(payload.get("input_sha256s", ()))
            record = DerivedArtifact(**payload)
        except (json.JSONDecodeError, TypeError) as exc:
            raise EvidenceCorruptionError(f"invalid derived artifact record: {path}") from exc
        body = self._derived_to_json(record)
        body.pop("artifact_id")
        expected = _record_id("artifact", body)
        if expected != record.artifact_id or path.stem != expected.split(":", 1)[1]:
            raise EvidenceCorruptionError(f"derived artifact content address mismatch: {path}")
        for value in (*record.input_sha256s, record.output_sha256):
            self.verify_object(value)
        _parse_timestamp(record.created_at)
        return record

    def verified_derived(
        self,
        artifact_id: str,
        *,
        transform_name: str,
        transform_version: str,
        transform: Transform,
    ) -> DerivedArtifact:
        """Replay a derived artifact and require byte-identical output."""
        record = self.load_derived_record(artifact_id)
        if (record.transform_name != transform_name
                or record.transform_version != transform_version):
            raise SemanticValidationError(
                "stored transform identity does not match the requested replay transform")
        inputs = tuple(self.get_bytes(value) for value in record.input_sha256s)
        replayed = transform(inputs, dict(record.parameters))
        if not isinstance(replayed, bytes) or sha256_bytes(replayed) != record.output_sha256:
            raise SemanticValidationError(
                f"derived artifact {artifact_id} cannot be reproduced from its inputs")
        return record

    def read_manifest(self) -> list[dict[str, Any]]:
        return _read_jsonl_strict(self.manifest_path)

    def _inventory_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        if self.objects_root.exists():
            for path in sorted(value for value in self.objects_root.glob("*/*") if value.is_file()):
                if path.name.startswith("."):
                    continue
                sha256 = "sha256:" + path.name
                payload = path.read_bytes()
                if sha256_bytes(payload) != sha256:
                    raise EvidenceCorruptionError(f"object content address mismatch: {path}")
                records.append({"kind": "raw_object", "sha256": sha256,
                                "size_bytes": len(payload)})
        if self.receipts_root.exists():
            for path in sorted(self.receipts_root.glob("*/*.json")):
                receipt = self._load_receipt_file(path)
                self.verify_object(receipt.sha256)
                records.append({"kind": "raw_receipt", **asdict(receipt)})
        if self.validated_root.exists():
            for path in sorted(self.validated_root.glob("*/*.json")):
                validation = self._load_validation_file(path)
                records.append({"kind": "validated_object", **self._validated_to_json(validation)})
        if self.derived_root.exists():
            for path in sorted(self.derived_root.glob("*.json")):
                artifact = self._load_derived_file(path)
                records.append({"kind": "derived_artifact", **self._derived_to_json(artifact)})
        return sorted(records, key=lambda value: _canonical_json(value))

    def rebuild_manifest(self) -> dict[str, int]:
        """Reconstruct a deterministic manifest from immutable durable records."""
        records = self._inventory_records()
        payload = b"".join(_canonical_json(record) for record in records)
        _atomic_write(self.manifest_path, payload)
        summary: dict[str, int] = {}
        for record in records:
            kind = str(record["kind"])
            summary[kind] = summary.get(kind, 0) + 1
        return summary

    def audit_manifest(self) -> bool:
        """Check that the current index is exactly reconstructible from durable truth."""
        current = sorted(self.read_manifest(), key=lambda value: _canonical_json(value))
        expected = self._inventory_records()
        return current == expected
