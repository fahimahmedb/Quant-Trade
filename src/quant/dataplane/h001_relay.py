"""H-001 forward collector: Pinnacle h2h (The Odds API) + same-run Polymarket/Kalshi quotes.

Research KPI (H-001): CLV of an executable prediction-market ask against Pinnacle's
*closing* no-vig fair value. The Odds API free tier has 500 requests/month and no
history, so every request is budgeted:

* one request = one sport (``regions=eu&markets=h2h&bookmakers=pinnacle`` costs 1);
* a sport is fetched only when (a) an event of it kicks off within ``CLOSE_WINDOW``
  and no snapshot has been taken inside that event's last ``CLOSE_TARGET`` minutes
  (closing-line capture) or (b) its newest snapshot is older than ``ANCHOR_HOURS``
  (discovery of new fixtures);
* hard caps: ``MAX_PER_RUN`` per run, ``DAILY_MAX`` per UTC day, ``MONTHLY_MAX`` per
  calendar month (counted from the request ledger), and no request once the last
  seen ``x-requests-remaining`` is at or below ``REMAINING_FLOOR``.

Polymarket (gamma events + CLOB book) and Kalshi (markets) quotes are fetched in the
SAME run, only for events Pinnacle was just fetched for, and every record of the run
carries the same ``observed_at`` (each request's own ``fetched_at`` is kept too).

Matching is an exact table (``TEAMS``): Odds API team name -> Polymarket name and
Kalshi ticker code. A name missing from the table is reported unmatched; there is no
fuzzy fill-in. Polymarket also has to agree on kickoff within ``KICKOFF_SKEW_S``;
Kalshi tickers carry only a (local) date, which must equal the UTC kickoff date or
the day before.

The API key is read from ``ODDS_API_KEY`` and never written: stored URLs pass through
``strip_key`` and error messages never contain the query string.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from .adapters import DataUnavailable
from .connectors import USER_AGENT, get_json, parse_order_book, _float

SPORTS = ("soccer_epl", "basketball_nba")
ODDS_URL = ("https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey={key}&regions=eu"
            "&markets=h2h&bookmakers=pinnacle&oddsFormat=decimal&dateFormat=iso")
MAX_PER_RUN = 2
DAILY_MAX = 14
MONTHLY_MAX = 430
REMAINING_FLOOR = 25
ANCHOR_HOURS = 12.0
CLOSE_WINDOW_MIN = 75       # an event kicking off within this many minutes is "closing"
CLOSE_TARGET_MIN = 60       # ...and needs a snapshot inside its last 60 minutes
CLOSE_LAG_FLAG_MIN = 60     # CLV against a snapshot older than this is flagged
KICKOFF_SKEW_S = 15 * 60
QUOTE_HORIZON_H = 72        # prediction-market quotes only for events kicking off soon

LEDGER = "odds/requests"
PINNACLE = "odds/pinnacle_h2h"
QUOTES_PM = "sports_quotes/polymarket"
QUOTES_KALSHI = "sports_quotes/kalshi"
MATCHES = "sports_quotes/matches"

PM_TAG = {"soccer_epl": "premier-league", "basketball_nba": "nba"}
PM_SLUG = {"soccer_epl": re.compile(r"^epl-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$"),
           "basketball_nba": re.compile(r"^nba-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$")}
PM_EVENTS = ("https://gamma-api.polymarket.com/events?tag_slug={tag}&closed=false"
             "&limit=500&start_date_min={start}")
PM_BOOK = "https://clob.polymarket.com/book?token_id={token}"
KALSHI_SERIES = {"soccer_epl": "KXEPLGAME", "basketball_nba": "KXNBAGAME"}
KALSHI_MARKETS = ("https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker={series}"
                  "&status=open&limit=1000")

# Odds API name -> (Polymarket name, Kalshi ticker code). Polymarket names are the
# EPL moneyline ``groupItemTitle`` / NBA moneyline outcome. Codes marked in
# TEAMS_UNVERIFIED were not yet observed on Kalshi (a wrong code only loses a match).
TEAMS: dict[str, dict[str, tuple[str, str | None]]] = {
    "soccer_epl": {
        "Arsenal": ("Arsenal FC", "ARS"), "Aston Villa": ("Aston Villa FC", "AVL"),
        "Bournemouth": ("AFC Bournemouth", "BOU"), "Brentford": ("Brentford FC", "BRE"),
        "Brighton and Hove Albion": ("Brighton & Hove Albion FC", "BRI"),
        "Burnley": ("Burnley FC", None), "Chelsea": ("Chelsea FC", "CFC"),
        "Coventry City": ("Coventry City FC", "COV"),
        "Crystal Palace": ("Crystal Palace FC", "CRY"), "Everton": ("Everton FC", "EVE"),
        "Fulham": ("Fulham FC", "FUL"), "Hull City": ("Hull City AFC", "HUL"),
        "Ipswich Town": ("Ipswich Town FC", "IPS"), "Leeds United": ("Leeds United FC", "LEE"),
        "Liverpool": ("Liverpool FC", "LFC"), "Manchester City": ("Manchester City FC", "MCI"),
        "Manchester United": ("Manchester United FC", "MUN"),
        "Newcastle United": ("Newcastle United FC", "NEW"),
        "Nottingham Forest": ("Nottingham Forest FC", "NFO"),
        "Sunderland": ("Sunderland AFC", "SUN"),
        "Tottenham Hotspur": ("Tottenham Hotspur FC", "TOT"),
        "West Ham United": ("West Ham United FC", None),
        "Wolverhampton Wanderers": ("Wolverhampton Wanderers FC", None),
    },
    "basketball_nba": {
        "Atlanta Hawks": ("Hawks", "ATL"), "Boston Celtics": ("Celtics", "BOS"),
        "Brooklyn Nets": ("Nets", "BKN"), "Charlotte Hornets": ("Hornets", "CHA"),
        "Chicago Bulls": ("Bulls", "CHI"), "Cleveland Cavaliers": ("Cavaliers", "CLE"),
        "Dallas Mavericks": ("Mavericks", "DAL"), "Denver Nuggets": ("Nuggets", "DEN"),
        "Detroit Pistons": ("Pistons", "DET"), "Golden State Warriors": ("Warriors", "GSW"),
        "Houston Rockets": ("Rockets", "HOU"), "Indiana Pacers": ("Pacers", "IND"),
        "Los Angeles Clippers": ("Clippers", "LAC"), "Los Angeles Lakers": ("Lakers", "LAL"),
        "Memphis Grizzlies": ("Grizzlies", "MEM"), "Miami Heat": ("Heat", "MIA"),
        "Milwaukee Bucks": ("Bucks", "MIL"), "Minnesota Timberwolves": ("Timberwolves", "MIN"),
        "New Orleans Pelicans": ("Pelicans", "NOP"), "New York Knicks": ("Knicks", "NYK"),
        "Oklahoma City Thunder": ("Thunder", "OKC"), "Orlando Magic": ("Magic", "ORL"),
        "Philadelphia 76ers": ("76ers", "PHI"), "Phoenix Suns": ("Suns", "PHX"),
        "Portland Trail Blazers": ("Trail Blazers", "POR"),
        "Sacramento Kings": ("Kings", "SAC"), "San Antonio Spurs": ("Spurs", "SAS"),
        "Toronto Raptors": ("Raptors", "TOR"), "Utah Jazz": ("Jazz", "UTA"),
        "Washington Wizards": ("Wizards", "WAS"),
    },
}
TEAMS_UNVERIFIED = {"basketball_nba": {"ATL", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "GSW",
                                       "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN",
                                       "NOP", "ORL", "PHX", "POR", "SAC", "TOR", "UTA", "WAS"}}
DRAW = "Draw"


# --- small helpers -------------------------------------------------------------------
def parse_time(value: str) -> datetime:
    """ISO-8601 (``Z``, ``+00``, space separator) -> aware UTC datetime."""
    text = value.strip().replace(" ", "T").replace("Z", "+00:00")
    if re.search(r"[+-]\d{2}$", text):
        text += ":00"
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def strip_key(url: str) -> str:
    """Remove ``apiKey`` from a URL so it can be stored."""
    parts = urllib.parse.urlsplit(url)
    query = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
             if k.lower() != "apikey"]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))


def read_stream(out: Path, stream: str) -> list[dict[str, Any]]:
    """Every stored item of a sharded stream (``<out>/<stream>/<YYYY-MM>.jsonl``)."""
    base = out / stream
    items = []
    for shard in sorted(base.glob("*.jsonl")) if base.is_dir() else []:
        for line in shard.read_text(encoding="utf-8").splitlines():
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return items


# --- budget ----------------------------------------------------------------------------
def plan_requests(now: datetime, ledger: Iterable[dict[str, Any]],
                  snapshots: Iterable[dict[str, Any]], sports: Iterable[str] = SPORTS, *,
                  max_per_run: int = MAX_PER_RUN, daily_max: int = DAILY_MAX,
                  monthly_max: int = MONTHLY_MAX, floor: int = REMAINING_FLOOR,
                  anchor_hours: float = ANCHOR_HOURS) -> tuple[list[tuple[str, str]], dict]:
    """Which sports to request now, and why (pure; ``ledger``/``snapshots`` are records).

    ``ledger`` rows: {fetched_at, sport, charged(bool), remaining(int|None)}.
    ``snapshots`` rows: Pinnacle records {sport, commence_time, observed_at}.
    """
    ledger = sorted(ledger, key=lambda row: row["fetched_at"])
    charged = [row for row in ledger if row.get("charged", True)]
    today = now.strftime("%Y-%m-%d")
    month = now.strftime("%Y-%m")
    used_today = sum(1 for row in charged if row["fetched_at"][:10] == today)
    used_month = sum(1 for row in charged if row["fetched_at"][:7] == month)
    remaining = next((row["remaining"] for row in reversed(ledger)
                      if row.get("remaining") is not None), None)
    info = {"used_today": used_today, "used_month": used_month, "last_remaining": remaining}
    if remaining is not None and remaining <= floor:
        return [], {**info, "blocked": f"x-requests-remaining {remaining} <= floor {floor}"}
    allowance = min(max_per_run, daily_max - used_today, monthly_max - used_month)
    if remaining is not None:
        allowance = min(allowance, remaining - floor)
    if allowance <= 0:
        return [], {**info, "blocked": "daily/monthly cap reached"}
    last_seen: dict[str, datetime] = {}
    upcoming: dict[str, set[datetime]] = {}
    for row in snapshots:
        seen = parse_time(row["observed_at"])
        sport = row["sport"]
        if sport not in last_seen or seen > last_seen[sport]:
            last_seen[sport] = seen
        upcoming.setdefault(sport, set()).add(parse_time(row["commence_time"]))
    closing, anchor = [], []
    for sport in sports:
        last = last_seen.get(sport)
        for kickoff in sorted(upcoming.get(sport, ())):
            if now < kickoff <= now + timedelta(minutes=CLOSE_WINDOW_MIN) and (
                    last is None or last < kickoff - timedelta(minutes=CLOSE_TARGET_MIN)):
                closing.append((sport, f"closing:{kickoff.isoformat()}"))
                break
        else:
            if last is None or now - last >= timedelta(hours=anchor_hours):
                anchor.append((sport, "anchor"))
    return (closing + anchor)[:allowance], info


# --- The Odds API ----------------------------------------------------------------------
Fetcher = Callable[[str], tuple[Any, dict[str, str]]]


def http_fetch(url: str) -> tuple[Any, dict[str, str]]:
    """GET JSON and response headers; errors never echo the query string (key)."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
            return json.loads(response.read()), headers
    except urllib.error.HTTPError as exc:
        headers = {k.lower(): v for k, v in (exc.headers or {}).items()}
        raise OddsHTTPError(f"{url.split('?')[0]}: HTTP {exc.code}", headers) from None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise DataUnavailable(f"{url.split('?')[0]}: {type(exc).__name__}") from None


class OddsHTTPError(DataUnavailable):
    def __init__(self, message: str, headers: dict[str, str]):
        super().__init__(message)
        self.headers = headers


def _int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_pinnacle(payload: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    """One record per event with Pinnacle's h2h decimal prices (by Odds API outcome name)."""
    out = []
    for event in payload or []:
        for book in event.get("bookmakers") or []:
            if book.get("key") != "pinnacle":
                continue
            for market in book.get("markets") or []:
                if market.get("key") != "h2h":
                    continue
                prices = {o.get("name"): _float(o.get("price")) for o in market.get("outcomes") or []}
                if not prices or any(v is None or v <= 1 for v in prices.values()):
                    continue
                out.append({"event_id": event.get("id"), "sport": event.get("sport_key") or sport,
                            "commence_time": event.get("commence_time"),
                            "home": event.get("home_team"), "away": event.get("away_team"),
                            "bookmaker": "pinnacle",
                            "quote_time": market.get("last_update") or book.get("last_update"),
                            "prices": prices})
    return out


def fetch_pinnacle(sport: str, key: str, fetch: Fetcher = http_fetch
                   ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    url = ODDS_URL.format(sport=sport, key=urllib.parse.quote(key, safe=""))
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        payload, headers = fetch(url)
    except OddsHTTPError as exc:
        meta = _ledger_row(sport, fetched_at, url, exc.headers, status=str(exc))
        return [], meta
    meta = _ledger_row(sport, fetched_at, url, headers, status="OK")
    records = parse_pinnacle(payload, sport)
    meta["events"] = len(records)
    return records, meta


def _ledger_row(sport: str, fetched_at: str, url: str, headers: dict[str, str],
                status: str) -> dict[str, Any]:
    return {"sport": sport, "fetched_at": fetched_at, "url": strip_key(url),
            "status": status, "charged": _int(headers.get("x-requests-last")) != 0,
            "remaining": _int(headers.get("x-requests-remaining")),
            "used": _int(headers.get("x-requests-used")),
            "last_cost": _int(headers.get("x-requests-last"))}


# --- matching --------------------------------------------------------------------------
def match_polymarket(event: dict[str, Any], pm_events: list[dict[str, Any]]
                     ) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Odds API outcome name -> Polymarket {market_id, token_id, pm_name}, exact table."""
    sport = event["sport"]
    table = TEAMS.get(sport, {})
    home, away = event["home"], event["away"]
    if home not in table or away not in table:
        return {}, {"status": "unmatched", "reason": "team not in table",
                    "missing": [t for t in (home, away) if t not in table]}
    names = {table[home][0]: home, table[away][0]: away}
    kickoff = parse_time(event["commence_time"])
    for pm in pm_events:
        if not PM_SLUG[sport].match(pm.get("slug") or ""):
            continue
        moneyline = [m for m in pm.get("markets") or [] if m.get("sportsMarketType") == "moneyline"]
        mapped: dict[str, dict[str, Any]] = {}
        start = pm.get("startTime") or next((m.get("gameStartTime") for m in moneyline
                                             if m.get("gameStartTime")), None)
        try:
            tokens_list = [(m, json.loads(m.get("clobTokenIds") or "[]"),
                            json.loads(m.get("outcomes") or "[]")) for m in moneyline]
        except json.JSONDecodeError:
            continue
        if sport == "basketball_nba":
            for market, tokens, outcomes in tokens_list:
                if set(outcomes) == set(names) and len(tokens) == len(outcomes):
                    for token, outcome in zip(tokens, outcomes):
                        mapped[names[outcome]] = {"market_id": market.get("conditionId"),
                                                  "token_id": token, "pm_name": outcome}
        else:
            titles = {}
            for market, tokens, outcomes in tokens_list:
                title = market.get("groupItemTitle") or ""
                if outcomes[:1] == ["Yes"] and tokens:
                    titles[title] = {"market_id": market.get("conditionId"), "token_id": tokens[0],
                                     "pm_name": title}
            draw = f"Draw ({table[home][0]} vs. {table[away][0]})"
            if set(names) <= set(titles) and draw in titles:
                mapped = {names[n]: titles[n] for n in names}
                mapped[DRAW] = titles[draw]
        if not mapped:
            continue
        if start is None:
            return {}, {"status": "unmatched", "reason": "polymarket event has no start time",
                        "slug": pm.get("slug")}
        skew = abs((parse_time(start) - kickoff).total_seconds())
        if skew > KICKOFF_SKEW_S:
            continue                        # same teams, another fixture (or rescheduled)
        return mapped, {"status": "matched", "slug": pm.get("slug"),
                        "pm_start": start, "kickoff_skew_s": skew}
    return {}, {"status": "unmatched", "reason": "no polymarket event with both teams at kickoff"}


def match_kalshi(event: dict[str, Any], markets: list[dict[str, Any]]
                 ) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Odds API outcome name -> Kalshi market, by ticker team codes + date."""
    sport = event["sport"]
    table = TEAMS.get(sport, {})
    home, away = event["home"], event["away"]
    codes = {name: (table.get(name) or (None, None))[1] for name in (home, away)}
    if None in codes.values():
        return {}, {"status": "unmatched", "reason": "team code not in table",
                    "missing": [n for n, c in codes.items() if c is None]}
    kickoff = parse_time(event["commence_time"])
    days = {(kickoff - timedelta(days=d)).strftime("%y%b%d").upper() for d in (0, 1)}
    by_event: dict[str, list[dict[str, Any]]] = {}
    for market in markets:
        by_event.setdefault(market.get("event_ticker") or "", []).append(market)
    series = KALSHI_SERIES[sport]
    for event_ticker, group in by_event.items():
        match = re.match(rf"^{series}-(\d{{2}}[A-Z]{{3}}\d{{2}})([A-Z]+)$", event_ticker)
        if not match or match.group(1) not in days:
            continue
        pair = match.group(2)
        if pair not in {codes[home] + codes[away], codes[away] + codes[home]}:
            continue
        suffix = {m["ticker"].rsplit("-", 1)[1]: m for m in group}
        mapped = {name: suffix[code] for name, code in codes.items() if code in suffix}
        if "TIE" in suffix:
            mapped[DRAW] = suffix["TIE"]
        needed = {home, away} | ({DRAW} if sport == "soccer_epl" else set())
        if set(mapped) != needed:
            return {}, {"status": "unmatched", "reason": "kalshi event lacks an outcome",
                        "event_ticker": event_ticker}
        return mapped, {"status": "matched", "event_ticker": event_ticker,
                        "ticker_date": match.group(1), "kickoff_basis": "ticker date only"}
    return {}, {"status": "unmatched", "reason": "no kalshi event with both codes on the date"}


def kalshi_quote(market: dict[str, Any]) -> dict[str, Any]:
    def dollars(field: str) -> float | None:
        value = _float(market.get(f"{field}_dollars"))
        if value is None:
            cents = _float(market.get(field))
            value = cents / 100 if cents is not None else None
        return value
    return {"ticker": market.get("ticker"), "event_ticker": market.get("event_ticker"),
            "best_bid": dollars("yes_bid"), "best_ask": dollars("yes_ask"),
            "no_bid": dollars("no_bid"), "no_ask": dollars("no_ask"),
            "volume_24h": _float(market.get("volume_24h")),
            "open_interest": _float(market.get("open_interest")),
            "rules_primary": market.get("rules_primary")}


# --- the run -----------------------------------------------------------------------------
def collect(out: Path, now: datetime, *, key: str | None = None, fetch: Fetcher = http_fetch,
            get: Callable[[str], Any] = get_json, sports: Iterable[str] = SPORTS
            ) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """Yield ``(stream, key, record)`` for one run; all share the caller's ``observed_at``.

    Raises DataUnavailable when no key is configured (nothing is requested).
    """
    key = key if key is not None else os.environ.get("ODDS_API_KEY")
    if not key:
        raise DataUnavailable("ODDS_API_KEY is not configured")
    stamp = now.isoformat(timespec="seconds")
    ledger = [item["record"] for item in read_stream(out, LEDGER)]
    snapshots = [{**item["record"], "observed_at": item["observed_at"]}
                 for item in read_stream(out, PINNACLE)]
    plan, info = plan_requests(now, ledger, snapshots, sports)
    yield "odds/plans.jsonl", stamp, {"plan": plan, **info}
    for sport, reason in plan:
        records, meta = fetch_pinnacle(sport, key, fetch)
        meta["reason"] = reason
        yield f"{LEDGER}.jsonl", f"{meta['fetched_at']}|{sport}", meta
        if meta["status"] != "OK":
            continue
        for record in records:
            kickoff = parse_time(record["commence_time"])
            record["snapshot_to_kickoff_min"] = round((kickoff - now).total_seconds() / 60, 1)
            record["source_url"] = meta["url"]
            yield f"{PINNACLE}.jsonl", f"{stamp}|{record['event_id']}", record
        live = [r for r in records
                if now < parse_time(r["commence_time"]) <= now + timedelta(hours=QUOTE_HORIZON_H)]
        if live:
            yield from _venue_quotes(sport, live, now, stamp, get)


def _venue_quotes(sport: str, events: list[dict[str, Any]], now: datetime, stamp: str,
                  get: Callable[[str], Any]) -> Iterator[tuple[str, str, dict[str, Any]]]:
    start = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    pm_url = PM_EVENTS.format(tag=PM_TAG[sport], start=start)
    k_url = KALSHI_MARKETS.format(series=KALSHI_SERIES[sport])
    try:
        pm_events, pm_error = get(pm_url) or [], None
    except DataUnavailable as exc:
        pm_events, pm_error = [], str(exc)[:200]
    try:
        k_markets, k_error = (get(k_url) or {}).get("markets") or [], None
    except DataUnavailable as exc:
        k_markets, k_error = [], str(exc)[:200]
    for event in events:
        base = {"odds_event_id": event["event_id"], "sport": sport,
                "commence_time": event["commence_time"], "home": event["home"],
                "away": event["away"]}
        pm_map, pm_info = match_polymarket(event, pm_events) if not pm_error else (
            {}, {"status": "unreachable", "reason": pm_error})
        k_map, k_info = match_kalshi(event, k_markets) if not k_error else (
            {}, {"status": "unreachable", "reason": k_error})
        yield (f"{MATCHES}.jsonl", f"{event['event_id']}|POLYMARKET",
               {**base, "venue": "POLYMARKET", **pm_info,
                "outcomes": {o: m["token_id"] for o, m in pm_map.items()}})
        yield (f"{MATCHES}.jsonl", f"{event['event_id']}|KALSHI",
               {**base, "venue": "KALSHI", **k_info,
                "outcomes": {o: m["ticker"] for o, m in k_map.items()}})
        for outcome, market in pm_map.items():
            fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                book = parse_order_book(get(PM_BOOK.format(token=market["token_id"])),
                                        "POLYMARKET", market["token_id"])
            except DataUnavailable:
                book = None
            record = {**base, "venue": "POLYMARKET", "outcome": outcome, **market,
                      "fetched_at": fetched_at, "source_url": PM_BOOK.split("?")[0],
                      "best_bid": book and book["best_bid"], "best_ask": book and book["best_ask"],
                      "ask_depth": book and book["ask_depth"], "asks": book and book["asks"][:5],
                      "bids": book and book["bids"][:5], "book_empty": book is None}
            yield f"{QUOTES_PM}.jsonl", f"{stamp}|{event['event_id']}|{outcome}", record
        for outcome, market in k_map.items():
            record = {**base, "venue": "KALSHI", "outcome": outcome, **kalshi_quote(market),
                      "fetched_at": stamp, "source_url": k_url}
            yield f"{QUOTES_KALSHI}.jsonl", f"{stamp}|{event['event_id']}|{outcome}", record
