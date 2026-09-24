"""One-look holdout request, holdout cache ledger and trial (multiplicity) ledger.

Authority for the single holdout look is the committed, write-once file
``research/fastlane/prereg/HOLDOUT_REQUEST.json``:

* it is created exclusively (temp file + hard link), so a second, different
  request cannot be written next to it;
* it must pass the git checks of :mod:`quant.fastlane.gitcheck` (exactly one
  commit ever touches it, ancestor of HEAD, published, bytes equal);
* its finalists must belong to the sealed grid and each must already have
  discovery and walk-forward records in the trial ledger; it stores the fast-
  lane code fingerprint, the evaluation-spec digest and the trial-ledger head.

``var/fastlane/ledgers/holdout_one_look.jsonl`` is a cache of that request: if
it is deleted the committed request is re-cached; if it disagrees with the
committed request, access is refused until an operator inspects it.

Both JSONL ledgers are hash-chained (``prev_sha`` = sha256 of the previous
line); an edited, reordered or torn ledger fails closed.
"""

from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes, sha256_file
from quant.fastlane.preregistration import (MAX_FINALISTS, PREREG_DIR, SPLITS,
                                            OutcomeAccessRefused, canonical_json, load_sealed,
                                            sealed_path)

GENESIS = "GENESIS"
REQUEST_NAME = "HOLDOUT_REQUEST.json"
REQUIRED_TRIAL_SPLITS = ("discovery", "walk_forward")


class HoldoutAlreadyConsumed(PermissionError):
    pass


class NoFinalists(ValueError):
    """Zero finalists: the verdict is NO_GO and the holdout stays unopened."""


class LedgerCorrupted(RuntimeError):
    pass


class TrialConflict(ValueError):
    pass


class SimulatedCrash(RuntimeError):
    """Raised only by tests' crash-injection hook."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def code_fingerprint() -> str:
    """sha256 over the fast-lane package sources (name + bytes, sorted)."""
    here = Path(__file__).resolve().parent
    parts = [f"{p.name}:{sha256_file(p)}" for p in sorted(here.glob("*.py"))]
    return "sha256:" + sha256_bytes("|".join(parts).encode("utf-8"))


# --- hash-chained JSONL ------------------------------------------------------------

def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = path.read_bytes()
    if not data:
        return []
    if not data.endswith(b"\n"):
        raise LedgerCorrupted(f"{path.name}: torn final line; refusing until inspected")
    records = []
    prev = GENESIS
    for number, line in enumerate(data.split(b"\n")[:-1], start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerCorrupted(f"{path.name}: line {number} is not JSON") from exc
        if record.get("prev_sha") != prev:
            raise LedgerCorrupted(f"{path.name}: hash chain broken at line {number}")
        prev = sha256_bytes(line)
        records.append(record)
    return records


def ledger_head(path: Path) -> str:
    if not path.exists() or not path.read_bytes():
        return GENESIS
    read_ledger(path)
    return sha256_bytes(path.read_bytes().split(b"\n")[-2])


def _append_chained(path: Path, record: dict) -> dict:
    record = {**record, "prev_sha": ledger_head(path)}
    line = canonical_json(record) + b"\n"
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)
    return record


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


# --- trial ledger ----------------------------------------------------------------------

class TrialLedger:
    """Every evaluated variant, under the sealed prereg, for multiplicity accounting."""

    def __init__(self, fw: Firewall) -> None:
        self.fw = fw
        self.path = fw.data("ledgers", "trials.jsonl")

    def records(self) -> list[dict]:
        return read_ledger(self.fw.guard(self.path, write=False))

    def head(self) -> str:
        return ledger_head(self.fw.guard(self.path, write=False))

    def record(self, trial_id: str, variant_id: str, split: str,
               spec: Mapping[str, Any]) -> dict:
        if split not in SPLITS:
            raise TrialConflict(f"unknown split {split!r}")
        sealed = load_sealed(self.fw)
        declared = {v["variant_id"] for v in sealed["protocol"]["variants"]}
        if variant_id not in declared:
            raise TrialConflict(f"variant {variant_id!r} is not in the sealed grid")
        spec_digest = "sha256:" + sha256_bytes(canonical_json(spec))
        self.fw.mkdirs(self.path.parent)
        with _locked(self.path):
            for existing in self.records():
                if existing.get("trial_id") == trial_id:
                    same = (existing.get("variant_id") == variant_id
                            and existing.get("split") == split
                            and existing.get("prereg_sha256") == sealed["protocol_sha256"]
                            and existing.get("spec_digest") == spec_digest)
                    if same:
                        return existing
                    raise TrialConflict(f"trial {trial_id} already recorded with other content")
            return _append_chained(self.path, {
                "lineage": LINEAGE_ID,
                "kind": "TRIAL",
                "trial_id": trial_id,
                "variant_id": variant_id,
                "split": split,
                "prereg_sha256": sealed["protocol_sha256"],
                "spec_digest": spec_digest,
                "recorded_at_utc": _now(),
            })

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


# --- holdout request (committed authority) ------------------------------------------------

def request_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, REQUEST_NAME)


def read_holdout_request(fw: Firewall) -> dict | None:
    path = request_path(fw)
    if not path.exists():
        return None
    try:
        return fw.read_json(path)
    except (ValueError, UnicodeDecodeError) as exc:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} is not valid JSON") from exc


def _check_finalists(fw: Firewall, sealed: Mapping[str, Any], finalists: Sequence[str]) -> list[dict]:
    if not finalists:
        raise NoFinalists("zero finalists: NO_GO is recorded and the holdout stays unopened")
    if len(finalists) > MAX_FINALISTS or len(set(finalists)) != len(finalists):
        raise ValueError(f"holdout admits 1..{MAX_FINALISTS} distinct finalists, "
                         f"got {list(finalists)}")
    declared = {v["variant_id"] for v in sealed["protocol"]["variants"]}
    unknown = sorted(set(finalists) - declared)
    if unknown:
        raise OutcomeAccessRefused(f"finalists {unknown} are not in the sealed grid")
    records = TrialLedger(fw).records()
    for variant in finalists:
        seen = {r["split"] for r in records if r["variant_id"] == variant
                and r["prereg_sha256"] == sealed["protocol_sha256"]}
        missing = [s for s in REQUIRED_TRIAL_SPLITS if s not in seen]
        if missing:
            raise OutcomeAccessRefused(f"finalist {variant} has no trial-ledger record for {missing}")
    return records


def write_holdout_request(fw: Firewall, request_id: str, finalists: Sequence[str],
                          eval_spec_digest: str) -> dict:
    """Create the single holdout request (to be committed and pushed before access)."""
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    if not request_id or not eval_spec_digest:
        raise ValueError("request_id and eval_spec_digest are required")
    sealed = load_sealed(fw)
    try:
        verify_committed(fw.repo_root, sealed_path(fw), write_once=True)
    except GitCheckFailed as exc:
        raise OutcomeAccessRefused(f"seal must be committed and published first: {exc}") from exc
    records = _check_finalists(fw, sealed, finalists)
    record = {
        "lineage": LINEAGE_ID,
        "kind": "HOLDOUT_ONE_LOOK_REQUEST",
        "request_id": request_id,
        "prereg_sha256": sealed["protocol_sha256"],
        "finalists": sorted(finalists),
        "code_fingerprint": code_fingerprint(),
        "eval_spec_digest": eval_spec_digest,
        "trial_ledger": {"head": TrialLedger(fw).head(), "count": len(records)},
        "created_at_utc": _now(),
    }
    path = request_path(fw)
    if path.exists():
        raise HoldoutAlreadyConsumed(f"{REQUEST_NAME} already exists; one look only")
    try:
        fw.create_exclusive(path, canonical_json(record) + b"\n")
    except FileExistsError as exc:
        raise HoldoutAlreadyConsumed(f"{REQUEST_NAME} was created concurrently") from exc
    return record


def request_fingerprint(request: Mapping[str, Any]) -> str:
    core = {k: request.get(k) for k in ("request_id", "prereg_sha256", "finalists",
                                        "code_fingerprint", "eval_spec_digest", "trial_ledger")}
    return "sha256:" + sha256_bytes(canonical_json(core))


def verify_holdout_request(fw: Firewall, sealed: Mapping[str, Any], request_id: str | None,
                           variants: Sequence[str] | None, eval_spec_digest: str | None) -> dict:
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    if not request_id or not variants or not eval_spec_digest:
        raise OutcomeAccessRefused("holdout access needs request_id, finalists and "
                                   "eval_spec_digest")
    path = request_path(fw)
    request = read_holdout_request(fw)
    if request is None:
        raise OutcomeAccessRefused(f"no committed {REQUEST_NAME}")
    try:
        committed = verify_committed(fw.repo_root, path, write_once=True)
    except GitCheckFailed as exc:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} is not anchored in git: {exc}") from exc
    if request.get("lineage") != LINEAGE_ID or request.get("prereg_sha256") != sealed["protocol_sha256"]:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} does not belong to the sealed prereg")
    if request.get("request_id") != request_id or request.get("finalists") != sorted(variants):
        raise HoldoutAlreadyConsumed(
            f"holdout is committed to request {request.get('request_id')} with finalists "
            f"{request.get('finalists')}; one look only")
    if request.get("eval_spec_digest") != eval_spec_digest:
        raise OutcomeAccessRefused("evaluation-spec digest differs from the committed request")
    if request.get("code_fingerprint") != code_fingerprint():
        raise OutcomeAccessRefused("fast-lane code changed since the holdout request was committed")
    records = _check_finalists(fw, sealed, request["finalists"])
    trial = request.get("trial_ledger") or {}
    count = int(trial.get("count", -1))
    if count > len(records) or count < 0:
        raise OutcomeAccessRefused("trial ledger is shorter than when the request was committed")
    raw = TrialLedger(fw).path
    lines = raw.read_bytes().split(b"\n")[:-1] if raw.exists() else []
    head = GENESIS if count == 0 else sha256_bytes(lines[count - 1])
    if head != trial.get("head"):
        raise OutcomeAccessRefused("trial ledger was rewritten after the request was committed")
    return {**request, "commit": committed.commit}


# --- holdout cache ledger -----------------------------------------------------------------

class HoldoutLedger:
    """Cache of the committed holdout request (``var/``); never an authority."""

    def __init__(self, fw: Firewall) -> None:
        self.fw = fw
        self.path = fw.data("ledgers", "holdout_one_look.jsonl")

    def records(self) -> list[dict]:
        return read_ledger(self.fw.guard(self.path, write=False))

    def sync(self, request: Mapping[str, Any], *, crash_after_append: bool = False) -> dict:
        fingerprint = request_fingerprint(request)
        self.fw.mkdirs(self.path.parent)
        with _locked(self.path):
            existing = self.records()
            if len(existing) > 1:
                raise LedgerCorrupted("holdout cache holds more than one access")
            if existing:
                if existing[0].get("request_fingerprint") == fingerprint:
                    return existing[0]
                raise HoldoutAlreadyConsumed(
                    "holdout cache names a different request than the committed one; the "
                    "committed request is authoritative - inspect the cache")
            record = _append_chained(self.path, {
                "lineage": LINEAGE_ID,
                "kind": "HOLDOUT_ONE_LOOK_CACHE",
                "request_id": request.get("request_id"),
                "prereg_sha256": request.get("prereg_sha256"),
                "finalists": request.get("finalists"),
                "request_fingerprint": fingerprint,
                "cached_at_utc": _now(),
            })
            if crash_after_append:
                raise SimulatedCrash("crash injected after the holdout cache append")
            return record
