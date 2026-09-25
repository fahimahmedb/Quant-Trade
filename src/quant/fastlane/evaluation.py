"""Calendar-time portfolio evaluation for ``QUANT_FASTLANE_HPIT_V1`` (sealed protocol).

From the sealed protocol, one variant, the bound primary event table, a
granted :class:`~quant.fastlane.prices.PriceVendor` and that vendor's session
calendar, :func:`evaluate_variant` builds the paper calendar-time portfolio
and its daily ``r_ex,t`` series. Every rule below is the sealed text; the
choices the text leaves open are recorded, with the conservative option taken,
in ``research/fastlane/PROTOCOL_CLARIFICATIONS_PRE_OUTCOME.md`` (C-numbers).

Selection (outcome-blind): issuer filing days of the variant's family
(``OD``/``CEO_CFO`` via :func:`quant.fastlane.census.family_days`;
``FROZEN_FV_10S`` = the literal D07 crossing <2 -> >=2 distinct O/D CIKs over
10 *vendor* sessions, EDGAR dates projected to the next vendor session, C1)
whose value reaches the variant floor, assigned to the split by FILING_DATE.

Entry: open of the first vendor session strictly after FILING_DATE. Purge
(discovery, walk-forward): events whose scheduled exit session e+h-1 falls
after the split end are excluded (logged). A holdout exit beyond the vendor
calendar refuses the evaluation (C17).

Pre-entry eligibility (only bars strictly before the entry session): PIT
security mapping as of the entry session, exactly one security (C11); bars on
each of the 20 vendor sessions before entry (C10); ADV20 = mean raw close x
raw volume over them, finite and > 0; last close >= USD 1; ADV20 >= USD 100k.
A missing entry bar skips the event (counted). Admission: K = 100 slots by
(entry session, sealed seeded tie-break), one slot per issuer, time-based
release (:func:`quant.fastlane.constructor.admit_detailed`). Allocation
``a_j = min(m C0 / K, 0.001 ADV20)``; fractional shares (C9).

Holding: buy-and-hold on invested capital, total return from raw prices plus
the SPLIT / CASH_DIVIDEND action ledger; a mid-hold missing bar carries the last
close (C8). Exit at the close of e+h-1; missing exit bar -> next available open
within 20 sessions; else the delisting treatment from the last traded price by
class (C6, C7). Frictions (:mod:`quant.fastlane.frictions`) on the entry and
exit legs, inputs from the sessions before each leg (C5).

Return: ``r_ex,t = sum_i w_{i,t-1} (r_{i,t} - r_SPY,t) / sum_i w_{i,t-1}`` over
sessions with invested capital; idle cash earns 0 % and is reported separately,
never in alpha; ``alpha = 252 x mean r_ex``. Scenarios: ``net`` (primary: base
frictions, base delisting), ``gross``, ``net_friction_stress`` (2x),
``net_delisting_stress`` (UNKNOWN -100 %).

Outputs are deterministic and carry a fingerprint of the code, the sealed
protocol, the event table and the vendor identity/manifests.
"""

from __future__ import annotations

import bisect
import hashlib
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from quant.fastlane import census
from quant.fastlane import constructor as ct
from quant.fastlane import frictions as fr
from quant.fastlane import holdout as ho
from quant.fastlane import prices as px
from quant.fastlane.events import read_jsonl_gz
from quant.fastlane.firewall import LINEAGE_ID, Firewall, sha256_bytes
from quant.fastlane.holdout import code_fingerprint
from quant.fastlane.preregistration import (SPLITS, OutcomeAccessGrant, OutcomeAccessRefused,
                                            benchmark_manifest_path, canonical_json,
                                            delisting_map_path)

SCHEMA = "fastlane.variant_evaluation.v1"
TRADING_DAYS = 252
ADV_WINDOW = 20
VOL_WINDOW = 20
MISSING_EXIT_LOOKAHEAD = 20
MAX_CALENDAR_GAP_DAYS = 7
FROZEN_FAMILY = "FROZEN_FV_10S"
CENSUS_FAMILY = {"OD": "OD", "CEO_CFO": "CEO_CFO", FROZEN_FAMILY: "FROZEN_FV_PROXY_10WD"}
FORMATION_SESSION_RULE = "NEXT_REGULAR_SESSION"
FROZEN_WINDOW_SESSIONS = census.CLUSTER_WINDOW

PRIMARY_SCENARIO = "net"
SCENARIO_RULES = {                     # (friction mode, delisting scenario)
    "gross": ("none", "base"),
    "net": ("base", "base"),
    "net_friction_stress": ("stress", "base"),
    "net_delisting_stress": ("base", "stress"),
}
SCENARIOS = tuple(SCENARIO_RULES)

REASON_FLOOR = "below_value_floor"
REASON_PURGED = "purged_exit_after_split_end"
REASON_UNMAPPED = "unmapped_security"
REASON_AMBIGUOUS = "ambiguous_security_mapping"
REASON_BARS = "incomplete_20_bars_before_entry"
REASON_ADV = "adv20_not_finite_positive"
REASON_PRICE = "last_close_below_min"
REASON_UNTRADEABLE = "untradeable_adv20"
REASON_ENTRY_BAR = "missing_entry_bar"
REASONS = (REASON_FLOOR, REASON_PURGED, REASON_UNMAPPED, REASON_AMBIGUOUS, REASON_BARS,
           REASON_ADV, REASON_PRICE, REASON_UNTRADEABLE, REASON_ENTRY_BAR,
           ct.REJECT_ISSUER_ACTIVE, ct.REJECT_BOOK_FULL)
PRE_ENTRY_REASONS = frozenset({REASON_UNMAPPED, REASON_AMBIGUOUS, REASON_BARS, REASON_ADV,
                               REASON_PRICE, REASON_UNTRADEABLE})

EXIT_CLOSE = "SCHEDULED_CLOSE"
EXIT_NEXT_OPEN = "NEXT_AVAILABLE_OPEN"
EXIT_DELISTING = "DELISTING_TREATMENT"

# Sealed rule texts this engine implements; any other text is refused.
SEALED_TEXT = {
    "timing.entry": "open of the first vendor session strictly after available_after_date",
    "timing.available_after_date": "FILING_DATE",
    "execution.missing_entry_bar": "no vendor bar at the entry session -> no fill",
    "execution.missing_exit_bar": "exit at the next available open; if none within 20 sessions, "
                                  "apply the delisting treatment from the last traded price",
    "constructor.allocation": "ADV20 = mean of raw_close*raw_volume over the 20 completed vendor "
                              "sessions before entry",
    "constructor.slot_release": "time-based at the scheduled exit close",
    "universe_eligibility.bars": "20 complete vendor bars before entry",
    "return_object.formula": "r_ex,t = sum_i w_{i,t-1} (r_{i,t} - r_SPY,t) / sum_i w_{i,t-1}",
    "return_object.annualized_alpha": "252 x arithmetic mean of r_ex,t over the split's sessions "
                                      "with at least one open position",
    "purge": "events whose scheduled exit session falls after the split end are excluded",
    "frictions.spread.variant": "two_day_corrected_mean",
    "frictions.impact.formula": "k * sigma_daily * sqrt(Q / ADV20)",
}


class EvaluationError(RuntimeError):
    pass


class CalendarIncomplete(EvaluationError):
    """The vendor calendar does not cover what the sealed rules need."""


class BenchmarkMissing(EvaluationError):
    """No SPY total return for a session with invested capital (no fallback)."""


class VendorMismatch(EvaluationError):
    pass


def _get(obj: Mapping[str, Any], dotted: str) -> Any:
    node: Any = obj
    for part in dotted.split("."):
        if not isinstance(node, Mapping) or part not in node:
            return None
        node = node[part]
    return node


def check_sealed_text(protocol: Mapping[str, Any]) -> None:
    for dotted, needle in SEALED_TEXT.items():
        value = _get(protocol, dotted)
        if not isinstance(value, str) or needle not in value:
            raise EvaluationError(f"sealed rule {dotted} does not say {needle!r}; this engine "
                                  "implements only that text")


def digest(obj: Any) -> str:
    return "sha256:" + sha256_bytes(canonical_json(obj))


# --- protocol parameters --------------------------------------------------------------------

@dataclass(frozen=True)
class Params:
    slots: int
    c0_usd: float
    min_last_close_usd: float
    spread_window: int
    tie_break_seed: int
    frictions: fr.FrictionParams

    @classmethod
    def from_protocol(cls, protocol: Mapping[str, Any]) -> "Params":
        check_sealed_text(protocol)
        return cls(
            slots=int(protocol["constructor"]["slots"]),
            c0_usd=float(protocol["constructor"]["C0_usd"]),
            min_last_close_usd=float(protocol["universe_eligibility"]["min_last_close_usd"]),
            spread_window=int(protocol["frictions"]["spread"]["window_sessions"]),
            tie_break_seed=int(protocol["inference"]["bootstrap_seed"]),
            frictions=fr.FrictionParams.from_protocol(protocol["frictions"]),
        )


@dataclass(frozen=True)
class Variant:
    variant_id: str
    family: str
    horizon: int
    value_floor_usd: float

    @classmethod
    def from_protocol(cls, protocol: Mapping[str, Any], variant_id: str) -> "Variant":
        for v in protocol["variants"]:
            if v["variant_id"] == variant_id:
                h = int(v["horizon_sessions"])
                expected = (f"regular close of vendor session e+{h - 1} ({h} sessions including "
                            "entry session e)")
                if v.get("exit") != expected:
                    raise EvaluationError(f"{variant_id}: exit rule {v.get('exit')!r} is not "
                                          f"the implemented {expected!r}")
                if v["family"] not in CENSUS_FAMILY:
                    raise EvaluationError(f"{variant_id}: unknown family {v['family']!r}")
                return cls(variant_id, v["family"], h, float(v["value_floor_usd"]))
        raise EvaluationError(f"variant {variant_id!r} is not in the sealed grid")


# --- event table ------------------------------------------------------------------------------

class EventTable:
    """The bound compact primary table, read through census.compact (filing data only)."""

    def __init__(self, rows: Iterable[Mapping[str, Any]], source: Mapping[str, Any] | None = None):
        rows = sorted(rows, key=lambda r: r["accession"])
        h = hashlib.sha256()
        seen = set()
        for row in rows:
            if row["accession"] in seen:
                raise EvaluationError(f"duplicate accession {row['accession']} in the event table")
            seen.add(row["accession"])
            h.update(canonical_json(row) + b"\n")
        self.digest = "sha256:" + h.hexdigest()
        self.rows = len(rows)
        self.source = dict(source or {"kind": "rows"})
        self.events = [census.compact(r) for r in rows]
        self._family: dict[str, list[census.DayRow]] = {}
        self._frozen: dict[str, list[census.DayRow]] = {}

    @classmethod
    def load_bound(cls, fw: Firewall, protocol: Mapping[str, Any]) -> "EventTable":
        binding = protocol["census_binding"]
        rel = binding["events_relpath"]
        path = fw.guard(fw.repo_root / rel, write=False)
        sha = fw.sha256_file(path)
        if sha != str(binding["events_sha256"]).replace("sha256:", ""):
            raise EvaluationError(f"event table {rel} sha256 {sha} != sealed binding")
        return cls(read_jsonl_gz(fw, path), {"kind": "bound_file", "relpath": rel,
                                              "file_sha256": sha})

    def family_rows(self, family: str) -> list[census.DayRow]:
        if family not in self._family:
            self._family[family] = census.family_days(CENSUS_FAMILY[family], self.events)
        return self._family[family]

    def frozen_rows(self, calendar: Sequence[date]) -> list[census.DayRow]:
        """Literal D07 crossings on vendor sessions (distinct O/D CIKs, no merging)."""
        key = digest([d.isoformat() for d in calendar])
        if key in self._frozen:
            return self._frozen[key]
        fam = CENSUS_FAMILY[FROZEN_FAMILY]
        first, last = calendar[0], calendar[-1]
        by_issuer_day: dict[tuple[str, date], list[census.Ev]] = defaultdict(list)
        for ev in self.events:
            if first <= ev.day <= last and census.family_owners(fam, ev):
                by_issuer_day[(ev.issuer, ev.day)].append(ev)
        per_issuer: dict[str, list[census.DayRow]] = defaultdict(list)
        for (issuer, day), evs in by_issuer_day.items():
            evs.sort(key=lambda e: e.accession)
            owners = set().union(*(census.family_owners(fam, e) for e in evs))
            per_issuer[issuer].append(census.DayRow(issuer, day, evs, owners,
                                                    sum(e.value for e in evs)))

        def formation_session(day: date) -> int:       # C1: NEXT_REGULAR_SESSION
            return bisect.bisect_left(calendar, day)

        out: list[census.DayRow] = []
        for rows in per_issuer.values():
            rows.sort(key=lambda r: r.day)
            census.crossings(rows, formation_session, FROZEN_WINDOW_SESSIONS, family=fam,
                             merge=False)
            out.extend(r for r in rows if r.crossing)
        out.sort(key=lambda r: (r.day, r.issuer))
        self._frozen[key] = out
        return out


# --- vendor context and market data -------------------------------------------------------------

class VendorContext:
    """Committed vendor manifests plus the vendor's attestation, cross-checked."""

    def __init__(self, fw: Firewall, vendor: px.PriceVendor) -> None:
        if not isinstance(vendor, px.PriceVendor):
            raise TypeError("vendor does not implement the PriceVendor protocol")
        self.vendor = vendor
        paths = {"delisting_map": delisting_map_path(fw),
                 "benchmark_manifest": benchmark_manifest_path(fw)}
        for name, path in paths.items():
            if not path.exists():
                raise OutcomeAccessRefused(f"vendor manifest {path.name} is missing")
        raw_map = fw.read_json(paths["delisting_map"])
        self.delisting_map = px.validate_delisting_map(raw_map)
        self.benchmark = px.validate_benchmark_manifest(fw.read_json(paths["benchmark_manifest"]))
        for name, manifest in (("delisting map", raw_map), ("benchmark manifest", self.benchmark)):
            if manifest.get("vendor_id") != vendor.vendor_id:
                raise VendorMismatch(f"{name} names vendor {manifest.get('vendor_id')!r}, not "
                                     f"{vendor.vendor_id!r}")
        self.attestation = vendor.attestation()
        if self.attestation.vendor_id != vendor.vendor_id:
            raise VendorMismatch("attestation names another vendor")
        self.manifest_sha256 = {name: fw.sha256_file(path) for name, path in paths.items()}

    def identity(self) -> dict:
        return {"vendor_id": self.vendor.vendor_id, "attestation": asdict(self.attestation),
                "evidence_label": self.attestation.evidence_label,
                "manifest_sha256": dict(sorted(self.manifest_sha256.items()))}


def _valid_bar(bar: px.DailyBar) -> bool:
    values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        return False
    return (bar.open > 0 and bar.low > 0 and bar.low <= bar.close <= bar.high
            and bar.volume >= 0)


class MarketData:
    """Granted, cached vendor reads for one split (bars keyed by calendar index)."""

    def __init__(self, vendor: px.PriceVendor, grant: OutcomeAccessGrant, split: str) -> None:
        if type(grant) is not OutcomeAccessGrant:
            raise OutcomeAccessRefused("market data needs an OutcomeAccessGrant")
        if grant.split != split:
            raise OutcomeAccessRefused(f"grant is for {grant.split}, not {split}")
        start, end = grant.price_window_start, grant.price_window_end
        px.check_grant(grant, start, end)
        self.vendor, self.grant, self.split = vendor, grant, split
        self.fw = Firewall(Path(grant.repo_root))
        self.vendor_identity = VendorContext(self.fw, vendor).identity()
        self.window = (start, end)
        sessions = list(vendor.sessions(start, end, grant=grant))
        self.calendar = self._check_calendar(sessions, split, start, end)
        self.index = {d: i for i, d in enumerate(self.calendar)}
        self.quality: Counter = Counter()
        self._bars: dict[str, dict[int, px.DailyBar]] = {}
        self._actions: dict[str, tuple[list[tuple[int, int]], list[px.CorporateAction]]] = {}
        self._delist: dict[str, list[px.CorporateAction]] = {}
        self._maps: dict[str, list[px.SecurityMapping]] = {}
        self._spy: dict[int, float] | None = None
        self._spy_intraday: dict[int, float] | None = None
        self._candidates: dict[str, list[Candidate]] = {}
        self._legs: dict[tuple[str, int], dict] = {}

    @staticmethod
    def _check_calendar(sessions: list, split: str, start: date, end: date) -> list[date]:
        if not sessions:
            raise CalendarIncomplete("vendor returned no sessions")
        if any(not isinstance(d, date) for d in sessions):
            raise CalendarIncomplete("vendor sessions must be dates")
        if any(b <= a for a, b in zip(sessions, sessions[1:])):
            raise CalendarIncomplete("vendor sessions must be strictly increasing")
        if sessions[0] < start or sessions[-1] > end:
            raise CalendarIncomplete("vendor sessions leave the grant window")
        gaps = [(a, b) for a, b in zip(sessions, sessions[1:])
                if (b - a).days > MAX_CALENDAR_GAP_DAYS]
        if gaps:
            raise CalendarIncomplete(f"vendor calendar has {len(gaps)} gap(s) longer than "
                                     f"{MAX_CALENDAR_GAP_DAYS} days, first {gaps[0]}")
        split_start, split_end = SPLITS[split]
        if bisect.bisect_left(sessions, split_start) < max(ADV_WINDOW, FROZEN_WINDOW_SESSIONS) + 1:
            raise CalendarIncomplete(f"fewer than {ADV_WINDOW + 1} vendor sessions before "
                                     f"{split_start}")
        if split == "holdout":
            if sessions[-1] <= split_end:
                raise CalendarIncomplete("holdout calendar does not extend past the split end")
        elif sessions[-1] < split_end - timedelta(days=MAX_CALENDAR_GAP_DAYS):
            raise CalendarIncomplete(f"{split} calendar ends {sessions[-1]}, before {split_end}")
        return sessions

    # -- vendor reads (each goes through the vendor's own grant check) --
    def bars(self, security_id: str) -> dict[int, px.DailyBar]:
        if security_id not in self._bars:
            out: dict[int, px.DailyBar] = {}
            for bar in self.vendor.daily_bars(security_id, *self.window, grant=self.grant):
                i = self.index.get(bar.session)
                if bar.security_id != security_id:
                    self.quality["bar_other_security"] += 1
                elif i is None:
                    self.quality["bar_off_calendar"] += 1
                elif not _valid_bar(bar):
                    self.quality["bar_malformed_dropped"] += 1
                elif i in out:
                    self.quality["bar_duplicate_dropped"] += 1
                else:
                    out[i] = bar
            self._bars[security_id] = out
        return self._bars[security_id]

    def _load_actions(self, security_id: str) -> None:
        if security_id in self._actions:
            return
        keyed, delist = [], []
        for act in self.vendor.corporate_actions(security_id, *self.window, grant=self.grant):
            if act.security_id != security_id:
                self.quality["action_other_security"] += 1
                continue
            if act.kind == px.ACTION_DELISTING:
                delist.append(act)
                continue
            if act.kind not in (px.ACTION_SPLIT, px.ACTION_CASH_DIVIDEND):
                self.quality[f"action_unhandled:{act.kind}"] += 1
                continue
            v = act.value
            ok = isinstance(v, (int, float)) and math.isfinite(v) and (
                v > 0 if act.kind == px.ACTION_SPLIT else v >= 0)
            if not ok:
                self.quality["action_malformed_dropped"] += 1
                continue
            i = bisect.bisect_left(self.calendar, act.ex_date)     # non-session -> next session
            if i >= len(self.calendar):
                continue
            keyed.append(((i, 0 if act.kind == px.ACTION_SPLIT else 1), act))
        keyed.sort(key=lambda kv: (kv[0], kv[1].kind, kv[1].value))
        self._actions[security_id] = ([k for k, _ in keyed], [a for _, a in keyed])
        self._delist[security_id] = sorted(delist, key=lambda a: (a.ex_date, str(a.code)))

    def actions_between(self, security_id: str, after: int, upto: int) -> list[px.CorporateAction]:
        """SPLIT/CASH_DIVIDEND actions with ex-session index in (after, upto]."""
        self._load_actions(security_id)
        keys, acts = self._actions[security_id]
        lo = bisect.bisect_left(keys, (after + 1, -1))
        hi = bisect.bisect_left(keys, (upto + 1, -1))
        return acts[lo:hi]

    def delistings(self, security_id: str) -> list[px.CorporateAction]:
        self._load_actions(security_id)
        return self._delist[security_id]

    def mappings(self, cik: str) -> list[px.SecurityMapping]:
        if cik not in self._maps:
            maps = self.vendor.security_mappings(cik, grant=self.grant)
            self._maps[cik] = [m for m in px.clip_mappings(maps, self.grant) if m.cik == cik]
        return self._maps[cik]

    def spy_returns(self) -> dict[int, float]:
        if self._spy is None:
            out: dict[int, float] = {}
            raw = self.vendor.benchmark_total_returns(*self.window, grant=self.grant)
            for day, value in raw.items():
                i = self.index.get(day)
                if i is None:
                    self.quality["spy_off_calendar"] += 1
                    continue
                if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= -1:
                    raise BenchmarkMissing(f"SPY total return on {day} is invalid: {value!r}")
                out[i] = float(value)
            self._spy = out
        return self._spy

    def spy_intraday(self) -> dict[int, float] | None:
        """Optional SPY open-to-close returns (C2 bias diagnostic only; never gating)."""
        fetch = getattr(self.vendor, "benchmark_intraday_returns", None)
        if fetch is None:
            return None
        if self._spy_intraday is None:
            out: dict[int, float] = {}
            for day, value in fetch(*self.window, grant=self.grant).items():
                i = self.index.get(day)
                if (i is not None and isinstance(value, (int, float)) and math.isfinite(value)
                        and value > -1):
                    out[i] = float(value)
            self._spy_intraday = out
        return self._spy_intraday

    # -- total-return arithmetic on raw prices plus the action ledger --
    def gross_return(self, security_id: str, frm: int, frm_price: float, to: int,
                     to_price: float) -> float:
        shares, cash = 1.0, 0.0
        for act in self.actions_between(security_id, frm, to):
            if act.kind == px.ACTION_SPLIT:
                shares *= act.value
            else:
                cash += act.value * shares
        return (shares * to_price + cash) / frm_price - 1.0

    def pair_factor(self, security_id: str, t: int, bars: Mapping[int, px.DailyBar]) -> float:
        """Scale for session t's prices that removes actions on (t, t+1]."""
        nxt = bars[t + 1].close
        g = self.gross_return(security_id, t, bars[t].close, t + 1, nxt)
        return nxt / ((1.0 + g) * bars[t].close)


# --- outcome-access accounting --------------------------------------------------------------------

def access_config_digest(market: MarketData, table: EventTable, seed: int,
                         c0_multiple: float) -> str:
    return digest({"prereg_sha256": market.grant.prereg_sha256, "events_digest": table.digest,
                   "vendor": market.vendor_identity, "seed": int(seed),
                   "c0_multiple": float(c0_multiple)})


def record_access(market: MarketData, variant_id: str, table: EventTable, seed: int,
                  c0_multiple: float) -> None:
    """Append (idempotently) the discovery/walk-forward read BEFORE any outcome is read.

    Keyed by (variant, split, configuration, code fingerprint); a screen and its
    recomputations reuse one key per variant and split, while any other seed, capacity
    multiple, code or vendor configuration is a new key and raises N_trials (C22).
    """
    if market.split == "holdout":
        return                          # the holdout is governed by the one-look request
    ho.AccessLedger(market.fw).record(
        variant_id=variant_id, split=market.split,
        config_digest=access_config_digest(market, table, seed, c0_multiple),
        prereg_sha256=market.grant.prereg_sha256)


# --- candidates and eligibility ------------------------------------------------------------------

@dataclass
class Candidate:
    issuer: str
    filing_date: date
    accessions: tuple[str, ...]
    value_usd: float
    entry_index: int | None = None
    reason: str | None = None
    security_id: str | None = None
    adv20: float | None = None
    last_close: float | None = None

    @property
    def pre_entry_eligible(self) -> bool:
        return self.reason is None or self.reason == REASON_ENTRY_BAR


def pre_entry_eligibility(market: MarketData, cik: str, e: int,
                          params: Params) -> tuple[str | None, dict]:
    """Uses only the mapping as of the entry session and bars strictly before it."""
    day = market.calendar[e]
    sids = sorted({m.security_id for m in market.mappings(cik)
                   if m.valid_from <= day and (m.valid_to is None or day <= m.valid_to)})
    if not sids:
        return REASON_UNMAPPED, {}
    if len(sids) > 1:
        return REASON_AMBIGUOUS, {"candidates": sids}
    sid = sids[0]
    bars = market.bars(sid)
    window = range(e - ADV_WINDOW, e)
    if e < ADV_WINDOW or any(i not in bars for i in window):
        return REASON_BARS, {"security_id": sid}
    adv20 = sum(bars[i].close * bars[i].volume for i in window) / ADV_WINDOW
    if not math.isfinite(adv20) or adv20 <= 0:
        return REASON_ADV, {"security_id": sid}
    last_close = bars[e - 1].close
    info = {"security_id": sid, "adv20": adv20, "last_close": last_close}
    if last_close < params.min_last_close_usd:
        return REASON_PRICE, info
    if not fr.is_tradeable(adv20, params.frictions):
        return REASON_UNTRADEABLE, info
    return None, info


def candidates(variant: Variant, table: EventTable, market: MarketData,
               params: Params) -> list[Candidate]:
    """Every issuer-day of the variant in the split, with its exclusion reason (or None)."""
    key = f"{variant.variant_id}|{table.digest}"
    cached = market._candidates.get(key)
    if cached is not None:
        return cached
    record_access(market, variant.variant_id, table, params.tie_break_seed, 1.0)
    cal = market.calendar
    split_start, split_end = SPLITS[market.split]
    if variant.family == FROZEN_FAMILY:
        rows = table.frozen_rows(cal)
    else:
        rows = table.family_rows(variant.family)
    out: list[Candidate] = []
    beyond: list[str] = []
    for row in rows:
        if not split_start <= row.day <= split_end:
            continue
        value = row.window_value if variant.family == FROZEN_FAMILY else row.value
        cand = Candidate(row.issuer, row.day, tuple(sorted(e.accession for e in row.events)),
                         float(value))
        out.append(cand)
        if value < variant.value_floor_usd:
            cand.reason = REASON_FLOOR
            continue
        e = bisect.bisect_right(cal, row.day)
        x = e + variant.horizon - 1
        if x >= len(cal) or (market.split != "holdout" and cal[x] > split_end):
            if market.split == "holdout":
                beyond.append(row.day.isoformat())
                continue
            cand.reason = REASON_PURGED
            continue
        cand.entry_index = e
        reason, info = pre_entry_eligibility(market, row.issuer, e, params)
        cand.security_id = info.get("security_id")
        cand.adv20 = info.get("adv20")
        cand.last_close = info.get("last_close")
        if reason is None and e not in market.bars(cand.security_id):
            reason = REASON_ENTRY_BAR
        cand.reason = reason
    if beyond:
        raise CalendarIncomplete(f"{len(beyond)} holdout events have a scheduled exit beyond the "
                                 f"vendor calendar (last {market.calendar[-1]}); first filing "
                                 f"{beyond[0]}")
    market._candidates[key] = out
    return out


def adequacy_counts(variant: Variant, table: EventTable, market: MarketData,
                    params: Params) -> dict:
    """Post-eligibility recheck input: pre-entry-eligible issuer-days per split year."""
    cands = candidates(variant, table, market, params)
    eligible = sum(1 for c in cands if c.reason != REASON_FLOOR and c.reason != REASON_PURGED
                   and c.pre_entry_eligible)
    years = census.split_years(market.split)
    return {"split": market.split, "pre_entry_eligible_issuer_days": eligible,
            "years": years, "per_year": eligible / years}


# --- positions ---------------------------------------------------------------------------------

def leg_inputs(market: MarketData, sid: str, leg: int, params: Params) -> dict:
    """ADV20, daily volatility and Abdi-Ranaldo spread from the sessions before a leg."""
    key = (sid, leg)
    if key not in market._legs:
        market._legs[key] = _leg_inputs(market, sid, leg, params)
    return dict(market._legs[key])


def _leg_inputs(market: MarketData, sid: str, leg: int, params: Params) -> dict:
    bars = market.bars(sid)
    present = [i for i in range(max(0, leg - ADV_WINDOW), leg) if i in bars]
    adv = (sum(bars[i].close * bars[i].volume for i in present) / len(present)) if present else None
    rets = []
    for t in range(max(1, leg - VOL_WINDOW), leg):
        if t in bars and t - 1 in bars:
            g = market.gross_return(sid, t - 1, bars[t - 1].close, t, bars[t].close)
            rets.append(math.log1p(g))
    sigma = statistics.stdev(rets) if len(rets) >= 2 else None
    pairs = []
    for t in range(max(0, leg - params.spread_window), leg - 1):
        if t in bars and t + 1 in bars:
            f = market.pair_factor(sid, t, bars)
            b0, b1 = bars[t], bars[t + 1]
            pairs.append(fr.abdi_ranaldo_spread([b0.high * f, b1.high], [b0.low * f, b1.low],
                                                [b0.close * f, b1.close],
                                                variant=params.frictions.spread_variant,
                                                min_pairs=1))
    ar = sum(pairs) / len(pairs) if len(pairs) >= params.frictions.spread_min_pairs else None
    return {"adv20": adv if adv and math.isfinite(adv) and adv > 0 else None,
            "sigma": sigma, "ar_spread": ar, "spread_pairs": len(pairs)}


@dataclass
class Plan:
    cand: Candidate
    slot: int
    e: int
    x: int
    notional: float
    shares: float
    entry_leg: dict
    path: list[tuple[int, float]]
    exit_kind: str
    exit_index: int | None = None
    exit_price: float | None = None
    exit_leg: dict | None = None
    delist_index: int | None = None
    delisting_class: str | None = None
    delisting_source: str | None = None
    lookahead_truncated: bool = False


def delisting_class(market: MarketData, sid: str, last_bar: int,
                    mapping: Mapping[str, str]) -> tuple[str, str]:
    last_day = market.calendar[last_bar]
    for act in market.delistings(sid):
        if act.ex_date >= last_day:
            code = str(act.code) if act.code is not None else None
            if code is not None and code in mapping:
                return mapping[code], f"vendor_code:{code}"
            return "UNKNOWN", f"unmapped_vendor_code:{code}"
    return "UNKNOWN", "no_delisting_action"


def plan_position(market: MarketData, cand: Candidate, slot: int, variant: Variant,
                  params: Params, c0_multiple: float, delisting_map: Mapping[str, str]) -> Plan:
    sid = cand.security_id
    bars = market.bars(sid)
    n = len(market.calendar)
    e = cand.entry_index
    x = e + variant.horizon - 1
    entry = bars[e]
    target = c0_multiple * params.c0_usd / params.slots
    notional = fr.participation_capped_notional(target, cand.adv20,
                                                params.frictions.participation_cap_adv20)
    entry_leg = leg_inputs(market, sid, e, params)
    entry_leg["adv20"] = cand.adv20                       # pre-entry ADV20 (all 20 bars)
    plan = Plan(cand, slot, e, x, notional, notional / entry.open, entry_leg,
                [(e, entry.close / entry.open - 1.0)], EXIT_CLOSE)

    def hold(through: int) -> int:
        last = e
        for t in range(e + 1, through + 1):
            if t in bars:
                plan.path.append((t, market.gross_return(sid, last, bars[last].close, t,
                                                         bars[t].close)))
                last = t
            else:
                plan.path.append((t, 0.0))            # C8: stale carry, gap booked later
        return last

    if x in bars:
        hold(x)
        plan.exit_index, plan.exit_price = x, bars[x].close
    else:
        horizon_end = min(x + MISSING_EXIT_LOOKAHEAD, n - 1)
        plan.lookahead_truncated = x + MISSING_EXIT_LOOKAHEAD > n - 1
        y = next((i for i in range(x + 1, horizon_end + 1) if i in bars), None)
        if y is not None:
            last = hold(y - 1)
            plan.path.append((y, market.gross_return(sid, last, bars[last].close, y,
                                                     bars[y].open)))
            plan.exit_kind, plan.exit_index, plan.exit_price = EXIT_NEXT_OPEN, y, bars[y].open
        else:
            last_bar = max(i for i in range(e, x + 1) if i in bars)
            hold(last_bar)
            plan.exit_kind = EXIT_DELISTING
            plan.delist_index = last_bar + 1                # C6: booked after the last trade
            plan.delisting_class, plan.delisting_source = delisting_class(
                market, sid, last_bar, delisting_map)
    if plan.exit_index is not None:
        plan.exit_leg = leg_inputs(market, sid, plan.exit_index, params)
    return plan


def _leg_cost(notional: float, price: float, leg: dict, fallback: dict, params: Params,
              mode: str, *, entry: bool) -> float:
    if mode == "none":
        return 0.0
    adv = leg.get("adv20") or fallback["adv20"]
    sigma = leg.get("sigma")
    if sigma is None:
        sigma = fallback.get("sigma") or 0.0
    return fr.one_side_cost_usd(notional, notional / price, adv, sigma, leg.get("ar_spread"),
                                params.frictions, stress=(mode == "stress"),
                                require_tradeable=entry)["total_usd"]


def simulate(plan: Plan, scenario: str, params: Params) -> dict:
    """Daily (index, w_{t-1}, r_t) of one position under one scenario."""
    mode, delist_mode = SCENARIO_RULES[scenario]
    a = plan.notional
    entry_price = a / plan.shares
    c_in = _leg_cost(a, entry_price, plan.entry_leg, plan.entry_leg, params, mode, entry=True)
    c_out = 0.0
    rows: list[tuple[int, float, float]] = []
    value = a
    for idx, g in plan.path:
        w = value
        if w <= 0:
            raise EvaluationError("position value reached zero before its exit")
        value = a * (1.0 + g) - c_in if idx == plan.e else value * (1.0 + g)
        if idx == plan.exit_index:
            c_out = _leg_cost(value, plan.exit_price, plan.exit_leg, plan.entry_leg, params,
                              mode, entry=False)
            value -= c_out
        rows.append((idx, w, value / w - 1.0))
    if plan.delist_index is not None:
        extra = fr.delisting_extra_return(plan.delisting_class, delist_mode, params.frictions)
        w = value
        value = w * (1.0 + extra)
        rows.append((plan.delist_index, w, extra))
    return {"rows": rows, "final_value": value, "pnl": value - a, "cost_in": c_in,
            "cost_out": c_out}


# --- evaluation -----------------------------------------------------------------------------------

def fingerprint(*, sealed: Mapping[str, Any], table: EventTable, context: VendorContext,
                split: str, variant_id: str, seed: int, c0_multiple: float) -> dict:
    core = {"engine": SCHEMA, "lineage": LINEAGE_ID, "code_fingerprint": code_fingerprint(),
            "prereg_sha256": sealed["protocol_sha256"], "events_digest": table.digest,
            "vendor": context.identity(), "split": split, "variant_id": variant_id,
            "seed": seed, "c0_multiple": c0_multiple}
    return {**core, "digest": digest(core)}


def _series(contribs: Iterable[tuple[int, float, float]], spy: Mapping[int, float],
            calendar: Sequence[date]) -> dict:
    num: dict[int, float] = defaultdict(float)
    den: dict[int, float] = defaultdict(float)
    ret: dict[int, float] = defaultdict(float)
    for idx, w, r in contribs:
        num[idx] += w * r
        den[idx] += w
        ret[idx] += w * r
    active = sorted(i for i, d in den.items() if d > 0)
    if not active:
        return {"start_index": None, "r_ex": [], "invested": [], "r_spy": [], "w_r": []}
    missing = [calendar[i].isoformat() for i in active if i not in spy]
    if missing:
        raise BenchmarkMissing(f"no SPY total return for {len(missing)} invested session(s), "
                               f"first {missing[0]}; the benchmark has no fallback")
    start, end = active[0], active[-1]
    r_ex, invested, r_spy, w_r = [], [], [], []
    for i in range(start, end + 1):
        d = den.get(i, 0.0)
        s = spy.get(i)
        if d > 0:
            r_ex.append((num[i] - d * s) / d)
        else:
            r_ex.append(None)
        invested.append(d)
        r_spy.append(s)
        w_r.append(ret.get(i, 0.0))
    return {"start_index": start, "r_ex": r_ex, "invested": invested, "r_spy": r_spy,
            "w_r": w_r}


def evaluate_variant(*, sealed: Mapping[str, Any], variant_id: str, table: EventTable,
                     market: MarketData, context: VendorContext, seed: int | None = None,
                     c0_multiple: float = 1.0, scenarios: Sequence[str] = SCENARIOS,
                     keep_positions: bool = False) -> dict:
    """Build one variant's calendar-time portfolio in one granted split."""
    protocol = sealed["protocol"]
    if market.grant.prereg_sha256 != sealed["protocol_sha256"]:
        raise OutcomeAccessRefused("grant and seal disagree")
    px.check_grant(market.grant, *market.window)
    params = Params.from_protocol(protocol)
    variant = Variant.from_protocol(protocol, variant_id)
    seed = params.tie_break_seed if seed is None else int(seed)
    if not (isinstance(c0_multiple, (int, float)) and c0_multiple > 0):
        raise ValueError("c0_multiple must be positive")
    record_access(market, variant_id, table, seed, float(c0_multiple))
    cands = candidates(variant, table, market, params)
    counts = Counter(c.reason for c in cands if c.reason)
    ready = [c for c in cands if c.reason is None]
    by_key = {(c.issuer, c.entry_index, c.accessions): c for c in ready}
    admitted, rejected = ct.admit_detailed(
        [ct.Entry(c.entry_index, c.issuer, c.accessions) for c in ready],
        slots=params.slots, horizon=variant.horizon, seed=seed)
    for _, why in rejected:
        counts[why] += 1
    counts["admitted"] = len(admitted)
    counts["issuer_days_in_split"] = len(cands)
    plans = [plan_position(market, by_key[(a.entry.issuer, a.entry.entry_index,
                                           a.entry.accessions)],
                           a.slot, variant, params, float(c0_multiple), context.delisting_map)
             for a in admitted]
    exits = Counter(p.exit_kind for p in plans)
    delisted = Counter(p.delisting_class for p in plans if p.delisting_class)
    spy = market.spy_returns()
    series: dict[str, dict] = {}
    summary: dict[str, dict] = {}
    pnl_by_plan: dict[str, list[float]] = {}
    c0 = float(c0_multiple) * params.c0_usd
    primary_sims: list[dict] | None = None
    for scenario in scenarios:
        sims = [simulate(p, scenario, params) for p in plans]
        if scenario == PRIMARY_SCENARIO:
            primary_sims = sims
        s = _series((row for sim in sims for row in sim["rows"]), spy, market.calendar)
        active = [v for v in s["r_ex"] if v is not None]
        mean = sum(active) / len(active) if active else None
        summary[scenario] = {
            "alpha_annual": TRADING_DAYS * mean if mean is not None else None,
            "mean_daily_r_ex": mean, "active_sessions": len(active),
            "pnl_usd": sum(sim["pnl"] for sim in sims),
            "costs_usd": sum(sim["cost_in"] + sim["cost_out"] for sim in sims)}
        series[scenario] = s
        pnl_by_plan[scenario] = [sim["pnl"] for sim in sims]
    primary = series.get(PRIMARY_SCENARIO) or next(iter(series.values()))
    span = len(primary["r_ex"])
    idle = {}
    if span:
        util = [inv / c0 for inv in primary["invested"]]
        spy_span = [r for r in primary["r_spy"] if r is not None]
        idle = {
            "c0_usd": c0,
            "span_sessions": span,
            "utilization_mean_over_span": sum(util) / span,
            "idle_cash_share_mean_over_span": 1.0 - sum(util) / span,
            "c0_basis_return_annual_idle_cash_at_0": TRADING_DAYS * sum(primary["w_r"]) / (c0 * span),
            "spy_total_return_annual_same_span": (TRADING_DAYS * sum(spy_span) / len(spy_span)
                                                  if spy_span else None),
            "note": "idle cash earns 0 %; reported here only, never in alpha",
        }
    start_index = primary["start_index"]
    diagnostic = c2_bias_diagnostic(plans, primary_sims, series.get(PRIMARY_SCENARIO), spy,
                                    market.spy_intraday())
    result = {
        "schema": SCHEMA, "lineage": LINEAGE_ID, "variant_id": variant_id,
        "split": market.split, "seed": seed, "c0_multiple": float(c0_multiple),
        "fingerprint": fingerprint(sealed=sealed, table=table, context=context,
                                   split=market.split, variant_id=variant_id, seed=seed,
                                   c0_multiple=float(c0_multiple)),
        "rules": {"formation_session": FORMATION_SESSION_RULE, "horizon_sessions": variant.horizon,
                  "value_floor_usd": variant.value_floor_usd, "family": variant.family,
                  "slots": params.slots},
        "counts": {k: counts.get(k, 0) for k in (*REASONS, "admitted", "issuer_days_in_split")},
        "exits": dict(sorted(exits.items())),
        "delisting_classes": dict(sorted(delisted.items())),
        "lookahead_truncated": sum(1 for p in plans if p.lookahead_truncated),
        "admitted_digest": digest(sorted([p.cand.issuer, market.calendar[p.e].isoformat(),
                                          p.cand.security_id] for p in plans)),
        "series": {
            "start_index": start_index,
            "start_session": (market.calendar[start_index].isoformat()
                              if start_index is not None else None),
            "sessions": [market.calendar[start_index + i].isoformat() for i in range(span)],
            "r_ex": {k: v["r_ex"] for k, v in series.items()},
            "invested_usd": primary["invested"],
            "r_spy": primary["r_spy"],
        },
        "summary": summary,
        "idle_cash": idle,
        "c2_bias_diagnostic": diagnostic,
    }
    if keep_positions:
        result["positions"] = [{
            "issuer": p.cand.issuer, "filing_date": p.cand.filing_date.isoformat(),
            "accessions": list(p.cand.accessions), "security_id": p.cand.security_id,
            "slot": p.slot, "entry_session": market.calendar[p.e].isoformat(),
            "scheduled_exit_session": market.calendar[p.x].isoformat(),
            "exit_kind": p.exit_kind,
            "exit_session": (market.calendar[p.exit_index].isoformat()
                             if p.exit_index is not None else None),
            "delisting_session": (market.calendar[p.delist_index].isoformat()
                                  if p.delist_index is not None else None),
            "delisting_class": p.delisting_class, "delisting_source": p.delisting_source,
            "adv20_usd": p.cand.adv20, "notional_usd": p.notional,
            "pnl_usd": {k: v[i] for k, v in pnl_by_plan.items()},
        } for i, p in enumerate(plans)]
    result["output_digest"] = digest({k: result[k] for k in (
        "variant_id", "split", "seed", "c0_multiple", "counts", "exits", "delisting_classes",
        "admitted_digest", "series", "summary", "idle_cash", "c2_bias_diagnostic")})
    return result


def c2_bias_diagnostic(plans: Sequence[Plan], sims: Sequence[dict] | None,
                       net: Mapping[str, Any] | None, spy: Mapping[int, float],
                       intraday: Mapping[int, float] | None) -> dict:
    """Realized size of the C2 benchmark-timing terms in net alpha (non-gating diagnostic).

    Entry session: the position earns open->close but r_ex subtracts SPY close->close, i.e.
    also the SPY overnight return. Next-open exit: the position earns close->open but r_ex
    subtracts the whole SPY session, i.e. also r_SPY minus its overnight part. Each term is
    ``-252/T sum_t (w_share_t x term_t)`` over the T sessions with invested capital, which is
    the amount the literal sealed formula adds to alpha relative to a matched benchmark.
    """
    out: dict[str, Any] = {
        "label": "C2 bias diagnostic (REPORTING ONLY, non-gating)", "gating": False,
        "available": False, "entry_day_spy_overnight_term_annual": None,
        "next_open_exit_spy_intraday_term_annual": None, "total_annual": None,
        "sessions_missing_spy_open": 0}
    if sims is None or net is None or net.get("start_index") is None:
        out["reason"] = "no invested session in the primary scenario"
        return out
    if intraday is None:
        out["reason"] = "the vendor provides no SPY open (benchmark_intraday_returns)"
        return out
    entry_w: dict[int, float] = defaultdict(float)
    exit_w: dict[int, float] = defaultdict(float)
    for plan, sim in zip(plans, sims):
        for idx, w, _ in sim["rows"]:
            if idx == plan.e:
                entry_w[idx] += w
            if plan.exit_kind == EXIT_NEXT_OPEN and idx == plan.exit_index:
                exit_w[idx] += w
    start = net["start_index"]
    active, entry_sum, exit_sum, missing = 0, 0.0, 0.0, 0
    for k, den in enumerate(net["invested"]):
        if den <= 0:
            continue
        active += 1
        t = start + k
        if t not in entry_w and t not in exit_w:
            continue
        if t not in intraday:
            missing += 1
            continue
        overnight = (1.0 + spy[t]) / (1.0 + intraday[t]) - 1.0
        entry_sum += entry_w.get(t, 0.0) / den * overnight
        exit_sum += exit_w.get(t, 0.0) / den * (spy[t] - overnight)
    entry_term = -TRADING_DAYS * entry_sum / active
    exit_term = -TRADING_DAYS * exit_sum / active
    out.update({"available": missing == 0, "entry_day_spy_overnight_term_annual": entry_term,
                "next_open_exit_spy_intraday_term_annual": exit_term,
                "total_annual": entry_term + exit_term, "sessions_missing_spy_open": missing,
                "sign": "negative = the literal formula understates alpha by that much"})
    return out
