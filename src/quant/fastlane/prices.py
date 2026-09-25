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
* Delisting treatment is vendor-agnostic by class; the adapter commits a
  vendor-code -> class map (:func:`validate_delisting_map`) and the SPY total-
  return source (:func:`validate_benchmark_manifest`) before any grant.
* Outcomes: GO, NO_GO, INCONCLUSIVE (GO fails but the one-sided 95 % upper
  bound reaches the 3 %/yr bar), NOT_GO_ELIGIBLE; zero finalists is NO_GO with
  the holdout unopened. Only GO may ever authorize (paper) sizing.
"""

from __future__ import annotations

import bisect
import os
from dataclasses import dataclass
from datetime import date
from typing import Mapping, Protocol, Sequence, runtime_checkable

from quant.fastlane.firewall import LINEAGE_ID
from quant.fastlane.preregistration import (OutcomeAccessGrant, OutcomeAccessRefused,
                                            verify_grant)

LABEL_SURVIVORSHIP_BIASED = "DEVELOPMENT_SURVIVORSHIP_BIASED"
LABEL_PIT_INCOMPLETE = "DEVELOPMENT_PIT_INCOMPLETE"
LABEL_HISTORICAL_PIT_CANDIDATE = "HISTORICAL_PIT_VALIDATION_CANDIDATE"

ACCEPTED_CORPORATE_ACTIONS = frozenset({"RAW_PRICES_PLUS_ACTIONS_LEDGER"})

VERDICT_GO = "GO"
VERDICT_NO_GO = "NO_GO"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE"
VERDICT_NOT_GO_ELIGIBLE = "NOT_GO_ELIGIBLE"
GO_ALPHA_BAR = 0.03

DELISTING_CLASSES = ("CASH_ACQUISITION", "STOCK_MERGER", "BANKRUPTCY_OR_CAUSE", "UNKNOWN")


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


def resolve_verdict(attestation: VendorAttestation, criteria_met: bool, *,
                    ci_upper_annual: float | None = None,
                    n_finalists: int | None = None) -> dict:
    """Apply the evidence label and the pinned outcome rules.

    * zero finalists -> NO_GO, holdout unopened;
    * survivorship-biased or PIT-incomplete evidence -> NOT_GO_ELIGIBLE, never GO;
    * GO criteria met -> GO;
    * otherwise INCONCLUSIVE if the one-sided 95 % upper bound of annualized net
      alpha is >= 3 %/yr, else NO_GO. Neither INCONCLUSIVE nor NO_GO authorizes sizing.
    """
    label = attestation.evidence_label
    holdout = "OPENED"
    if n_finalists == 0:
        verdict, holdout = VERDICT_NO_GO, "UNOPENED"
    elif not attestation.go_eligible:
        verdict = VERDICT_NOT_GO_ELIGIBLE
    elif criteria_met:
        verdict = VERDICT_GO
    elif ci_upper_annual is not None and ci_upper_annual >= GO_ALPHA_BAR:
        verdict = VERDICT_INCONCLUSIVE
    else:
        verdict = VERDICT_NO_GO
    return {"verdict": verdict, "evidence_label": label, "vendor_id": attestation.vendor_id,
            "criteria_met": bool(criteria_met), "holdout": holdout,
            "sizing_authorized": verdict == VERDICT_GO}


def validate_delisting_map(manifest: Mapping) -> dict:
    """The adapter's committed vendor-code -> delisting-class map.

    It must be derived only from vendor documentation (never from observed
    returns): ``derivation`` = VENDOR_DOCUMENTATION_ONLY and ``source`` cites the
    documentation URL and its retrieval date.
    """
    if not isinstance(manifest, Mapping) or manifest.get("lineage") != LINEAGE_ID:
        raise ValueError("delisting map must name the fast-lane lineage")
    if not manifest.get("vendor_id"):
        raise ValueError("delisting map must name the vendor")
    if manifest.get("derivation") != "VENDOR_DOCUMENTATION_ONLY":
        raise ValueError("delisting map must be derived from vendor documentation only")
    source = manifest.get("source") or {}
    url = str(source.get("documentation_url") or "")
    if not url.startswith("https://"):
        raise ValueError("delisting map must cite the vendor documentation URL")
    try:
        date.fromisoformat(str(source.get("retrieved_on")))
    except ValueError as exc:
        raise ValueError("delisting map must record the documentation retrieval date") from exc
    mapping = manifest.get("mapping")
    if not isinstance(mapping, Mapping) or not mapping:
        raise ValueError("delisting map is empty")
    bad = {code: cls for code, cls in mapping.items() if cls not in DELISTING_CLASSES}
    if bad:
        raise ValueError(f"unknown delisting classes {bad}")
    return dict(mapping)


def validate_benchmark_manifest(manifest: Mapping) -> dict:
    """SPY total return from the licensed vendor; no fallback source."""
    if not isinstance(manifest, Mapping) or manifest.get("lineage") != LINEAGE_ID:
        raise ValueError("benchmark manifest must name the fast-lane lineage")
    expected = {"series": "SPY", "return_type": "TOTAL_RETURN", "fallback": "NONE"}
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"benchmark manifest {key} must be {value!r}")
    if not manifest.get("vendor_id") or not manifest.get("dataset"):
        raise ValueError("benchmark manifest must name the vendor and dataset")
    return dict(manifest)


@dataclass(frozen=True)
class DailyBar:
    security_id: str
    session: date
    open: float
    high: float
    low: float
    close: float
    volume: float


ACTION_SPLIT = "SPLIT"                  # value = new shares per old share (> 0)
ACTION_CASH_DIVIDEND = "CASH_DIVIDEND"  # value = cash (or cash-equivalent) per share held
ACTION_DELISTING = "DELISTING"          # code = vendor delisting code (DELISTING_CLASS_MAP)


@dataclass(frozen=True)
class CorporateAction:
    """One vendor action. The adapter converts every distribution into SPLIT or
    CASH_DIVIDEND terms; other kinds are counted by the evaluation, never applied."""

    security_id: str
    ex_date: date
    kind: str            # SPLIT | CASH_DIVIDEND | DELISTING | ...
    value: float | None
    code: str | None = None


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

    def benchmark_total_returns(self, start: date, end: date, *,
                                grant: OutcomeAccessGrant) -> Mapping[date, float]:
        """SPY daily total return (close to close, dividends reinvested) per vendor
        session in [start, end], from the dataset named in the committed
        benchmark manifest; no fallback source."""
        ...


def check_grant(grant: OutcomeAccessGrant, start: date, end: date) -> None:
    """Never trust the caller's grant: re-verify token, seal, window and ledgers."""
    verify_grant(grant, start, end)


def clip_mappings(mappings: Sequence[SecurityMapping],
                  grant: OutcomeAccessGrant) -> list[SecurityMapping]:
    """Clip security-mapping validity to the grant window (no later identity leaks)."""
    out = []
    for m in mappings:
        if m.valid_from > grant.price_window_end:
            continue
        end = grant.price_window_end if m.valid_to is None else min(m.valid_to,
                                                                    grant.price_window_end)
        out.append(SecurityMapping(m.cik, m.security_id, m.ticker, m.valid_from, end))
    return out


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

    def benchmark_total_returns(self, start, end, *, grant):
        check_grant(grant, start, end)
        self._not_wired("benchmark_total_returns")

    def _fetch_mappings(self, cik):
        self._not_wired("security_mappings")

    def security_mappings(self, cik, *, grant):
        if type(grant) is not OutcomeAccessGrant:
            raise OutcomeAccessRefused("outcome data needs an OutcomeAccessGrant")
        check_grant(grant, grant.price_window_start, grant.price_window_end)
        return clip_mappings(self._fetch_mappings(cik), grant)
