"""One-look holdout request, holdout cache ledger and trial (multiplicity) ledger.

Authority for the single holdout look is the committed, write-once file
``research/fastlane/prereg/HOLDOUT_REQUEST.json``:

* it is created exclusively (temp file + hard link), so a second, different
  request cannot be written next to it;
* it must pass the git checks of :mod:`quant.fastlane.gitcheck` (exactly one
  commit ever touches it, ancestor of HEAD, published, bytes equal);
* it can only be written through the verified path
  (:func:`quant.fastlane.screen.request_holdout`), which re-runs the whole
  discovery/walk-forward screen under normal grants and mints an in-process
  receipt; :func:`_write_holdout_request` refuses without that receipt;
* every declared variant must have discovery AND walk-forward trial records
  matching the committed ``SCREEN_REPORT.json`` (write-once, git-anchored like
  the request); it stores the fast-lane code fingerprint, the evaluation-spec
  and screen-report digests, the trial- and access-ledger heads, the
  multiplicity count (:func:`n_trials_conservative`) and the seal commit;
* the holdout grant additionally needs a receipt minted by a fresh
  recomputation of the screen in the same process (``verdict.evaluate_holdout``);
* at every grant the seal's adding commit must still equal the pinned
  ``seal_commit`` and be contained in a branch the real remote advertises, so a
  force-push that rewrites the seal commit is detected.

``var/fastlane/ledgers/holdout_one_look.jsonl`` is a cache of that request: if
it is deleted the committed request is re-cached; if it disagrees with the
committed request, access is refused until an operator inspects it.

Both JSONL ledgers are hash-chained (``prev_sha`` = sha256 of the previous
line); an edited, reordered or torn ledger fails closed.
"""

from __future__ import annotations

import fcntl
import hashlib
import hmac
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
SCREEN_REPORT_NAME = "SCREEN_REPORT.json"
EVAL_SPEC_NAME = "HOLDOUT_EVAL_SPEC.json"
REQUIRED_TRIAL_SPLITS = ("discovery", "walk_forward")
ACCESS_SPLITS = ("discovery", "walk_forward")


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
        out = {
            "trials": len(records),
            "distinct_variants": len({r["variant_id"] for r in records}),
            "distinct_variants_by_split": {k: len(v) for k, v in sorted(by_split.items())},
        }
        try:
            out["n_trials_for_dsr"] = n_trials_for_dsr(load_sealed(self.fw), records)
        except Exception:
            pass
        return out


# --- outcome-access ledger (exploratory reruns are counted) ---------------------------------

class AccessLedger:
    """One record per (variant, split, configuration, code) that read discovery or
    walk-forward outcomes; idempotent, hash-chained, fail-closed like the trial ledger."""

    def __init__(self, fw: Firewall) -> None:
        self.fw = fw
        self.path = fw.data("ledgers", "outcome_access.jsonl")

    def records(self) -> list[dict]:
        return read_ledger(self.fw.guard(self.path, write=False))

    def head(self) -> str:
        return ledger_head(self.fw.guard(self.path, write=False))

    def record(self, *, variant_id: str, split: str, config_digest: str, prereg_sha256: str,
               code: str | None = None) -> dict:
        if split not in ACCESS_SPLITS:
            raise TrialConflict(f"access records are for {ACCESS_SPLITS}, not {split!r}")
        code = code or code_fingerprint()
        access_id = "sha256:" + sha256_bytes(canonical_json(
            [variant_id, split, config_digest, code, prereg_sha256]))
        self.fw.mkdirs(self.path.parent)
        with _locked(self.path):
            for existing in self.records():
                if existing.get("access_id") == access_id:
                    return existing
            return _append_chained(self.path, {
                "lineage": LINEAGE_ID, "kind": "OUTCOME_ACCESS", "access_id": access_id,
                "variant_id": variant_id, "split": split, "config_digest": config_digest,
                "code_fingerprint": code, "prereg_sha256": prereg_sha256,
                "recorded_at_utc": _now()})


def n_trials_conservative(fw: Firewall, sealed: Mapping[str, Any]) -> dict:
    """N_trials = max(sealed rule, 2 x M_declared, distinct configurations accessed).

    The sealed rule is ``max(M_declared, trial-ledger evaluations)``; a screen evaluates every
    declared variant in two splits, and any discovery/walk-forward read outside the screen
    (another seed, capacity multiple, code or vendor configuration) is one more access
    record (PROTOCOL_CLARIFICATIONS C22).
    """
    m_declared = int(sealed["protocol"]["multiplicity"]["M_declared"])
    sealed_rule = n_trials_for_dsr(sealed, TrialLedger(fw).records())
    accessed = {r["access_id"] for r in AccessLedger(fw).records()
                if r.get("prereg_sha256") == sealed["protocol_sha256"]}
    return {"n_trials_for_dsr": max(sealed_rule, 2 * m_declared, len(accessed)),
            "sealed_rule": sealed_rule, "two_x_m_declared": 2 * m_declared,
            "distinct_configurations_accessed": len(accessed)}


# --- holdout request (committed authority) ------------------------------------------------

def request_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, REQUEST_NAME)


def screen_report_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, SCREEN_REPORT_NAME)


def eval_spec_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, EVAL_SPEC_NAME)


def json_digest(obj: Any) -> str:
    return "sha256:" + sha256_bytes(canonical_json(obj))


def _screen_receipt(fw: Firewall, prereg_sha256: str, request_id: str, finalists: Sequence[str],
                    eval_spec_digest: str, screen_report_digest: str) -> str:
    """In-process proof that the screen was just recomputed and matched (never persisted).

    Minted only by :mod:`quant.fastlane.screen` after a full recomputation; keyed by the
    per-process secret nonce of :mod:`quant.fastlane.preregistration`.
    """
    from quant.fastlane.preregistration import _PROCESS_NONCE
    message = canonical_json(["SCREEN_RECOMPUTED", str(fw.repo_root), prereg_sha256, request_id,
                              sorted(finalists), eval_spec_digest, screen_report_digest])
    return hmac.new(_PROCESS_NONCE + b"|screen-receipt", message, hashlib.sha256).hexdigest()


def _check_receipt(fw: Firewall, receipt: Any, prereg_sha256: str, request_id: str,
                   finalists: Sequence[str], eval_spec_digest: str,
                   screen_report_digest: str) -> None:
    expected = _screen_receipt(fw, prereg_sha256, request_id, finalists, eval_spec_digest,
                               screen_report_digest)
    if not isinstance(receipt, str) or not hmac.compare_digest(expected, receipt):
        raise OutcomeAccessRefused(
            "no receipt from a fresh recomputation of the screen in this process: the holdout "
            "request and the look go only through screen.request_holdout / "
            "verdict.evaluate_holdout")


def _check_screen_report(fw: Firewall, sealed: Mapping[str, Any], screen_report_digest: str,
                         eval_spec_digest: str, finalists: Sequence[str], *,
                         anchored: bool, max_age_s: float = 0.0) -> dict:
    """The committed screen report must match its digest, the spec, the finalists and every
    declared variant's discovery AND walk-forward trial records."""
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    paths = (screen_report_path(fw), eval_spec_path(fw))
    for path in paths:
        if not path.exists():
            raise OutcomeAccessRefused(f"{path.name} is missing")
    try:
        report = fw.read_json(paths[0])
        spec = fw.read_json(paths[1])
    except (ValueError, UnicodeDecodeError) as exc:
        raise OutcomeAccessRefused("screen report or evaluation spec is not valid JSON") from exc
    if json_digest(report) != screen_report_digest:
        raise OutcomeAccessRefused(f"{SCREEN_REPORT_NAME} differs from the pinned digest")
    if json_digest(spec) != eval_spec_digest:
        raise OutcomeAccessRefused(f"{EVAL_SPEC_NAME} differs from the pinned digest")
    payload = report.get("holdout_request_payload") or {}
    if (report.get("prereg_sha256") != sealed["protocol_sha256"]
            or payload.get("eval_spec_digest") != eval_spec_digest
            or sorted(report.get("finalists") or []) != sorted(finalists)
            or sorted(spec.get("finalists") or []) != sorted(finalists)):
        raise OutcomeAccessRefused("screen report, evaluation spec and finalists disagree")
    listing = report.get("trials") or {}
    records = {r["trial_id"]: r for r in TrialLedger(fw).records()
               if r.get("prereg_sha256") == sealed["protocol_sha256"]}
    for variant in [v["variant_id"] for v in sealed["protocol"]["variants"]]:
        for split in REQUIRED_TRIAL_SPLITS:
            entry = (listing.get(variant) or {}).get(split) or {}
            rec = records.get(entry.get("trial_id"))
            if (rec is None or rec.get("variant_id") != variant or rec.get("split") != split
                    or rec.get("spec_digest") != entry.get("spec_digest")):
                raise OutcomeAccessRefused(
                    f"{variant} has no {split} trial record matching the screen report")
    if anchored:
        for path in paths:
            try:
                verify_committed(fw.repo_root, path, write_once=True, max_age_s=max_age_s)
            except GitCheckFailed as exc:
                raise OutcomeAccessRefused(f"{path.name} is not anchored in git: {exc}") from exc
    return report


def read_holdout_request(fw: Firewall) -> dict | None:
    path = request_path(fw)
    if not path.exists():
        return None
    try:
        return fw.read_json(path)
    except (ValueError, UnicodeDecodeError) as exc:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} is not valid JSON") from exc


def n_trials_for_dsr(sealed: Mapping[str, Any], records: Sequence[Mapping[str, Any]]) -> int:
    """N_trials = max(M_declared, number of trial-ledger evaluations)."""
    declared = int(sealed["protocol"]["multiplicity"]["M_declared"])
    evaluations = {r["trial_id"] for r in records
                   if r.get("prereg_sha256") == sealed["protocol_sha256"]}
    return max(declared, len(evaluations))


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
    screened = {r["variant_id"] for r in records if r["split"] == "discovery"
                and r["prereg_sha256"] == sealed["protocol_sha256"]}
    unscreened = sorted(declared - screened)
    if unscreened:
        raise OutcomeAccessRefused(
            f"{len(unscreened)} declared variants have no discovery trial record (all "
            f"M_declared must be screened before a holdout request): {unscreened[:5]}")
    for variant in finalists:
        seen = {r["split"] for r in records if r["variant_id"] == variant
                and r["prereg_sha256"] == sealed["protocol_sha256"]}
        missing = [s for s in REQUIRED_TRIAL_SPLITS if s not in seen]
        if missing:
            raise OutcomeAccessRefused(f"finalist {variant} has no trial-ledger record for {missing}")
    return records


def _write_holdout_request(fw: Firewall, request_id: str, finalists: Sequence[str],
                           eval_spec_digest: str, screen_report_digest: str, *,
                           receipt: str) -> dict:
    """Create the single holdout request (to be committed and pushed before access).

    Private: only :func:`quant.fastlane.screen.request_holdout` calls it, after re-running the
    screen and writing the matching SCREEN_REPORT.json and HOLDOUT_EVAL_SPEC.json.
    """
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    if not request_id or not eval_spec_digest or not screen_report_digest:
        raise ValueError("request_id, eval_spec_digest and screen_report_digest are required")
    sealed = load_sealed(fw)
    _check_receipt(fw, receipt, sealed["protocol_sha256"], request_id, finalists,
                   eval_spec_digest, screen_report_digest)
    try:
        seal = verify_committed(fw.repo_root, sealed_path(fw), write_once=True)
    except GitCheckFailed as exc:
        raise OutcomeAccessRefused(f"seal must be committed and published first: {exc}") from exc
    path = request_path(fw)
    if path.exists():
        raise HoldoutAlreadyConsumed(f"{REQUEST_NAME} already exists; one look only")
    records = _check_finalists(fw, sealed, finalists)
    report = _check_screen_report(fw, sealed, screen_report_digest, eval_spec_digest, finalists,
                                  anchored=False)
    access = AccessLedger(fw).records()
    n_trials = n_trials_conservative(fw, sealed)
    if report.get("n_trials_for_dsr") != n_trials["n_trials_for_dsr"]:
        raise OutcomeAccessRefused("the screen report was derived with another N_trials than "
                                   "the ledgers give now; recompute it")
    record = {
        "lineage": LINEAGE_ID,
        "kind": "HOLDOUT_ONE_LOOK_REQUEST",
        "request_id": request_id,
        "prereg_sha256": sealed["protocol_sha256"],
        "seal_commit": seal.commit,
        "finalists": sorted(finalists),
        "code_fingerprint": code_fingerprint(),
        "eval_spec_digest": eval_spec_digest,
        "screen_report_digest": screen_report_digest,
        "trial_ledger": {"head": TrialLedger(fw).head(), "count": len(records)},
        "access_ledger": {"head": AccessLedger(fw).head(), "count": len(access)},
        "multiplicity": {"M_declared": sealed["protocol"]["multiplicity"]["M_declared"],
                         **n_trials},
        "created_at_utc": _now(),
    }
    try:
        fw.create_exclusive(path, canonical_json(record) + b"\n")
    except FileExistsError as exc:
        raise HoldoutAlreadyConsumed(f"{REQUEST_NAME} was created concurrently") from exc
    return record


def request_fingerprint(request: Mapping[str, Any]) -> str:
    core = {k: request.get(k) for k in ("request_id", "prereg_sha256", "seal_commit",
                                        "finalists", "code_fingerprint", "eval_spec_digest",
                                        "screen_report_digest", "trial_ledger", "access_ledger",
                                        "multiplicity")}
    return "sha256:" + sha256_bytes(canonical_json(core))


def verify_committed_request(fw: Firewall, sealed: Mapping[str, Any], seal_commit: str, *,
                             max_age_s: float = 0.0) -> dict:
    """Git-anchor the request and check it pins the current seal commit."""
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    request = read_holdout_request(fw)
    if request is None:
        raise OutcomeAccessRefused(f"no committed {REQUEST_NAME}")
    try:
        committed = verify_committed(fw.repo_root, request_path(fw), write_once=True,
                                     max_age_s=max_age_s)
    except GitCheckFailed as exc:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} is not anchored in git: {exc}") from exc
    if request.get("lineage") != LINEAGE_ID or request.get("prereg_sha256") != sealed["protocol_sha256"]:
        raise OutcomeAccessRefused(f"{REQUEST_NAME} does not belong to the sealed prereg")
    if request.get("seal_commit") != seal_commit:
        raise OutcomeAccessRefused(
            f"the seal commit changed since the request was committed ({request.get('seal_commit')}"
            f" -> {seal_commit}): history was rewritten")
    return {**request, "commit": committed.commit}


def _ledger_prefix_ok(path: Path, pinned: Mapping[str, Any] | None, what: str) -> None:
    pinned = pinned or {}
    count = int(pinned.get("count", -1))
    raw = path.read_bytes() if path.exists() else b""
    lines = raw.split(b"\n")[:-1] if raw else []
    if count < 0 or count > len(lines):
        raise OutcomeAccessRefused(f"{what} is shorter than when the request was committed")
    head = GENESIS if count == 0 else sha256_bytes(lines[count - 1])
    if head != pinned.get("head"):
        raise OutcomeAccessRefused(f"{what} was rewritten after the request was committed")


def verify_holdout_request(fw: Firewall, sealed: Mapping[str, Any], request_id: str | None,
                           variants: Sequence[str] | None, eval_spec_digest: str | None, *,
                           seal_commit: str, receipt: str | None = None) -> dict:
    if not request_id or not variants or not eval_spec_digest:
        raise OutcomeAccessRefused("holdout access needs request_id, finalists and "
                                   "eval_spec_digest")
    request = verify_committed_request(fw, sealed, seal_commit, max_age_s=60.0)
    _check_receipt(fw, receipt, sealed["protocol_sha256"], str(request.get("request_id")),
                   request.get("finalists") or [], str(request.get("eval_spec_digest")),
                   str(request.get("screen_report_digest")))
    if request.get("request_id") != request_id or request.get("finalists") != sorted(variants):
        raise HoldoutAlreadyConsumed(
            f"holdout is committed to request {request.get('request_id')} with finalists "
            f"{request.get('finalists')}; one look only")
    if request.get("eval_spec_digest") != eval_spec_digest:
        raise OutcomeAccessRefused("evaluation-spec digest differs from the committed request")
    if request.get("code_fingerprint") != code_fingerprint():
        raise OutcomeAccessRefused("fast-lane code changed since the holdout request was committed")
    _check_finalists(fw, sealed, request["finalists"])
    _ledger_prefix_ok(TrialLedger(fw).path, request.get("trial_ledger"), "trial ledger")
    _ledger_prefix_ok(AccessLedger(fw).path, request.get("access_ledger"), "access ledger")
    _check_screen_report(fw, sealed, str(request.get("screen_report_digest")),
                         str(request["eval_spec_digest"]), request["finalists"],
                         anchored=True, max_age_s=60.0)
    return request


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
