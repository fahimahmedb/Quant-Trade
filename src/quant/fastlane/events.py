"""Point-in-time purchase-event builder for ``QUANT_FASTLANE_HPIT_V1``.

Base population (D5): original Form 4 only (``DOCUMENT_TYPE`` exactly ``"4"``;
``4/A``, ``3``, ``5`` and their amendments never create or modify an event),
non-derivative rows with ``TRANS_CODE == "P"`` and acquired/disposed flag
``"A"``. An accession whose sequence year is later than its ``FILING_DATE``
year cannot have been filed on that date and is excluded (backdating guard).
This base population is kept only as a sensitivity ("unfiltered").

Primary population (the one the protocol evaluates) additionally requires:

* ``SECURITY_TITLE`` matching :data:`SECURITY_TITLE_INCLUDE` and not
  :data:`SECURITY_TITLE_EXCLUDE` (common equity only);
* no footnote referenced by the row, and no filing ``REMARKS``, matching the
  frozen :data:`FOOTNOTE_EXCLUSION` regexes (plan/DRIP/fees, IPO/underwritten,
  conversion, private placement);
* exact-duplicate removal, first-seen by (FILING_DATE, accession), on (issuer,
  owner set, transaction tuples).

Timing: ``available_after_date`` is the EDGAR ``FILING_DATE``. Entry is the
open of the first *vendor* session strictly after that date; sessions come
from the licensed vendor's calendar, so none is invented here. ``TRANS_DATE``
is never a public date.

The accession number is the unique key; duplicates inside or across quarters
are build errors. Every excluded transaction row is counted under exactly one
reason (first failing rule in a fixed precedence). Tickers are as filed and
flagged as not being a point-in-time security mapping.
"""

from __future__ import annotations

import bisect
import gzip
import json
import os
import re
import zipfile
from array import array
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes, sha256_file
from quant.fastlane.sec_insider import (
    SecParseError, TableStats, iter_table, load_manifest, parse_number, parse_sec_date,
    quarter_bounds, quarter_key, raw_path)

EVENT_SCHEMA = "fastlane.purchase_event.v1"
ISSUER_DAY_SCHEMA = "fastlane.issuer_filing_day.v1"
ENTRY_RULE = "OPEN_OF_FIRST_VENDOR_SESSION_STRICTLY_AFTER_AVAILABLE_AFTER_DATE"
ORIGINAL_FORM4 = "4"

ACCESSION_RE = re.compile(r"(\d{10})-(\d{2})-(\d{6})")

CEO_RE = re.compile(r"\bC\.?\s?E\.?\s?O\b|CHIEF\s+EXEC", re.IGNORECASE)
CFO_RE = re.compile(r"\bC\.?\s?F\.?\s?O\b|CHIEF\s+FINANCIAL", re.IGNORECASE)

# Frozen population filters (chosen from title counts / filing text only, never outcomes).
SECURITY_TITLE_INCLUDE = r"(COMMON|ORDINARY|CL(ASS)? [A-Z] COMMON|COMMON STOCK)"
SECURITY_TITLE_EXCLUDE = (r"\b(PREFERRED|UNITS?|FUNDS?|PLANS?|WARRANTS?|NOTES?|DEBENTURES?"
                          r"|OPTIONS?|RIGHTS?)\b")
_TITLE_INCLUDE_RE = re.compile(SECURITY_TITLE_INCLUDE)
_TITLE_EXCLUDE_RE = re.compile(SECURITY_TITLE_EXCLUDE)
FOOTNOTE_EXCLUSION = {
    "plan_drip_fees": (r"dividend reinvestment|\bdrip\b|employee stock purchase|\bespp\b"
                       r"|401\(k\)|deferred compensation"
                       r"|in lieu of (cash )?(director|board|fees|compensation|salary)"
                       r"|director'?s'? fee"),
    "ipo_underwritten": r"initial public offering|\bipo\b|underwrit|directed share|registered direct",
    "conversion": r"upon (the )?conversion|converted into|upon exercise of (the )?warrant",
    "private_placement": (r"private placement|privately negotiated|subscription agreement"
                          r"|securities purchase agreement|accredited investor"),
}
_FOOTNOTE_RES = tuple((name, re.compile(rx, re.IGNORECASE))
                      for name, rx in FOOTNOTE_EXCLUSION.items())
_FOOTNOTE_ID_RE = re.compile(r"F\d+")

# Exclusion precedence for NONDERIV_TRANS rows (first failing rule wins).
EXCLUSION_PRECEDENCE = (
    "accession_malformed",
    "accession_missing_from_submission",
    "document_type_not_original_form4",   # detailed by document type below
    "trans_code_not_P",
    "P_acquired_disposed_not_A",
    "filing_date_missing_or_unparseable",
    "issuer_cik_missing",
    "shares_missing_nonpositive_or_unparseable",
    "accession_year_after_filing_year",
    "no_reporting_owner_rows",
)
PRIMARY_EXCLUSION_PRECEDENCE = (
    "security_title_not_common_equity",
    "footnote_exclusion",                 # detailed by category below
    "remarks_exclusion",
    "exact_duplicate_of_earlier_accession",
)


class DuplicateAccessionError(ValueError):
    """The same accession appears twice (within or across quarters)."""


def accession_int(accession: str) -> int:
    m = ACCESSION_RE.fullmatch(accession.strip())
    if not m:
        raise SecParseError(f"malformed accession {accession!r}")
    return int(m.group(1) + m.group(2) + m.group(3))


def normalize_cik(value: str | None) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    if not text.isdigit():
        raise SecParseError(f"non-numeric CIK {value!r}")
    return text.zfill(10)


def classify_owner(relationship: str, title: str, other_text: str) -> dict[str, Any]:
    """Role flags from the relationship field; a title never promotes a role.

    CEO/CFO requires the Officer relationship flag plus a CEO/CFO title.
    """
    rel = (relationship or "").upper()
    ttl = (title or "").strip()
    is_director = "DIRECTOR" in rel
    is_officer = "OFFICER" in rel
    is_ten = "TENPERCENTOWNER" in rel
    is_other = "OTHER" in rel
    is_ceo = is_officer and bool(CEO_RE.search(ttl))
    is_cfo = is_officer and bool(CFO_RE.search(ttl))
    if is_ceo or is_cfo:
        role_class = "CEO_CFO"
    elif is_officer:
        role_class = "OTHER_OFFICER"
    elif is_director:
        role_class = "DIRECTOR"
    elif is_ten:
        role_class = "TEN_PERCENT_OWNER"
    else:
        role_class = "OTHER"
    return {
        "is_director": is_director,
        "is_officer": is_officer,
        "is_ten_percent_owner": is_ten,
        "is_other": is_other,
        "is_ceo": is_ceo,
        "is_cfo": is_cfo,
        "officer_title": ttl or None,
        "other_text": (other_text or "").strip() or None,
        "role_class": role_class,
        # D07 §2.1: director and/or officer qualifies; 10% ownership alone does not.
        "officer_or_director": is_director or is_officer,
    }


def normalize_title(title: str) -> str:
    return " ".join((title or "").upper().split())


def title_is_common_equity(title: str) -> bool:
    norm = normalize_title(title)
    return bool(_TITLE_INCLUDE_RE.search(norm)) and not _TITLE_EXCLUDE_RE.search(norm)


def footnote_category(texts: Iterable[str]) -> str | None:
    """First frozen exclusion category matched by any text, else None."""
    texts = [t for t in texts if t]
    for name, rx in _FOOTNOTE_RES:
        for text in texts:
            if text and rx.search(text):
                return name
    return None


def row_footnote_ids(row: Mapping[str, str]) -> set[str]:
    ids: set[str] = set()
    for key, value in row.items():
        if key.endswith("_FN") and value:
            ids.update(_FOOTNOTE_ID_RE.findall(value))
    return ids


def accession_year(accession: str) -> int:
    return 2000 + int(accession[11:13])


@dataclass
class BuildCounters:
    exclusions: Counter = field(default_factory=Counter)
    excluded_by_document_type: Counter = field(default_factory=Counter)
    primary_exclusions: Counter = field(default_factory=Counter)
    footnote_categories: Counter = field(default_factory=Counter)
    flags: Counter = field(default_factory=Counter)
    population: Counter = field(default_factory=Counter)

    def as_dict(self) -> dict:
        return {
            "exclusion_precedence": list(EXCLUSION_PRECEDENCE),
            "excluded_transaction_rows": dict(sorted(self.exclusions.items())),
            "excluded_P_A_rows_by_document_type": dict(sorted(
                self.excluded_by_document_type.items())),
            "primary_exclusion_precedence": list(PRIMARY_EXCLUSION_PRECEDENCE),
            "primary_excluded_transaction_rows": dict(sorted(self.primary_exclusions.items())),
            "primary_footnote_exclusion_rows_by_category": dict(sorted(
                self.footnote_categories.items())),
            "flags": dict(sorted(self.flags.items())),
            "population": dict(sorted(self.population.items())),
        }


@dataclass
class QuarterResult:
    quarter: str
    events: list[dict]               # base (unfiltered) population
    primary_events: list[dict]       # before cross-quarter dedupe
    accession_ints: array
    table_stats: list[dict]


def _load_submissions(archive_source, quarter: str, counters: BuildCounters,
                      stats: TableStats) -> tuple[dict[str, dict], array]:
    submissions: dict[str, dict] = {}
    accs = array("Q")
    for row in iter_table(archive_source, "SUBMISSION.tsv", stats):
        acc = row["ACCESSION_NUMBER"].strip()
        try:
            acc_i = accession_int(acc)
        except SecParseError:
            counters.population["submission_accession_malformed"] += 1
            continue
        if acc in submissions:
            raise DuplicateAccessionError(
                f"accession {acc} appears twice in SUBMISSION.tsv of {quarter}")
        doc_type = row["DOCUMENT_TYPE"].strip()
        counters.population[f"submissions_document_type_{doc_type or 'EMPTY'}"] += 1
        submissions[acc] = row
        accs.append(acc_i)
    return submissions, accs


def _load_owners(archive_source, wanted: set[str], stats: TableStats) -> dict[str, list[dict]]:
    owners: dict[str, list[dict]] = defaultdict(list)
    for row in iter_table(archive_source, "REPORTINGOWNER.tsv", stats):
        acc = row["ACCESSION_NUMBER"].strip()
        if acc not in wanted:
            continue
        cik = normalize_cik(row["RPTOWNERCIK"])
        if cik is None:
            continue
        info = classify_owner(row["RPTOWNER_RELATIONSHIP"], row["RPTOWNER_TITLE"],
                              row["RPTOWNER_TXT"])
        info["owner_cik"] = cik
        owners[acc].append(info)
    return owners


def _load_footnotes(archive_source, wanted: set[str], stats: TableStats) -> dict[tuple[str, str], str]:
    notes: dict[tuple[str, str], str] = {}
    for row in iter_table(archive_source, "FOOTNOTES.tsv", stats):
        acc = row["ACCESSION_NUMBER"].strip()
        if acc in wanted:
            notes[(acc, row["FOOTNOTE_ID"].strip())] = row["FOOTNOTE_TXT"]
    return notes


def build_quarter(archive_source, quarter: str, counters: BuildCounters,
                  source_sha256: str | None = None) -> QuarterResult:
    """Build base and primary original-Form-4 P/A events for one quarter's data set."""
    own = not isinstance(archive_source, zipfile.ZipFile)
    archive = zipfile.ZipFile(archive_source) if own else archive_source
    try:
        sub_stats = TableStats("SUBMISSION.tsv")
        own_stats = TableStats("REPORTINGOWNER.tsv")
        tr_stats = TableStats("NONDERIV_TRANS.tsv")
        fn_stats = TableStats("FOOTNOTES.tsv")
        submissions, accs = _load_submissions(archive, quarter, counters, sub_stats)
        q_start, q_end = quarter_bounds(quarter)

        rows_by_acc: dict[str, list[dict]] = defaultdict(list)
        for row in iter_table(archive, "NONDERIV_TRANS.tsv", tr_stats):
            counters.population["nonderiv_trans_rows"] += 1
            acc = row["ACCESSION_NUMBER"].strip()
            if not ACCESSION_RE.fullmatch(acc):
                counters.exclusions["accession_malformed"] += 1
                continue
            sub = submissions.get(acc)
            if sub is None:
                counters.exclusions["accession_missing_from_submission"] += 1
                continue
            doc_type = sub["DOCUMENT_TYPE"].strip()
            code = row["TRANS_CODE"].strip()
            acq = row["TRANS_ACQUIRED_DISP_CD"].strip()
            if doc_type != ORIGINAL_FORM4:
                counters.exclusions["document_type_not_original_form4"] += 1
                if code == "P" and acq == "A":
                    counters.excluded_by_document_type[doc_type or "EMPTY"] += 1
                continue
            if code != "P":
                counters.exclusions["trans_code_not_P"] += 1
                continue
            if acq != "A":
                counters.exclusions["P_acquired_disposed_not_A"] += 1
                continue
            try:
                filing_date = parse_sec_date(sub["FILING_DATE"])
            except SecParseError:
                filing_date = None
            if filing_date is None:
                counters.exclusions["filing_date_missing_or_unparseable"] += 1
                continue
            try:
                issuer_cik = normalize_cik(sub["ISSUERCIK"])
            except SecParseError:
                issuer_cik = None
            if issuer_cik is None:
                counters.exclusions["issuer_cik_missing"] += 1
                continue
            try:
                shares = parse_number(row["TRANS_SHARES"])
            except SecParseError:
                shares = None
            if shares is None or shares <= 0:
                counters.exclusions["shares_missing_nonpositive_or_unparseable"] += 1
                continue
            if accession_year(acc) > filing_date.year:
                # The accession sequence was assigned in a later year than the claimed
                # FILING_DATE: the fact was not public on that date.
                counters.exclusions["accession_year_after_filing_year"] += 1
                continue
            rows_by_acc[acc].append(row)

        wanted = set(rows_by_acc)
        owners = _load_owners(archive, wanted, own_stats)
        notes = _load_footnotes(archive, wanted, fn_stats)
        events: list[dict] = []
        primary: list[dict] = []
        for acc in sorted(rows_by_acc):
            sub = submissions[acc]
            rows = rows_by_acc[acc]
            acc_owners = sorted(owners.get(acc, []), key=lambda o: o["owner_cik"])
            if not acc_owners:
                counters.exclusions["no_reporting_owner_rows"] += len(rows)
                continue
            counters.population["transaction_rows_in_events"] += len(rows)
            events.append(_event(acc, sub, rows, acc_owners, quarter, q_start, q_end,
                                 counters, source_sha256, "UNFILTERED"))
            remarks_cat = footnote_category([sub.get("REMARKS") or ""])
            kept = []
            for row in rows:
                if not title_is_common_equity(row["SECURITY_TITLE"]):
                    counters.primary_exclusions["security_title_not_common_equity"] += 1
                    continue
                cat = footnote_category(notes.get((acc, fid), "") for fid in sorted(row_footnote_ids(row)))
                if cat is not None:
                    counters.primary_exclusions["footnote_exclusion"] += 1
                    counters.footnote_categories[cat] += 1
                    continue
                if remarks_cat is not None:
                    counters.primary_exclusions["remarks_exclusion"] += 1
                    counters.footnote_categories["remarks:" + remarks_cat] += 1
                    continue
                kept.append(row)
            if kept:
                primary.append(_event(acc, sub, kept, acc_owners, quarter, q_start, q_end,
                                      BuildCounters(), source_sha256, "PRIMARY"))
        events.sort(key=lambda e: (e["filing_date"], e["accession"]))
        primary.sort(key=lambda e: (e["filing_date"], e["accession"]))
        counters.population["events"] += len(events)
        return QuarterResult(quarter, events, primary, accs,
                             [s.as_dict() for s in (sub_stats, own_stats, tr_stats, fn_stats)])
    finally:
        if own:
            archive.close()


def duplicate_signature(event: Mapping[str, Any]) -> tuple:
    tx = tuple(sorted((t["trans_date"] or "", float(t["shares"]),
                       -1.0 if t["price_per_share"] is None else float(t["price_per_share"]))
                      for t in event["transactions"]))
    return (event["issuer_cik"], tuple(sorted(event["owner_ciks"])), tx)


def dedupe_first_seen(events: list[dict], counters: BuildCounters) -> tuple[list[dict], list[list[str]]]:
    """Drop exact duplicates, keeping the earliest by (FILING_DATE, accession)."""
    first: dict[tuple, str] = {}
    kept, dropped = [], []
    for event in sorted(events, key=lambda e: (e["filing_date"], e["accession"])):
        sig = duplicate_signature(event)
        if sig in first:
            counters.primary_exclusions["exact_duplicate_of_earlier_accession"] += \
                event["n_transactions"]
            dropped.append([event["accession"], first[sig]])
            continue
        first[sig] = event["accession"]
        kept.append(event)
    return kept, dropped


def _event(acc: str, sub: Mapping[str, str], rows: list[dict], owners: list[dict],
           quarter: str, q_start: date, q_end: date, counters: BuildCounters,
           source_sha256: str | None, population: str) -> dict:
    filing_date = parse_sec_date(sub["FILING_DATE"])
    assert filing_date is not None
    if not (q_start <= filing_date <= q_end):
        counters.flags["filing_date_outside_quarter"] += 1
    transactions = []
    trans_dates: list[date] = []
    shares_total = 0.0
    value_total = 0.0
    priced_shares = 0.0
    direct_indirect = set()
    swap_any = False
    form_types = set()
    for row in sorted(rows, key=lambda r: r["NONDERIV_TRANS_SK"]):
        shares = parse_number(row["TRANS_SHARES"]) or 0.0
        try:
            price = parse_number(row["TRANS_PRICEPERSHARE"])
        except SecParseError:
            price = None
            counters.flags["price_unparseable_rows"] += 1
        try:
            tdate = parse_sec_date(row["TRANS_DATE"])
        except SecParseError:
            tdate = None
            counters.flags["trans_date_unparseable_rows"] += 1
        if tdate is None:
            counters.flags["trans_date_missing_rows"] += 1
        else:
            trans_dates.append(tdate)
        if price is None or price <= 0:
            counters.flags["price_missing_or_zero_rows"] += 1
        else:
            value_total += shares * price
            priced_shares += shares
        shares_total += shares
        di = row["DIRECT_INDIRECT_OWNERSHIP"].strip().upper() or "?"
        direct_indirect.add(di)
        swap = row["EQUITY_SWAP_INVOLVED"].strip().lower() in ("1", "true", "y", "yes")
        swap_any = swap_any or swap
        form_types.add(row["TRANS_FORM_TYPE"].strip())
        transactions.append({
            "sk": row["NONDERIV_TRANS_SK"].strip(),
            "security_title": row["SECURITY_TITLE"].strip(),
            "trans_date": tdate.isoformat() if tdate else None,
            "shares": shares,
            "price_per_share": price,
            "direct_indirect": di,
            "equity_swap": swap,
            "trans_form_type": row["TRANS_FORM_TYPE"].strip(),
        })
    if any(ft != ORIGINAL_FORM4 for ft in form_types):
        counters.flags["events_with_non4_trans_form_type_rows"] += 1
    first_trans = min(trans_dates) if trans_dates else None
    last_trans = max(trans_dates) if trans_dates else None
    lag = (filing_date - first_trans).days if first_trans else None
    if lag is not None and lag < 0:
        counters.flags["events_negative_filing_lag"] += 1
    od = [o for o in owners if o["officer_or_director"]]
    event = {
        "schema": EVENT_SCHEMA,
        "lineage": LINEAGE_ID,
        "population": population,
        "accession": acc,
        "quarter": quarter,
        "source_zip_sha256": source_sha256,
        "document_type": sub["DOCUMENT_TYPE"].strip(),
        "filing_date": filing_date.isoformat(),
        "available_after_date": filing_date.isoformat(),
        "entry_rule": ENTRY_RULE,
        "period_of_report": _iso(sub.get("PERIOD_OF_REPORT")),
        "issuer_cik": normalize_cik(sub["ISSUERCIK"]),
        "issuer_name_as_filed": sub["ISSUERNAME"].strip(),
        "ticker_as_filed": sub["ISSUERTRADINGSYMBOL"].strip().upper() or None,
        "ticker_is_pit_security_mapping": False,
        "aff10b5one": (sub.get("AFF10B5ONE") or "").strip() or None,
        "trans_date_first": first_trans.isoformat() if first_trans else None,
        "trans_date_last": last_trans.isoformat() if last_trans else None,
        "filing_lag_days": lag,
        "n_transactions": len(transactions),
        "shares": shares_total,
        "value_usd": round(value_total, 2),
        "priced_shares": priced_shares,
        "avg_price_per_share": (round(value_total / priced_shares, 6)
                                if priced_shares > 0 else None),
        "direct_indirect": "+".join(sorted(direct_indirect)),
        "equity_swap_any": swap_any,
        "owners": owners,
        "owner_ciks": [o["owner_cik"] for o in owners],
        "od_owner_ciks": [o["owner_cik"] for o in od],
        "any_officer_or_director": bool(od),
        "any_ceo_cfo": any(o["role_class"] == "CEO_CFO" for o in owners),
        "any_other_officer": any(o["role_class"] == "OTHER_OFFICER" for o in owners),
        "any_director": any(o["is_director"] for o in owners),
        "any_ten_percent_owner": any(o["is_ten_percent_owner"] for o in owners),
        "ten_percent_only": (not od) and any(o["is_ten_percent_owner"] for o in owners),
        "primary_role_class": _primary_role(owners),
        "transactions": transactions,
    }
    return event


def _primary_role(owners: list[dict]) -> str:
    order = ("CEO_CFO", "OTHER_OFFICER", "DIRECTOR", "TEN_PERCENT_OWNER", "OTHER")
    classes = {o["role_class"] for o in owners}
    for role in order:
        if role in classes:
            return role
    return "OTHER"


def _iso(text: str | None) -> str | None:
    try:
        value = parse_sec_date(text)
    except SecParseError:
        return None
    return value.isoformat() if value else None


# --- cross-quarter uniqueness ---------------------------------------------------

def check_cross_quarter_duplicates(per_quarter: Mapping[str, array]) -> dict:
    """Raise DuplicateAccessionError if any accession appears in two quarters."""
    combined = array("Q")
    sorted_by_quarter: dict[str, array] = {}
    for quarter, accs in per_quarter.items():
        ordered = array("Q", sorted(accs))
        sorted_by_quarter[quarter] = ordered
        combined.extend(ordered)
    everything = sorted(combined)
    dups = sorted({a for a, b in zip(everything, everything[1:]) if a == b})
    if dups:
        details = []
        for value in dups[:50]:
            where = [q for q, arr in sorted_by_quarter.items()
                     if _contains(arr, value)]
            text = f"{value:018d}"
            details.append({"accession": f"{text[:10]}-{text[10:12]}-{text[12:]}",
                            "quarters": where})
        raise DuplicateAccessionError(
            f"{len(dups)} accession(s) appear in more than one quarter: {details[:10]}")
    return {"submission_accessions_checked": len(everything), "duplicates": 0}


def _contains(arr: array, value: int) -> bool:
    i = bisect.bisect_left(arr, value)
    return i < len(arr) and arr[i] == value


# --- issuer filing-day aggregation ------------------------------------------------

def aggregate_issuer_days(events: Iterable[Mapping[str, Any]]) -> list[dict]:
    groups: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for event in events:
        groups[(event["issuer_cik"], event["filing_date"])].append(event)
    out = []
    for (issuer, filing_date), members in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        owners = sorted({c for e in members for c in e["owner_ciks"]})
        od = sorted({c for e in members for c in e["od_owner_ciks"]})
        lags = [e["filing_lag_days"] for e in members if e["filing_lag_days"] is not None]
        tickers = sorted({e["ticker_as_filed"] for e in members if e["ticker_as_filed"]})
        out.append({
            "schema": ISSUER_DAY_SCHEMA,
            "issuer_cik": issuer,
            "filing_date": filing_date,
            "available_after_date": filing_date,
            "entry_rule": ENTRY_RULE,
            "accessions": sorted(e["accession"] for e in members),
            "n_accessions": len(members),
            "owner_ciks": owners,
            "od_owner_ciks": od,
            "value_usd": round(sum(e["value_usd"] for e in members), 2),
            "od_value_usd": round(sum(e["value_usd"] for e in members
                                      if e["any_officer_or_director"]), 2),
            "max_accession_value_usd": max(e["value_usd"] for e in members),
            "any_officer_or_director": any(e["any_officer_or_director"] for e in members),
            "any_ceo_cfo": any(e["any_ceo_cfo"] for e in members),
            "any_other_officer": any(e["any_other_officer"] for e in members),
            "any_director": any(e["any_director"] for e in members),
            "primary_role_class": _primary_role([o for e in members for o in e["owners"]]),
            "ceo_cfo_value_usd": round(sum(e["value_usd"] for e in members
                                           if e["any_ceo_cfo"]), 2),
            "any_ten_percent_owner": any(e["any_ten_percent_owner"] for e in members),
            "min_filing_lag_days": min(lags) if lags else None,
            "max_filing_lag_days": max(lags) if lags else None,
            "tickers_as_filed": tickers,
            "ticker_is_pit_security_mapping": False,
        })
    return out


# --- compact primary table ------------------------------------------------------------

COMPACT_SCHEMA = "fastlane.primary_event.compact.v1"
COMPACT_FIELDS = {
    "accession": "unique key",
    "quarter": "source data-set quarter",
    "issuer_cik": "issuer CIK (10 digits)",
    "filing_date": "EDGAR FILING_DATE = available_after_date; entry at the first vendor "
                   "session strictly after it",
    "ticker_as_filed": "ISSUERTRADINGSYMBOL as filed; NOT a PIT security mapping",
    "value_usd": "sum of shares x reported per-share figure over kept rows (0 if unreported)",
    "shares": "sum of shares over kept rows",
    "filing_lag_days": "FILING_DATE - earliest TRANS_DATE (calendar days)",
    "owners": "[owner_cik, role_class, is_director, is_officer, is_ten_percent_owner]",
    "tx": "[trans_date, shares, per-share figure or null, direct_indirect] per kept row",
}
DATA_EXPORT_LIMIT_BYTES = 25_000_000


def to_compact(event: Mapping[str, Any]) -> dict:
    return {
        "accession": event["accession"],
        "quarter": event["quarter"],
        "issuer_cik": event["issuer_cik"],
        "filing_date": event["filing_date"],
        "ticker_as_filed": event["ticker_as_filed"],
        "value_usd": event["value_usd"],
        "shares": event["shares"],
        "filing_lag_days": event["filing_lag_days"],
        "owners": [[o["owner_cik"], o["role_class"], int(o["is_director"]), int(o["is_officer"]),
                    int(o["is_ten_percent_owner"])] for o in event["owners"]],
        "tx": [[t["trans_date"], t["shares"], t["price_per_share"], t["direct_indirect"]]
               for t in event["transactions"]],
    }


# --- I/O --------------------------------------------------------------------------

def events_path(fw: Firewall) -> Path:
    """Unfiltered base population (sensitivity only)."""
    return fw.data("derived", "events_v1.jsonl.gz")


def primary_full_path(fw: Firewall) -> Path:
    return fw.data("derived", "events_primary_full_v1.jsonl.gz")


def primary_table_candidates(fw: Firewall) -> tuple[Path, Path]:
    return (fw.artifact("data", "events_primary_v1.jsonl.gz"),
            fw.data("derived", "events_primary_v1.jsonl.gz"))


def issuer_days_path(fw: Firewall) -> Path:
    return fw.data("derived", "issuer_days_v1.jsonl.gz")


def build_manifest_path(fw: Firewall) -> Path:
    return fw.data("derived", "events_build_manifest_v1.json")


def write_jsonl_gz(fw: Firewall, path: Path, records: Iterable[Mapping[str, Any]]) -> tuple[str, int]:
    """Deterministic gzip JSONL (mtime=0, sorted keys); atomic replace."""
    target = fw.guard(path, write=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    count = 0
    with open(tmp, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            for record in records:
                gz.write((json.dumps(record, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
                count += 1
        raw.flush()
        os.fsync(raw.fileno())
    os.replace(tmp, target)
    return sha256_file(target), count


def read_jsonl_gz(fw: Firewall, path: Path) -> Iterator[dict]:
    source = fw.guard(path, write=False)
    with gzip.open(source, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def code_fingerprint() -> str:
    here = Path(__file__).resolve().parent
    parts = []
    for name in ("events.py", "sec_insider.py"):
        parts.append(name + ":" + sha256_file(here / name))
    return "sha256:" + sha256_bytes("|".join(parts).encode("utf-8"))


def _write_primary_table(fw: Firewall, compact: list[dict]) -> dict:
    """Write the compact primary table to research/ if small enough, else to var/."""
    committed, local = primary_table_candidates(fw)
    sha, rows = write_jsonl_gz(fw, local, compact)
    size = local.stat().st_size
    if size <= DATA_EXPORT_LIMIT_BYTES:
        committed.parent.mkdir(parents=True, exist_ok=True)
        os.replace(local, committed)
        target, location = committed, "research/fastlane/data (committable)"
    else:
        if committed.exists():
            committed.unlink()           # never leave a stale committed copy behind
        target, location = local, "var/fastlane/derived (too large to commit)"
    return {"relpath": target.relative_to(fw.repo_root).as_posix(), "sha256": sha, "rows": rows,
            "bytes": size, "location": location, "limit_bytes": DATA_EXPORT_LIMIT_BYTES,
            "schema": COMPACT_SCHEMA, "fields": COMPACT_FIELDS}


def build_all(fw: Firewall, quarters: list[str], *, log=print) -> dict:
    """Build base and primary event tables from fetched, manifest-verified zips."""
    counters = BuildCounters()
    per_quarter_accs: dict[str, array] = {}
    all_events: list[dict] = []
    primary_events: list[dict] = []
    inputs = []
    table_stats = {}
    for quarter in sorted(quarters, key=quarter_key):
        manifest = load_manifest(fw, quarter)
        if manifest is None:
            raise FileNotFoundError(f"no manifest for {quarter}; run fetch-insider first")
        zip_path = fw.guard(raw_path(fw, quarter), write=False)
        digest = sha256_file(zip_path)
        if digest != manifest["sha256"]:
            raise ValueError(f"{quarter}: zip sha256 {digest} != manifest {manifest['sha256']}")
        result = build_quarter(zip_path, quarter, counters, digest)
        per_quarter_accs[quarter] = result.accession_ints
        all_events.extend(result.events)
        primary_events.extend(result.primary_events)
        table_stats[quarter] = result.table_stats
        inputs.append({"quarter": quarter, "sha256": digest,
                       "fingerprint": manifest.get("fingerprint")})
        log(f"{quarter}: {len(result.events)} events, {len(result.primary_events)} primary")
    dup = check_cross_quarter_duplicates(per_quarter_accs)
    seen: dict[str, str] = {}
    for event in all_events:
        if event["accession"] in seen:
            raise DuplicateAccessionError(
                f"event accession {event['accession']} built twice "
                f"({seen[event['accession']]}, {event['quarter']})")
        seen[event["accession"]] = event["quarter"]
    all_events.sort(key=lambda e: (e["filing_date"], e["accession"]))
    primary, dropped = dedupe_first_seen(primary_events, counters)
    counters.population["primary_events"] = len(primary)
    counters.population["primary_transaction_rows"] = sum(e["n_transactions"] for e in primary)
    ev_sha, ev_rows = write_jsonl_gz(fw, events_path(fw), all_events)
    full_sha, full_rows = write_jsonl_gz(fw, primary_full_path(fw), primary)
    table = _write_primary_table(fw, [to_compact(e) for e in primary])
    days = aggregate_issuer_days(primary)
    day_sha, day_rows = write_jsonl_gz(fw, issuer_days_path(fw), days)
    fw.write_json_atomic(fw.data("derived", "primary_duplicates_v1.json"),
                         {"dropped_then_kept": dropped})
    malformed = {q: {s["member"]: s["malformed_rows"] for s in stats}
                 for q, stats in table_stats.items()}
    manifest = {
        "lineage": LINEAGE_ID,
        "schema": {"events": EVENT_SCHEMA, "issuer_days": ISSUER_DAY_SCHEMA,
                   "primary_table": COMPACT_SCHEMA},
        "code_fingerprint": code_fingerprint(),
        "population_rule": {
            "document_type": "exactly '4' (4/A, 3, 3/A, 5, 5/A excluded)",
            "table": "NONDERIV_TRANS",
            "trans_code": "P",
            "acquired_disposed": "A",
            "backdating": "accession sequence year > FILING_DATE year -> excluded; same-year "
                          "backdating cannot be detected from the data sets (residual risk)",
            "available_after_date": "FILING_DATE",
            "entry_rule": ENTRY_RULE,
            "ticker": "as filed (ISSUERTRADINGSYMBOL); not a PIT security mapping",
            "unique_key": "ACCESSION_NUMBER; duplicates are errors",
            "roles": "relationship flags only; CEO/CFO = Officer flag + CEO/CFO title",
        },
        "primary_filters": {
            "security_title_include_regex": SECURITY_TITLE_INCLUDE,
            "security_title_exclude_regex": SECURITY_TITLE_EXCLUDE,
            "security_title_normalization": "upper case, whitespace collapsed; re.search",
            "footnote_exclusion_regex": FOOTNOTE_EXCLUSION,
            "footnote_scope": "footnotes referenced by any *_FN column of the row, plus the "
                              "filing REMARKS; case-insensitive",
            "dedupe": "first-seen by (FILING_DATE, accession) on (issuer, sorted owner CIKs, "
                      "sorted (trans_date, shares, per-share figure) tuples)",
        },
        "inputs": inputs,
        "outputs": {
            "events_unfiltered": {"path": events_path(fw).relative_to(fw.repo_root).as_posix(),
                                  "sha256": ev_sha, "rows": ev_rows},
            "events_primary_full": {
                "path": primary_full_path(fw).relative_to(fw.repo_root).as_posix(),
                "sha256": full_sha, "rows": full_rows},
            "primary_table": table,
            "issuer_days": {"path": issuer_days_path(fw).relative_to(fw.repo_root).as_posix(),
                            "sha256": day_sha, "rows": day_rows},
        },
        "counts": counters.as_dict(),
        "duplicate_accession_check": dup,
        "malformed_rows_by_quarter": malformed,
        "table_columns_by_quarter": {q: {s["member"]: s["columns"] for s in stats}
                                     for q, stats in table_stats.items()},
    }
    fw.write_json_atomic(build_manifest_path(fw), manifest)
    return manifest
