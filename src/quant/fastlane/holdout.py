"""One-look holdout ledger and trial (multiplicity) ledger.

Both ledgers are append-only JSONL under ``var/fastlane/ledgers/`` and are
restart-safe:

* the holdout ledger admits exactly one access request. Replaying the same
  ``request_id`` with the same payload after a crash returns the committed
  record (idempotent); any other request is refused forever;
* the trial ledger records every evaluated variant, idempotently by
  ``trial_id``, so multiplicity (M, Deflated Sharpe trial count) is counted
  from evidence rather than memory.

A torn or unparsable ledger line fails closed: the ledger cannot tell whether
an access happened, so it refuses until an operator inspects it.
"""

from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes
from quant.fastlane.preregistration import MAX_FINALISTS, SPLITS, canonical_json


class HoldoutAlreadyConsumed(PermissionError):
    pass


class LedgerCorrupted(RuntimeError):
    pass


class TrialConflict(ValueError):
    pass


class SimulatedCrash(RuntimeError):
    """Raised only by tests' crash-injection hook."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = path.read_bytes()
    if not data:
        return []
    if not data.endswith(b"\n"):
        raise LedgerCorrupted(f"{path.name}: torn final line; refusing until inspected")
    records = []
    for number, line in enumerate(data.split(b"\n")[:-1], start=1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise LedgerCorrupted(f"{path.name}: line {number} is not JSON") from exc
    return records


def _append(path: Path, record: Mapping[str, Any]) -> None:
    line = canonical_json(record) + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    lock = path.with_name(path.name + ".lock")
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


class HoldoutLedger:
    def __init__(self, fw: Firewall) -> None:
        self.fw = fw
        self.path = fw.data("ledgers", "holdout_one_look.jsonl")

    def records(self) -> list[dict]:
        return read_ledger(self.fw.guard(self.path, write=False))

    @staticmethod
    def request_fingerprint(request_id: str, prereg_sha256: str, variants: Sequence[str]) -> str:
        return "sha256:" + sha256_bytes(canonical_json({
            "request_id": request_id, "prereg_sha256": prereg_sha256,
            "variants": sorted(variants)}))

    def request(self, request_id: str, prereg_sha256: str, variants: Sequence[str], *,
                crash_after_append: bool = False) -> dict:
        if not request_id:
            raise ValueError("request_id is required")
        if not 1 <= len(variants) <= MAX_FINALISTS or len(set(variants)) != len(variants):
            raise ValueError(
                f"holdout admits 1..{MAX_FINALISTS} distinct finalists, got {list(variants)}")
        fingerprint = self.request_fingerprint(request_id, prereg_sha256, variants)
        self.fw.mkdirs(self.path.parent)
        with _locked(self.path):
            existing = self.records()
            if len(existing) > 1:
                raise LedgerCorrupted("holdout ledger holds more than one access")
            if existing:
                first = existing[0]
                if (first.get("request_id") == request_id
                        and first.get("request_fingerprint") == fingerprint):
                    return first
                raise HoldoutAlreadyConsumed(
                    f"holdout already consumed by request {first.get('request_id')} at "
                    f"{first.get('requested_at_utc')}; one look only")
            record = {
                "lineage": LINEAGE_ID,
                "kind": "HOLDOUT_ONE_LOOK",
                "request_id": request_id,
                "prereg_sha256": prereg_sha256,
                "variants": sorted(variants),
                "request_fingerprint": fingerprint,
                "requested_at_utc": _now(),
            }
            _append(self.path, record)
            if crash_after_append:
                raise SimulatedCrash("crash injected after the holdout append was committed")
            return record


class TrialLedger:
    def __init__(self, fw: Firewall) -> None:
        self.fw = fw
        self.path = fw.data("ledgers", "trials.jsonl")

    def records(self) -> list[dict]:
        return read_ledger(self.fw.guard(self.path, write=False))

    def record(self, trial_id: str, variant_id: str, split: str, prereg_sha256: str,
               spec: Mapping[str, Any], *, declared_variants: Sequence[str] | None = None) -> dict:
        if split not in SPLITS:
            raise TrialConflict(f"unknown split {split!r}")
        if declared_variants is not None and variant_id not in set(declared_variants):
            raise TrialConflict(f"variant {variant_id!r} is not in the pre-declared grid")
        spec_digest = "sha256:" + sha256_bytes(canonical_json(spec))
        self.fw.mkdirs(self.path.parent)
        with _locked(self.path):
            for existing in self.records():
                if existing.get("trial_id") == trial_id:
                    same = (existing.get("variant_id") == variant_id
                            and existing.get("split") == split
                            and existing.get("prereg_sha256") == prereg_sha256
                            and existing.get("spec_digest") == spec_digest)
                    if same:
                        return existing
                    raise TrialConflict(f"trial {trial_id} already recorded with other content")
            record = {
                "lineage": LINEAGE_ID,
                "kind": "TRIAL",
                "trial_id": trial_id,
                "variant_id": variant_id,
                "split": split,
                "prereg_sha256": prereg_sha256,
                "spec_digest": spec_digest,
                "recorded_at_utc": _now(),
            }
            _append(self.path, record)
            return record

    def multiplicity(self) -> dict:
        records = self.records()
        by_split: dict[str, set[str]] = {}
        for rec in records:
            by_split.setdefault(rec["split"], set()).add(rec["variant_id"])
        return {
            "trials": len(records),
            "distinct_variants": len({r["variant_id"] for r in records}),
            "distinct_variants_by_split": {k: len(v) for k, v in sorted(by_split.items())},
        }
