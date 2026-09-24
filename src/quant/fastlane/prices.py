"""Price-vendor interface for ``QUANT_FASTLANE_HPIT_V1``.

No price vendor is licensed yet (D5: the purchase is an owner action). This
module fixes the contract a vendor must satisfy and the evidence label its
attestation implies; it performs no network access.

* Every outcome-bearing call takes an :class:`OutcomeAccessGrant`, which only
  :func:`quant.fastlane.preregistration.require_outcome_access` can issue after
  a sealed pre-registration, and the requested date range must fall inside the
  grant's split price window.
* Entry sessions come from the *vendor's* calendar
  (:func:`first_session_strictly_after`); no exchange calendar is invented.
* A vendor without delisted securities yields
  ``DEVELOPMENT_SURVIVORSHIP_BIASED`` evidence, which can never produce GO.
"""

from __future__ import annotations

import bisect
import os
from dataclasses import dataclass
from datetime import date
from typing import Mapping, Protocol, Sequence, runtime_checkable

from quant.fastlane.preregistration import OutcomeAccessGrant, OutcomeAccessRefused

LABEL_SURVIVORSHIP_BIASED = "DEVELOPMENT_SURVIVORSHIP_BIASED"
LABEL_PIT_INCOMPLETE = "DEVELOPMENT_PIT_INCOMPLETE"
LABEL_HISTORICAL_PIT_CANDIDATE = "HISTORICAL_PIT_VALIDATION_CANDIDATE"

ACCEPTED_CORPORATE_ACTIONS = frozenset({"RAW_PRICES_PLUS_ACTIONS_LEDGER"})

VERDICT_GO = "GO"
VERDICT_NO_GO = "NO_GO"
VERDICT_NOT_GO_ELIGIBLE = "NOT_GO_ELIGIBLE"


class VendorUnavailable(RuntimeError):
    """The vendor is not configured/licensed in this environment."""


@dataclass(frozen=True)
class VendorAttestation:
    vendor_id: str
    includes_delisted: bool
    corporate_actions: str          # e.g. RAW_PRICES_PLUS_ACTIONS_LEDGER | ADJUSTED_ONLY | NONE
    pit_security_mapping: bool      # CIK -> security identity as of each date
    license_note: str
    verified: bool = False          # claimed by docs (False) vs verified on licensed data

    @property
    def evidence_label(self) -> str:
        if not self.includes_delisted:
            return LABEL_SURVIVORSHIP_BIASED
        if (not self.pit_security_mapping
                or self.corporate_actions not in ACCEPTED_CORPORATE_ACTIONS
                or not self.verified):
            return LABEL_PIT_INCOMPLETE
        return LABEL_HISTORICAL_PIT_CANDIDATE

    @property
    def go_eligible(self) -> bool:
        return self.evidence_label == LABEL_HISTORICAL_PIT_CANDIDATE


def resolve_verdict(attestation: VendorAttestation, criteria_met: bool) -> dict:
    """Apply the evidence label to a GO/NO-GO computation.

    Survivorship-biased (or otherwise PIT-incomplete) evidence can never yield
    GO, however favourable the numbers.
    """
    label = attestation.evidence_label
    if not attestation.go_eligible:
        verdict = VERDICT_NOT_GO_ELIGIBLE
    else:
        verdict = VERDICT_GO if criteria_met else VERDICT_NO_GO
    return {"verdict": verdict, "evidence_label": label,
            "vendor_id": attestation.vendor_id, "criteria_met": bool(criteria_met)}


@dataclass(frozen=True)
class DailyBar:
    security_id: str
    session: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class CorporateAction:
    security_id: str
    ex_date: date
    kind: str            # SPLIT | CASH_DIVIDEND | DELISTING | ...
    value: float | None


@dataclass(frozen=True)
class SecurityMapping:
    cik: str
    security_id: str
    ticker: str
    valid_from: date
    valid_to: date | None


@runtime_checkable
class PriceVendor(Protocol):
    vendor_id: str

    def attestation(self) -> VendorAttestation: ...

    def sessions(self, start: date, end: date, *, grant: OutcomeAccessGrant) -> list[date]: ...

    def daily_bars(self, security_id: str, start: date, end: date, *,
                   grant: OutcomeAccessGrant) -> list[DailyBar]: ...

    def corporate_actions(self, security_id: str, start: date, end: date, *,
                          grant: OutcomeAccessGrant) -> list[CorporateAction]: ...

    def security_mappings(self, cik: str, *, grant: OutcomeAccessGrant) -> list[SecurityMapping]: ...


def check_grant(grant: OutcomeAccessGrant, start: date, end: date) -> None:
    if not isinstance(grant, OutcomeAccessGrant):
        raise OutcomeAccessRefused("outcome data needs an OutcomeAccessGrant from a sealed prereg")
    if not grant.covers(start, end):
        raise OutcomeAccessRefused(
            f"{start}..{end} is outside the {grant.split} price window "
            f"{grant.price_window_start}..{grant.price_window_end}")


def first_session_strictly_after(available_after: date, sessions: Sequence[date]) -> date | None:
    """Entry session: the first vendor session strictly after ``available_after``.

    ``sessions`` must be the vendor's sorted session list. Returns None when the
    calendar does not extend past the date (unresolved, never rolled forward).
    """
    if any(b <= a for a, b in zip(sessions, sessions[1:])):
        raise ValueError("vendor sessions must be strictly increasing")
    i = bisect.bisect_right(list(sessions), available_after)
    return sessions[i] if i < len(sessions) else None


class SharadarVendor:
    """Skeleton for Sharadar (Nasdaq Data Link: SEP, ACTIONS, TICKERS with CIK).

    Requires ``NASDAQ_DATA_LINK_API_KEY``; without it construction raises
    :class:`VendorUnavailable`. No network code is wired in weeks 0-2: data
    calls validate the grant and then raise ``VendorUnavailable`` until the
    owner licenses the feed and the attestation is verified on real data.
    """

    vendor_id = "SHARADAR_NASDAQ_DATA_LINK"
    API_KEY_ENV = "NASDAQ_DATA_LINK_API_KEY"

    def __init__(self, env: Mapping[str, str] | None = None) -> None:
        source = os.environ if env is None else env
        key = (source.get(self.API_KEY_ENV) or "").strip()
        if not key:
            raise VendorUnavailable(
                f"{self.API_KEY_ENV} is not set; Sharadar is not licensed in this environment")
        self._key_present = True

    def attestation(self) -> VendorAttestation:
        # Claims from vendor documentation, NOT yet verified on licensed data.
        return VendorAttestation(
            vendor_id=self.vendor_id,
            includes_delisted=True,
            corporate_actions="RAW_PRICES_PLUS_ACTIONS_LEDGER",
            pit_security_mapping=True,
            license_note="Nasdaq Data Link Sharadar SEP/ACTIONS/TICKERS; subscription is an "
                         "owner action; redistribution terms to be checked at purchase",
            verified=False,
        )

    def _not_wired(self, what: str):
        raise VendorUnavailable(f"Sharadar {what} is not wired yet (weeks 0-2 skeleton)")

    def sessions(self, start, end, *, grant):
        check_grant(grant, start, end)
        self._not_wired("sessions")

    def daily_bars(self, security_id, start, end, *, grant):
        check_grant(grant, start, end)
        self._not_wired("daily_bars")

    def corporate_actions(self, security_id, start, end, *, grant):
        check_grant(grant, start, end)
        self._not_wired("corporate_actions")

    def security_mappings(self, cik, *, grant):
        check_grant(grant, grant.price_window_start, grant.price_window_end)
        self._not_wired("security_mappings")
