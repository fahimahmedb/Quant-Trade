"""Point-in-time issuer, security, ticker and listing identity contracts.

Ticker text is never an identity key. Resolution always carries an ``as_of``
instant, returns ambiguity explicitly, and preserves the evidence hashes that
support the mapping so downstream joins can be audited and replayed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Iterable


RESOLUTION_STATUSES = ("RESOLVED", "NOT_FOUND", "AMBIGUOUS")


def parse_pit_instant(value: str) -> datetime:
    candidate = value.strip()
    if not candidate:
        raise ValueError("empty point-in-time value")
    if "T" not in candidate:
        parsed_date = date.fromisoformat(candidate)
        return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _validate_interval(valid_from: str, valid_to: str | None) -> None:
    start = parse_pit_instant(valid_from)
    if valid_to is not None and parse_pit_instant(valid_to) <= start:
        raise ValueError(f"invalid half-open interval [{valid_from}, {valid_to})")


def _contains(valid_from: str, valid_to: str | None, as_of: str) -> bool:
    point = parse_pit_instant(as_of)
    return parse_pit_instant(valid_from) <= point and (
        valid_to is None or point < parse_pit_instant(valid_to))


def validate_evidence_hash(value: str) -> None:
    if not value.startswith("sha256:"):
        raise ValueError(f"identity lineage must use sha256 evidence hashes: {value!r}")
    digest = value.split(":", 1)[1]
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"invalid sha256 evidence hash: {value!r}")


def _validate_lineage(values: tuple[str, ...]) -> None:
    if not values:
        raise ValueError("identity assertions require at least one evidence hash")
    for value in values:
        validate_evidence_hash(value)


@dataclass(frozen=True)
class IssuerIdentity:
    """Stable company/issuer identity over a point-in-time lifetime."""

    issuer_id: str
    valid_from: str
    valid_to: str | None
    identifiers: dict[str, str]
    evidence_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.issuer_id:
            raise ValueError("issuer_id is required")
        _validate_interval(self.valid_from, self.valid_to)
        _validate_lineage(self.evidence_hashes)

    def contains(self, as_of: str) -> bool:
        return _contains(self.valid_from, self.valid_to, as_of)


@dataclass(frozen=True)
class IssuerNameInterval:
    """A legal/display name assertion valid only for a half-open time interval."""

    issuer_id: str
    name: str
    valid_from: str
    valid_to: str | None
    evidence_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("issuer name is required")
        _validate_interval(self.valid_from, self.valid_to)
        _validate_lineage(self.evidence_hashes)

    def contains(self, as_of: str) -> bool:
        return _contains(self.valid_from, self.valid_to, as_of)


@dataclass(frozen=True)
class SecurityIdentity:
    """Stable security/share-class identity; ticker is intentionally absent."""

    security_id: str
    issuer_id: str
    security_type: str
    valid_from: str
    valid_to: str | None
    identifiers: dict[str, str]
    evidence_hashes: tuple[str, ...]
    share_class: str | None = None
    currency: str | None = None

    def __post_init__(self) -> None:
        if not self.security_id or not self.issuer_id or not self.security_type:
            raise ValueError("security_id, issuer_id and security_type are required")
        _validate_interval(self.valid_from, self.valid_to)
        _validate_lineage(self.evidence_hashes)

    def contains(self, as_of: str) -> bool:
        return _contains(self.valid_from, self.valid_to, as_of)


@dataclass(frozen=True)
class TickerInterval:
    """Ticker assertion for one security and, when known, one venue."""

    security_id: str
    ticker: str
    valid_from: str
    valid_to: str | None
    evidence_hashes: tuple[str, ...]
    venue: str | None = None

    def __post_init__(self) -> None:
        if not self.security_id or not self.ticker:
            raise ValueError("security_id and ticker are required")
        _validate_interval(self.valid_from, self.valid_to)
        _validate_lineage(self.evidence_hashes)

    def contains(self, as_of: str) -> bool:
        return _contains(self.valid_from, self.valid_to, as_of)


@dataclass(frozen=True)
class ListingInterval:
    """Venue/listing assertion for one security over a half-open interval."""

    security_id: str
    venue: str
    valid_from: str
    valid_to: str | None
    evidence_hashes: tuple[str, ...]
    listing_id: str | None = None
    status: str = "LISTED"

    def __post_init__(self) -> None:
        if not self.security_id or not self.venue:
            raise ValueError("security_id and venue are required")
        _validate_interval(self.valid_from, self.valid_to)
        _validate_lineage(self.evidence_hashes)

    def contains(self, as_of: str) -> bool:
        return _contains(self.valid_from, self.valid_to, as_of)


@dataclass(frozen=True)
class IdentityResolution:
    """Explicit PIT ticker resolution; ambiguity is a first-class result."""

    status: str
    ticker: str
    as_of: str
    venue: str | None
    candidate_security_ids: tuple[str, ...] = ()
    lineage_hashes: tuple[str, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status not in RESOLUTION_STATUSES:
            raise ValueError(f"unknown resolution status: {self.status}")

    @property
    def security_id(self) -> str | None:
        if self.status != "RESOLVED" or len(self.candidate_security_ids) != 1:
            return None
        return self.candidate_security_ids[0]


@dataclass(frozen=True)
class NameResolution:
    status: str
    issuer_id: str
    as_of: str
    names: tuple[str, ...] = ()
    lineage_hashes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in RESOLUTION_STATUSES:
            raise ValueError(f"unknown resolution status: {self.status}")

    @property
    def name(self) -> str | None:
        return self.names[0] if self.status == "RESOLVED" and len(self.names) == 1 else None


class IdentityBook:
    """In-memory generic PIT resolver over explicit identity contracts.

    Persistence belongs to the evidence layer or a future identity repository;
    this object deliberately contains no vendor-specific lookup logic.
    """

    def __init__(
        self,
        *,
        issuers: Iterable[IssuerIdentity],
        securities: Iterable[SecurityIdentity],
        names: Iterable[IssuerNameInterval] = (),
        tickers: Iterable[TickerInterval] = (),
        listings: Iterable[ListingInterval] = (),
    ):
        self.issuers = tuple(issuers)
        self.securities = tuple(securities)
        self.names = tuple(names)
        self.tickers = tuple(tickers)
        self.listings = tuple(listings)
        self._issuer_ids = {value.issuer_id for value in self.issuers}
        self._security_ids = {value.security_id for value in self.securities}
        if len(self._issuer_ids) != len(self.issuers):
            raise ValueError("issuer_id must identify exactly one IssuerIdentity contract")
        if len(self._security_ids) != len(self.securities):
            raise ValueError("security_id must identify exactly one SecurityIdentity contract")
        for security in self.securities:
            if security.issuer_id not in self._issuer_ids:
                raise ValueError(
                    f"security {security.security_id} references unknown issuer {security.issuer_id}")
        for name in self.names:
            if name.issuer_id not in self._issuer_ids:
                raise ValueError(f"name interval references unknown issuer {name.issuer_id}")
        for ticker in self.tickers:
            if ticker.security_id not in self._security_ids:
                raise ValueError(f"ticker interval references unknown security {ticker.security_id}")
        for listing in self.listings:
            if listing.security_id not in self._security_ids:
                raise ValueError(f"listing interval references unknown security {listing.security_id}")

    def has_issuer_id(self, issuer_id: str) -> bool:
        return issuer_id in self._issuer_ids

    def has_security_id(self, security_id: str) -> bool:
        return security_id in self._security_ids

    def issuer_at(self, issuer_id: str, as_of: str) -> IssuerIdentity | None:
        for issuer in self.issuers:
            if issuer.issuer_id == issuer_id and issuer.contains(as_of):
                return issuer
        return None

    def security_at(self, security_id: str, as_of: str) -> SecurityIdentity | None:
        for security in self.securities:
            if security.security_id == security_id and security.contains(as_of):
                return security
        return None

    def resolve_name(self, issuer_id: str, as_of: str) -> NameResolution:
        parse_pit_instant(as_of)
        issuer = self.issuer_at(issuer_id, as_of)
        if issuer is None:
            return NameResolution("NOT_FOUND", issuer_id, as_of)
        matches = [value for value in self.names
                   if value.issuer_id == issuer_id and value.contains(as_of)]
        names = tuple(sorted({value.name for value in matches}))
        lineage_values = set(issuer.evidence_hashes)
        lineage_values.update(item for value in matches for item in value.evidence_hashes)
        lineage = tuple(sorted(lineage_values))
        if not names:
            return NameResolution("NOT_FOUND", issuer_id, as_of, lineage_hashes=lineage)
        if len(names) > 1:
            return NameResolution("AMBIGUOUS", issuer_id, as_of, names, lineage)
        return NameResolution("RESOLVED", issuer_id, as_of, names, lineage)

    def resolve_ticker(
        self,
        ticker: str,
        *,
        as_of: str,
        venue: str | None = None,
    ) -> IdentityResolution:
        """Resolve ticker text without ever treating ticker alone as identity."""
        parse_pit_instant(as_of)
        ticker_matches = [
            value for value in self.tickers
            if value.ticker == ticker and value.contains(as_of)
            and (venue is None or value.venue == venue)
        ]
        candidates: dict[str, set[str]] = {}
        for ticker_interval in ticker_matches:
            security = self.security_at(ticker_interval.security_id, as_of)
            if security is None:
                continue
            issuer = self.issuer_at(security.issuer_id, as_of)
            if issuer is None:
                continue
            lineage = set(ticker_interval.evidence_hashes)
            lineage.update(security.evidence_hashes)
            lineage.update(issuer.evidence_hashes)
            if venue is not None:
                listings = [
                    value for value in self.listings
                    if value.security_id == security.security_id
                    and value.venue == venue and value.contains(as_of)
                ]
                if not listings:
                    continue
                for listing in listings:
                    lineage.update(listing.evidence_hashes)
            candidates.setdefault(security.security_id, set()).update(lineage)

        ids = tuple(sorted(candidates))
        lineage_hashes = tuple(sorted({item for values in candidates.values() for item in values}))
        if not ids:
            return IdentityResolution(
                "NOT_FOUND", ticker, as_of, venue, reason="no PIT-valid identity mapping")
        if len(ids) > 1:
            return IdentityResolution(
                "AMBIGUOUS", ticker, as_of, venue, ids, lineage_hashes,
                reason="multiple PIT-valid security identities share this ticker mapping")
        return IdentityResolution("RESOLVED", ticker, as_of, venue, ids, lineage_hashes)
