from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import statistics
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
UTC = timezone.utc
POINT_VALUE_USD = 1000.0
EXPLICIT_FEE_PER_SIDE_USD = 3.00
BBO_TOLERANCE = timedelta(seconds=60)
SAMPLE_START = date(2015, 1, 1)
SAMPLE_END = date(2026, 9, 30)
RECENT_START = date(2025, 1, 1)
NW_LAG = 3
PROMOTE_T = 1.645  # one-sided 5%, frozen before outcome exposure


class ProtocolError(ValueError):
    pass


class MissingBBO(ProtocolError):
    pass


@dataclass(frozen=True)
class AuctionEvent:
    announcement_date: date
    auction_date: date
    security_type: str
    security_term: str
    reopening: bool
    competitive_close_et: str
    close_utc: datetime
    original_announcement_url: str
    cusip: str = ""

    @property
    def pre_entry_utc(self) -> datetime:
        return self.close_utc - timedelta(minutes=180)

    @property
    def pre_exit_boundary_utc(self) -> datetime:
        return self.close_utc

    @property
    def post_entry_utc(self) -> datetime:
        return self.close_utc + timedelta(minutes=10)

    @property
    def post_exit_utc(self) -> datetime:
        return self.close_utc + timedelta(minutes=180)


@dataclass(frozen=True)
class ContractSelection:
    root: str
    symbol: str
    delivery_month: int
    delivery_year: int


@dataclass(frozen=True)
class BBO:
    ts_utc: datetime
    bid: float
    ask: float

    def __post_init__(self) -> None:
        if self.ts_utc.tzinfo is None:
            raise ProtocolError("BBO timestamp must be timezone-aware")
        if not (math.isfinite(self.bid) and math.isfinite(self.ask)):
            raise ProtocolError("BBO prices must be finite")
        if self.bid <= 0 or self.ask <= 0 or self.bid > self.ask:
            raise ProtocolError("invalid BBO")


@dataclass(frozen=True)
class LegResult:
    leg: str
    entry_ts_utc: datetime
    exit_ts_utc: datetime
    entry_price: float
    exit_price: float
    gross_usd: float
    explicit_fees_usd: float
    net_usd: float


@dataclass(frozen=True)
class EventResult:
    auction_date: date
    pre: LegResult
    post: LegResult

    @property
    def combined_net_usd(self) -> float:
        return self.pre.net_usd + self.post.net_usd


FROZEN_PROTOCOL = {
    "universe": "US Treasury nominal 5-Year Note auctions announced as 5-Year Note",
    "sample_start": SAMPLE_START.isoformat(),
    "sample_end": SAMPLE_END.isoformat(),
    "include_reopenings": True,
    "post_result_exclusions": False,
    "timezone": "America/New_York",
    "pre_window": "short T-180m to last BBO strictly before T",
    "post_window": "long first BBO >=T+10m to first BBO >=T+180m",
    "endpoint_tolerance_seconds": int(BBO_TOLERANCE.total_seconds()),
    "contract_rule": "earliest Mar/Jun/Sep/Dec ZF contract whose delivery-month first day is >= auction_date+14 calendar days",
    "bbo_execution": "sell at bid, buy at ask; no midpoint",
    "explicit_fee_per_side_usd": EXPLICIT_FEE_PER_SIDE_USD,
    "point_value_usd": POINT_VALUE_USD,
    "statistics": "event-level mean/median/sign-rate; Newey-West t-stat lag 3 on combined net USD",
    "kill": "KILL if mean PRE<=0 OR mean POST<=0 OR mean COMBINED<=0 OR recent(2025+) mean COMBINED<=0",
    "keep": "KEEP_AS_RESERVE if all frozen directional means including recent are >0 but combined NW t<1.645",
    "promote": "PROMOTE_TO_EXPERIMENT_DESIGN if all frozen directional means including recent are >0 and combined NW t>=1.645",
    "data_quality": "BLOCKED_DATA_QUALITY if fewer than 90% of manifest events have all four executable BBO endpoints",
}

_TIME_RE = re.compile(r"^\s*(?P<h>\d{1,2}):(?P<m>\d{2})\s*(?P<ampm>a\.?m\.?|p\.?m\.?)?\s*ET\s*$", re.I)


def parse_competitive_close(auction_date: date, text: str) -> tuple[str, datetime]:
    """Parse an ET close from the original Treasury announcement; reject ambiguous timestamps."""
    m = _TIME_RE.match(text)
    if not m:
        raise ProtocolError(f"competitive close must explicitly include ET: {text!r}")
    hour = int(m.group("h"))
    minute = int(m.group("m"))
    ampm = m.group("ampm")
    if minute > 59:
        raise ProtocolError("invalid minute")
    if ampm:
        if not 1 <= hour <= 12:
            raise ProtocolError("invalid 12-hour clock")
        norm = ampm.lower().replace(".", "")
        if norm == "pm" and hour != 12:
            hour += 12
        if norm == "am" and hour == 12:
            hour = 0
    elif not 0 <= hour <= 23:
        raise ProtocolError("invalid 24-hour clock")
    local = datetime.combine(auction_date, time(hour, minute), tzinfo=NY)
    return f"{hour:02d}:{minute:02d} ET", local.astimezone(UTC)


def _bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1"}:
        return True
    if text in {"false", "no", "n", "0", "", "none", "n/a"}:
        return False
    raise ProtocolError(f"unrecognized boolean: {value!r}")


def _date(value: object) -> date:
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ProtocolError(f"unrecognized date: {value!r}")


def normalize_treasury_row(row: Mapping[str, object]) -> AuctionEvent:
    """Normalize one outcome-blind Treasury calendar row plus original-announcement fields."""
    announcement_date = _date(row["announcement_date"])
    auction_date = _date(row["auction_date"])
    security_type = str(row["security_type"]).strip()
    security_term = str(row["security_term"]).strip()
    original_url = str(row["original_announcement_url"]).strip()
    close_text = str(row["competitive_close_et"]).strip()
    if announcement_date >= auction_date:
        raise ProtocolError("announcement must predate auction; same-day metadata is not accepted")
    if security_type.lower() != "note" or security_term.lower() not in {"5-year", "5-year note"}:
        raise ProtocolError("row is not a nominal 5-Year Note auction")
    if not original_url.startswith("https://www.treasurydirect.gov/"):
        raise ProtocolError("original Treasury announcement URL required")
    if not SAMPLE_START <= auction_date <= SAMPLE_END:
        raise ProtocolError("auction outside frozen sample")
    close_norm, close_utc = parse_competitive_close(auction_date, close_text)
    # No-look-ahead invariant: even conservatively treating the announcement as available at end-of-day,
    # it must precede the PRE entry day.
    announcement_eod = datetime.combine(announcement_date, time(23, 59, 59), tzinfo=NY).astimezone(UTC)
    if announcement_eod >= close_utc - timedelta(minutes=180):
        raise ProtocolError("announcement availability is not safely before PRE entry")
    return AuctionEvent(
        announcement_date=announcement_date,
        auction_date=auction_date,
        security_type="Note",
        security_term="5-Year",
        reopening=_bool(row.get("reopening", False)),
        competitive_close_et=close_norm,
        close_utc=close_utc,
        original_announcement_url=original_url,
        cusip=str(row.get("cusip", "")).strip(),
    )


def load_treasury_csv(text: str) -> list[AuctionEvent]:
    return build_event_manifest(csv.DictReader(io.StringIO(text)))


def build_event_manifest(rows: Iterable[Mapping[str, object]]) -> list[AuctionEvent]:
    events = [normalize_treasury_row(r) for r in rows]
    events.sort(key=lambda e: (e.close_utc, e.cusip, e.original_announcement_url))
    seen: set[tuple[date, str, str]] = set()
    for e in events:
        key = (e.auction_date, e.cusip, e.original_announcement_url)
        if key in seen:
            raise ProtocolError(f"duplicate event: {key}")
        seen.add(key)
    return events


def manifest_digest(events: Sequence[AuctionEvent]) -> str:
    payload = []
    for e in events:
        d = asdict(e)
        d["announcement_date"] = e.announcement_date.isoformat()
        d["auction_date"] = e.auction_date.isoformat()
        d["close_utc"] = e.close_utc.isoformat()
        payload.append(d)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


_MONTH_CODES = {3: "H", 6: "M", 9: "U", 12: "Z"}


def select_zf_contract(auction_date: date) -> ContractSelection:
    """Outcome-blind roll: switch away from a delivery month 14 calendar days before its first day."""
    threshold = auction_date + timedelta(days=14)
    for year in range(auction_date.year, auction_date.year + 3):
        for month in (3, 6, 9, 12):
            first = date(year, month, 1)
            if first >= threshold:
                yy = year % 100
                return ContractSelection("ZF", f"ZF{_MONTH_CODES[month]}{yy:02d}", month, year)
    raise ProtocolError("could not select ZF contract")


def validate_windows(event: AuctionEvent) -> None:
    if not (event.pre_entry_utc < event.pre_exit_boundary_utc < event.post_entry_utc < event.post_exit_utc):
        raise ProtocolError("non-monotone event windows")
    if event.post_entry_utc - event.close_utc != timedelta(minutes=10):
        raise ProtocolError("POST buffer drift")


def _first_at_or_after(quotes: Sequence[BBO], target: datetime) -> BBO:
    eligible = [q for q in quotes if target <= q.ts_utc <= target + BBO_TOLERANCE]
    if not eligible:
        raise MissingBBO(f"no BBO at/after {target.isoformat()} within tolerance")
    return min(eligible, key=lambda q: q.ts_utc)


def _last_strictly_before(quotes: Sequence[BBO], boundary: datetime) -> BBO:
    eligible = [q for q in quotes if boundary - BBO_TOLERANCE <= q.ts_utc < boundary]
    if not eligible:
        raise MissingBBO(f"no BBO strictly before {boundary.isoformat()} within tolerance")
    return max(eligible, key=lambda q: q.ts_utc)


def calculate_event(event: AuctionEvent, quotes: Sequence[BBO]) -> EventResult:
    validate_windows(event)
    pre_entry = _first_at_or_after(quotes, event.pre_entry_utc)
    pre_exit = _last_strictly_before(quotes, event.pre_exit_boundary_utc)
    post_entry = _first_at_or_after(quotes, event.post_entry_utc)
    post_exit = _first_at_or_after(quotes, event.post_exit_utc)

    explicit = 2 * EXPLICIT_FEE_PER_SIDE_USD
    pre_gross = (pre_entry.bid - pre_exit.ask) * POINT_VALUE_USD
    post_gross = (post_exit.bid - post_entry.ask) * POINT_VALUE_USD
    pre = LegResult("PRE_SHORT", pre_entry.ts_utc, pre_exit.ts_utc, pre_entry.bid, pre_exit.ask,
                    pre_gross, explicit, pre_gross - explicit)
    post = LegResult("POST_LONG", post_entry.ts_utc, post_exit.ts_utc, post_entry.ask, post_exit.bid,
                     post_gross, explicit, post_gross - explicit)
    return EventResult(event.auction_date, pre, post)


def _nw_t(values: Sequence[float], lag: int = NW_LAG) -> float:
    n = len(values)
    if n < 2:
        return float("nan")
    mean = statistics.fmean(values)
    x = [v - mean for v in values]
    gamma0 = sum(v * v for v in x) / n
    var = gamma0
    for l in range(1, min(lag, n - 1) + 1):
        gamma = sum(x[t] * x[t - l] for t in range(l, n)) / n
        weight = 1.0 - l / (lag + 1.0)
        var += 2.0 * weight * gamma
    if var <= 0:
        return float("inf") if mean > 0 else float("-inf") if mean < 0 else 0.0
    se = math.sqrt(var / n)
    return mean / se


def summarize_and_decide(results: Sequence[EventResult], manifest_count: int) -> dict[str, object]:
    if manifest_count <= 0:
        raise ProtocolError("manifest_count must be positive")
    usable_ratio = len(results) / manifest_count
    if usable_ratio < 0.90:
        return {"decision": "BLOCKED_DATA_QUALITY", "usable_ratio": usable_ratio}
    pre = [r.pre.net_usd for r in results]
    post = [r.post.net_usd for r in results]
    combined = [r.combined_net_usd for r in results]
    recent = [r.combined_net_usd for r in results if r.auction_date >= RECENT_START]
    if not recent:
        raise ProtocolError("recent slice missing")
    stats = {
        "n": len(results),
        "usable_ratio": usable_ratio,
        "pre_mean_usd": statistics.fmean(pre),
        "post_mean_usd": statistics.fmean(post),
        "combined_mean_usd": statistics.fmean(combined),
        "combined_median_usd": statistics.median(combined),
        "combined_sign_rate": sum(v > 0 for v in combined) / len(combined),
        "combined_nw_t_lag3": _nw_t(combined),
        "recent_combined_mean_usd": statistics.fmean(recent),
    }
    if (stats["pre_mean_usd"] <= 0 or stats["post_mean_usd"] <= 0 or
            stats["combined_mean_usd"] <= 0 or stats["recent_combined_mean_usd"] <= 0):
        decision = "KILL"
    elif stats["combined_nw_t_lag3"] >= PROMOTE_T:
        decision = "PROMOTE_TO_EXPERIMENT_DESIGN"
    else:
        decision = "KEEP_AS_RESERVE"
    return {"decision": decision, **stats}
