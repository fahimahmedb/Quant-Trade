"""Pre-registration and outcome-access gate for ``QUANT_FASTLANE_HPIT_V1``.

A protocol is canonical JSON (sorted keys, compact separators, UTF-8, no NaN).
Sealing writes one record holding the protocol and its sha256, atomically and
exactly once (temp file + hard link); a different protocol is refused.

Outcome access (prices, returns, market caps, delisting status) in any split
requires :func:`require_outcome_access`, which trusts nothing the caller built:

* it reloads the seal from disk, re-validates it as sealable and re-derives the
  split's price window from the sealed protocol;
* the seal must be anchored in git (:mod:`quant.fastlane.gitcheck`: exactly one
  commit ever touches it, complete clone, ancestor of HEAD, contained in a branch
  tip advertised by ``git ls-remote origin``, bytes equal);
* the vendor's delisting-class map and benchmark-source manifest must be
  committed the same way; the bound event table must match the sealed hash;
* holdout access additionally needs the committed, write-once
  ``research/fastlane/prereg/HOLDOUT_REQUEST.json`` (see
  :mod:`quant.fastlane.holdout`); the ``var/`` ledger is only a cache.

Grants carry an HMAC token keyed by the seal hash and a per-process secret
nonce, so a hand-built :class:`OutcomeAccessGrant` is refused by
:func:`verify_grant`, which again reloads the seal and consults the ledgers.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes

STATUS_DRAFT = "DRAFT_NOT_SEALED"
STATUS_FINAL = "FINAL_FOR_SEAL"
MAX_VARIANTS = 48
MAX_FINALISTS = 3
BOOTSTRAP_SEED = 20260924

# D5 splits (frozen). Values are inclusive calendar dates of available_after_date.
SPLITS: Mapping[str, tuple[date, date]] = {
    "discovery": (date(2006, 1, 1), date(2018, 12, 31)),
    "walk_forward": (date(2019, 1, 1), date(2021, 6, 30)),
    "holdout": (date(2021, 7, 1), date(2026, 6, 30)),
}

PREREG_DIR = ("prereg",)
VENDOR_DIR = ("vendor",)
DELISTING_MAP_NAME = "DELISTING_CLASS_MAP.json"
BENCHMARK_MANIFEST_NAME = "BENCHMARK_SOURCE.json"

# Every rule a sealable protocol must carry (dotted paths, non-empty).
REQUIRED_RULES = (
    "population.document_type", "population.rows", "population.security_title_include_regex",
    "population.security_title_exclude_regex", "population.footnote_exclusion_regex",
    "population.dedupe", "population.backdating_exclusion", "population.unfiltered_role",
    "timing.entry", "timing.calendar",
    "return_object.formula", "return_object.weights", "return_object.idle_cash",
    "return_object.annualized_alpha",
    "inference.primary_test", "inference.block_length_sessions", "inference.bootstrap_draws",
    "inference.bootstrap_seed", "inference.co_check", "inference.robustness",
    "multiplicity.M_declared", "multiplicity.dsr", "multiplicity.finalist_rule",
    "multiplicity.holdout",
    "constructor.slots", "constructor.C0_usd", "constructor.tie_break",
    "execution.missing_entry_bar", "execution.missing_exit_bar",
    "delisting.classes", "delisting.mapping_manifest",
    "benchmark.series", "benchmark.manifest", "benchmark.fallback",
    "robustness.ff5_umd_files",
    "outcomes.zero_finalists", "outcomes.inconclusive", "outcomes.no_go",
    "go_criterion.all_of", "frictions.stress", "frictions.untradeable_adv20_below_usd",
    "census_binding.events_sha256", "census_binding.events_relpath",
    "census_binding.grid_selection_disclosure", "variant_grid_rule.post_eligibility_recheck",
    "firewall.outcome_access", "governance.external_anchor", "governance.branch_protection",
    "governance.residual_risk", "inference.seed_robustness.role",
)
# D5 / lead-decision numbers: any deviation refuses the seal.
FROZEN_SPREAD_FLOORS = [
    {"adv_below_usd": 500_000.0, "floor_bps": 250.0},
    {"adv_below_usd": 2_000_000.0, "floor_bps": 120.0},
    {"adv_below_usd": 10_000_000.0, "floor_bps": 60.0},
    {"adv_below_usd": 50_000_000.0, "floor_bps": 30.0},
    {"adv_below_usd": None, "floor_bps": 10.0},
]
ROBUSTNESS_SEEDS = [BOOTSTRAP_SEED + i for i in range(1, 6)]
PINNED_VALUES = {
    "inference.block_length_sessions": 80,
    "inference.bootstrap_draws": 10_000,
    "inference.bootstrap_seed": BOOTSTRAP_SEED,
    "inference.co_check.kernel": "Bartlett",
    "inference.co_check.bandwidth_b": 0.1,
    "inference.seed_robustness.seeds": ROBUSTNESS_SEEDS,
    "inference.seed_robustness.gating": False,
    "benchmark.fallback": "NONE",
    "multiplicity.max_finalists": MAX_FINALISTS,
    "multiplicity.n_trials_rule": "max(M_declared, trial_ledger_evaluations)",
    "multiplicity.all_declared_need_discovery_trials": True,
    "go_criterion.alpha_min_annual": 0.03,
    "go_criterion.holm_family_alpha": 0.05,
    "go_criterion.dsr_min": 0.95,
    "outcomes.inconclusive_upper_bound_min_annual": 0.03,
    "outcomes.inconclusive_ci_level_one_sided": 0.95,
    "frictions.participation_cap_adv20": 0.001,
    "frictions.untradeable_adv20_below_usd": 100_000.0,
    "frictions.spread.adv20_bucket_floor_bps": FROZEN_SPREAD_FLOORS,
    "frictions.commission.per_share_usd": 0.0035,
    "frictions.commission.minimum_usd": 0.35,
    "frictions.impact.coefficient": 1.0,
    "frictions.delisting_classes.UNKNOWN": {"base": -0.30, "stress": -1.0},
    "frictions.delisting_classes.BANKRUPTCY_OR_CAUSE": {"base": -1.0, "stress": -1.0},
    "delisting.mapping_source": "VENDOR_DOCUMENTATION_ONLY",
    "governance.branch_protection_required": True,
    "governance.external_anchor_required": True,
}
DELISTING_CLASS_NAMES = ("BANKRUPTCY_OR_CAUSE", "CASH_ACQUISITION", "STOCK_MERGER", "UNKNOWN")


class PreregError(RuntimeError):
    pass


class PreregAlreadySealed(PreregError):
    """A different protocol is already sealed; sealing is write-once."""


class PreregNotSealed(PreregError):
    pass


class PreregTampered(PreregError):
    pass


class PreregInvalid(PreregError):
    pass


class OutcomeAccessRefused(PermissionError):
    pass


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def protocol_sha256(protocol: Mapping[str, Any]) -> str:
    return "sha256:" + sha256_bytes(canonical_json(protocol))


def split_of(day: date) -> str | None:
    for name, (start, end) in SPLITS.items():
        if start <= day <= end:
            return name
    return None


def sealed_path(fw: Firewall) -> Path:
    return fw.artifact(*PREREG_DIR, f"{LINEAGE_ID}_PREREG_SEALED.json")


def delisting_map_path(fw: Firewall) -> Path:
    return fw.artifact(*VENDOR_DIR, DELISTING_MAP_NAME)


def benchmark_manifest_path(fw: Firewall) -> Path:
    return fw.artifact(*VENDOR_DIR, BENCHMARK_MANIFEST_NAME)


def _get(obj: Mapping[str, Any], dotted: str) -> Any:
    node: Any = obj
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return None
        node = node[part]
    return node


def _same(actual: Any, expected: Any) -> bool:
    """Structural equality; numbers compare by value but bool is never a number."""
    if isinstance(expected, bool) or isinstance(actual, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return float(actual) == float(expected)
    if isinstance(expected, list):
        return (isinstance(actual, list) and len(actual) == len(expected)
                and all(_same(a, e) for a, e in zip(actual, expected)))
    if isinstance(expected, dict):
        return (isinstance(actual, dict) and set(actual) == set(expected)
                and all(_same(actual[k], expected[k]) for k in expected))
    return actual == expected


def _empty(value: Any) -> bool:
    return value is None or (isinstance(value, (str, list, dict, tuple)) and len(value) == 0)


def validate_protocol(protocol: Mapping[str, Any], *, for_seal: bool) -> None:
    if protocol.get("lineage") != LINEAGE_ID:
        raise PreregInvalid(f"protocol lineage must be {LINEAGE_ID}")
    status = protocol.get("status")
    if for_seal and status != STATUS_FINAL:
        raise PreregInvalid(
            f"protocol status is {status!r}; only {STATUS_FINAL!r} may be sealed "
            "(a draft must be finalized by an explicit owner/lead decision)")
    splits = protocol.get("splits") or {}
    for name, (start, end) in SPLITS.items():
        declared = splits.get(name) or {}
        if declared.get("start") != start.isoformat() or declared.get("end") != end.isoformat():
            raise PreregInvalid(f"split {name} must be {start}..{end} (D5 frozen)")
    variants = protocol.get("variants") or []
    if not 1 <= len(variants) <= MAX_VARIANTS:
        raise PreregInvalid(f"variant grid must hold 1..{MAX_VARIANTS} variants")
    ids = [v.get("variant_id") for v in variants]
    if len(set(ids)) != len(ids) or any(not i for i in ids):
        raise PreregInvalid("variant ids must be unique and non-empty")
    mult = protocol.get("multiplicity") or {}
    if int(mult.get("max_finalists", 0) or 0) > MAX_FINALISTS:
        raise PreregInvalid(f"at most {MAX_FINALISTS} finalists")
    if not for_seal:
        return
    if protocol.get("open_decisions") != []:
        raise PreregInvalid("open_decisions must be [] before sealing")
    from quant.fastlane.frictions import FrictionParams
    try:
        FrictionParams.from_protocol(protocol.get("frictions") or {})
    except Exception as exc:  # any malformed friction section blocks the seal
        raise PreregInvalid(f"frictions section invalid: {exc!r}") from exc
    if mult.get("M_declared") != len(variants):
        raise PreregInvalid(f"multiplicity.M_declared {mult.get('M_declared')} != "
                            f"{len(variants)} declared variants")
    seed = _get(protocol, "inference.bootstrap_seed")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise PreregInvalid("inference.bootstrap_seed must be an integer")
    for rule in REQUIRED_RULES:
        if _empty(_get(protocol, rule)):
            raise PreregInvalid(f"required rule {rule} is missing")
    for dotted, value in PINNED_VALUES.items():
        if not _same(_get(protocol, dotted), value):
            raise PreregInvalid(f"{dotted} must be {value!r}")
    for dotted in ("delisting.classes", "frictions.delisting_classes"):
        if sorted(_get(protocol, dotted) or {}) != list(DELISTING_CLASS_NAMES):
            raise PreregInvalid(f"{dotted} must hold exactly {DELISTING_CLASS_NAMES}")
    for name in SPLITS:
        start, end = price_window(protocol, name)
        if end < start:
            raise PreregInvalid(f"{name} price_window is empty")
    for name in ("discovery", "walk_forward"):
        _, end = price_window(protocol, name)
        if end > SPLITS[name][1]:
            raise PreregInvalid(f"{name} price_window ends {end} after the split end "
                                f"{SPLITS[name][1]}: holdout prices would be reachable")
    for v in variants:
        for key in ("census_family", "value_floor_usd", "horizon_sessions"):
            if _empty(v.get(key)) and v.get(key) != 0:
                raise PreregInvalid(f"variant {v.get('variant_id')} lacks {key}")


def seal_protocol(fw: Firewall, protocol: Mapping[str, Any], *,
                  sealed_at_utc: str | None = None) -> dict:
    validate_protocol(protocol, for_seal=True)
    digest = protocol_sha256(protocol)
    path = sealed_path(fw)
    if path.exists():
        existing = load_sealed(fw)
        if existing["protocol_sha256"] == digest:
            return existing
        raise PreregAlreadySealed(
            f"{path.name} already seals {existing['protocol_sha256']}; refusing to "
            f"overwrite with {digest}")
    record = {
        "lineage": LINEAGE_ID,
        "protocol_sha256": digest,
        "sealed_at_utc": sealed_at_utc or datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "protocol": protocol,
    }
    try:
        fw.create_exclusive(path, canonical_json(record) + b"\n")
    except FileExistsError as exc:
        raise PreregAlreadySealed(f"{path.name} was sealed concurrently") from exc
    return record


def load_sealed(fw: Firewall) -> dict:
    path = sealed_path(fw)
    if not path.exists():
        raise PreregNotSealed(f"no sealed pre-registration at {path}")
    try:
        record = fw.read_json(path)
    except (ValueError, UnicodeDecodeError) as exc:
        raise PreregTampered(f"sealed file {path.name} is not valid JSON") from exc
    if not isinstance(record, dict):
        raise PreregTampered("sealed file is not a JSON object")
    recomputed = protocol_sha256(record.get("protocol") or {})
    if recomputed != record.get("protocol_sha256"):
        raise PreregTampered(
            f"sealed protocol hash {record.get('protocol_sha256')} != recomputed {recomputed}")
    return record


def price_window(protocol: Mapping[str, Any], split: str) -> tuple[date, date]:
    declared = ((protocol.get("splits") or {}).get(split) or {}).get("price_window") or {}
    try:
        return (date.fromisoformat(declared["start"]), date.fromisoformat(declared["end"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise PreregInvalid(f"split {split} declares no valid price_window") from exc


# --- grants -------------------------------------------------------------------------

_PROCESS_NONCE = secrets.token_bytes(32)
_ISSUED: dict[tuple, "OutcomeAccessGrant"] = {}


@dataclass(frozen=True)
class OutcomeAccessGrant:
    """Proof that outcome data may be read for one split under one sealed prereg.

    Only :func:`require_outcome_access` mints valid tokens; anything else is
    refused by :func:`verify_grant`.
    """

    lineage: str
    split: str
    prereg_sha256: str
    price_window_start: date
    price_window_end: date
    holdout_request_id: str | None
    repo_root: str
    token: str

    def covers(self, start: date, end: date) -> bool:
        return self.price_window_start <= start <= end <= self.price_window_end


def _token(lineage: str, split: str, prereg_sha256: str, start: date, end: date,
           request_id: str | None, repo_root: str) -> str:
    message = canonical_json([lineage, split, prereg_sha256, start.isoformat(), end.isoformat(),
                              request_id, repo_root])
    return hmac.new(_PROCESS_NONCE + prereg_sha256.encode("utf-8"), message,
                    hashlib.sha256).hexdigest()


def _load_or_refuse(fw: Firewall) -> dict:
    try:
        return load_sealed(fw)
    except PreregError as exc:
        raise OutcomeAccessRefused(f"outcome access refused: {exc}") from exc


def _bound_events_ok(fw: Firewall, protocol: Mapping[str, Any]) -> None:
    binding = protocol.get("census_binding") or {}
    rel, expected = binding.get("events_relpath"), binding.get("events_sha256")
    if not rel or not expected:
        raise OutcomeAccessRefused("sealed protocol binds no event table")
    try:
        path = fw.guard(fw.repo_root / rel, write=False)
    except PermissionError as exc:
        raise OutcomeAccessRefused(f"bound event table path refused: {exc}") from exc
    if not path.exists():
        raise OutcomeAccessRefused(f"bound event table {rel} is missing")
    actual = fw.sha256_file(path)
    if actual != str(expected).replace("sha256:", ""):
        raise OutcomeAccessRefused(f"event table {rel} sha256 {actual} != sealed {expected}")


def _vendor_manifests_ok(fw: Firewall) -> None:
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    from quant.fastlane.prices import validate_benchmark_manifest, validate_delisting_map
    for path, validator in ((delisting_map_path(fw), validate_delisting_map),
                            (benchmark_manifest_path(fw), validate_benchmark_manifest)):
        if not path.exists():
            raise OutcomeAccessRefused(f"vendor manifest {path.name} is not committed")
        try:
            verify_committed(fw.repo_root, path, write_once=True, max_age_s=60.0)
            validator(fw.read_json(path))
        except (GitCheckFailed, ValueError) as exc:
            raise OutcomeAccessRefused(f"vendor manifest {path.name}: {exc}") from exc


# Remote tips older than this may be reused by verify_grant (each vendor call);
# require_outcome_access (each grant) always queries the remote afresh.
GRANT_RECHECK_TIPS_MAX_AGE_S = 300.0


def _anchor_seal(fw: Firewall, *, max_age_s: float) -> str:
    from quant.fastlane.gitcheck import GitCheckFailed, verify_committed
    try:
        return verify_committed(fw.repo_root, sealed_path(fw), write_once=True,
                                max_age_s=max_age_s).commit
    except GitCheckFailed as exc:
        raise OutcomeAccessRefused(f"seal is not anchored in git: {exc}") from exc


def require_outcome_access(fw: Firewall, split: str, expected_prereg_sha256: str, *,
                           holdout_request_id: str | None = None,
                           holdout_variants: Sequence[str] | None = None,
                           eval_spec_digest: str | None = None) -> OutcomeAccessGrant:
    """Gate every outcome read. Raises OutcomeAccessRefused unless every check passes."""
    from quant.fastlane.holdout import (HoldoutLedger, LedgerCorrupted, TrialLedger,
                                        verify_holdout_request)
    if split not in SPLITS:
        raise OutcomeAccessRefused(f"unknown split {split!r}")
    sealed = _load_or_refuse(fw)
    if sealed["protocol_sha256"] != expected_prereg_sha256:
        raise OutcomeAccessRefused(
            f"expected prereg {expected_prereg_sha256} but sealed is {sealed['protocol_sha256']}")
    protocol = sealed["protocol"]
    try:
        validate_protocol(protocol, for_seal=True)
    except PreregInvalid as exc:
        raise OutcomeAccessRefused(f"sealed protocol is not sealable: {exc}") from exc
    seal_commit = _anchor_seal(fw, max_age_s=0.0)
    _vendor_manifests_ok(fw)
    _bound_events_ok(fw, protocol)
    try:
        TrialLedger(fw).records()
    except LedgerCorrupted as exc:
        raise OutcomeAccessRefused(f"trial ledger: {exc}") from exc
    start, end = price_window(protocol, split)
    request_id = None
    if split == "holdout":
        request = verify_holdout_request(fw, sealed, holdout_request_id, holdout_variants,
                                         eval_spec_digest, seal_commit=seal_commit)
        try:
            HoldoutLedger(fw).sync(request)
        except LedgerCorrupted as exc:
            raise OutcomeAccessRefused(f"holdout cache: {exc}") from exc
        request_id = request["request_id"]
    key = (str(fw.repo_root), split, sealed["protocol_sha256"], request_id)
    issued = _ISSUED.get(key)
    if issued is not None:
        return issued
    root = str(fw.repo_root)
    grant = OutcomeAccessGrant(LINEAGE_ID, split, sealed["protocol_sha256"], start, end,
                               request_id, root,
                               _token(LINEAGE_ID, split, sealed["protocol_sha256"], start, end,
                                      request_id, root))
    _ISSUED[key] = grant
    return grant


def verify_grant(grant: Any, start: date, end: date) -> None:
    """Re-check a grant against the disk and the ledgers before any outcome read."""
    from quant.fastlane.holdout import HoldoutLedger, LedgerCorrupted, verify_committed_request
    if type(grant) is not OutcomeAccessGrant:
        raise OutcomeAccessRefused("outcome data needs an OutcomeAccessGrant from a sealed prereg")
    expected = _token(grant.lineage, grant.split, grant.prereg_sha256, grant.price_window_start,
                      grant.price_window_end, grant.holdout_request_id, grant.repo_root)
    if not hmac.compare_digest(expected, str(grant.token)):
        raise OutcomeAccessRefused("grant was not issued by require_outcome_access in this process")
    fw = Firewall(Path(grant.repo_root))
    sealed = _load_or_refuse(fw)
    if sealed["protocol_sha256"] != grant.prereg_sha256:
        raise OutcomeAccessRefused("the seal on disk no longer matches the grant")
    if grant.split not in SPLITS:
        raise OutcomeAccessRefused(f"unknown split {grant.split!r}")
    if price_window(sealed["protocol"], grant.split) != (grant.price_window_start,
                                                         grant.price_window_end):
        raise OutcomeAccessRefused("grant window differs from the sealed protocol")
    seal_commit = _anchor_seal(fw, max_age_s=GRANT_RECHECK_TIPS_MAX_AGE_S)
    if grant.split == "holdout":
        try:
            request = verify_committed_request(fw, sealed, seal_commit,
                                               max_age_s=GRANT_RECHECK_TIPS_MAX_AGE_S)
            if request.get("request_id") != grant.holdout_request_id:
                raise OutcomeAccessRefused("committed holdout request does not match the grant")
            HoldoutLedger(fw).sync(request)
        except LedgerCorrupted as exc:
            raise OutcomeAccessRefused(f"holdout ledger: {exc}") from exc
    if not grant.covers(start, end):
        raise OutcomeAccessRefused(
            f"{start}..{end} is outside the {grant.split} price window "
            f"{grant.price_window_start}..{grant.price_window_end}")
