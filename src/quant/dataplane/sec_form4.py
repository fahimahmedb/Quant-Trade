"""Deterministic SEC Form-4 census primitives for the V2-A1 data-semantics gate.

No return, P&L, alpha, Sharpe, hit-rate or threshold-rescue logic lives here.
Economic event formation uses only official SEC filing data plus a pinned XNYS
regular-session calendar. Price-path availability is downstream-only.
"""
from __future__ import annotations

import bisect
import csv
import hashlib
import html
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

START_DATE = date(2020, 1, 1)
END_DATE = date(2026, 6, 30)
PARSER_VERSION = "sec-form4-census-v2a1/3"
SEC_USER_AGENT_ENV = "SEC_USER_AGENT"
SEC_REFUSED_UA_TOKENS = ("github.com",)
OLD_SEC_ZIP_ROOT = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets"
NEW_SEC_ZIP_ROOT = "https://www.sec.gov/files/datastandardsinnovation/data/insider-transactions-data-sets"
SEC_ARCHIVE_ROOT = "https://www.sec.gov/Archives/edgar/data"
YAHOO_CHART_ROOT = "https://query1.finance.yahoo.com/v8/finance/chart"
DEFAULT_SEC_RATE_PER_SECOND = 5.0
ACCEPTANCE_CHECKPOINT_BATCH = 200

REASON_CODES = {
    "FORM_AMENDMENT", "NOT_P_ACQUIRED", "TRANSACTION_DATE_OUT_OF_SCOPE",
    "QUALIFIED_ROLE_FALSE", "OWNER_ID_UNRESOLVED", "JOINT_OWNER_AMBIGUOUS",
    "DUPLICATE_ACCESSION", "DUPLICATE_ACCESSION_CONFLICT",
    "DUPLICATE_REPORTING_OWNER_ROW", "DUPLICATE_REPORTING_OWNER_ROW_CONFLICT",
    "DUPLICATE_TRANSACTION_ROW", "DUPLICATE_TRANSACTION_ROW_CONFLICT",
    "ISSUER_ID_UNRESOLVED", "ACCEPTANCE_TIMESTAMP_UNRESOLVED",
    "EDGAR_HEADER_PARSE_UNRESOLVED", "EDGAR_HEADER_IDENTITY_MISMATCH",
    "RAW_PRIMARY_KEY_UNRESOLVED", "ORPHAN_RAW_ROW",
    "TICKER_CHANGED", "TICKER_REUSED_OR_AMBIGUOUS", "NONSTANDARD_SECURITY",
    "CIK_SYMBOL_CONFLICT", "DELISTED_OR_NO_HISTORY", "CORPORATE_ACTION_UNRESOLVED",
    "PRICE_SOURCE_UNAVAILABLE",
}

# Published SEC Insider Transactions table contracts. AFF10B5ONE is the
# documented SUBMISSION extension introduced in the refreshed 2023-2025 files.
SUBMISSION_COLUMNS = {
    "ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT", "DATE_OF_ORIG_SUB",
    "NO_SECURITIES_OWNED", "NOT_SUBJECT_SEC16", "FORM3_HOLDING_REPORTED",
    "FORM4_TRANS_REPORTED", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME",
    "ISSUERTRADINGSYMBOL", "REMARKS", "AFF10B5ONE",
}
SUBMISSION_REQUIRED = {"ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"}
REPORTINGOWNER_COLUMNS = {
    "ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP",
    "RPTOWNER_TITLE", "RPTOWNER_TXT", "RPTOWNER_STREET1", "RPTOWNER_STREET2",
    "RPTOWNER_CITY", "RPTOWNER_STATE", "RPTOWNER_ZIPCODE", "RPTOWNER_STATE_DESC", "FILE_NUMBER",
}
REPORTINGOWNER_REQUIRED = {"ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP"}
NONDERIV_TRANS_COLUMNS = {
    "ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "SECURITY_TITLE", "SECURITY_TITLE_FN",
    "TRANS_DATE", "TRANS_DATE_FN", "DEEMED_EXECUTION_DATE", "DEEMED_EXECUTION_DATE_FN",
    "TRANS_FORM_TYPE", "TRANS_CODE", "EQUITY_SWAP_INVOLVED", "EQUITY_SWAP_TRANS_CD_FN",
    "TRANS_TIMELINESS", "TRANS_TIMELINESS_FN", "TRANS_SHARES", "TRANS_SHARES_FN",
    "TRANS_PRICEPERSHARE", "TRANS_PRICEPERSHARE_FN", "TRANS_ACQUIRED_DISP_CD",
    "TRANS_ACQUIRED_DISP_CD_FN", "SHRS_OWND_FOLWNG_TRANS", "SHRS_OWND_FOLWNG_TRANS_FN",
    "VALU_OWND_FOLWNG_TRANS", "VALU_OWND_FOLWNG_TRANS_FN", "DIRECT_INDIRECT_OWNERSHIP",
    "DIRECT_INDIRECT_OWNERSHIP_FN", "NATURE_OF_OWNERSHIP", "NATURE_OF_OWNERSHIP_FN",
}
NONDERIV_TRANS_REQUIRED = {"ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "TRANS_DATE", "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD"}
TABLE_SCHEMAS = {
    "SUBMISSION": (SUBMISSION_COLUMNS, SUBMISSION_REQUIRED),
    "REPORTINGOWNER": (REPORTINGOWNER_COLUMNS, REPORTINGOWNER_REQUIRED),
    "NONDERIV_TRANS": (NONDERIV_TRANS_COLUMNS, NONDERIV_TRANS_REQUIRED),
}


class SecIdentityError(RuntimeError):
    """Declared automated SEC identity is absent or non-compliant."""


class SecTableSchemaError(ValueError):
    """Quarterly SEC TSV does not satisfy the documented table contract."""


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_hash(payload: Any, prefix: str) -> str:
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return prefix + hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:24]


def normalize_cik(value: Any) -> str | None:
    raw = _clean(value)
    return raw.zfill(10) if raw and raw.isdigit() else None


def normalize_accession(value: Any) -> str | None:
    raw = _clean(value)
    return raw if re.fullmatch(r"\d{10}-\d{2}-\d{6}", raw) else None


def parse_sec_date(value: str) -> date:
    raw = _clean(value)
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unsupported SEC date: {value!r}")


def iso_or_none(value: str) -> str | None:
    return None if not _clean(value) else parse_sec_date(value).isoformat()


def sec_identity_problem(user_agent: str) -> str | None:
    if not user_agent.strip():
        return f"no SEC identity declared; set {SEC_USER_AGENT_ENV}"
    token = next((part for part in user_agent.split() if "@" in part), "")
    local, _, domain = token.partition("@")
    if not local or "." not in domain:
        return "SEC Fair Access requires a reachable contact email in the User-Agent"
    for refused in SEC_REFUSED_UA_TOKENS:
        if refused in user_agent.lower():
            return f"SEC refuses User-Agent token {refused!r}"
    return None


def sec_identity_is_compliant(user_agent: str) -> bool:
    return sec_identity_problem(user_agent) is None


def sec_user_agent() -> str:
    declared = os.environ.get(SEC_USER_AGENT_ENV, "").strip()
    problem = sec_identity_problem(declared)
    if problem:
        raise SecIdentityError(problem)
    return declared


def sec_request_headers(user_agent: str | None = None) -> dict[str, str]:
    return {
        "User-Agent": user_agent or sec_user_agent(),
        "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8", "Accept-Encoding": "identity",
    }


def source_url_candidates(year: int, quarter: int) -> list[str]:
    name = f"{year}q{quarter}_form345.zip"
    roots = ([NEW_SEC_ZIP_ROOT, OLD_SEC_ZIP_ROOT] if (year, quarter) >= (2026, 2)
             else [OLD_SEC_ZIP_ROOT, NEW_SEC_ZIP_ROOT])
    return [f"{root}/{name}" for root in roots]


def source_url(year: int, quarter: int) -> str:
    return source_url_candidates(year, quarter)[0]


def quarter_specs() -> list[tuple[int, int]]:
    return [(year, q) for year in range(2020, 2027) for q in range(1, (2 if year == 2026 else 4) + 1)]


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
    submissions: dict[str, dict[str, str]]
    owners_by_accession: dict[str, list[dict[str, str]]]
    transaction_rows: list[dict[str, str]]
    observations: list[PurchaseObservation]
    events: list[Form4Event]
    losses: list[LossLedgerRecord]
    waterfall: dict[str, int]
    diagnostics: dict[str, Any]
    normalized_candidates: list[NormalizedCandidateRecord] = field(default_factory=list)


@dataclass(frozen=True)
class EdgarHeaderMetadata:
    accession: str
    submission_type: str
    issuer_cik: str
    reporting_owner_ciks: tuple[str, ...]
    acceptance_time: str


class SessionCalendar:
    """Pinned XNYS regular-session calendar; exactly 10 qualifies, 11 does not."""
    def __init__(self, sessions: Sequence[str], source: str, version: str):
        parsed = sorted({date.fromisoformat(s) for s in sessions})
        if not parsed:
            raise ValueError("empty session calendar")
        self.sessions, self.source, self.version = parsed, source, version

    @classmethod
    def from_csv(cls, path: Path) -> "SessionCalendar":
        rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
        if not rows:
            raise ValueError("calendar file is empty")
        return cls([r["session"] for r in rows], rows[0].get("source", ""), rows[0].get("version", ""))

    def distance(self, earlier: str | date, later: str | date) -> int:
        a = date.fromisoformat(earlier) if isinstance(earlier, str) else earlier
        b = date.fromisoformat(later) if isinstance(later, str) else later
        if b < a:
            raise ValueError("session distance requires chronological dates")
        return bisect.bisect_right(self.sessions, b) - bisect.bisect_right(self.sessions, a)


def _member_name(names: Sequence[str], token: str) -> str:
    matches = [n for n in names if token.upper() in n.upper()]
    if not matches:
        raise SecTableSchemaError(f"zip missing required table {token}")
    matches.sort(key=lambda n: (0 if n.lower().endswith((".tsv", ".txt")) else 1, len(n), n))
    return matches[0]


def _read_tsv(zf: zipfile.ZipFile, token: str) -> list[dict[str, str]]:
    member = _member_name(zf.namelist(), token)
    text = zf.read(member).decode("utf-8-sig", errors="strict")
    reader = csv.reader(io.StringIO(text), delimiter="\t", strict=True)
    try:
        header_raw = next(reader)
    except StopIteration:
        raise SecTableSchemaError(f"{token}: empty table")
    header = [_clean(x).upper() for x in header_raw]
    if any(not x for x in header) or len(header) != len(set(header)):
        raise SecTableSchemaError(f"{token}: invalid/duplicate column names")
    allowed, required = TABLE_SCHEMAS[token]
    missing, unknown = sorted(required - set(header)), sorted(set(header) - allowed)
    if missing or unknown:
        raise SecTableSchemaError(f"{token}: schema mismatch missing={missing} unknown={unknown}")
    rows: list[dict[str, str]] = []
    for line_no, values in enumerate(reader, 2):
        if len(values) != len(header):
            raise SecTableSchemaError(f"{token}: row {line_no} width {len(values)} != {len(header)}")
        rows.append({key: _clean(value) for key, value in zip(header, values)})
    return rows


def parse_quarter_zip(data: bytes, period: str) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        submissions = _read_tsv(zf, "SUBMISSION")
        owners = _read_tsv(zf, "REPORTINGOWNER")
        transactions = _read_tsv(zf, "NONDERIV_TRANS")
    for rows in (submissions, owners, transactions):
        for row in rows:
            row["_SOURCE_PERIOD"] = period
    return submissions, owners, transactions


def _semantic_row(row: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in row.items() if k != "_SOURCE_PERIOD"}


def _row_repr(row: dict[str, str]) -> str:
    return json.dumps(_semantic_row(row), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass
class _PKState:
    canonical: dict[str, str]
    canonical_repr: str
    copies: int = 1
    conflict: bool = False
    source_periods: set[str] = field(default_factory=set)


class _PrimaryKeyIndex:
    """Order-independent primary-key resolver; conflicts are never economic truth."""
    def __init__(self, name: str):
        self.name = name
        self.states: dict[tuple[str, ...], _PKState] = {}
        self.raw_rows = 0
        self.unkeyed_rows = 0

    def add(self, key: tuple[str, ...], row: dict[str, str]) -> None:
        self.raw_rows += 1
        if not key or any(not _clean(part) for part in key):
            self.unkeyed_rows += 1
            return
        rendered = _row_repr(row)
        state = self.states.get(key)
        if state is None:
            self.states[key] = _PKState(row, rendered, source_periods={row.get("_SOURCE_PERIOD", "")})
            return
        state.copies += 1
        state.source_periods.add(row.get("_SOURCE_PERIOD", ""))
        if rendered != state.canonical_repr:
            state.conflict = True
            if rendered < state.canonical_repr:
                state.canonical, state.canonical_repr = row, rendered

    @property
    def duplicate_rows(self) -> int:
        return sum(max(0, s.copies - 1) for s in self.states.values())

    @property
    def exact_duplicate_rows(self) -> int:
        return sum(max(0, s.copies - 1) for s in self.states.values() if not s.conflict)

    @property
    def conflict_keys(self) -> int:
        return sum(s.conflict for s in self.states.values())

    def valid_items(self):
        for key in sorted(self.states):
            if not self.states[key].conflict:
                yield key, self.states[key].canonical

    def audit(self) -> dict[str, int]:
        return {
            "raw_rows": self.raw_rows, "keyed_rows": self.raw_rows - self.unkeyed_rows,
            "unkeyed_rows": self.unkeyed_rows, "unique_primary_keys": len(self.states),
            "duplicate_rows": self.duplicate_rows, "exact_duplicate_rows": self.exact_duplicate_rows,
            "conflict_keys": self.conflict_keys,
        }


def _role_flags(relationship: str) -> tuple[bool, bool]:
    value = re.sub(r"[^A-Z]", "", _clean(relationship).upper())
    return "DIRECTOR" in value, "OFFICER" in value


def build_census(quarter_payloads: Sequence[tuple[str, bytes]], calendar: SessionCalendar) -> CensusBuild:
    losses: list[LossLedgerRecord] = []
    waterfall: Counter[str] = Counter()
    sub_idx, owner_idx, tx_idx = _PrimaryKeyIndex("SUBMISSION"), _PrimaryKeyIndex("REPORTINGOWNER"), _PrimaryKeyIndex("NONDERIV_TRANS")
    source_period_rows: dict[str, dict[str, int]] = {}
    for period, payload in sorted(quarter_payloads, key=lambda x: x[0]):
        q_sub, q_owner, q_tx = parse_quarter_zip(payload, period)
        source_period_rows[period] = {"submission_rows": len(q_sub), "reporting_owner_rows": len(q_owner), "nonderivative_rows": len(q_tx)}
        for row in q_sub:
            sub_idx.add((_clean(row.get("ACCESSION_NUMBER")),), row)
        for row in q_owner:
            owner_idx.add((_clean(row.get("ACCESSION_NUMBER")), _clean(row.get("RPTOWNERCIK"))), row)
        for row in q_tx:
            tx_idx.add((_clean(row.get("ACCESSION_NUMBER")), _clean(row.get("NONDERIV_TRANS_SK"))), row)

    waterfall.update({"source_quarters": len(quarter_payloads), "submission_rows": sub_idx.raw_rows,
                      "reporting_owner_rows": owner_idx.raw_rows, "nonderivative_rows": tx_idx.raw_rows})

    def pk_diagnostics(index: _PrimaryKeyIndex, exact_code: str, conflict_code: str) -> None:
        for key in sorted(index.states):
            state = index.states[key]
            if state.copies <= 1:
                continue
            reason = conflict_code if state.conflict else exact_code
            waterfall[reason.lower()] += state.copies - 1
            losses.append(LossLedgerRecord(
                _stable_hash([index.name, key, reason, state.copies, sorted(state.source_periods)], "LOSS-"),
                None, key[0] if key else None, None,
                normalize_cik(key[1]) if index.name == "REPORTINGOWNER" and len(key) > 1 else None,
                "EXCLUDED" if state.conflict else "DIAGNOSTIC", (reason,),
                "conflicting primary-key variants; no variant is economic truth" if state.conflict else "exact primary-key duplicate collapsed"))
        if index.unkeyed_rows:
            losses.append(LossLedgerRecord(_stable_hash([index.name, "unkeyed", index.unkeyed_rows], "LOSS-"),
                None, None, None, None, "EXCLUDED", ("RAW_PRIMARY_KEY_UNRESOLVED",),
                f"{index.unkeyed_rows} {index.name} rows lack a complete documented primary key"))

    pk_diagnostics(sub_idx, "DUPLICATE_ACCESSION", "DUPLICATE_ACCESSION_CONFLICT")
    pk_diagnostics(owner_idx, "DUPLICATE_REPORTING_OWNER_ROW", "DUPLICATE_REPORTING_OWNER_ROW_CONFLICT")
    pk_diagnostics(tx_idx, "DUPLICATE_TRANSACTION_ROW", "DUPLICATE_TRANSACTION_ROW_CONFLICT")

    submissions = {key[0]: row for key, row in sub_idx.valid_items()}
    submission_conflicts = {key[0] for key, state in sub_idx.states.items() if state.conflict}
    owners_by_accession: dict[str, list[dict[str, str]]] = defaultdict(list)
    owner_conflict_accessions: set[str] = set()
    owner_orphans = 0
    for key, state in owner_idx.states.items():
        acc = key[0]
        if acc not in submissions or acc in submission_conflicts:
            owner_orphans += state.copies
        elif state.conflict:
            owner_conflict_accessions.add(acc)
        else:
            owners_by_accession[acc].append(state.canonical)
    for acc in owners_by_accession:
        owners_by_accession[acc].sort(key=lambda r: (_clean(r.get("RPTOWNERCIK")), _row_repr(r)))

    canonical_tx: list[dict[str, str]] = []
    tx_orphans = tx_conflict_rows = 0
    for key, state in tx_idx.states.items():
        acc = key[0]
        if acc not in submissions or acc in submission_conflicts:
            tx_orphans += state.copies
        elif state.conflict:
            tx_conflict_rows += state.copies
        else:
            canonical_tx.append(state.canonical)
    canonical_tx.sort(key=lambda r: (_clean(r.get("ACCESSION_NUMBER")), _clean(r.get("NONDERIV_TRANS_SK"))))
    waterfall["canonical_nonderivative_rows"] = len(canonical_tx)
    waterfall["orphan_reporting_owner_rows"] = owner_orphans
    waterfall["orphan_nonderivative_rows"] = tx_orphans
    waterfall["conflicted_transaction_source_rows"] = tx_conflict_rows
    if owner_orphans or tx_orphans:
        losses.append(LossLedgerRecord(_stable_hash(["orphan", owner_orphans, tx_orphans], "LOSS-"),
            None, None, None, None, "EXCLUDED", ("ORPHAN_RAW_ROW",),
            f"reporting_owner={owner_orphans}; nonderivative={tx_orphans}"))

    normalized: list[NormalizedCandidateRecord] = []
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in canonical_tx:
        acc = _clean(row.get("ACCESSION_NUMBER")); sub = submissions[acc]
        form = _clean(sub.get("DOCUMENT_TYPE")).upper()
        if form == "4":
            waterfall["original_form4_nonderivative_rows"] += 1
        elif form == "4/A":
            waterfall["form4a_nonderivative_rows"] += 1
        else:
            waterfall["other_form_nonderivative_rows"] += 1
            continue
        code, acquired = _clean(row.get("TRANS_CODE")).upper(), _clean(row.get("TRANS_ACQUIRED_DISP_CD")).upper()
        if not (code == "P" and acquired == "A"):
            waterfall["original_form4_not_p_acquired_rows" if form == "4" else "form4a_not_p_acquired_rows"] += 1
            continue
        waterfall["original_form4_p_acquired_rows" if form == "4" else "form4a_p_acquired_rows"] += 1
        issuer_cik, symbol = normalize_cik(sub.get("ISSUERCIK")), _clean(sub.get("ISSUERTRADINGSYMBOL")).upper()
        owners = owners_by_accession.get(acc, [])
        owner_ids = [normalize_cik(o.get("RPTOWNERCIK")) for o in owners]
        unresolved_owner_rows = sum(x is None for x in owner_ids)
        owner_ciks = tuple(sorted({x for x in owner_ids if x}))
        owner_conflict = acc in owner_conflict_accessions
        single_owner = owner_ciks[0] if not owner_conflict and unresolved_owner_rows == 0 and len(owner_ciks) == 1 else None
        flags = [_role_flags(o.get("RPTOWNER_RELATIONSHIP", "")) for o in owners if single_owner and normalize_cik(o.get("RPTOWNERCIK")) == single_owner]
        is_director = any(x[0] for x in flags) if single_owner else None
        is_officer = any(x[1] for x in flags) if single_owner else None
        try:
            tx_date = parse_sec_date(row.get("TRANS_DATE", "")); tx_date_iso = tx_date.isoformat()
        except ValueError:
            tx_date, tx_date_iso = None, None
        base = dict(accession=acc, row_id=_clean(row.get("NONDERIV_TRANS_SK")), source_period=row.get("_SOURCE_PERIOD", ""),
                    document_type=form, issuer_cik=issuer_cik, issuer_trading_symbol=symbol,
                    owner_cik=single_owner, reporting_owner_ciks=owner_ciks, reporting_owner_rows=len(owners),
                    unresolved_owner_cik_rows=unresolved_owner_rows, is_director=is_director, is_officer=is_officer,
                    transaction_date=tx_date_iso, transaction_code=code, acquired_disposed_code=acquired)
        if form == "4/A":
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=("FORM_AMENDMENT",))); continue
        if tx_date is None or not (START_DATE <= tx_date <= END_DATE):
            waterfall["p_acquired_rows_date_out_of_scope"] += 1
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=("TRANSACTION_DATE_OUT_OF_SCOPE",))); continue
        waterfall["p_acquired_rows_in_scope"] += 1
        if owner_conflict or not owners or unresolved_owner_rows:
            waterfall["owner_id_unresolved_rows"] += 1
            reasons = ("DUPLICATE_REPORTING_OWNER_ROW_CONFLICT",) if owner_conflict else ("OWNER_ID_UNRESOLVED",)
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=reasons)); continue
        waterfall["resolvable_owner_cik_rows"] += 1
        if len(owner_ciks) != 1:
            waterfall["joint_owner_ambiguous_rows"] += 1
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=("JOINT_OWNER_AMBIGUOUS",))); continue
        waterfall["single_owner_unambiguous_rows"] += 1
        if not (is_director or is_officer):
            waterfall["unqualified_role_rows"] += 1
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=("QUALIFIED_ROLE_FALSE",))); continue
        waterfall["qualified_officer_director_rows"] += 1
        if issuer_cik is None:
            waterfall["issuer_id_unresolved_rows"] += 1
            normalized.append(NormalizedCandidateRecord(**base, status="EXCLUDED", reason_codes=("ISSUER_ID_UNRESOLVED",))); continue
        waterfall["resolvable_issuer_cik_rows"] += 1
        waterfall["qualified_unambiguous_p_acquired_rows"] += 1
        normalized.append(NormalizedCandidateRecord(**base, status="QUALIFYING", reason_codes=()))
        key = (issuer_cik, single_owner, tx_date_iso)
        item = grouped.setdefault(key, {"accessions": set(), "symbols": set(), "rows": 0})
        item["accessions"].add(acc); item["rows"] += 1
        if symbol: item["symbols"].add(symbol)

    waterfall["original_form4_filings"] = len({a for a,s in submissions.items() if _clean(s.get("DOCUMENT_TYPE")).upper()=="4"})
    waterfall["form4a_filings"] = len({a for a,s in submissions.items() if _clean(s.get("DOCUMENT_TYPE")).upper()=="4/A"})
    observations: list[PurchaseObservation] = []
    for (issuer_cik, owner_cik, tx_date), item in sorted(grouped.items()):
        accessions, symbols = tuple(sorted(item["accessions"])), tuple(sorted(item["symbols"]))
        observations.append(PurchaseObservation(_stable_hash([issuer_cik, owner_cik, tx_date, accessions], "F4OBS-"),
            issuer_cik, owner_cik, tx_date, symbols, accessions, item["rows"]))
    waterfall["purchase_observations"] = len(observations)
    waterfall["distinct_issuer_ciks_in_observations"] = len({o.issuer_cik for o in observations})
    waterfall["distinct_owner_ciks_in_observations"] = len({o.owner_cik for o in observations})

    by_issuer: dict[str,list[PurchaseObservation]] = defaultdict(list)
    for obs in observations: by_issuer[obs.issuer_cik].append(obs)
    events: list[Form4Event] = []
    for issuer_cik in sorted(by_issuer):
        by_date: dict[str,list[PurchaseObservation]] = defaultdict(list)
        for obs in by_issuer[issuer_cik]: by_date[obs.transaction_date].append(obs)
        window: deque[PurchaseObservation] = deque(); counts: Counter[str] = Counter()
        for tx_date in sorted(by_date):
            while window and calendar.distance(window[0].transaction_date, tx_date) > 10:
                old=window.popleft(); counts[old.owner_cik]-=1
                if counts[old.owner_cik] <= 0: del counts[old.owner_cik]
            before=len(counts)
            for obs in sorted(by_date[tx_date], key=lambda x:(x.owner_cik,x.observation_id)):
                window.append(obs); counts[obs.owner_cik]+=1
            if before < 2 <= len(counts):
                relevant=tuple(sorted(window,key=lambda x:(x.transaction_date,x.owner_cik,x.observation_id)))
                owners=tuple(sorted(counts)); accessions=tuple(sorted({a for x in relevant for a in x.accessions}))
                start=relevant[0].transaction_date; dist=calendar.distance(start,tx_date)
                events.append(Form4Event(_stable_hash([issuer_cik,tx_date,owners,tuple(x.observation_id for x in relevant),accessions],"F4EV-"),
                    issuer_cik,tx_date,start,owners,tuple(x.observation_id for x in relevant),accessions,dist))
    waterfall["economic_formations"] = len(events)

    raw_audit={"SUBMISSION":sub_idx.audit(),"REPORTINGOWNER":owner_idx.audit(),"NONDERIV_TRANS":tx_idx.audit()}
    for table,audit in raw_audit.items():
        if audit["raw_rows"] != audit["unkeyed_rows"]+audit["unique_primary_keys"]+audit["duplicate_rows"]:
            raise AssertionError(f"raw reconciliation failed for {table}: {audit}")
    diagnostics={"calendar_source":calendar.source,"calendar_version":calendar.version,
        "calendar_semantics":"session_distance(a,b)=count XNYS regular sessions with a < session <= b",
        "same_transaction_date_tie_semantics":"all qualifying observations on a date enter atomically before crossing evaluation",
        "start_date":START_DATE.isoformat(),"end_date":END_DATE.isoformat(),"parser_version":PARSER_VERSION,
        "raw_row_reconciliation":raw_audit,"source_period_raw_rows":source_period_rows,
        "primary_key_conflict_policy":"any conflicting documented primary key is excluded from economic truth; lexical canonical is diagnostic only",
        "normalized_candidate_scope":"all canonical Form 4 / 4-A non-derivative P+A rows; every raw row reconciles in raw_row_reconciliation",
        "original_form4_filings_by_source_period":dict(sorted(Counter(s.get("_SOURCE_PERIOD","UNKNOWN") for s in submissions.values() if _clean(s.get("DOCUMENT_TYPE")).upper()=="4").items())),
        "form4a_filings_by_source_period":dict(sorted(Counter(s.get("_SOURCE_PERIOD","UNKNOWN") for s in submissions.values() if _clean(s.get("DOCUMENT_TYPE")).upper()=="4/A").items()))}
    return CensusBuild(submissions,dict(owners_by_accession),canonical_tx,observations,events,
                       sorted(losses,key=lambda x:x.record_id),dict(sorted(waterfall.items())),diagnostics,normalized)


class RateLimiter:
    """Process-global token bucket. Every HTTP attempt, including retry, draws one token."""
    def __init__(self, rate_per_second: float, burst: float | None = None):
        if rate_per_second <= 0: raise ValueError("rate_per_second must be positive")
        self._rate=float(rate_per_second); self._capacity=float(burst) if burst is not None else 1.0
        self._tokens=self._capacity; self._updated=time.monotonic(); self._lock=threading.Lock()
    @property
    def rate_per_second(self)->float: return self._rate
    def acquire(self,tokens:float=1.0)->None:
        while True:
            with self._lock:
                now=time.monotonic(); self._tokens=min(self._capacity,self._tokens+(now-self._updated)*self._rate); self._updated=now
                if self._tokens>=tokens: self._tokens-=tokens; return
                wait=(tokens-self._tokens)/self._rate
            time.sleep(wait)


def _http_get(url: str, user_agent: str | None = None, timeout: int = 60, retries: int = 4,
              delay: float = 0.0, limiter: RateLimiter | None = None) -> bytes:
    error: Exception | None = None
    for attempt in range(retries):
        if limiter is not None: limiter.acquire()
        try:
            req=urllib.request.Request(url,headers=sec_request_headers(user_agent))
            with urllib.request.urlopen(req,timeout=timeout) as response: data=response.read()
            if delay: time.sleep(delay)
            return data
        except urllib.error.HTTPError as exc:
            if exc.code in (403,404): raise
            error=exc
        except (urllib.error.URLError,TimeoutError,ConnectionError) as exc:
            error=exc
        if attempt+1<retries: time.sleep(min(4.0,0.5*(2**attempt)))
    raise RuntimeError(f"failed GET {url}: {error}")


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(f"{path.name}.tmp.{os.getpid()}.{threading.get_ident()}")
    try:
        with tmp.open("wb") as handle: handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
        try:
            fd=os.open(path.parent,os.O_RDONLY); os.fsync(fd); os.close(fd)
        except OSError: pass
    finally:
        if tmp.exists(): tmp.unlink()


def assign_disjoint(items: Sequence[str], workers: int) -> list[list[str]]:
    if workers<1: raise ValueError("workers must be >= 1")
    out=[[] for _ in range(workers)]
    for i,item in enumerate(items): out[i%workers].append(item)
    return out


def acceptance_header_url(archive_cik: str, accession: str) -> str:
    return f"{SEC_ARCHIVE_ROOT}/{int(archive_cik)}/{accession.replace('-','')}/{accession}-index-headers.html"


def acceptance_header_url_candidates(accession: str, issuer_cik: str, owner_ciks: Sequence[str]=()) -> list[str]:
    ciks=[]
    for value in [*owner_ciks,issuer_cik,accession[:10]]:
        norm=normalize_cik(value)
        if norm and norm not in ciks: ciks.append(norm)
    return [acceptance_header_url(cik,accession) for cik in ciks]


def _field(text: str, label: str) -> str | None:
    match=re.search(rf"(?im)^\s*{re.escape(label)}\s*:\s*([^\r\n]+)",text)
    return _clean(match.group(1)) if match else None


def parse_edgar_header(payload: bytes) -> EdgarHeaderMetadata:
    text=html.unescape(payload.decode("utf-8",errors="replace")).replace("\r\n","\n")
    acc=_field(text,"ACCESSION NUMBER")
    if not acc:
        m=re.search(r"(?i)<ACCESSION-NUMBER>\s*([^\s<]+)",text); acc=_clean(m.group(1)) if m else None
    form=_field(text,"CONFORMED SUBMISSION TYPE")
    if not form:
        m=re.search(r"(?i)<CONFORMED-SUBMISSION-TYPE>\s*([^\s<]+)",text); form=_clean(m.group(1)) if m else None
    m=re.search(r"(?i)<ACCEPTANCE-DATETIME>\s*(\d{14})",text)
    if not m: raise ValueError("ACCEPTANCE-DATETIME not found")
    accepted=datetime.strptime(m.group(1),"%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")
    norm_acc=normalize_accession(acc)
    if not norm_acc: raise ValueError(f"invalid/missing accession in EDGAR header: {acc!r}")
    if not form: raise ValueError("missing conformed submission type")
    owners=[]
    for section in re.split(r"(?im)^\s*REPORTING-OWNER\s*:\s*$",text)[1:]:
        section=re.split(r"(?im)^\s*(?:REPORTING-OWNER|ISSUER)\s*:\s*$",section,maxsplit=1)[0]
        cik=normalize_cik(_field(section,"CENTRAL INDEX KEY"))
        if cik: owners.append(cik)
    issuer_parts=re.split(r"(?im)^\s*ISSUER\s*:\s*$",text,maxsplit=1)
    issuer=normalize_cik(_field(issuer_parts[1],"CENTRAL INDEX KEY")) if len(issuer_parts)==2 else None
    if not issuer: raise ValueError("issuer CIK not found in EDGAR header")
    if not owners: raise ValueError("reporting-owner CIK not found in EDGAR header")
    return EdgarHeaderMetadata(norm_acc,form.upper(),issuer,tuple(sorted(set(owners))),accepted)


def parse_acceptance_timestamp(payload: bytes) -> str:
    text=html.unescape(payload.decode("utf-8",errors="replace"))
    match=re.search(r"(?i)<ACCEPTANCE-DATETIME>\s*(\d{14})",text)
    if not match: raise ValueError("ACCEPTANCE-DATETIME not found")
    return datetime.strptime(match.group(1),"%Y%m%d%H%M%S").strftime("%Y-%m-%dT%H:%M:%S")


def validate_edgar_header(payload: bytes, accession: str, issuer_cik: str,
                          owner_ciks: Sequence[str], form_type: str="4") -> EdgarHeaderMetadata:
    meta=parse_edgar_header(payload)
    expected=tuple(sorted({normalize_cik(x) for x in owner_ciks if normalize_cik(x)}))
    problems=[]
    if meta.accession!=accession: problems.append(f"accession {meta.accession} != {accession}")
    if meta.submission_type!=form_type.upper(): problems.append(f"form {meta.submission_type} != {form_type.upper()}")
    if meta.issuer_cik!=normalize_cik(issuer_cik): problems.append(f"issuer {meta.issuer_cik} != {normalize_cik(issuer_cik)}")
    if meta.reporting_owner_ciks!=expected: problems.append(f"owners {meta.reporting_owner_ciks} != {expected}")
    if problems: raise ValueError("EDGAR_HEADER_IDENTITY_MISMATCH: "+"; ".join(problems))
    return meta


def _repair_jsonl_tail(path: Path) -> None:
    if not path.exists(): return
    data=path.read_bytes()
    if not data or data.endswith(b"\n"): return
    last=data.rfind(b"\n"); tail=data[last+1:]
    try: json.loads(tail.decode("utf-8"))
    except Exception: write_atomic(path,data[:last+1] if last>=0 else b"")
    else: write_atomic(path,data+b"\n")


def load_acceptance_checkpoint(path: Path | None) -> dict[str,dict[str,Any]]:
    if path is None or not path.exists(): return {}
    _repair_jsonl_tail(path)
    done={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try: record=json.loads(line)
        except json.JSONDecodeError: continue
        if record.get("accession"): done[record["accession"]]=record
    return done


def validate_acceptance_cache(done: dict[str,dict[str,Any]], cache_dir: Path | None,
                              expectations: dict[str,dict[str,Any]] | None=None
                              ) -> tuple[dict[str,dict[str,Any]],list[str]]:
    if cache_dir is None: return {},sorted(done)
    good={}; stale=[]
    for accession in sorted(done):
        path=cache_dir/f"{accession}.html"
        if not path.exists(): stale.append(accession); continue
        payload=path.read_bytes()
        try:
            exp=(expectations or {}).get(accession)
            meta=(validate_edgar_header(payload,accession,exp["issuer_cik"],exp["owner_ciks"],exp.get("form_type","4"))
                  if exp else parse_edgar_header(payload))
            if not exp and meta.accession!=accession: raise ValueError("cache filename/accession mismatch")
        except Exception:
            stale.append(accession); continue
        good[accession]={"accession":accession,"url":done[accession].get("url",""),
                         "sha256":_sha256_bytes(payload),"bytes":len(payload),
                         "acceptance_time":meta.acceptance_time,"submission_type":meta.submission_type,
                         "issuer_cik":meta.issuer_cik,"reporting_owner_ciks":list(meta.reporting_owner_ciks)}
    return good,stale


def resolve_acceptance_documents(accessions: Sequence[str], issuer_of: dict[str,str],
                                 cache_dir: Path | None=None, checkpoint_path: Path | None=None,
                                 fetcher: Any=None, workers: int=1, limiter: RateLimiter | None=None,
                                 rate_per_second: float=DEFAULT_SEC_RATE_PER_SECOND,
                                 batch_size: int=ACCEPTANCE_CHECKPOINT_BATCH,
                                 owner_ciks_of: dict[str,Sequence[str]] | None=None,
                                 form_type_of: dict[str,str] | None=None, kill_hook: Any=None
                                 ) -> tuple[dict[str,dict[str,str]],list[tuple[str,str]]]:
    external_fetcher=fetcher is not None; fetcher=fetcher or _http_get
    limiter=limiter or RateLimiter(rate_per_second); wanted=sorted(set(accessions))
    expectations={acc:{"issuer_cik":issuer_of.get(acc,""),"owner_ciks":list((owner_ciks_of or {}).get(acc,())),
                       "form_type":(form_type_of or {}).get(acc,"4")}
                  for acc in wanted if (owner_ciks_of or {}).get(acc)}
    checkpoint=load_acceptance_checkpoint(checkpoint_path)
    resumed,stale=validate_acceptance_cache(checkpoint,cache_dir,expectations)
    pending=[a for a in wanted if a not in resumed]; force_refetch=set(stale)
    store=dict(resumed); failures={}; store_lock=threading.Lock(); checkpoint_lock=threading.Lock(); buffered=[]

    def checkpoint_append(batch):
        if checkpoint_path is None or not batch: return
        with checkpoint_lock:
            checkpoint_path.parent.mkdir(parents=True,exist_ok=True); _repair_jsonl_tail(checkpoint_path)
            if kill_hook: kill_hook("before_checkpoint_append",batch[0]["accession"])
            with checkpoint_path.open("a",encoding="utf-8") as handle:
                for record in batch: handle.write(json.dumps(record,sort_keys=True)+"\n")
                handle.flush(); os.fsync(handle.fileno())
            if kill_hook: kill_hook("after_checkpoint_fsync",batch[-1]["accession"])

    def flush(force=False):
        with store_lock:
            if not buffered or (len(buffered)<batch_size and not force): return
            batch=list(buffered); buffered.clear()
        checkpoint_append(batch)

    def parse_for(accession,payload):
        owners=(owner_ciks_of or {}).get(accession)
        if owners: return validate_edgar_header(payload,accession,issuer_of.get(accession,""),owners,(form_type_of or {}).get(accession,"4"))
        meta=parse_edgar_header(payload)
        if meta.accession!=accession or meta.issuer_cik!=normalize_cik(issuer_of.get(accession,"")):
            raise ValueError("EDGAR_HEADER_IDENTITY_MISMATCH: accession/issuer mismatch")
        return meta

    def work(shard):
        for accession in shard:
            expected_owners=tuple((owner_ciks_of or {}).get(accession,()))
            urls=acceptance_header_url_candidates(accession,issuer_of.get(accession,""),expected_owners)
            local=cache_dir/f"{accession}.html" if cache_dir else None
            try:
                payload=None; used_url=""
                if local is not None and accession not in force_refetch and local.exists():
                    candidate=local.read_bytes()
                    try: parse_for(accession,candidate); payload=candidate; used_url=checkpoint.get(accession,{}).get("url","legacy-cache")
                    except Exception: payload=None
                if payload is None:
                    last_404=None
                    for url in urls:
                        try:
                            if external_fetcher: limiter.acquire(); candidate=fetcher(url)
                            else: candidate=fetcher(url,limiter=limiter)
                        except urllib.error.HTTPError as exc:
                            if exc.code==404: last_404=exc; continue
                            raise
                        meta=parse_for(accession,candidate); payload=candidate; used_url=url; break
                    if payload is None:
                        if last_404 is not None: raise last_404
                        raise RuntimeError("no EDGAR archive CIK candidate resolved")
                    if local is not None:
                        if kill_hook: kill_hook("before_cache_write",accession)
                        write_atomic(local,payload)
                        if kill_hook: kill_hook("after_cache_write",accession)
                else: meta=parse_for(accession,payload)
                record={"accession":accession,"url":used_url,"sha256":_sha256_bytes(payload),"bytes":len(payload),
                        "acceptance_time":meta.acceptance_time,"submission_type":meta.submission_type,"issuer_cik":meta.issuer_cik,
                        "reporting_owner_ciks":list(meta.reporting_owner_ciks)}
            except Exception as exc:
                with store_lock: failures[accession]=f"{type(exc).__name__}: {exc}"
                continue
            with store_lock:
                store[accession]=record; buffered.append(record); ready=len(buffered)>=batch_size
            if ready: flush()
    shards=assign_disjoint(pending,max(1,workers))
    if workers<=1: work(pending)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for future in [pool.submit(work,shard) for shard in shards if shard]: future.result()
    flush(force=True)
    resolved={a:{"acceptance_time":store[a]["acceptance_time"],"url":store[a]["url"],"sha256":store[a]["sha256"],
                 "submission_type":store[a]["submission_type"],"issuer_cik":store[a]["issuer_cik"],
                 "reporting_owner_ciks":store[a]["reporting_owner_ciks"]} for a in wanted if a in store}
    return resolved,sorted(failures.items())


def resolve_event_times(build: CensusBuild, fetcher: Any=None, cache_dir: Path | None=None,
                        checkpoint_path: Path | None=None, workers: int=1,
                        limiter: RateLimiter | None=None, rate_per_second: float=DEFAULT_SEC_RATE_PER_SECOND,
                        kill_hook: Any=None) -> tuple[list[Form4Event],list[LossLedgerRecord],dict[str,dict[str,str]]]:
    observations={o.observation_id:o for o in build.observations}; needed=sorted({a for e in build.events for a in e.accessions})
    issuer_of={}; owners_of: dict[str,set[str]]=defaultdict(set)
    for event in build.events:
        for oid in event.constituent_observation_ids:
            obs=observations[oid]
            for acc in obs.accessions: issuer_of[acc]=event.issuer_cik; owners_of[acc].add(obs.owner_cik)
    resolved,failures=resolve_acceptance_documents(needed,issuer_of,cache_dir,checkpoint_path,fetcher,workers,limiter,
        rate_per_second,owner_ciks_of={k:tuple(sorted(v)) for k,v in owners_of.items()},form_type_of={a:"4" for a in needed},kill_hook=kill_hook)
    losses=list(build.losses)
    for acc,detail in failures:
        code="EDGAR_HEADER_IDENTITY_MISMATCH" if "IDENTITY_MISMATCH" in detail else ("EDGAR_HEADER_PARSE_UNRESOLVED" if "ValueError" in detail else "ACCEPTANCE_TIMESTAMP_UNRESOLVED")
        losses.append(LossLedgerRecord(_stable_hash(["acceptance",acc,code],"LOSS-"),None,acc,issuer_of.get(acc),None,"UNRESOLVED",(code,),detail))
    out=[]
    for event in build.events:
        relevant=[observations[x] for x in event.constituent_observation_ids]; owner_times=[]; unknown=False
        for owner in event.owner_ciks:
            owner_accessions=sorted({a for o in relevant if o.owner_cik==owner for a in o.accessions})
            if not owner_accessions or any(a not in resolved for a in owner_accessions): unknown=True; continue
            owner_times.append(min(resolved[a]["acceptance_time"] for a in owner_accessions))
        pairs=tuple(sorted((a,resolved[a]["acceptance_time"]) for a in event.accessions if a in resolved))
        if unknown or len(owner_times)<2:
            out.append(Form4Event(**{**asdict(event),"acceptance_timestamps":pairs,"event_time":None,"event_time_status":"UNRESOLVED"}))
            losses.append(LossLedgerRecord(_stable_hash(["event-time",event.event_id],"LOSS-"),event.event_id,None,event.issuer_cik,None,
                "UNRESOLVED",("ACCEPTANCE_TIMESTAMP_UNRESOLVED",),"at least one relevant owner has incomplete validated acceptance lineage; earliest public observability is unknown"))
        else:
            out.append(Form4Event(**{**asdict(event),"acceptance_timestamps":pairs,"event_time":sorted(owner_times)[1],"event_time_status":"RESOLVED"}))
    return out,sorted(losses,key=lambda x:x.record_id),resolved


def ticker_history(build: CensusBuild) -> dict[str,list[tuple[str,str,str]]]:
    out: dict[str,list[tuple[str,str,str]]]=defaultdict(list)
    for acc,sub in build.submissions.items():
        if _clean(sub.get("DOCUMENT_TYPE")).upper()!="4": continue
        cik=normalize_cik(sub.get("ISSUERCIK")); symbol=_clean(sub.get("ISSUERTRADINGSYMBOL")).upper()
        try: filing=iso_or_none(sub.get("FILING_DATE",""))
        except ValueError: filing=None
        if cik and filing: out[cik].append((filing,symbol,acc))
    return {k:sorted(v) for k,v in out.items()}


def build_mapping_ledger(build: CensusBuild, events: Sequence[Form4Event], price_status: dict[str,dict[str,Any]] | None=None) -> list[dict[str,Any]]:
    history=ticker_history(build); symbol_ciks: dict[str,set[str]]=defaultdict(set)
    for cik,rows in history.items():
        for _,sym,_ in rows:
            if sym: symbol_ciks[sym].add(cik)
    out=[]
    for event in events:
        symbols=sorted({_clean(build.submissions[a].get("ISSUERTRADINGSYMBOL")).upper() for a in event.accessions if a in build.submissions and _clean(build.submissions[a].get("ISSUERTRADINGSYMBOL"))})
        reasons=[]; diagnostic=[]
        if not symbols: reasons.append("NONSTANDARD_SECURITY"); chosen=None
        elif len(symbols)>1: reasons.append("TICKER_CHANGED"); chosen=None
        else:
            chosen=symbols[0]
            if len({s for _,s,_ in history.get(event.issuer_cik,[]) if s})>1: diagnostic.append("TICKER_CHANGED")
            if len(symbol_ciks.get(chosen,set()))>1: reasons.append("TICKER_REUSED_OR_AMBIGUOUS")
            if not re.fullmatch(r"[A-Z0-9.\-]{1,15}",chosen): reasons.append("NONSTANDARD_SECURITY")
            if price_status is not None and not reasons:
                p=price_status.get(chosen)
                if not p: reasons.append("PRICE_SOURCE_UNAVAILABLE")
                elif p.get("status")=="NO_HISTORY": reasons.append("DELISTED_OR_NO_HISTORY")
                elif p.get("status")!="AVAILABLE": reasons.append("PRICE_SOURCE_UNAVAILABLE")
                elif event.formation_transaction_date not in set(p.get("covered_event_dates",[])): reasons.append("DELISTED_OR_NO_HISTORY")
        out.append({"event_id":event.event_id,"issuer_cik":event.issuer_cik,"formation_transaction_date":event.formation_transaction_date,
                    "as_filed_symbols":symbols,"selected_symbol":chosen,"mapping_status":"MAPPABLE" if not reasons else "UNRESOLVED",
                    "reason_codes":sorted(set(reasons)),"diagnostic_codes":sorted(set(diagnostic))})
    return out


def probe_yahoo_symbols(symbol_events: dict[str,list[str]], timeout: int=30) -> dict[str,dict[str,Any]]:
    statuses={}
    for symbol,event_dates in sorted(symbol_events.items()):
        start=int(datetime(2019,12,1,tzinfo=timezone.utc).timestamp()); end=int(datetime(2026,8,1,tzinfo=timezone.utc).timestamp())
        url=f"{YAHOO_CHART_ROOT}/{urllib.parse.quote(symbol)}?period1={start}&period2={end}&interval=1d&events=history&includeAdjustedClose=false"
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 Quant-Trade coverage probe"})
            with urllib.request.urlopen(req,timeout=timeout) as response: payload=json.loads(response.read().decode("utf-8"))
            result=((payload.get("chart") or {}).get("result") or [None])[0]
            if not result: statuses[symbol]={"status":"NO_HISTORY","covered_event_dates":[],"source":url}; continue
            available={datetime.fromtimestamp(int(ts),tz=timezone.utc).date() for ts in (result.get("timestamp") or [])}
            covered=[d for d in event_dates if any(abs((x-date.fromisoformat(d)).days)<=7 for x in available)]
            statuses[symbol]={"status":"AVAILABLE","covered_event_dates":sorted(set(covered)),"source":url,"timestamp_count":len(available)}
        except Exception as exc:
            statuses[symbol]={"status":"UNAVAILABLE","covered_event_dates":[],"source":url,"error":f"{type(exc).__name__}: {exc}"}
    return statuses


def census_summary(build: CensusBuild, events: Sequence[Form4Event], mapping: Sequence[dict[str,Any]] | None=None) -> dict[str,Any]:
    by_year=Counter(e.formation_transaction_date[:4] for e in events); by_issuer=Counter(e.issuer_cik for e in events); total=len(events)
    resolved=sum(e.event_time_status=="RESOLVED" for e in events); mappable=None if mapping is None else sum(r["mapping_status"]=="MAPPABLE" for r in mapping)
    coverage_by_year={}; coverage_by_issuer={}
    if mapping is not None:
        for row in mapping:
            for bucket,key in ((coverage_by_year,row["formation_transaction_date"][:4]),(coverage_by_issuer,row["issuer_cik"])):
                item=bucket.setdefault(key,{"events":0,"raw_symbol_identified":0,"mappable":0,"unmappable":0}); item["events"]+=1
                item["raw_symbol_identified"]+=int(bool(row.get("as_filed_symbols"))); clean=row["mapping_status"]=="MAPPABLE"; item["mappable"]+=int(clean); item["unmappable"]+=int(not clean)
    avg=total/len(by_issuer) if by_issuer else 0.0
    n_eff={str(rho):round(total/(1+max(0.0,avg-1)*rho),2) if total else 0.0 for rho in (0.0,0.25,0.5,0.75)}
    return {"time_range":[START_DATE.isoformat(),END_DATE.isoformat()],"formations":total,"event_time_resolved":resolved,
        "event_time_unresolved":total-resolved,"distinct_qualifying_issuers":build.waterfall.get("distinct_issuer_ciks_in_observations",0),
        "distinct_qualifying_insiders":build.waterfall.get("distinct_owner_ciks_in_observations",0),"distinct_event_issuers":len(by_issuer),
        "distinct_event_insiders":len({o for e in events for o in e.owner_ciks}),"annual_formations":dict(sorted(by_year.items())),
        "issuer_event_distribution":dict(sorted(by_issuer.items())),"top_10_issuer_share":sum(c for _,c in by_issuer.most_common(10))/total if total else 0.0,
        "issuer_hhi":sum((c/total)**2 for c in by_issuer.values()) if total else 0.0,"repeat_formations":max(0,total-len(by_issuer)),
        "mappable_events":mappable,"unmappable_events":None if mappable is None else total-mappable,
        "mapping_coverage_by_year":dict(sorted(coverage_by_year.items())),"mapping_coverage_by_issuer":dict(sorted(coverage_by_issuer.items())),
        "design_n_effective_by_intracluster_rho":n_eff,"waterfall":build.waterfall,"diagnostics":build.diagnostics}


def event_to_dict(x: Form4Event)->dict[str,Any]: return asdict(x)
def candidate_to_dict(x: NormalizedCandidateRecord)->dict[str,Any]: return asdict(x)
def observation_to_dict(x: PurchaseObservation)->dict[str,Any]: return asdict(x)
def loss_to_dict(x: LossLedgerRecord)->dict[str,Any]: return asdict(x)
def jsonl_bytes(rows: Iterable[dict[str,Any]])->bytes:
    return b"".join((json.dumps(row,sort_keys=True,separators=(",",":"))+"\n").encode("utf-8") for row in rows)
