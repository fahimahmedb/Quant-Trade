"""Deterministic SEC Form-4 census primitives for the V2-A data-semantics gate.

This module deliberately contains no return, P&L, alpha, Sharpe or performance
logic.  The certified population is constructed only from official SEC ownership
filings plus a pinned regular-session calendar.  Security/price-path coverage is
an optional downstream diagnostic and cannot alter event formation.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
import urllib.parse
import zipfile
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable, Iterator, Sequence

START_DATE = date(2020, 1, 1)
END_DATE = date(2026, 6, 30)
PARSER_VERSION = "sec-form4-census-v2a/3"
#: SEC Fair Access requires automated traffic to declare a reachable contact
#: address. Two empirically verified rules govern what SEC's edge accepts, and
#: both were established by probing the official 2020Q1 URL directly:
#:
#: 1. The declaration must carry a contact email, or the request is refused with
#:    HTTP 403 whose body reads "Request Rate Threshold Exceeded". That message
#:    is misleading: it is a compliance rejection, not a rate limit.
#: 2. The declaration must not contain ``github.com`` in any form. A
#:    ``user@users.noreply.github.com`` address and a trailing repository URL are
#:    both refused, while the same request with an ordinary mailbox succeeds.
#:
#: There is deliberately no default identity. A committed default would either
#: embed a personal contact address in a public repository or invent an
#: unreachable one, and an unreachable contact is not Fair-Access compliance. The
#: operator declares the identity through the environment instead.
SEC_USER_AGENT_ENV = "SEC_USER_AGENT"
#: Substrings empirically refused by SEC's edge inside a User-Agent.
SEC_REFUSED_UA_TOKENS = ("github.com",)


class SecIdentityError(RuntimeError):
    """The declared SEC identity is missing or not Fair-Access compliant."""


def sec_identity_problem(user_agent: str) -> str | None:
    """Why this User-Agent would be refused, or None when it is acceptable."""
    if not user_agent.strip():
        return f"no SEC identity declared; set {SEC_USER_AGENT_ENV}"
    token = next((part for part in user_agent.split() if "@" in part), "")
    local, _, domain = token.partition("@")
    if not local or "." not in domain:
        return ("SEC Fair Access requires a reachable contact email in the "
                f"User-Agent; got {user_agent!r}")
    for refused in SEC_REFUSED_UA_TOKENS:
        if refused in user_agent.lower():
            return (f"SEC refuses any User-Agent containing {refused!r} "
                    f"(verified against the official 2020Q1 URL); got {user_agent!r}")
    return None


def sec_identity_is_compliant(user_agent: str) -> bool:
    return sec_identity_problem(user_agent) is None


def sec_user_agent() -> str:
    """The single source of truth for this project's declared SEC identity.

    Every SEC request -- connectivity preflight, quarterly ZIP acquisition and
    EDGAR acceptance headers alike -- resolves its identity here. When a
    preflight and the acquisition it is meant to validate derive their identity
    separately, the preflight can pass while the acquisition is refused, which is
    precisely the failure this function exists to prevent.
    """
    declared = os.environ.get(SEC_USER_AGENT_ENV, "").strip()
    problem = sec_identity_problem(declared)
    if problem:
        raise SecIdentityError(problem)
    return declared


def sec_request_headers(user_agent: str | None = None) -> dict[str, str]:
    """The complete HTTP identity used for every SEC request.

    Returned as one mapping so a caller cannot accidentally send a different
    header set from the one the acquisition path uses.
    """
    return {
        "User-Agent": user_agent or sec_user_agent(),
        "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8",
        "Accept-Encoding": "identity",
    }
OLD_SEC_ZIP_ROOT = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets"
NEW_SEC_ZIP_ROOT = "https://www.sec.gov/files/datastandardsinnovation/data/insider-transactions-data-sets"
SEC_ARCHIVE_ROOT = "https://www.sec.gov/Archives/edgar/data"
YAHOO_CHART_ROOT = "https://query1.finance.yahoo.com/v8/finance/chart"

REASON_CODES = {
    "FORM_AMENDMENT",
    "NOT_P_ACQUIRED",
    "TRANSACTION_DATE_OUT_OF_SCOPE",
    "QUALIFIED_ROLE_FALSE",
    "OWNER_ID_UNRESOLVED",
    "JOINT_OWNER_AMBIGUOUS",
    "DUPLICATE_ACCESSION",
    "DUPLICATE_ACCESSION_CONFLICT",
    "DUPLICATE_REPORTING_OWNER_ROW",
    "DUPLICATE_REPORTING_OWNER_ROW_CONFLICT",
    "DUPLICATE_TRANSACTION_ROW",
    "DUPLICATE_TRANSACTION_ROW_CONFLICT",
    "MALFORMED_SOURCE_ROW",
    "SUBMISSION_ROW_MISSING",
    "ISSUER_ID_UNRESOLVED",
    "ACCEPTANCE_TIMESTAMP_UNRESOLVED",
    "TICKER_CHANGED",
    "TICKER_REUSED_OR_AMBIGUOUS",
    "NONSTANDARD_SECURITY",
    "CIK_SYMBOL_CONFLICT",
    "DELISTED_OR_NO_HISTORY",
    "CORPORATE_ACTION_UNRESOLVED",
    "PRICE_SOURCE_UNAVAILABLE",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_hash(payload: Any, prefix: str) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return prefix + hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:24]


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def normalize_cik(value: Any) -> str | None:
    raw = _clean(value)
    if not raw or not raw.isdigit():
        return None
    return raw.zfill(10)


def parse_sec_date(value: str) -> date:
    raw = _clean(value)
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unsupported SEC date: {value!r}")


def iso_or_none(value: str) -> str | None:
    raw = _clean(value)
    if not raw:
        return None
    return parse_sec_date(raw).isoformat()


def source_url(year: int, quarter: int) -> str:
    """Primary canonical URL for a quarter. See ``source_url_candidates``."""
    return source_url_candidates(year, quarter)[0]


def source_url_candidates(year: int, quarter: int) -> list[str]:
    """Both canonical SEC locations for a quarter, most likely first.

    SEC serves these archives from two official roots and has migrated the
    boundary over time: as verified against the live service, 2026Q1 is still
    published under the legacy root while 2026Q2 is published under the newer
    one. A hardcoded year boundary therefore requests the wrong root for at
    least one in-scope quarter and receives a 404.

    Both entries are official SEC roots, so trying the second is not a mirror or
    a substitute source; it is the same publisher. The root that actually served
    each quarter is recorded in provenance.
    """
    name = f"{year}q{quarter}_form345.zip"
    roots = ([NEW_SEC_ZIP_ROOT, OLD_SEC_ZIP_ROOT] if (year, quarter) >= (2026, 2)
             else [OLD_SEC_ZIP_ROOT, NEW_SEC_ZIP_ROOT])
    return [f"{root}/{name}" for root in roots]


def quarter_specs() -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for year in range(2020, 2027):
        last_q = 2 if year == 2026 else 4
        out.extend((year, q) for q in range(1, last_q + 1))
    return out


@dataclass(frozen=True)
class SourceRecord:
    period: str
    source_url: str
    sha256: str
    bytes: int
    retrieved_at: str
    parser_version: str = PARSER_VERSION
    local_path: str | None = None


@dataclass(frozen=True)
class NormalizedCandidateRecord:
    accession: str
    row_id: str
    source_period: str
    document_type: str
    issuer_cik: str | None
    issuer_trading_symbol: str
    owner_cik: str | None
    reporting_owner_ciks: tuple[str, ...]
    reporting_owner_rows: int
    unresolved_owner_cik_rows: int
    is_director: bool | None
    is_officer: bool | None
    transaction_date: str | None
    transaction_code: str
    acquired_disposed_code: str
    status: str
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PurchaseObservation:
    observation_id: str
    issuer_cik: str
    owner_cik: str
    transaction_date: str
    issuer_symbols: tuple[str, ...]
    accessions: tuple[str, ...]
    source_rows: int


@dataclass(frozen=True)
class Form4Event:
    event_id: str
    issuer_cik: str
    formation_transaction_date: str
    window_start_date: str
    owner_ciks: tuple[str, ...]
    constituent_observation_ids: tuple[str, ...]
    accessions: tuple[str, ...]
    session_distance: int
    acceptance_timestamps: tuple[tuple[str, str], ...] = ()
    event_time: str | None = None
    event_time_timezone: str = "America/New_York"
    event_time_status: str = "PENDING"


@dataclass(frozen=True)
class LossLedgerRecord:
    record_id: str
    event_id: str | None
    accession: str | None
    issuer_cik: str | None
    owner_cik: str | None
    status: str
    reason_codes: tuple[str, ...]
    detail: str = ""


@dataclass
class CensusBuild:
    submissions: dict[str, "SubmissionRecord"]
    owners_by_accession: dict[str, list["ReportingOwnerRecord"]]
    transaction_rows: list[dict[str, str]]
    observations: list[PurchaseObservation]
    events: list[Form4Event]
    losses: list[LossLedgerRecord]
    waterfall: dict[str, int]
    diagnostics: dict[str, Any]
    normalized_candidates: list[NormalizedCandidateRecord] = field(default_factory=list)


class SessionCalendar:
    """Pinned U.S. regular-session dates; distance is sessions crossed.

    session_distance(a, b) counts regular sessions s with a < s <= b when a<=b.
    Thus same-date distance is 0, adjacent regular sessions are distance 1, and
    exactly 10 qualifies while 11 does not.  Off-session transaction dates are
    handled by the same interval rule, avoiding ad-hoc weekend/holiday shifts.
    """

    def __init__(self, sessions: Sequence[str], source: str, version: str):
        parsed = sorted({date.fromisoformat(s) for s in sessions})
        if not parsed:
            raise ValueError("empty session calendar")
        self.sessions = parsed
        self.source = source
        self.version = version

    @classmethod
    def from_csv(cls, path: Path) -> "SessionCalendar":
        rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
        if not rows:
            raise ValueError("calendar file is empty")
        source = rows[0].get("source", "")
        version = rows[0].get("version", "")
        return cls([r["session"] for r in rows], source, version)

    def distance(self, earlier: str | date, later: str | date) -> int:
        a = date.fromisoformat(earlier) if isinstance(earlier, str) else earlier
        b = date.fromisoformat(later) if isinstance(later, str) else later
        if b < a:
            raise ValueError("session distance requires chronological dates")
        # bisect without importing another dependency.
        import bisect
        return bisect.bisect_right(self.sessions, b) - bisect.bisect_right(self.sessions, a)


def _member_name(names: Sequence[str], token: str) -> str:
    token = token.upper()
    matches = [n for n in names if token in n.upper()]
    if not matches:
        raise KeyError(f"zip missing member containing {token}; members={list(names)!r}")
    # Prefer .tsv/.txt and shortest canonical-looking path deterministically.
    matches.sort(key=lambda n: (0 if n.lower().endswith((".tsv", ".txt")) else 1, len(n), n))
    return matches[0]


#: Primary key SEC documents for each raw table used by the certified census.
TABLE_KEY_COLUMNS: dict[str, tuple[str, ...]] = {
    "SUBMISSION": ("ACCESSION_NUMBER",),
    "REPORTINGOWNER": ("ACCESSION_NUMBER", "RPTOWNERCIK"),
    "NONDERIV_TRANS": ("ACCESSION_NUMBER", "NONDERIV_TRANS_SK"),
}

#: The exact columns the certified population reads.  Declaring them turns a
#: renamed, dropped or reordered SEC column into a hard failure instead of an
#: empty string that would silently reclassify filings (an absent DOCUMENT_TYPE
#: would make every filing "not a Form 4", an absent TRANS_CODE would make every
#: row "not a purchase") while the waterfall still looked plausible.
TABLE_REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "SUBMISSION": ("ACCESSION_NUMBER", "DOCUMENT_TYPE", "ISSUERCIK",
                   "ISSUERTRADINGSYMBOL", "FILING_DATE"),
    "REPORTINGOWNER": ("ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP"),
    "NONDERIV_TRANS": ("ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "TRANS_DATE",
                       "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD"),
}


def _intern_or_none(value: str | None) -> str | None:
    """Intern repeated identity strings; 26 quarters share very few distinct ones."""
    return None if value is None else sys.intern(value)


class CensusSchemaError(RuntimeError):
    """A raw SEC table does not satisfy the declared certified schema."""


class CensusConservationError(RuntimeError):
    """Raw source rows are not exhaustively accounted for by the waterfall."""


@dataclass(frozen=True)
class RawTableRead:
    """One raw SEC table read under the declared schema, with row conservation.

    ``data_lines`` counts physical data records in the member.  Every one of
    them is either parsed into ``rows`` or counted in ``malformed_lines``; the
    reader refuses to return unless those two account for all of them.
    """

    token: str
    member: str
    columns: tuple[str, ...]
    rows: list[dict[str, str]]
    data_lines: int
    malformed_lines: int
    malformed_accessions: tuple[str, ...]
    malformed_details: tuple[str, ...]


@dataclass(frozen=True)
class QuarterTables:
    period: str
    submissions: RawTableRead
    owners: RawTableRead
    transactions: RawTableRead


def _read_tsv(zf: zipfile.ZipFile, token: str) -> RawTableRead:
    member = _member_name(zf.namelist(), token)
    text = zf.read(member).decode("utf-8-sig", errors="strict")
    reader = csv.reader(io.StringIO(text), delimiter="\t")
    try:
        header = next(reader)
    except StopIteration:
        raise CensusSchemaError(f"{member}: table has no header row") from None
    columns = tuple(_clean(c).upper() for c in header)
    duplicated = sorted({c for c in columns if columns.count(c) > 1})
    if duplicated:
        raise CensusSchemaError(f"{member}: duplicated column name(s) {duplicated}")
    missing = [c for c in TABLE_REQUIRED_COLUMNS[token] if c not in columns]
    if missing:
        raise CensusSchemaError(
            f"{member}: missing required column(s) {missing}; declared columns={list(columns)}")
    acc_index = columns.index("ACCESSION_NUMBER")
    width = len(columns)
    rows: list[dict[str, str]] = []
    malformed_accessions: list[str] = []
    details: list[str] = []
    data_lines = 0
    malformed_lines = 0
    for lineno, fields in enumerate(reader, start=2):
        data_lines += 1
        if len(fields) != width:
            malformed_lines += 1
            recovered = _clean(fields[acc_index]) if len(fields) > acc_index else ""
            if not recovered:
                # A malformed line whose accession cannot even be read has an
                # unbounded effect on the certified population: it could belong
                # to any filing.  Fail the build rather than publish a census
                # with content that cannot be attributed or excluded.
                raise CensusSchemaError(
                    f"{member} line {lineno}: malformed row with no recoverable "
                    f"ACCESSION_NUMBER ({len(fields)} field(s), header declares {width})")
            malformed_accessions.append(recovered)
            if len(details) < 8:
                details.append(
                    f"{member} line {lineno}: {len(fields)} field(s), header declares {width}")
            continue
        rows.append({columns[i]: _clean(fields[i]) for i in range(width)})
    if len(rows) + malformed_lines != data_lines:
        raise CensusConservationError(
            f"{member}: {data_lines} data line(s) but {len(rows)} parsed + "
            f"{malformed_lines} malformed")
    return RawTableRead(
        token=token, member=member, columns=columns, rows=rows, data_lines=data_lines,
        malformed_lines=malformed_lines,
        malformed_accessions=tuple(sorted(set(malformed_accessions))),
        malformed_details=tuple(details),
    )


def parse_quarter_zip(data: bytes, period: str) -> QuarterTables:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return QuarterTables(
            period=period,
            submissions=_read_tsv(zf, "SUBMISSION"),
            owners=_read_tsv(zf, "REPORTINGOWNER"),
            transactions=_read_tsv(zf, "NONDERIV_TRANS"),
        )


def _read_quarter_table(data: bytes, token: str) -> RawTableRead:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        return _read_tsv(zf, token)


class KeyConflictResolver:
    """Order-independent primary-key resolution for one raw SEC table.

    The outcome for a key is a function of the *set* of distinct row contents
    carrying that key, never of which physical row the reader happened to see
    first:

    * one distinct content, one occurrence  -> canonical row
    * one distinct content, N occurrences   -> canonical row + N-1 benign copies
    * two or more distinct contents         -> CONFLICT

    A conflict is fail-closed: the key is removed from the certified population
    and ledgered.  "First line wins" is never an outcome, because the census
    cannot silently prefer one of two irreconcilable official rows.  Detecting
    a conflict by comparing each occurrence against one arbitrary reference is
    itself order-free: a key whose contents are all equal never produces an
    inequality in any order, and a key with two distinct contents produces one
    in every order.
    """

    __slots__ = ("name", "_fingerprint", "duplicate_occurrences", "conflicting",
                 "duplicate_periods")

    def __init__(self, name: str) -> None:
        self.name = name
        self._fingerprint: dict[str, bytes] = {}
        #: extra physical rows beyond the first, per duplicated key only
        self.duplicate_occurrences: Counter[str] = Counter()
        self.duplicate_periods: dict[str, list[str]] = {}
        self.conflicting: set[str] = set()

    @staticmethod
    def fingerprint(row: dict[str, str]) -> bytes:
        payload = "\x1f".join(f"{k}\x1e{row[k]}" for k in sorted(row))
        return hashlib.sha256(payload.encode("utf-8")).digest()[:16]

    def observe(self, key: str, row: dict[str, str], period: str) -> bool:
        """Record one physical row; return True only for a key's first row."""
        fingerprint = self.fingerprint(row)
        known = self._fingerprint.get(key)
        if known is None:
            self._fingerprint[key] = fingerprint
            return True
        self.duplicate_occurrences[key] += 1
        self.duplicate_periods.setdefault(key, []).append(period)
        if known != fingerprint:
            self.conflicting.add(key)
        return False

    @property
    def duplicated_keys(self) -> set[str]:
        return set(self.duplicate_occurrences)

    def rows_for(self, keys: Iterable[str]) -> int:
        """Total physical rows carried by the given keys."""
        return sum(1 + self.duplicate_occurrences.get(k, 0) for k in keys)

    def release(self) -> None:
        """Drop the per-key fingerprint index once resolution is complete."""
        self._fingerprint = {}


@dataclass(frozen=True, slots=True)
class SubmissionRecord:
    """Only the submission fields the certified population is allowed to read."""

    accession: str
    source_period: str
    document_type: str
    issuer_cik: str | None
    issuer_symbol: str
    filing_date: str | None


@dataclass(frozen=True, slots=True)
class ReportingOwnerRecord:
    """Only the reporting-owner fields the certified population may read.

    ``owner_cik`` is ``None`` when the authoritative CIK is absent or not a
    number; identity is never inferred from the name.
    """

    accession: str
    source_period: str
    owner_cik: str | None
    is_director: bool
    is_officer: bool


def _role_flags(relationship: str) -> tuple[bool, bool]:
    value = re.sub(r"[^A-Z]", "", _clean(relationship).upper())
    return "DIRECTOR" in value, "OFFICER" in value


def _role_qualified(relationship: str) -> bool:
    is_director, is_officer = _role_flags(relationship)
    return is_director or is_officer


#: (label, raw total key, mutually exclusive disposition keys).  Every raw line
#: read from an official table must land in exactly one bucket.
CONSERVATION_IDENTITIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("submission_rows", "submission_rows", (
        "submission_rows_malformed",
        "submission_rows_blank_accession",
        "submission_rows_key_conflicting",
        "submission_rows_duplicate_identical",
        "submission_rows_excluded_accession",
        "original_form4_filings",
        "form4a_filings",
        "submission_rows_other_form_type",
    )),
    ("reporting_owner_rows", "reporting_owner_rows", (
        "reporting_owner_rows_malformed",
        "reporting_owner_rows_blank_accession",
        "reporting_owner_rows_key_conflicting",
        "reporting_owner_rows_duplicate_identical",
        "reporting_owner_rows_without_submission",
        "reporting_owner_rows_excluded_accession",
        "canonical_reporting_owner_rows",
    )),
    ("nonderivative_rows", "nonderivative_rows", (
        "nonderivative_rows_malformed",
        "nonderivative_rows_blank_accession",
        "nonderivative_rows_key_conflicting",
        "nonderivative_rows_duplicate_identical",
        "nonderivative_rows_without_submission",
        "nonderivative_rows_excluded_accession",
        "canonical_nonderivative_rows",
    )),
    ("canonical_nonderivative_rows", "canonical_nonderivative_rows", (
        "original_form4_nonderivative_rows",
        "form4a_nonderivative_rows",
        "nonderivative_rows_other_form_type",
    )),
    ("original_form4_nonderivative_rows", "original_form4_nonderivative_rows", (
        "original_form4_not_p_acquired_rows",
        "original_form4_p_acquired_rows",
    )),
    ("form4a_nonderivative_rows", "form4a_nonderivative_rows", (
        "form4a_not_p_acquired_rows",
        "form4a_p_acquired_rows",
    )),
    ("original_form4_p_acquired_rows", "original_form4_p_acquired_rows", (
        "p_acquired_rows_date_out_of_scope",
        "p_acquired_rows_in_scope",
    )),
    ("p_acquired_rows_in_scope", "p_acquired_rows_in_scope", (
        "owner_id_unresolved_rows",
        "resolvable_owner_cik_rows",
    )),
    ("resolvable_owner_cik_rows", "resolvable_owner_cik_rows", (
        "joint_owner_ambiguous_rows",
        "single_owner_unambiguous_rows",
    )),
    ("single_owner_unambiguous_rows", "single_owner_unambiguous_rows", (
        "unqualified_role_rows",
        "qualified_officer_director_rows",
    )),
    ("qualified_officer_director_rows", "qualified_officer_director_rows", (
        "issuer_id_unresolved_rows",
        "resolvable_issuer_cik_rows",
    )),
    ("normalized_candidate_rows", "normalized_candidate_rows", (
        "original_form4_p_acquired_rows",
        "form4a_p_acquired_rows",
    )),
)


def _assert_conservation(waterfall: dict[str, int] | Counter) -> list[dict[str, Any]]:
    """Fail closed unless every raw row is accounted for exactly once."""
    report: list[dict[str, Any]] = []
    for label, total_key, parts in CONSERVATION_IDENTITIES:
        total = int(waterfall.get(total_key, 0))
        accounted = sum(int(waterfall.get(part, 0)) for part in parts)
        report.append({
            "identity": label, "total_key": total_key, "total": total,
            "accounted": accounted, "parts": {p: int(waterfall.get(p, 0)) for p in parts},
        })
        if accounted != total:
            detail = ", ".join(f"{p}={int(waterfall.get(p, 0))}" for p in parts)
            raise CensusConservationError(
                f"raw row conservation violated for {label}: {total_key}={total} "
                f"but dispositions sum to {accounted} ({detail})")
    return report


def build_census(quarter_payloads: Sequence[tuple[str, bytes]], calendar: SessionCalendar) -> CensusBuild:
    """Build the price-independent economic formation population.

    The build is two-phase on purpose.  Phase one resolves the *identity* layer
    (submissions and reporting owners) across every quarter, so the complete
    universe of canonical filings and their conflicts is fixed before a single
    transaction row is normalized.  Phase two then normalizes transactions
    against that frozen universe.  Nothing in the certified output can therefore
    depend on the physical order in which quarters, members or lines are read.

    Only the declared columns are read, only P/acquired candidate rows are
    retained row-by-row, and every raw line is accounted for in the waterfall.
    """
    losses: list[LossLedgerRecord] = []
    waterfall: Counter[str] = Counter()
    submissions: dict[str, SubmissionRecord] = {}
    owner_records: list[ReportingOwnerRecord] = []
    normalized_candidates: list[NormalizedCandidateRecord] = []
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

    payloads = sorted(quarter_payloads, key=lambda item: item[0])
    waterfall["source_quarters"] = len(payloads)

    submission_keys = KeyConflictResolver("SUBMISSION")
    owner_keys = KeyConflictResolver("REPORTINGOWNER")
    transaction_keys = KeyConflictResolver("NONDERIV_TRANS")
    malformed_accessions: dict[str, set[str]] = defaultdict(set)

    # ---- phase one: identity layer over every quarter -----------------------
    for period, payload in payloads:
        tables = parse_quarter_zip(payload, period)

        waterfall["submission_rows"] += tables.submissions.data_lines
        waterfall["submission_rows_malformed"] += tables.submissions.malformed_lines
        waterfall["reporting_owner_rows"] += tables.owners.data_lines
        waterfall["reporting_owner_rows_malformed"] += tables.owners.malformed_lines
        waterfall["nonderivative_rows"] += tables.transactions.data_lines
        waterfall["nonderivative_rows_malformed"] += tables.transactions.malformed_lines
        for table in (tables.submissions, tables.owners, tables.transactions):
            for accession in table.malformed_accessions:
                malformed_accessions[accession].add(table.token)

        for row in tables.submissions.rows:
            accession = _clean(row.get("ACCESSION_NUMBER"))
            if not accession:
                waterfall["submission_rows_blank_accession"] += 1
                continue
            if not submission_keys.observe(accession, row, period):
                continue
            try:
                filing_date = iso_or_none(row.get("FILING_DATE", ""))
            except ValueError:
                filing_date = None
                waterfall["submission_rows_unparseable_filing_date"] += 1
            submissions[accession] = SubmissionRecord(
                accession=accession,
                source_period=sys.intern(period),
                document_type=sys.intern(_clean(row.get("DOCUMENT_TYPE")).upper()),
                issuer_cik=_intern_or_none(normalize_cik(row.get("ISSUERCIK"))),
                issuer_symbol=sys.intern(_clean(row.get("ISSUERTRADINGSYMBOL")).upper()),
                filing_date=_intern_or_none(filing_date),
            )

        for row in tables.owners.rows:
            accession = _clean(row.get("ACCESSION_NUMBER"))
            if not accession:
                waterfall["reporting_owner_rows_blank_accession"] += 1
                continue
            owner_cik = _intern_or_none(normalize_cik(row.get("RPTOWNERCIK")))
            # SEC documents (ACCESSION_NUMBER, RPTOWNERCIK) as the primary key.
            # Relationship text is never part of the identity key: adding it
            # could turn one owner with conflicting duplicate metadata into two
            # apparent owners.  Rows with no authoritative CIK have no usable
            # key at all, so they are keyed by their own content instead: two
            # genuinely different unidentified filers must stay two unresolved
            # rows, not collapse into one apparent duplicate.
            if owner_cik is None:
                key = f"{accession}|?|{KeyConflictResolver.fingerprint(row).hex()}"
            else:
                key = f"{accession}|{owner_cik}"
            if not owner_keys.observe(key, row, period):
                continue
            is_director, is_officer = _role_flags(row.get("RPTOWNER_RELATIONSHIP", ""))
            owner_records.append(ReportingOwnerRecord(
                accession=accession, source_period=sys.intern(period),
                owner_cik=owner_cik, is_director=is_director, is_officer=is_officer,
            ))

        for row in tables.transactions.rows:
            accession = _clean(row.get("ACCESSION_NUMBER"))
            if not accession:
                waterfall["nonderivative_rows_blank_accession"] += 1
                continue
            transaction_keys.observe(
                f"{accession}|{_clean(row.get('NONDERIV_TRANS_SK'))}", row, period)

    submission_keys.release()
    owner_keys.release()
    transaction_keys.release()

    # ---- fail-closed exclusion set -----------------------------------------
    excluded: dict[str, set[str]] = defaultdict(set)
    for accession in submission_keys.conflicting:
        excluded[accession].add("DUPLICATE_ACCESSION_CONFLICT")
    for key in owner_keys.conflicting:
        excluded[key.split("|", 1)[0]].add("DUPLICATE_REPORTING_OWNER_ROW_CONFLICT")
    for key in transaction_keys.conflicting:
        excluded[key.split("|", 1)[0]].add("DUPLICATE_TRANSACTION_ROW_CONFLICT")
    for accession in malformed_accessions:
        excluded[accession].add("MALFORMED_SOURCE_ROW")

    excluded_submission_rows = 0
    for accession, reasons in sorted(excluded.items()):
        record = submissions.get(accession)
        losses.append(LossLedgerRecord(
            record_id=_stable_hash(["excluded-accession", accession, sorted(reasons)], "LOSS-"),
            event_id=None, accession=accession,
            issuer_cik=record.issuer_cik if record else None, owner_cik=None,
            status="EXCLUDED", reason_codes=tuple(sorted(reasons)),
            detail=("official source rows for this accession are irreconcilable or "
                    "malformed; the whole filing is excluded from the certified "
                    "population rather than resolved by physical row order"),
        ))
        waterfall["fail_closed_excluded_accessions"] += 1
        # The row a first-line-wins reader would have kept is discarded here:
        # a conflicted key contributes nothing to the certified population.
        if record is not None and accession not in submission_keys.conflicting:
            excluded_submission_rows += 1
        submissions.pop(accession, None)
    waterfall["submission_rows_excluded_accession"] = excluded_submission_rows

    # Benign duplicates are recorded but change nothing: every occurrence of the
    # key carried byte-identical content.
    for resolver, label in ((submission_keys, "DUPLICATE_ACCESSION"),
                            (owner_keys, "DUPLICATE_REPORTING_OWNER_ROW"),
                            (transaction_keys, "DUPLICATE_TRANSACTION_ROW")):
        for key in sorted(resolver.duplicated_keys - resolver.conflicting):
            accession = key.split("|", 1)[0]
            periods = sorted(set(resolver.duplicate_periods.get(key, [])))
            losses.append(LossLedgerRecord(
                record_id=_stable_hash(["duplicate", resolver.name, key, periods], "LOSS-"),
                event_id=None, accession=accession,
                issuer_cik=(submissions[accession].issuer_cik if accession in submissions else None),
                owner_cik=None, status="DIAGNOSTIC", reason_codes=(label,),
                detail=(f"{resolver.duplicate_occurrences[key]} identical copy/copies of "
                        f"{resolver.name} key {key!r} in period(s) {periods}; content is "
                        "byte-identical so the certified population is unchanged"),
            ))

    waterfall["submission_rows_key_conflicting"] = submission_keys.rows_for(submission_keys.conflicting)
    waterfall["submission_rows_duplicate_identical"] = sum(
        submission_keys.duplicate_occurrences[k]
        for k in submission_keys.duplicated_keys - submission_keys.conflicting)
    waterfall["reporting_owner_rows_key_conflicting"] = owner_keys.rows_for(owner_keys.conflicting)
    waterfall["reporting_owner_rows_duplicate_identical"] = sum(
        owner_keys.duplicate_occurrences[k]
        for k in owner_keys.duplicated_keys - owner_keys.conflicting)
    waterfall["nonderivative_rows_key_conflicting"] = transaction_keys.rows_for(transaction_keys.conflicting)
    waterfall["nonderivative_rows_duplicate_identical"] = sum(
        transaction_keys.duplicate_occurrences[k]
        for k in transaction_keys.duplicated_keys - transaction_keys.conflicting)

    owners_by_accession: dict[str, list[ReportingOwnerRecord]] = defaultdict(list)
    orphan_owner_accessions: set[str] = set()
    for record in owner_records:
        # Rows of a conflicting owner key are already accounted for as
        # conflicting rows; the first-seen row a physical-order reader would
        # have kept is discarded here rather than counted twice.
        if (record.owner_cik is not None
                and f"{record.accession}|{record.owner_cik}" in owner_keys.conflicting):
            continue
        if record.accession not in submissions:
            if record.accession in excluded:
                waterfall["reporting_owner_rows_excluded_accession"] += 1
            else:
                waterfall["reporting_owner_rows_without_submission"] += 1
                orphan_owner_accessions.add(record.accession)
            continue
        owners_by_accession[record.accession].append(record)
        waterfall["canonical_reporting_owner_rows"] += 1
    owner_records.clear()

    original_accessions = {a for a, s in submissions.items() if s.document_type == "4"}
    amendment_accessions = {a for a, s in submissions.items() if s.document_type == "4/A"}
    waterfall["original_form4_filings"] = len(original_accessions)
    waterfall["form4a_filings"] = len(amendment_accessions)
    waterfall["submission_rows_other_form_type"] = (
        len(submissions) - len(original_accessions) - len(amendment_accessions))

    # ---- phase two: transactions against the frozen identity universe -------
    transaction_duplicates = transaction_keys.duplicated_keys - transaction_keys.conflicting
    emitted_duplicates: set[str] = set()
    orphan_transaction_accessions: set[str] = set()
    for period, payload in payloads:
        table = _read_quarter_table(payload, "NONDERIV_TRANS")
        for row in table.rows:
            acc = _clean(row.get("ACCESSION_NUMBER"))
            if not acc:
                continue
            sk = _clean(row.get("NONDERIV_TRANS_SK"))
            key = f"{acc}|{sk}"
            if key in transaction_keys.conflicting:
                continue
            if key in transaction_duplicates:
                if key in emitted_duplicates:
                    continue
                emitted_duplicates.add(key)
            sub = submissions.get(acc)
            if sub is None:
                if acc in excluded:
                    waterfall["nonderivative_rows_excluded_accession"] += 1
                else:
                    waterfall["nonderivative_rows_without_submission"] += 1
                    orphan_transaction_accessions.add(acc)
                continue
            waterfall["canonical_nonderivative_rows"] += 1

            form = sub.document_type
            if form == "4":
                waterfall["original_form4_nonderivative_rows"] += 1
            elif form == "4/A":
                waterfall["form4a_nonderivative_rows"] += 1
            else:
                waterfall["nonderivative_rows_other_form_type"] += 1
                continue

            code = _clean(row.get("TRANS_CODE")).upper()
            acquired = _clean(row.get("TRANS_ACQUIRED_DISP_CD")).upper()
            if not (code == "P" and acquired == "A"):
                if form == "4":
                    waterfall["original_form4_not_p_acquired_rows"] += 1
                else:
                    waterfall["form4a_not_p_acquired_rows"] += 1
                continue

            if form == "4":
                waterfall["original_form4_p_acquired_rows"] += 1
            else:
                waterfall["form4a_p_acquired_rows"] += 1

            issuer_cik = sub.issuer_cik
            symbol = sub.issuer_symbol
            owners = owners_by_accession.get(acc, [])
            unresolved_owner_rows = sum(o.owner_cik is None for o in owners)
            owner_ciks = tuple(sorted({o.owner_cik for o in owners if o.owner_cik is not None}))
            # A filing with one valid owner CIK plus one missing/invalid owner CIK is
            # not a single-owner filing.  Certified identity may never be inferred
            # from the surviving row.  Treat any unresolved reporting-owner key as
            # an identity failure before joint/single-owner classification.
            single_owner = owner_ciks[0] if unresolved_owner_rows == 0 and len(owner_ciks) == 1 else None
            owner_rows = [o for o in owners if single_owner and o.owner_cik == single_owner]
            is_director = any(o.is_director for o in owner_rows) if single_owner else None
            is_officer = any(o.is_officer for o in owner_rows) if single_owner else None

            tx_date_iso: str | None = None
            try:
                tx_date = parse_sec_date(row.get("TRANS_DATE", ""))
                tx_date_iso = tx_date.isoformat()
            except ValueError:
                tx_date = None

            base_candidate = dict(
                accession=acc, row_id=sk, source_period=period, document_type=form,
                issuer_cik=issuer_cik, issuer_trading_symbol=symbol,
                owner_cik=single_owner, reporting_owner_ciks=owner_ciks,
                reporting_owner_rows=len(owners), unresolved_owner_cik_rows=unresolved_owner_rows,
                is_director=is_director, is_officer=is_officer,
                transaction_date=tx_date_iso, transaction_code=code,
                acquired_disposed_code=acquired,
            )

            if form == "4/A":
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("FORM_AMENDMENT",)))
                continue

            if tx_date is None or not (START_DATE <= tx_date <= END_DATE):
                waterfall["p_acquired_rows_date_out_of_scope"] += 1
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("TRANSACTION_DATE_OUT_OF_SCOPE",)))
                if tx_date is None:
                    losses.append(LossLedgerRecord(
                        record_id=_stable_hash(["bad-date", acc, sk], "LOSS-"), event_id=None,
                        accession=acc, issuer_cik=issuer_cik, owner_cik=single_owner,
                        status="EXCLUDED", reason_codes=("TRANSACTION_DATE_OUT_OF_SCOPE",),
                        detail=f"unparseable transaction date {row.get('TRANS_DATE')!r}",
                    ))
                continue
            waterfall["p_acquired_rows_in_scope"] += 1

            if not owners or unresolved_owner_rows:
                waterfall["owner_id_unresolved_rows"] += 1
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("OWNER_ID_UNRESOLVED",)))
                losses.append(LossLedgerRecord(
                    record_id=_stable_hash(["owner-missing", acc, sk, unresolved_owner_rows], "LOSS-"), event_id=None,
                    accession=acc, issuer_cik=issuer_cik, owner_cik=None, status="EXCLUDED",
                    reason_codes=("OWNER_ID_UNRESOLVED",),
                    detail=(f"{unresolved_owner_rows} reporting-owner row(s) lack a valid authoritative CIK"
                            if owners else "no reporting-owner row is available"),
                ))
                continue
            waterfall["resolvable_owner_cik_rows"] += 1
            if len(owner_ciks) != 1:
                waterfall["joint_owner_ambiguous_rows"] += 1
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("JOINT_OWNER_AMBIGUOUS",)))
                losses.append(LossLedgerRecord(
                    record_id=_stable_hash(["joint", acc, sk], "LOSS-"), event_id=None,
                    accession=acc, issuer_cik=issuer_cik, owner_cik=None, status="EXCLUDED",
                    reason_codes=("JOINT_OWNER_AMBIGUOUS",),
                    detail=f"{len(owner_ciks)} distinct reporting-owner CIKs; transaction row has no owner attribution",
                ))
                continue
            waterfall["single_owner_unambiguous_rows"] += 1
            if not (is_director or is_officer):
                waterfall["unqualified_role_rows"] += 1
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("QUALIFIED_ROLE_FALSE",)))
                continue
            waterfall["qualified_officer_director_rows"] += 1
            waterfall["qualified_unambiguous_p_acquired_rows"] += 1

            if issuer_cik is None:
                waterfall["issuer_id_unresolved_rows"] += 1
                normalized_candidates.append(NormalizedCandidateRecord(
                    **base_candidate, status="EXCLUDED", reason_codes=("ISSUER_ID_UNRESOLVED",)))
                losses.append(LossLedgerRecord(
                    record_id=_stable_hash(["issuer-missing", acc, sk], "LOSS-"), event_id=None,
                    accession=acc, issuer_cik=None, owner_cik=single_owner, status="EXCLUDED",
                    reason_codes=("ISSUER_ID_UNRESOLVED",), detail="issuer CIK is not resolvable",
                ))
                continue
            waterfall["resolvable_issuer_cik_rows"] += 1

            normalized_candidates.append(NormalizedCandidateRecord(
                **base_candidate, status="QUALIFYING", reason_codes=()))
            group_key = (issuer_cik, single_owner, tx_date_iso)
            item = grouped.setdefault(group_key, {"accessions": set(), "symbols": set(), "rows": 0})
            item["accessions"].add(acc)
            if symbol:
                item["symbols"].add(symbol)
            item["rows"] += 1

    for label, accessions, rows in (
            ("reporting-owner", orphan_owner_accessions,
             int(waterfall["reporting_owner_rows_without_submission"])),
            ("non-derivative transaction", orphan_transaction_accessions,
             int(waterfall["nonderivative_rows_without_submission"]))):
        if not rows:
            continue
        sample = sorted(accessions)[:20]
        losses.append(LossLedgerRecord(
            record_id=_stable_hash(["orphan-rows", label, rows, sample], "LOSS-"),
            event_id=None, accession=None, issuer_cik=None, owner_cik=None,
            status="EXCLUDED", reason_codes=("SUBMISSION_ROW_MISSING",),
            detail=(f"{rows} official {label} row(s) across {len(accessions)} accession(s) "
                    f"carry no SUBMISSION row in any acquired quarter; sample={sample}"),
        ))

    waterfall["normalized_candidate_rows"] = len(normalized_candidates)

    observations: list[PurchaseObservation] = []
    for (issuer_cik, owner_cik, tx_date), item in sorted(grouped.items()):
        accessions = tuple(sorted(item["accessions"]))
        observations.append(PurchaseObservation(
            observation_id=_stable_hash([issuer_cik, owner_cik, tx_date, accessions], "OBS-"),
            issuer_cik=issuer_cik, owner_cik=owner_cik, transaction_date=tx_date,
            issuer_symbols=tuple(sorted(item["symbols"])), accessions=accessions,
            source_rows=int(item["rows"]),
        ))
    waterfall["certified_purchase_observations"] = len(observations)
    waterfall["distinct_issuer_ciks_in_observations"] = len({o.issuer_cik for o in observations})
    waterfall["distinct_owner_ciks_in_observations"] = len({o.owner_cik for o in observations})

    events: list[Form4Event] = []
    obs_by_issuer: dict[str, list[PurchaseObservation]] = defaultdict(list)
    for obs in observations:
        obs_by_issuer[obs.issuer_cik].append(obs)
    for issuer_cik, issuer_obs in sorted(obs_by_issuer.items()):
        by_date: dict[str, list[PurchaseObservation]] = defaultdict(list)
        for obs in sorted(issuer_obs, key=lambda o: (o.transaction_date, o.owner_cik, o.observation_id)):
            by_date[obs.transaction_date].append(obs)
        window: deque[PurchaseObservation] = deque()
        owner_counts: Counter[str] = Counter()
        for tx_date in sorted(by_date):
            while window and calendar.distance(window[0].transaction_date, tx_date) > 10:
                expired = window.popleft()
                owner_counts[expired.owner_cik] -= 1
                if owner_counts[expired.owner_cik] <= 0:
                    del owner_counts[expired.owner_cik]
            distinct_before = len(owner_counts)
            for obs in sorted(by_date[tx_date], key=lambda o: (o.owner_cik, o.observation_id)):
                window.append(obs)
                owner_counts[obs.owner_cik] += 1
            if distinct_before < 2 <= len(owner_counts):
                owners = tuple(sorted(owner_counts))
                relevant = tuple(sorted(window, key=lambda x: (x.transaction_date, x.owner_cik, x.observation_id)))
                accessions = tuple(sorted({a for x in relevant for a in x.accessions}))
                start_date = relevant[0].transaction_date
                distance = calendar.distance(start_date, tx_date)
                event_payload = [issuer_cik, tx_date, owners,
                                 tuple(x.observation_id for x in relevant), accessions]
                events.append(Form4Event(
                    event_id=_stable_hash(event_payload, "F4EV-"), issuer_cik=issuer_cik,
                    formation_transaction_date=tx_date, window_start_date=start_date,
                    owner_ciks=owners,
                    constituent_observation_ids=tuple(x.observation_id for x in relevant),
                    accessions=accessions, session_distance=distance,
                ))
    waterfall["economic_formations"] = len(events)

    filings_by_period = Counter(s.source_period for s in submissions.values() if s.document_type == "4")
    amendments_by_period = Counter(s.source_period for s in submissions.values() if s.document_type == "4/A")
    conservation = _assert_conservation(waterfall)
    diagnostics = {
        "calendar_source": calendar.source,
        "calendar_version": calendar.version,
        "calendar_semantics": "session_distance(a,b)=count of XNYS regular sessions with a < session <= b",
        "same_transaction_date_tie_semantics": "all qualifying observations on one transaction date enter atomically before threshold crossing is evaluated",
        "start_date": START_DATE.isoformat(), "end_date": END_DATE.isoformat(),
        "parser_version": PARSER_VERSION,
        "normalized_candidate_scope": "all Form 4 / 4-A non-derivative P+acquired rows; non-P/A rows are counted in the waterfall but not persisted row-by-row",
        "declared_source_columns": {t: list(c) for t, c in sorted(TABLE_REQUIRED_COLUMNS.items())},
        "primary_key_columns": {t: list(c) for t, c in sorted(TABLE_KEY_COLUMNS.items())},
        "key_conflict_policy": ("a primary key carrying two or more distinct official row "
                                "contents is fail-closed: the whole accession is excluded from "
                                "the certified population and ledgered; identical duplicates are "
                                "ledgered as diagnostics and change nothing; no disposition "
                                "depends on physical row, member or quarter order"),
        "raw_row_conservation": conservation,
        "original_form4_filings_by_source_period": dict(sorted(filings_by_period.items())),
        "form4a_filings_by_source_period": dict(sorted(amendments_by_period.items())),
    }
    return CensusBuild(submissions, dict(owners_by_accession), [], observations, events, losses,
                       dict(sorted(waterfall.items())), diagnostics, normalized_candidates)


class RateLimiter:
    """Process-global token bucket shared by every SEC worker.

    Fair Access is a property of the whole process, not of one thread. Each
    worker must draw from the same bucket or concurrency silently multiplies the
    request rate by the worker count.
    """

    def __init__(self, rate_per_second: float, burst: float | None = None):
        if rate_per_second <= 0:
            raise ValueError("rate_per_second must be positive")
        self._rate = float(rate_per_second)
        # Default to a single token: a large bucket would let a run open with a
        # burst well above the declared pace, which is exactly what Fair Access
        # asks callers not to do. Callers may widen it deliberately.
        self._capacity = float(burst) if burst is not None else 1.0
        self._tokens = self._capacity
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    @property
    def rate_per_second(self) -> float:
        return self._rate

    def acquire(self, tokens: float = 1.0) -> None:
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(self._capacity,
                                   self._tokens + (now - self._updated) * self._rate)
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                wait = (tokens - self._tokens) / self._rate
            time.sleep(wait)


def write_atomic(path: Path, data: bytes) -> None:
    """Replace a cache entry atomically.

    A reader -- including a second resolver process sharing this directory --
    must never observe a half-written document.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp.{os.getpid()}.{threading.get_ident()}")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def assign_disjoint(items: Sequence[str], workers: int) -> list[list[str]]:
    """Deterministically partition work so no accession is fetched twice.

    Strided rather than contiguous so every shard spans the whole range and the
    workers finish together.
    """
    if workers < 1:
        raise ValueError("workers must be >= 1")
    shards: list[list[str]] = [[] for _ in range(workers)]
    for index, item in enumerate(items):
        shards[index % workers].append(item)
    return shards


def acceptance_header_url(issuer_cik: str, accession: str) -> str:
    cik = str(int(issuer_cik))
    acc_dir = accession.replace("-", "")
    return f"{SEC_ARCHIVE_ROOT}/{cik}/{acc_dir}/{accession}-index-headers.html"


def _http_get(url: str, user_agent: str | None = None, timeout: int = 60, retries: int = 4,
              delay: float = 0.13, limiter: "RateLimiter | None" = None) -> bytes:
    """Fetch official SEC bytes under the one declared identity.

    ``user_agent`` defaults to ``None`` rather than to the module constant on
    purpose: a default argument binds at import time, which would freeze the
    identity before the environment is read and silently reintroduce the
    preflight/acquisition divergence this module guards against.
    """
    error: Exception | None = None
    for attempt in range(retries):
        try:
            # Every attempt is a real request to SEC, so every attempt draws from
            # the budget. Charging only the first would let retries present a
            # multiple of the declared pace during exactly the conditions that
            # provoke retries.
            if limiter is not None:
                limiter.acquire()
            req = urllib.request.Request(url, headers=sec_request_headers(user_agent))
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
            if delay:
                time.sleep(delay)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404):
                raise
            error = exc
            time.sleep(min(4.0, 0.5 * (2 ** attempt)))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            error = exc
            time.sleep(min(4.0, 0.5 * (2 ** attempt)))
    raise RuntimeError(f"failed GET {url}: {error}")


class AcceptanceIdentityError(ValueError):
    """An EDGAR document is not the document it was fetched for."""


@dataclass(frozen=True)
class AcceptanceDocument:
    """Identity and acceptance time read out of one EDGAR header."""

    accession: str
    submission_type: str
    issuer_ciks: tuple[str, ...]
    owner_ciks: tuple[str, ...]
    acceptance_time: str

    def to_dict(self) -> dict[str, Any]:
        return {"accession": self.accession, "submission_type": self.submission_type,
                "issuer_ciks": list(self.issuer_ciks), "owner_ciks": list(self.owner_ciks),
                "acceptance_time": self.acceptance_time}


def parse_acceptance_document(payload: bytes) -> AcceptanceDocument:
    """Read identity and acceptance time from the authoritative SGML header.

    An EDGAR index-headers document carries the machine-readable header inside an
    HTML comment and repeats it afterwards as escaped human-readable text. Only
    the SGML block is parsed: the rendering is a duplicate, and reading identity
    from a duplicate is how a substituted document passes inspection.

    ``<CIK>`` appears under both ``<ISSUER>`` and ``<REPORTING-OWNER>``, so the
    parse tracks which block it is inside rather than matching the tag globally.
    """
    text = payload.decode("utf-8", errors="replace")
    start = text.find("<SEC-HEADER>")
    if start < 0:
        raise AcceptanceIdentityError("no SEC-HEADER block")
    header = text[start:]
    end = header.find("-->")
    if end >= 0:
        header = header[:end]

    accession = ""
    submission_type = ""
    acceptance = ""
    issuers: list[str] = []
    owners: list[str] = []
    block = ""
    for raw_line in header.splitlines():
        line = raw_line.strip()
        if line.startswith("<REPORTING-OWNER>"):
            block = "owner"
        elif line.startswith("<ISSUER>"):
            block = "issuer"
        elif line.startswith(("</REPORTING-OWNER>", "</ISSUER>")):
            block = ""
        elif line.startswith("<ACCEPTANCE-DATETIME>") and not acceptance:
            acceptance = line[len("<ACCEPTANCE-DATETIME>"):].strip()
        elif line.startswith("<ACCESSION-NUMBER>") and not accession:
            accession = line[len("<ACCESSION-NUMBER>"):].strip()
        elif line.startswith("<TYPE>") and not submission_type:
            submission_type = line[len("<TYPE>"):].strip()
        elif line.startswith("<CIK>"):
            cik = normalize_cik(line[len("<CIK>"):].strip())
            if cik and block == "issuer":
                issuers.append(cik)
            elif cik and block == "owner":
                owners.append(cik)

    if not re.fullmatch(r"\d{14}", acceptance or ""):
        raise AcceptanceIdentityError("ACCEPTANCE-DATETIME not found")
    if not accession:
        raise AcceptanceIdentityError("ACCESSION-NUMBER not found")
    stamp = datetime.strptime(acceptance, "%Y%m%d%H%M%S").replace(
        tzinfo=timezone(timedelta(hours=-5)))
    # The EDGAR header does not encode a DST offset. Preserve the authoritative
    # wall clock and label the timezone separately rather than inventing a UTC
    # conversion. The ISO string intentionally carries no offset.
    return AcceptanceDocument(
        accession=accession, submission_type=submission_type.upper(),
        issuer_ciks=tuple(sorted(set(issuers))), owner_ciks=tuple(sorted(set(owners))),
        acceptance_time=stamp.strftime("%Y-%m-%dT%H:%M:%S"))


def verify_acceptance_document(payload: bytes, accession: str, issuer_cik: str | None = None,
                               owner_ciks: Sequence[str] = ()) -> AcceptanceDocument:
    """Accept an acceptance time only from a document proven to be the right one.

    A timestamp is meaningless unless the document it came from is this
    accession, is an original Form 4, and belongs to the issuer and reporting
    owners the census expects. Checking that the bytes merely parse would let a
    substituted, truncated or mis-cached document supply a timestamp.
    """
    document = parse_acceptance_document(payload)
    if document.accession != accession:
        raise AcceptanceIdentityError(
            f"document is accession {document.accession}, expected {accession}")
    if document.submission_type != "4":
        raise AcceptanceIdentityError(
            f"submission type {document.submission_type!r} is not an original Form 4")
    expected_issuer = normalize_cik(issuer_cik) if issuer_cik else None
    if expected_issuer and expected_issuer not in document.issuer_ciks:
        raise AcceptanceIdentityError(
            f"issuer {expected_issuer} absent from document issuers {document.issuer_ciks}")
    missing = sorted({normalize_cik(o) for o in owner_ciks if normalize_cik(o)}
                     - set(document.owner_ciks))
    if missing:
        raise AcceptanceIdentityError(
            f"reporting owners {missing} absent from document owners {document.owner_ciks}")
    return document


def parse_acceptance_timestamp(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="replace")
    match = re.search(r"<ACCEPTANCE-DATETIME>\s*(\d{14})", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError("ACCEPTANCE-DATETIME not found")
    dt = datetime.strptime(match.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone(timedelta(hours=-5)))
    # EDGAR header does not encode DST offset. Preserve the authoritative wall clock and label timezone separately
    # instead of inventing a UTC conversion. The ISO string intentionally carries no offset.
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


#: Requests per second the resolver will draw, process-wide. SEC's Fair Access
#: guidance is stricter than this only under sustained abuse; the default leaves
#: a wide margin and is never raised to buy speed.
DEFAULT_SEC_RATE_PER_SECOND = 5.0
#: Completed accessions are checkpointed in batches of this size.
ACCEPTANCE_CHECKPOINT_BATCH = 200


def repair_checkpoint_tail(path: Path | None) -> int:
    """Truncate a checkpoint to its last complete line. Returns bytes dropped.

    A process killed mid-append leaves a partial final line. Appending after it
    fuses the fragment with the next record, producing a line that is neither
    the old one nor the new one, so the damage outlives the crash.
    """
    if path is None or not path.exists():
        return 0
    data = path.read_bytes()
    if not data or data.endswith(b"\n"):
        return 0
    cut = data.rfind(b"\n")
    keep = data[:cut + 1] if cut >= 0 else b""
    dropped = len(data) - len(keep)
    write_atomic(path, keep)
    return dropped


def load_acceptance_checkpoint(path: Path | None) -> dict[str, dict[str, Any]]:
    """Previously completed accessions, keyed by accession."""
    if path is None or not path.exists():
        return {}
    done: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue  # a line torn by a kill is simply not yet done
        if record.get("accession"):
            done[record["accession"]] = record
    return done


def validate_acceptance_cache(done: dict[str, dict[str, Any]], cache_dir: Path | None,
                              issuer_of: dict[str, str] | None = None,
                              owners_of: dict[str, Sequence[str]] | None = None,
                              ) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Re-derive every resumed record from the cached bytes.

    A matching sha256 proves the bytes are unchanged since they were recorded.
    It does not prove the recorded acceptance time or URL were ever derived from
    those bytes, nor that the document is the right one. Resume therefore
    re-parses and re-verifies each document and rebuilds the record from what
    the bytes actually say; a stored field that disagrees makes the entry stale.
    """
    if cache_dir is None:
        return {}, sorted(done)
    issuer_of = issuer_of or {}
    owners_of = owners_of or {}
    good: dict[str, dict[str, Any]] = {}
    stale: list[str] = []
    for accession, record in done.items():
        path = cache_dir / f"{accession}.html"
        if not path.exists():
            stale.append(accession)
            continue
        payload = path.read_bytes()
        digest = _sha256_bytes(payload)
        if digest != record.get("sha256"):
            stale.append(accession)
            continue
        try:
            document = verify_acceptance_document(
                payload, accession, issuer_of.get(accession), owners_of.get(accession, ()))
        except (AcceptanceIdentityError, ValueError):
            stale.append(accession)
            continue
        if record.get("acceptance_time") and record["acceptance_time"] != document.acceptance_time:
            stale.append(accession)
            continue
        good[accession] = {"accession": accession,
                           "url": acceptance_header_url(issuer_of.get(accession, ""), accession),
                           "sha256": digest, "bytes": len(payload),
                           "acceptance_time": document.acceptance_time,
                           "submission_type": document.submission_type}
    return good, sorted(stale)


def resolve_acceptance_documents(
    accessions: Sequence[str], issuer_of: dict[str, str],
    owners_of: dict[str, Sequence[str]] | None = None, cache_dir: Path | None = None,
    checkpoint_path: Path | None = None, fetcher: Any = None, workers: int = 1,
    limiter: "RateLimiter | None" = None,
    rate_per_second: float = DEFAULT_SEC_RATE_PER_SECOND,
    batch_size: int = ACCEPTANCE_CHECKPOINT_BATCH,
) -> tuple[dict[str, dict[str, str]], list[tuple[str, str]]]:
    """Fetch EDGAR acceptance headers durably, optionally with several workers.

    Concurrency is admissible here only because three properties hold together:

    * one process-global rate limiter, so Fair Access pace is independent of the
      worker count;
    * disjoint accession assignment, so no document is ever fetched twice;
    * atomic cache writes and a batched checkpoint carrying each document's
      sha256, so a kill at any instant resumes exactly.

    The returned mapping is assembled from the sorted accession list, so the
    result is byte-identical whatever the worker count or completion order.
    """
    limiter = limiter or RateLimiter(rate_per_second)
    owners_of = owners_of or {}
    # An injected fetcher does its own thing, so the caller is charged once per
    # accession. The default fetcher charges every attempt from inside, so
    # charging here as well would double-count.
    budgeted_inside = fetcher is None
    if budgeted_inside:
        def fetcher(url: str) -> bytes:  # noqa: F811 - default, budget-aware
            return _http_get(url, limiter=limiter, delay=0.0)
    wanted = sorted(set(accessions))

    repair_checkpoint_tail(checkpoint_path)
    resumed, stale = validate_acceptance_cache(
        load_acceptance_checkpoint(checkpoint_path), cache_dir, issuer_of, owners_of)
    pending = [a for a in wanted if a not in resumed]

    force_refetch = set(stale)
    store: dict[str, dict[str, Any]] = dict(resumed)
    failures: dict[str, str] = {}
    store_lock = threading.Lock()
    checkpoint_lock = threading.Lock()
    buffered: list[dict[str, Any]] = []

    def flush(force: bool = False) -> None:
        # The buffer is drained under the same lock that fills it. Guarding one
        # list with two locks loses records appended between read and clear,
        # which would leave completed work absent from the checkpoint and
        # silently re-fetched on resume.
        with store_lock:
            if not buffered or (len(buffered) < batch_size and not force):
                return
            batch = list(buffered)
            buffered.clear()
        if checkpoint_path is None:
            return
        with checkpoint_lock:
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in batch)
            with checkpoint_path.open("a", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())

    def work(shard: Sequence[str]) -> None:
        for accession in shard:
            issuer = issuer_of.get(accession, "")
            url = acceptance_header_url(issuer, accession)
            local = cache_dir / f"{accession}.html" if cache_dir is not None else None
            expected_owners = owners_of.get(accession, ())
            try:
                payload: bytes | None = None
                # A document the checkpoint marked stale failed verification, so
                # its cached bytes are not trustworthy and must be fetched again.
                # A cache entry that no checkpoint vouches for is not promoted on
                # the strength of a parsable timestamp either: it has to pass the
                # same identity verification a fresh fetch would.
                if local is not None and accession not in force_refetch and local.exists():
                    candidate = local.read_bytes()
                    try:
                        verify_acceptance_document(candidate, accession,
                                                   issuer, expected_owners)
                        payload = candidate
                    except Exception:
                        payload = None
                if payload is None:
                    if not budgeted_inside:
                        limiter.acquire()
                    payload = fetcher(url)
                    if local is not None:
                        write_atomic(local, payload)
                document = verify_acceptance_document(payload, accession, issuer,
                                                      expected_owners)
                record = {"accession": accession, "url": url,
                          "sha256": _sha256_bytes(payload), "bytes": len(payload),
                          "acceptance_time": document.acceptance_time,
                          "submission_type": document.submission_type}
            except Exception as exc:
                with store_lock:
                    failures[accession] = f"{type(exc).__name__}: {exc}"
                continue
            with store_lock:
                store[accession] = record
                buffered.append(record)
                ready = len(buffered) >= batch_size
            if ready:
                flush()

    shards = assign_disjoint(pending, max(1, workers))
    if workers <= 1:
        work(pending)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for future in [pool.submit(work, shard) for shard in shards if shard]:
                future.result()
    flush(force=True)

    resolved = {a: {"acceptance_time": store[a]["acceptance_time"], "url": store[a]["url"],
                    "sha256": store[a]["sha256"]}
                for a in wanted if a in store}
    return resolved, sorted(failures.items())


def resolve_event_times(build: CensusBuild, fetcher: Any = _http_get, cache_dir: Path | None = None,
                        checkpoint_path: Path | None = None, workers: int = 1,
                        rate_per_second: float = DEFAULT_SEC_RATE_PER_SECOND,
                        ) -> tuple[list[Form4Event], list[LossLedgerRecord], dict[str, dict[str, str]]]:
    """Resolve acceptance time only for accession lineage used by economic formations."""
    observations = {o.observation_id: o for o in build.observations}
    needed = sorted({acc for event in build.events for acc in event.accessions})
    accession_issuer: dict[str, str] = {}
    for event in build.events:
        for acc in event.accessions:
            accession_issuer.setdefault(acc, event.issuer_cik)
    losses = list(build.losses)
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
    accession_owners: dict[str, set[str]] = defaultdict(set)
    for obs in build.observations:
        for acc in obs.accessions:
            accession_owners[acc].add(obs.owner_cik)
    resolved, failures = resolve_acceptance_documents(
        needed, accession_issuer, owners_of={k: sorted(v) for k, v in accession_owners.items()},
        cache_dir=cache_dir,
        checkpoint_path=checkpoint_path, fetcher=fetcher, workers=workers,
        rate_per_second=rate_per_second)
    for acc, detail in failures:
        losses.append(LossLedgerRecord(
            record_id=_stable_hash(["acceptance", acc], "LOSS-"), event_id=None, accession=acc,
            issuer_cik=accession_issuer.get(acc), owner_cik=None, status="UNRESOLVED",
            reason_codes=("ACCEPTANCE_TIMESTAMP_UNRESOLVED",), detail=detail,
        ))

    out: list[Form4Event] = []
    for event in build.events:
        owner_times: list[str] = []
        unknown_owners: list[str] = []
        missing_accessions: set[str] = set()
        relevant_obs = [observations[x] for x in event.constituent_observation_ids]
        for owner in event.owner_ciks:
            owner_accessions = {a for o in relevant_obs if o.owner_cik == owner
                                for a in o.accessions}
            outstanding = sorted(a for a in owner_accessions if a not in resolved)
            if outstanding or not owner_accessions:
                # R-05. The earliest instant this owner became public is bounded
                # below by an accession whose acceptance time is unknown, so the
                # minimum over the resolved subset is not the owner's earliest.
                # Treating it as such would report an event_time earlier than the
                # evidence supports.
                unknown_owners.append(owner)
                missing_accessions.update(outstanding)
                continue
            owner_times.append(min(resolved[a]["acceptance_time"] for a in owner_accessions))
        accession_times = tuple(sorted((a, resolved[a]["acceptance_time"]) for a in event.accessions if a in resolved))
        if unknown_owners or len(owner_times) < 2:
            out.append(Form4Event(**{**asdict(event), "acceptance_timestamps": accession_times, "event_time": None, "event_time_status": "UNRESOLVED"}))
            losses.append(LossLedgerRecord(
                record_id=_stable_hash(["event-time", event.event_id], "LOSS-"), event_id=event.event_id,
                accession=None, issuer_cik=event.issuer_cik, owner_cik=None, status="UNRESOLVED",
                reason_codes=("ACCEPTANCE_TIMESTAMP_UNRESOLVED",),
                detail=(f"earliest public observability unknown for owners "
                        f"{sorted(unknown_owners)} via unresolved accessions "
                        f"{sorted(missing_accessions)}" if unknown_owners else
                        "fewer than two distinct constituent owners have resolved "
                        "acceptance timestamps"),
            ))
        else:
            event_time = sorted(owner_times)[1]
            out.append(Form4Event(**{**asdict(event), "acceptance_timestamps": accession_times, "event_time": event_time, "event_time_status": "RESOLVED"}))
    return out, losses, resolved


def ticker_history(build: CensusBuild) -> dict[str, list[tuple[str, str, str]]]:
    history: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for acc, sub in build.submissions.items():
        if sub.document_type != "4":
            continue
        if sub.issuer_cik and sub.filing_date:
            history[sub.issuer_cik].append((sub.filing_date, sub.issuer_symbol, acc))
    return {k: sorted(v) for k, v in history.items()}


def build_mapping_ledger(build: CensusBuild, events: Sequence[Form4Event], price_status: dict[str, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Map events after formation. `price_status` may be absent without changing events."""
    history = ticker_history(build)
    symbol_ciks: dict[str, set[str]] = defaultdict(set)
    for cik, rows in history.items():
        for _, sym, _ in rows:
            if sym:
                symbol_ciks[sym].add(cik)
    out: list[dict[str, Any]] = []
    for event in events:
        symbols = sorted({build.submissions[a].issuer_symbol for a in event.accessions
                          if a in build.submissions and build.submissions[a].issuer_symbol})
        reasons: list[str] = []
        diagnostic: list[str] = []
        if len(symbols) == 0:
            reasons.append("NONSTANDARD_SECURITY")
            chosen = None
        elif len(symbols) > 1:
            # Multiple as-filed symbols on one stable issuer CIK are a temporal
            # ticker-path issue, not an issuer-identity split.  Keep the event
            # and make the mapping loss explicit.
            reasons.append("TICKER_CHANGED")
            chosen = None
        else:
            chosen = symbols[0]
            issuer_symbols = {sym for _, sym, _ in history.get(event.issuer_cik, []) if sym}
            if len(issuer_symbols) > 1:
                diagnostic.append("TICKER_CHANGED")
            if len(symbol_ciks.get(chosen, set())) > 1:
                reasons.append("TICKER_REUSED_OR_AMBIGUOUS")
            if not re.fullmatch(r"[A-Z0-9.\-]{1,15}", chosen):
                reasons.append("NONSTANDARD_SECURITY")
            if price_status is not None and not reasons:
                p = price_status.get(chosen)
                if not p:
                    reasons.append("PRICE_SOURCE_UNAVAILABLE")
                elif p.get("status") == "NO_HISTORY":
                    reasons.append("DELISTED_OR_NO_HISTORY")
                elif p.get("status") != "AVAILABLE":
                    reasons.append("PRICE_SOURCE_UNAVAILABLE")
                elif event.formation_transaction_date not in set(p.get("covered_event_dates", [])):
                    reasons.append("DELISTED_OR_NO_HISTORY")
        out.append({
            "event_id": event.event_id,
            "issuer_cik": event.issuer_cik,
            "formation_transaction_date": event.formation_transaction_date,
            "as_filed_symbols": symbols,
            "selected_symbol": chosen,
            "mapping_status": "MAPPABLE" if not reasons else "UNRESOLVED",
            "reason_codes": sorted(set(reasons)),
            "diagnostic_codes": sorted(set(diagnostic)),
        })
    return out


def probe_yahoo_symbols(symbol_events: dict[str, list[str]], timeout: int = 30) -> dict[str, dict[str, Any]]:
    """Coverage-only probe. Reads timestamps, never price/return arrays."""
    statuses: dict[str, dict[str, Any]] = {}
    for symbol, event_dates in sorted(symbol_events.items()):
        start = int(datetime(2019, 12, 1, tzinfo=timezone.utc).timestamp())
        end = int(datetime(2026, 8, 1, tzinfo=timezone.utc).timestamp())
        url = f"{YAHOO_CHART_ROOT}/{urllib.parse.quote(symbol)}?period1={start}&period2={end}&interval=1d&events=history&includeAdjustedClose=false"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Quant-Trade coverage probe"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            result = ((payload.get("chart") or {}).get("result") or [None])[0]
            if not result:
                statuses[symbol] = {"status": "NO_HISTORY", "covered_event_dates": [], "source": url}
                continue
            timestamps = result.get("timestamp") or []
            available_dates = {datetime.fromtimestamp(int(ts), tz=timezone.utc).date() for ts in timestamps}
            covered: list[str] = []
            for d in event_dates:
                event_d = date.fromisoformat(d)
                if any(abs((x - event_d).days) <= 7 for x in available_dates):
                    covered.append(d)
            statuses[symbol] = {"status": "AVAILABLE", "covered_event_dates": sorted(set(covered)), "source": url, "timestamp_count": len(timestamps)}
            time.sleep(0.05)
        except Exception as exc:
            statuses[symbol] = {"status": "UNAVAILABLE", "covered_event_dates": [], "source": url, "error": f"{type(exc).__name__}: {exc}"}
    return statuses


def census_summary(build: CensusBuild, events: Sequence[Form4Event], mapping: Sequence[dict[str, Any]] | None = None) -> dict[str, Any]:
    by_year = Counter(e.formation_transaction_date[:4] for e in events)
    by_issuer = Counter(e.issuer_cik for e in events)
    total = len(events)
    shares = [(count / total) for count in by_issuer.values()] if total else []
    top10 = sum(count for _, count in by_issuer.most_common(10))
    resolved = sum(e.event_time_status == "RESOLVED" for e in events)
    mappable = None if mapping is None else sum(r["mapping_status"] == "MAPPABLE" for r in mapping)
    coverage_by_year: dict[str, dict[str, int]] = {}
    coverage_by_issuer: dict[str, dict[str, int]] = {}
    if mapping is not None:
        for row in mapping:
            year = row["formation_transaction_date"][:4]
            issuer = row["issuer_cik"]
            raw_identified = bool(row.get("as_filed_symbols"))
            clean = row["mapping_status"] == "MAPPABLE"
            for bucket, key in ((coverage_by_year, year), (coverage_by_issuer, issuer)):
                item = bucket.setdefault(key, {"events": 0, "raw_symbol_identified": 0, "mappable": 0, "unmappable": 0})
                item["events"] += 1
                item["raw_symbol_identified"] += int(raw_identified)
                item["mappable"] += int(clean)
                item["unmappable"] += int(not clean)
        coverage_by_year = dict(sorted(coverage_by_year.items()))
        coverage_by_issuer = dict(sorted(coverage_by_issuer.items()))
    avg_events = (total / len(by_issuer)) if by_issuer else 0.0
    n_eff = {}
    for rho in (0.0, 0.25, 0.5, 0.75):
        denom = 1.0 + max(0.0, avg_events - 1.0) * rho
        n_eff[str(rho)] = round(total / denom, 2) if denom else float(total)
    return {
        "time_range": [START_DATE.isoformat(), END_DATE.isoformat()],
        "formations": total,
        "event_time_resolved": resolved,
        "event_time_unresolved": total - resolved,
        "distinct_qualifying_issuers": build.waterfall.get("distinct_issuer_ciks_in_observations", 0),
        "distinct_qualifying_insiders": build.waterfall.get("distinct_owner_ciks_in_observations", 0),
        "distinct_event_issuers": len(by_issuer),
        "distinct_event_insiders": len({owner for e in events for owner in e.owner_ciks}),
        "annual_formations": dict(sorted(by_year.items())),
        "issuer_event_distribution": dict(sorted(by_issuer.items())),
        "top_10_issuer_share": (top10 / total) if total else 0.0,
        "issuer_hhi": sum(s * s for s in shares),
        "repeat_formations": max(0, total - len(by_issuer)),
        "mappable_events": mappable,
        "unmappable_events": None if mappable is None else total - mappable,
        "mapping_coverage_by_year": coverage_by_year,
        "mapping_coverage_by_issuer": coverage_by_issuer,
        "design_n_effective_by_intracluster_rho": n_eff,
        "waterfall": build.waterfall,
        "diagnostics": build.diagnostics,
    }


def event_to_dict(event: Form4Event) -> dict[str, Any]:
    return asdict(event)


def candidate_to_dict(row: NormalizedCandidateRecord) -> dict[str, Any]:
    return asdict(row)


def observation_to_dict(obs: PurchaseObservation) -> dict[str, Any]:
    return asdict(obs)


def loss_to_dict(loss: LossLedgerRecord) -> dict[str, Any]:
    return asdict(loss)


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8") for row in rows)
