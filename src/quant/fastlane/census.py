"""Outcome-blind census of fast-lane purchase events.

Reads only filing-derived event tables: the compact *primary* table (the
population the protocol evaluates) and, as a sensitivity, the unfiltered base
table. It never touches prices, returns, market caps or delisting status;
:func:`assert_outcome_blind` rejects any census object whose keys name such a
field before it is written.

Unit of an *entry event* is the issuer filing day (issuer CIK x FILING_DATE).

Candidate filter families (all expressible from filing data):

``ALL_P``                 any primary purchase
``OD``                    >=1 officer/director owner (relationship flags only)
``CEO_CFO``               >=1 owner with the Officer flag and a CEO/CFO title
``OD_CLUSTER_10CD``       crossing <2 -> >=2 distinct O/D *decision units* at one
                          issuer over filing dates [d-9, d], re-armed only after the
                          window count falls below 2. Owners on the same accession,
                          or reporting an identical (date, shares, per-share) row at
                          the issuer, are merged into one unit (PIT: merges use
                          only filings up to d)
``FROZEN_FV_PROXY_10WD``  the frozen first-vertical signal taken literally (D07
                          §2.1-2.2: two distinct O/D CIKs, trailing 10 regular
                          sessions, crossing <2 -> >=2, re-arm below two) with
                          sessions APPROXIMATED by weekdays; a rate estimate only
``FROZEN_FV_PROXY_10WD_MERGED``  sensitivity: the same with decision-unit merging

Non-frozen families' cluster metrics use the merged decision units.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping

from quant.fastlane.events import (build_manifest_path, events_path, read_jsonl_gz,
                                   to_compact)
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.preregistration import SPLITS

CENSUS_SCHEMA = "fastlane.census.v2"
FAMILIES = ("ALL_P", "OD", "CEO_CFO", "OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD",
            "FROZEN_FV_PROXY_10WD_MERGED")
SENSITIVITY_FAMILIES = ("FROZEN_FV_PROXY_10WD_MERGED",)
CROSSING_FAMILIES = ("OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD", "FROZEN_FV_PROXY_10WD_MERGED")
VALUE_TIERS = (("ge_10k", 10_000.0), ("ge_100k", 100_000.0), ("ge_1m", 1_000_000.0))
CLUSTER_WINDOW = 10
FROZEN_DEFINITION_SOURCE = "governance/D07_OPEN_SPACE_BOUNDARY.md"
STANDARD_TICKER_RE = re.compile(r"[A-Z]{1,5}([.\-][A-Z]{1,2})?")
PLACEHOLDER_TICKERS = frozenset({"NA", "NONE", "NULL", "N"})

# Keys that would indicate outcome-bearing content. Checked on every census key.
FORBIDDEN_KEY_TOKENS = ("price", "return", "ret_", "market_cap", "marketcap", "mcap",
                        "delist", "close", "volume", "adv20", "alpha", "sharpe", "pnl",
                        "drawdown", "excess")
# The only event fields the census reads (all filing-derived).
CENSUS_INPUT_FIELDS = ("accession", "issuer_cik", "filing_date", "value_usd", "filing_lag_days",
                       "ticker_as_filed", "owners", "tx")


class OutcomeLeak(ValueError):
    pass


def assert_outcome_blind(obj: Any, path: str = "$") -> None:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            lowered = str(key).lower()
            for token in FORBIDDEN_KEY_TOKENS:
                if token in lowered:
                    raise OutcomeLeak(f"census key {path}.{key} names outcome field {token!r}")
            assert_outcome_blind(value, f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            assert_outcome_blind(value, f"{path}[{i}]")


# --- compact event view ---------------------------------------------------------

@dataclass(frozen=True)
class Owner:
    cik: str
    role_class: str
    od: bool
    director: bool
    ten_pct: bool


@dataclass(frozen=True)
class Ev:
    accession: str
    issuer: str
    day: date
    value: float
    lag: int | None
    ticker_missing: bool
    owners: tuple[Owner, ...]
    tx: frozenset = field(default_factory=frozenset)


def compact(row: Mapping[str, Any]) -> Ev:
    """Read one compact primary-table row (see ``events.COMPACT_FIELDS``)."""
    owners = tuple(Owner(o[0], o[1], bool(o[2]) or bool(o[3]), bool(o[2]), bool(o[4]))
                   for o in row["owners"])
    ticker = row.get("ticker_as_filed") or ""
    tx = frozenset((t[0], float(t[1]), None if t[2] is None else float(t[2]))
                   for t in row.get("tx", []))
    return Ev(row["accession"], row["issuer_cik"], date.fromisoformat(row["filing_date"]),
              float(row["value_usd"]), row["filing_lag_days"],
              ticker in PLACEHOLDER_TICKERS or not STANDARD_TICKER_RE.fullmatch(ticker),
              owners, tx)


def family_owners(family: str, ev: Ev) -> set[str]:
    if family == "ALL_P":
        return {o.cik for o in ev.owners}
    if family in ("OD", "OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD",
                  "FROZEN_FV_PROXY_10WD_MERGED"):
        return {o.cik for o in ev.owners if o.od}
    if family == "CEO_CFO":
        return {o.cik for o in ev.owners if o.role_class == "CEO_CFO"}
    raise KeyError(family)


def merges_owners(family: str) -> bool:
    return family != "FROZEN_FV_PROXY_10WD"


def weekday_index(day: date) -> int:
    """Weekday counter; a weekend date maps to the next Monday (O1 NEXT)."""
    o = day.toordinal() - 1          # 0 = Monday 0001-01-01
    week, dow = divmod(o, 7)
    return week * 5 + (dow if dow < 5 else 5)


def calendar_index(day: date) -> int:
    return day.toordinal()


@dataclass
class DayRow:
    issuer: str
    day: date
    events: list[Ev]
    owners: set[str]
    value: float
    member: bool = False           # >=2 distinct family units in window
    crossing: bool = False         # <2 -> >=2 with re-arm
    window_value: float = 0.0


class _Units:
    """Incremental union-find of owner CIKs into decision units (PIT)."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.tx_owner: dict[tuple, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)

    def absorb(self, owners: list[str], tx: Iterable[tuple]) -> None:
        if not owners:
            return
        head = owners[0]
        for other in owners[1:]:
            self.union(head, other)
        for t in tx:
            if t in self.tx_owner:
                self.union(self.tx_owner[t], head)
            else:
                self.tx_owner[t] = head


def crossings(days: list[DayRow], index, window: int, *, family: str = "",
              merge: bool = False) -> None:
    """Mark window membership and threshold crossings for one issuer's days (sorted).

    Expiry precedes same-day additions (D07 WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS).
    With ``merge``, distinct counts are over decision units built from filings up
    to and including the current day only.
    """
    last_seen: dict[str, int] = {}
    values: list[tuple[int, float]] = []
    units = _Units()
    armed = True

    def count() -> int:
        return len({units.find(c) for c in last_seen}) if merge else len(last_seen)

    for row in days:
        idx = index(row.day)
        for cik in [c for c, i in last_seen.items() if i <= idx - window]:
            del last_seen[cik]
        values = [(i, v) for i, v in values if i > idx - window]
        if count() < 2:
            armed = True
        if merge:
            for ev in row.events:
                units.absorb(sorted(family_owners(family, ev)), sorted(ev.tx, key=repr))
        for cik in row.owners:
            last_seen[cik] = idx
        values.append((idx, row.value))
        row.window_value = sum(v for _, v in values)
        row.member = count() >= 2
        if armed and row.member:
            row.crossing = True
            armed = False


def family_days(family: str, events: list[Ev]) -> list[DayRow]:
    """Issuer filing days that are entry events for ``family``."""
    by_issuer_day: dict[tuple[str, date], list[Ev]] = defaultdict(list)
    for ev in events:
        if family_owners(family, ev):
            by_issuer_day[(ev.issuer, ev.day)].append(ev)
    rows_by_issuer: dict[str, list[DayRow]] = defaultdict(list)
    for (issuer, day), evs in by_issuer_day.items():
        evs.sort(key=lambda e: e.accession)
        owners = set().union(*(family_owners(family, e) for e in evs))
        rows_by_issuer[issuer].append(DayRow(issuer, day, evs, owners, sum(e.value for e in evs)))
    index = weekday_index if family.startswith("FROZEN") else calendar_index
    out: list[DayRow] = []
    for issuer, rows in rows_by_issuer.items():
        rows.sort(key=lambda r: r.day)
        crossings(rows, index, CLUSTER_WINDOW, family=family, merge=merges_owners(family))
        if family in CROSSING_FAMILIES:
            out.extend(r for r in rows if r.crossing)
        else:
            out.extend(rows)
    out.sort(key=lambda r: (r.day, r.issuer))
    return out


# --- metrics ----------------------------------------------------------------------

def _quantile(sorted_values: list[int], q: float) -> int | None:
    if not sorted_values:
        return None
    rank = max(1, min(len(sorted_values), int(-(-q * len(sorted_values) // 1))))
    return sorted_values[rank - 1]


def lag_distribution(lags: Iterable[int | None]) -> dict:
    values = list(lags)
    known = sorted(v for v in values if v is not None)
    n = len(known)
    return {
        "n": n,
        "missing": len(values) - n,
        "negative": sum(1 for v in known if v < 0),
        "p10": _quantile(known, 0.10), "p25": _quantile(known, 0.25),
        "p50": _quantile(known, 0.50), "p75": _quantile(known, 0.75),
        "p90": _quantile(known, 0.90), "p99": _quantile(known, 0.99),
        "max": known[-1] if known else None,
        "share_le_2d": round(sum(1 for v in known if 0 <= v <= 2) / n, 4) if n else None,
        "share_gt_2d": round(sum(1 for v in known if v > 2) / n, 4) if n else None,
        "share_gt_30d": round(sum(1 for v in known if v > 30) / n, 4) if n else None,
    }


def metrics(family: str, rows: list[DayRow], years: float | None) -> dict:
    tier_value = (lambda r: r.window_value) if family in CROSSING_FAMILIES else (lambda r: r.value)
    accessions = [e for r in rows for e in r.events]
    roles = Counter()
    primary = Counter()
    order = ("CEO_CFO", "OTHER_OFFICER", "DIRECTOR", "TEN_PERCENT_OWNER", "OTHER")
    for r in rows:
        classes = {o.role_class for e in r.events for o in e.owners}
        roles["any_ceo_cfo"] += "CEO_CFO" in classes
        roles["any_other_officer"] += "OTHER_OFFICER" in classes
        roles["any_director"] += any(o.director for e in r.events for o in e.owners)
        roles["any_ten_percent_owner"] += any(o.ten_pct for e in r.events for o in e.owners)
        primary[next((c for c in order if c in classes), "OTHER")] += 1
    tiers = {name: sum(1 for r in rows if tier_value(r) >= floor) for name, floor in VALUE_TIERS}
    return {
        "issuer_days": len(rows),
        "per_year": round(len(rows) / years, 1) if years else None,
        "accessions": len(accessions),
        "unique_issuers": len({r.issuer for r in rows}),
        "value_tiers_issuer_days": tiers,
        "value_tiers_per_year": ({k: round(v / years, 1) for k, v in tiers.items()}
                                 if years else None),
        "roles_issuer_days": dict(roles),
        "primary_role_issuer_days": dict(primary),
        "cluster_member_issuer_days": sum(1 for r in rows if r.member),
        "cluster_formations": sum(1 for r in rows if r.crossing),
        "filing_lag_days": lag_distribution(e.lag for e in accessions),
        "ticker_as_filed_nonstandard_issuer_days": sum(1 for r in rows
                                                       if all(e.ticker_missing for e in r.events)),
    }


def split_years(name: str) -> float:
    start, end = SPLITS[name]
    return round(((end - start).days + 1) / 365.25, 2)


def census(rows: Iterable[Mapping[str, Any]], *, with_years: bool = True) -> dict:
    """Census over compact rows (see ``events.COMPACT_FIELDS``)."""
    evs = [compact(r) for r in rows]
    result: dict[str, Any] = {"by_split": {}}
    if with_years:
        result["by_year"] = {}
    for family in FAMILIES:
        fam_rows = family_days(family, evs)
        by_split: dict[str, list[DayRow]] = defaultdict(list)
        by_year: dict[int, list[DayRow]] = defaultdict(list)
        for r in fam_rows:
            by_year[r.day.year].append(r)
            for name, (start, end) in SPLITS.items():
                if start <= r.day <= end:
                    by_split[name].append(r)
        for name in SPLITS:
            result["by_split"].setdefault(name, {})[family] = metrics(
                family, by_split.get(name, []), split_years(name))
        if with_years:
            for year in sorted(by_year):
                result["by_year"].setdefault(str(year), {})[family] = metrics(
                    family, by_year[year], None)
    first = min((e.day for e in evs), default=None)
    last = max((e.day for e in evs), default=None)
    result["coverage"] = {"first_filing_date": first.isoformat() if first else None,
                          "last_filing_date": last.isoformat() if last else None,
                          "events_accession_level": len(evs)}
    return result


def definitions() -> dict:
    return {
        "entry_event_unit": "issuer CIK x FILING_DATE (available_after_date); entry at the first "
                            "vendor session strictly after it",
        "families": {
            "ALL_P": "any primary purchase",
            "OD": "at least one officer/director owner by relationship flag (10%-only and "
                  "Other-only excluded; titles never promote)",
            "CEO_CFO": "at least one owner with the Officer relationship flag and a CEO/CFO title",
            "OD_CLUSTER_10CD": "crossing <2 -> >=2 distinct O/D decision units over filing dates "
                               "[d-9,d], re-armed below 2; owners on one accession or with an "
                               "identical (date, shares, per-share) row are one unit (PIT merge)",
            "FROZEN_FV_PROXY_10WD": "frozen first-vertical signal taken literally (distinct O/D "
                                    "CIKs, D07 2.1-2.2) with regular sessions approximated by "
                                    "weekdays; rate estimate only, not the frozen object",
            "FROZEN_FV_PROXY_10WD_MERGED": "SENSITIVITY: the frozen proxy with decision-unit "
                                           "merging; not a grid family",
        },
        "value_tiers": {name: floor for name, floor in VALUE_TIERS},
        "value_basis": "sum of reported shares x reported per-share figure on the issuer day "
                       "(window sum for crossing families); rows without a reported per-share "
                       "figure contribute 0",
        "cluster_rule": "per family: >=2 distinct family-qualifying decision units (literal CIKs "
                        "for the frozen family) at one issuer over filing dates [d-9, d]; "
                        "formations use <2 -> >=2 crossings with re-arm",
        "roles": "CEO_CFO = Officer flag + CEO/CFO title; OTHER_OFFICER = Officer flag otherwise; "
                 "DIRECTOR; TEN_PERCENT_OWNER; OTHER. Role counts are non-exclusive; primary "
                 "role uses that precedence",
        "filing_lag": "FILING_DATE - earliest TRANS_DATE of the accession's kept rows, "
                      "calendar days",
        "splits": {k: {"start": v[0].isoformat(), "end": v[1].isoformat(),
                       "years": split_years(k)} for k, v in SPLITS.items()},
        "frozen_definition_source": FROZEN_DEFINITION_SOURCE,
        "populations": {
            "primary": "original Form 4 P/A, common-equity titles, frozen footnote/remarks "
                       "exclusions, exact duplicates removed (first seen), backdated "
                       "accessions excluded",
            "unfiltered": "SENSITIVITY ONLY: original Form 4 P/A with backdated accessions "
                          "excluded, before title/footnote/duplicate filters",
        },
    }


def run_census(fw: Firewall) -> dict:
    build_manifest = fw.read_json(build_manifest_path(fw))
    table = build_manifest["outputs"]["primary_table"]
    table_path = fw.guard(fw.repo_root / table["relpath"], write=False)
    if fw.sha256_file(table_path) != table["sha256"]:
        raise ValueError("primary table bytes differ from the build manifest")
    body = census(read_jsonl_gz(fw, table_path))
    sensitivity = None
    if events_path(fw).exists():
        sensitivity = census((to_compact(e) for e in read_jsonl_gz(fw, events_path(fw))),
                             with_years=False)
    try:
        frozen_sha = fw.sha256_file(fw.repo_root / FROZEN_DEFINITION_SOURCE)
    except (OSError, PermissionError):
        frozen_sha = None
    sec_manifest = fw.artifact("sec_insider_manifest_v1.json")
    doc = {
        "schema": CENSUS_SCHEMA,
        "lineage": LINEAGE_ID,
        "outcome_blind": True,
        "outcome_fields_read": [],
        "input_fields_read": list(CENSUS_INPUT_FIELDS),
        "inputs": {
            "events_sha256": table["sha256"],
            "events_relpath": table["relpath"],
            "events_rows": table["rows"],
            "events_code_fingerprint": build_manifest["code_fingerprint"],
            "unfiltered_events_sha256": build_manifest["outputs"]["events_unfiltered"]["sha256"],
            "sec_manifest_set_fingerprint": (fw.read_json(sec_manifest).get("set_fingerprint")
                                             if sec_manifest.exists() else None),
            "frozen_definition_sha256": frozen_sha,
            "build_counts": {k: build_manifest["counts"][k] for k in (
                "excluded_transaction_rows", "excluded_P_A_rows_by_document_type",
                "primary_excluded_transaction_rows",
                "primary_footnote_exclusion_rows_by_category", "population")},
        },
        "definitions": definitions(),
        **body,
        "sensitivity_unfiltered": sensitivity,
    }
    doc["headline"] = headline(doc)
    assert_outcome_blind(doc)
    fw.write_json_atomic(fw.artifact("census_v1.json"), doc)
    fw.write_text_atomic(fw.artifact("census_v1.md"), render_markdown(doc))
    return doc


def headline(doc: Mapping[str, Any]) -> dict:
    out = {}
    for split in SPLITS:
        out[split] = {f: {"per_year": m["per_year"], "issuer_days": m["issuer_days"],
                          "unique_issuers": m["unique_issuers"],
                          "cluster_formations": m["cluster_formations"]}
                      for f, m in doc["by_split"][split].items()}
    return out


def render_markdown(doc: Mapping[str, Any]) -> str:
    counts = doc["inputs"]["build_counts"]
    lines = [
        f"# Fast-lane census v1 — `{LINEAGE_ID}`",
        "",
        "Outcome-blind: built only from SEC Insider Transactions Data Sets filing fields. "
        "No prices, returns, market caps or delisting status were read.",
        "",
        f"Coverage: {doc['coverage']['first_filing_date']} → {doc['coverage']['last_filing_date']}, "
        f"{doc['coverage']['events_accession_level']} primary accessions "
        f"(`{doc['inputs']['events_relpath']}`, sha256 `{doc['inputs']['events_sha256'][:16]}…`).",
        "",
        "Primary population: original Form 4 P/A, common-equity titles, frozen footnote/"
        "remarks exclusions, exact duplicates removed, backdated accessions excluded. "
        "Entry-event unit: issuer × filing date.",
        "",
        "Row exclusions (base): " + ", ".join(
            f"{k} {v}" for k, v in counts["excluded_transaction_rows"].items()) + ".",
        "",
        "Row exclusions (primary): " + ", ".join(
            f"{k} {v}" for k, v in counts["primary_excluded_transaction_rows"].items()) + "; "
        "footnote categories: " + ", ".join(
            f"{k} {v}" for k, v in counts["primary_footnote_exclusion_rows_by_category"].items())
        + ".",
        "",
        "## Primary entry events per year by split",
        "",
        "| Family | Split | Issuer-days/yr | Issuer-days | Unique issuers | ≥$10k/yr | ≥$100k/yr | ≥$1M/yr | Cluster formations | Lag p50/p90 (d) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for family in FAMILIES:
        for split in SPLITS:
            m = doc["by_split"][split][family]
            t = m["value_tiers_per_year"] or {}
            lag = m["filing_lag_days"]
            lines.append(f"| {family} | {split} | {m['per_year']} | {m['issuer_days']} | "
                         f"{m['unique_issuers']} | {t.get('ge_10k')} | {t.get('ge_100k')} | "
                         f"{t.get('ge_1m')} | {m['cluster_formations']} | {lag['p50']}/{lag['p90']} |")
    sens = doc.get("sensitivity_unfiltered")
    if sens:
        lines += ["", "## Sensitivity: unfiltered population (issuer-days/yr)", "",
                  "| Family | " + " | ".join(SPLITS) + " |", "|---|" + "---:|" * len(SPLITS)]
        for family in FAMILIES:
            lines.append(f"| {family} | " + " | ".join(
                str(sens["by_split"][s][family]["per_year"]) for s in SPLITS) + " |")
    lines += ["", "## Primary issuer-days per calendar year", "",
              "| Year | " + " | ".join(FAMILIES) + " |",
              "|---|" + "---:|" * len(FAMILIES)]
    for year, fams in doc["by_year"].items():
        lines.append(f"| {year} | " + " | ".join(str(fams.get(f, {}).get("issuer_days", 0))
                                                for f in FAMILIES) + " |")
    lines += ["", "## Definitions", ""]
    for name, text in doc["definitions"]["families"].items():
        lines.append(f"- `{name}`: {text}.")
    lines += [
        "",
        "Caveats: tickers are as filed, not a point-in-time security mapping; the frozen "
        "proxies approximate regular sessions by weekdays; counts precede PIT security "
        "mapping and liquidity eligibility; the data sets are SEC-published extracts "
        "(fingerprinted in `sec_insider_manifest_v1.json`), not the raw XML; same-year "
        "backdating cannot be detected from the data sets.",
        "",
    ]
    return "\n".join(lines)
