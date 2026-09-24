"""Outcome-blind census of fast-lane purchase events.

Reads only the filing-derived event table (``var/fastlane/derived/
events_v1.jsonl.gz``). It never touches prices, returns, market caps or
delisting status; :func:`assert_outcome_blind` rejects any census object whose
keys name such a field before it is written.

Unit of an *entry event* is the issuer filing day (issuer CIK x FILING_DATE):
the date after which information is public and the portfolio could act.

Candidate filter families (all expressible from filing data):

``ALL_P``                 any original Form 4 P/A purchase
``OD``                    >=1 officer/director owner (frozen S01 qualification;
                          10%-only and Other-only owners excluded)
``CEO_CFO``               >=1 owner whose title is CEO or CFO
``OD_CLUSTER_10CD``       crossing <2 -> >=2 distinct O/D owner CIKs at one issuer
                          over filing dates [d-9, d] (10 calendar days), re-armed
                          only after the window count falls below 2
``FROZEN_FV_PROXY_10WD``  the frozen first-vertical signal (D07 §2.1-2.2: O/D,
                          two distinct CIKs, trailing 10 regular sessions,
                          crossing <2 -> >=2, re-arm below two) with sessions
                          APPROXIMATED by weekdays (no holiday calendar). It is a
                          rate estimate only, not the frozen object: exact
                          sessions come from the vendor calendar.

"Cluster" metrics per family use the same crossing rule on that family's
qualifying owners over [d-9, d] calendar days, measured on filing dates (PIT).
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping

from quant.fastlane.events import events_path, read_jsonl_gz
from quant.fastlane.firewall import LINEAGE_ID, Firewall
from quant.fastlane.preregistration import SPLITS

CENSUS_SCHEMA = "fastlane.census.v1"
FAMILIES = ("ALL_P", "OD", "CEO_CFO", "OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD")
VALUE_TIERS = (("ge_10k", 10_000.0), ("ge_100k", 100_000.0), ("ge_1m", 1_000_000.0))
CLUSTER_WINDOW = 10
# As-filed symbols that are empty, "N/A", "(NONE)", multi-class lists, exchange
# prefixes, etc. are counted as non-standard (a PIT mapping must resolve them).
STANDARD_TICKER_RE = re.compile(r"[A-Z]{1,5}([.\-][A-Z]{1,2})?")
PLACEHOLDER_TICKERS = frozenset({"NA", "NONE", "NULL", "N"})
FROZEN_DEFINITION_SOURCE = "governance/D07_OPEN_SPACE_BOUNDARY.md"

# Keys that would indicate outcome-bearing content. Checked on every census key.
FORBIDDEN_KEY_TOKENS = ("price", "return", "ret_", "market_cap", "marketcap", "mcap",
                        "delist", "close", "volume", "adv20", "alpha", "sharpe", "pnl",
                        "drawdown", "excess")
# The only event fields the census reads (all filing-derived).
CENSUS_INPUT_FIELDS = ("accession", "issuer_cik", "filing_date", "value_usd", "filing_lag_days",
                       "ticker_as_filed", "owners")


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


def compact(event: Mapping[str, Any]) -> Ev:
    owners = tuple(Owner(o["owner_cik"], o["role_class"], bool(o["officer_or_director"]),
                         bool(o["is_director"]), bool(o["is_ten_percent_owner"]))
                   for o in event["owners"])
    ticker = event.get("ticker_as_filed") or ""
    return Ev(event["accession"], event["issuer_cik"], date.fromisoformat(event["filing_date"]),
              float(event["value_usd"]), event["filing_lag_days"],
              ticker in PLACEHOLDER_TICKERS or not STANDARD_TICKER_RE.fullmatch(ticker), owners)


def family_owners(family: str, ev: Ev) -> set[str]:
    if family == "ALL_P":
        return {o.cik for o in ev.owners}
    if family in ("OD", "OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD"):
        return {o.cik for o in ev.owners if o.od}
    if family == "CEO_CFO":
        return {o.cik for o in ev.owners if o.role_class == "CEO_CFO"}
    raise KeyError(family)


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
    member: bool = False           # >=2 distinct family owners in window
    crossing: bool = False         # <2 -> >=2 with re-arm
    window_value: float = 0.0


def crossings(days: list[DayRow], index, window: int) -> None:
    """Mark window membership and threshold crossings for one issuer's days (sorted)."""
    last_seen: dict[str, int] = {}
    values: list[tuple[int, float]] = []
    armed = True
    for row in days:
        idx = index(row.day)
        for cik in [c for c, i in last_seen.items() if i <= idx - window]:
            del last_seen[cik]
        values = [(i, v) for i, v in values if i > idx - window]
        if len(last_seen) < 2:
            armed = True
        for cik in row.owners:
            last_seen[cik] = idx
        values.append((idx, row.value))
        row.window_value = sum(v for _, v in values)
        row.member = len(last_seen) >= 2
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
        owners = set().union(*(family_owners(family, e) for e in evs))
        rows_by_issuer[issuer].append(DayRow(issuer, day, evs, owners, sum(e.value for e in evs)))
    out: list[DayRow] = []
    for issuer, rows in rows_by_issuer.items():
        rows.sort(key=lambda r: r.day)
        if family == "FROZEN_FV_PROXY_10WD":
            crossings(rows, weekday_index, CLUSTER_WINDOW)
        else:
            crossings(rows, calendar_index, CLUSTER_WINDOW)
        if family in ("OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD"):
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
    cluster_family = family in ("OD_CLUSTER_10CD", "FROZEN_FV_PROXY_10WD")
    tier_value = (lambda r: r.window_value) if cluster_family else (lambda r: r.value)
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
    out = {
        "issuer_days": len(rows),
        "per_year": round(len(rows) / years, 1) if years else None,
        "accessions": len(accessions),
        "unique_issuers": len({r.issuer for r in rows}),
        "value_tiers_issuer_days": {name: sum(1 for r in rows if tier_value(r) >= floor)
                                    for name, floor in VALUE_TIERS},
        "value_tiers_per_year": ({name: round(sum(1 for r in rows if tier_value(r) >= floor) / years, 1)
                                  for name, floor in VALUE_TIERS} if years else None),
        "roles_issuer_days": dict(roles),
        "primary_role_issuer_days": dict(primary),
        "cluster_member_issuer_days": sum(1 for r in rows if r.member),
        "cluster_formations": sum(1 for r in rows if r.crossing),
        "filing_lag_days": lag_distribution(e.lag for e in accessions),
        "ticker_as_filed_nonstandard_issuer_days": sum(1 for r in rows
                                                   if all(e.ticker_missing for e in r.events)),
    }
    return out


def split_years(name: str) -> float:
    start, end = SPLITS[name]
    return round(((end - start).days + 1) / 365.25, 2)


def census(events: Iterable[Mapping[str, Any]]) -> dict:
    evs = [compact(e) for e in events]
    result: dict[str, Any] = {"by_split": {}, "by_year": {}}
    for family in FAMILIES:
        rows = family_days(family, evs)
        by_split: dict[str, list[DayRow]] = defaultdict(list)
        by_year: dict[int, list[DayRow]] = defaultdict(list)
        for r in rows:
            by_year[r.day.year].append(r)
            for name, (start, end) in SPLITS.items():
                if start <= r.day <= end:
                    by_split[name].append(r)
        for name in SPLITS:
            result["by_split"].setdefault(name, {})[family] = metrics(
                family, by_split.get(name, []), split_years(name))
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
            "ALL_P": "any original Form 4 non-derivative P/A purchase",
            "OD": "at least one officer/director reporting owner (10%-only/Other-only excluded)",
            "CEO_CFO": "at least one owner whose title matches CEO or CFO",
            "OD_CLUSTER_10CD": "crossing <2 -> >=2 distinct O/D owner CIKs over filing dates "
                               "[d-9,d], re-armed only after the window count falls below 2",
            "FROZEN_FV_PROXY_10WD": "frozen first-vertical signal (D07 2.1-2.2) with regular "
                                    "sessions approximated by weekdays (no holidays); rate "
                                    "estimate only, not the frozen object",
        },
        "value_tiers": {name: floor for name, floor in VALUE_TIERS},
        "value_basis": "sum of reported shares x reported transaction value per share on the "
                       "issuer day (window sum for crossing families); rows without a reported "
                       "per-share figure contribute 0",
        "cluster_rule": "per family: >=2 distinct family-qualifying owner CIKs at one issuer over "
                        "filing dates [d-9, d]; formations use <2 -> >=2 crossings with re-arm",
        "roles": "CEO_CFO by title regex; OTHER_OFFICER = officer flag without CEO/CFO title; "
                 "DIRECTOR; TEN_PERCENT_OWNER; OTHER. Role counts are non-exclusive; primary "
                 "role uses that precedence",
        "filing_lag": "FILING_DATE - earliest TRANS_DATE of the accession's qualifying rows, "
                      "calendar days",
        "splits": {k: {"start": v[0].isoformat(), "end": v[1].isoformat(),
                       "years": split_years(k)} for k, v in SPLITS.items()},
        "frozen_definition_source": FROZEN_DEFINITION_SOURCE,
    }


def run_census(fw: Firewall) -> dict:
    events_file = events_path(fw)
    build_manifest = fw.read_json(fw.data("derived", "events_build_manifest_v1.json"))
    body = census(read_jsonl_gz(fw, events_file))
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
            "events_sha256": build_manifest["outputs"]["events"]["sha256"],
            "events_rows": build_manifest["outputs"]["events"]["rows"],
            "events_code_fingerprint": build_manifest["code_fingerprint"],
            "sec_manifest_set_fingerprint": (fw.read_json(sec_manifest).get("set_fingerprint")
                                             if sec_manifest.exists() else None),
            "frozen_definition_sha256": frozen_sha,
        },
        "definitions": definitions(),
        **body,
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
    lines = [
        f"# Fast-lane census v1 — `{LINEAGE_ID}`",
        "",
        "Outcome-blind: built only from SEC Insider Transactions Data Sets filing fields. "
        "No prices, returns, market caps or delisting status were read.",
        "",
        f"Coverage: {doc['coverage']['first_filing_date']} → {doc['coverage']['last_filing_date']}, "
        f"{doc['coverage']['events_accession_level']} original Form 4 P/A accessions. "
        f"Events input `{doc['inputs']['events_sha256'][:16]}…`.",
        "",
        "Entry-event unit: issuer × filing date. Value tiers use the reported transaction "
        "value (window sum for the crossing families).",
        "",
        "## Entry events per year by split",
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
    lines += ["", "## Issuer-days per calendar year", "",
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
        "Caveats: tickers are as filed, not a point-in-time security mapping; the "
        "`FROZEN_FV_PROXY_10WD` family approximates regular sessions by weekdays; the data "
        "sets are SEC-published extracts (fingerprinted in `sec_insider_manifest_v1.json`), "
        "not the raw XML.",
        "",
    ]
    return "\n".join(lines)
