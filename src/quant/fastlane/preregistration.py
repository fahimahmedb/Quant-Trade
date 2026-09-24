"""Pre-registration for ``QUANT_FASTLANE_HPIT_V1``.

A protocol is canonical JSON (sorted keys, compact separators, UTF-8, no NaN).
Sealing writes one record holding the protocol and its sha256; it is written
exactly once and never overwritten (an identical re-seal replays the existing
record, a different protocol is refused).

Any outcome access (prices, returns, market caps, delisting status) in any
split requires a sealed pre-registration whose hash matches the caller's
expected hash. Holdout access additionally consumes the one-look ledger
(:mod:`quant.fastlane.holdout`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes

STATUS_DRAFT = "DRAFT_NOT_SEALED"
STATUS_FINAL = "FINAL_FOR_SEAL"
MAX_VARIANTS = 48
MAX_FINALISTS = 3

# D5 splits (frozen). Values are inclusive calendar dates of available_after_date.
SPLITS: Mapping[str, tuple[date, date]] = {
    "discovery": (date(2006, 1, 1), date(2018, 12, 31)),
    "walk_forward": (date(2019, 1, 1), date(2021, 6, 30)),
    "holdout": (date(2021, 7, 1), date(2026, 6, 30)),
}


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
    return fw.artifact("prereg", f"{LINEAGE_ID}_PREREG_SEALED.json")


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
    if int(mult.get("max_finalists", 0)) > MAX_FINALISTS:
        raise PreregInvalid(f"at most {MAX_FINALISTS} finalists")


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
    record = fw.read_json(path)
    recomputed = protocol_sha256(record.get("protocol") or {})
    if recomputed != record.get("protocol_sha256"):
        raise PreregTampered(
            f"sealed protocol hash {record.get('protocol_sha256')} != recomputed {recomputed}")
    return record


@dataclass(frozen=True)
class OutcomeAccessGrant:
    """Proof that outcome data may be read for one split under one sealed prereg."""

    lineage: str
    split: str
    prereg_sha256: str
    price_window_start: date
    price_window_end: date
    holdout_request_id: str | None = None

    def covers(self, start: date, end: date) -> bool:
        return self.price_window_start <= start <= end <= self.price_window_end


def price_window(protocol: Mapping[str, Any], split: str) -> tuple[date, date]:
    declared = ((protocol.get("splits") or {}).get(split) or {}).get("price_window") or {}
    try:
        return (date.fromisoformat(declared["start"]), date.fromisoformat(declared["end"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise PreregInvalid(f"split {split} declares no valid price_window") from exc


def require_outcome_access(fw: Firewall, split: str, expected_prereg_sha256: str, *,
                           holdout_request_id: str | None = None,
                           holdout_variants: Sequence[str] | None = None) -> OutcomeAccessGrant:
    """Gate every outcome read. Raises unless a matching sealed prereg exists."""
    if split not in SPLITS:
        raise OutcomeAccessRefused(f"unknown split {split!r}")
    try:
        sealed = load_sealed(fw)
    except PreregError as exc:
        raise OutcomeAccessRefused(f"outcome access refused: {exc}") from exc
    if sealed["protocol_sha256"] != expected_prereg_sha256:
        raise OutcomeAccessRefused(
            f"expected prereg {expected_prereg_sha256} but sealed is {sealed['protocol_sha256']}")
    start, end = price_window(sealed["protocol"], split)
    request_id = None
    if split == "holdout":
        if not holdout_request_id or not holdout_variants:
            raise OutcomeAccessRefused("holdout access needs a request_id and <=3 finalists")
        from quant.fastlane.holdout import HoldoutLedger
        record = HoldoutLedger(fw).request(holdout_request_id, sealed["protocol_sha256"],
                                           list(holdout_variants))
        request_id = record["request_id"]
    return OutcomeAccessGrant(LINEAGE_ID, split, sealed["protocol_sha256"], start, end,
                              request_id)
