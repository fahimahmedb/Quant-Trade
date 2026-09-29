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

H-011 niche leagues (budget arithmetic)
----------------------------------------
H-011 reuses this SAME budget-guarded relay for three niche leagues (``NICHE_SPORTS``):
K-League 1, Liga MX and NCAA football (ITF tennis has no Odds API key and is excluded
per the registry). They are the ex-ante picks the mission named, to be confirmed by
name against the Odds API's own ``/v4/sports`` listing (free, no quota cost) whenever
a key is available; this build had none (``ODDS_API_KEY`` unset here and, per
``FAST_RAIL_STATE.md``, still unset in production), so the hard-coded list is used, as
the mission explicitly allows. Niche sports anchor at ``NICHE_ANCHOR_HOURS`` (24h,
half H-001's own 12h) via a per-sport mapping (``ANCHOR_HOURS_BY_SPORT``); the
closing-line logic and every hard cap (``MAX_PER_RUN``/``DAILY_MAX``/``MONTHLY_MAX``/
``REMAINING_FLOOR``) are UNCHANGED and shared GLOBALLY across all 5 sports, not
per-sport, so adding niche sports only competes for the existing budget, never raises
its ceiling.

Budget arithmetic (2026-09-27 design estimate; the ``odds/requests`` ledger is the
source of truth once this runs live, and should update these numbers, not be argued
with by them):

* absolute ceiling, independent of sport count: ``min(DAILY_MAX*30, MONTHLY_MAX)``
  = ``min(14*30, 430)`` = 420/month -- the daily cap is already binding over a
  30-day month, ``MONTHLY_MAX`` is a slightly looser second backstop, and
  ``REMAINING_FLOOR`` (25) is a final brake against a mis-estimated month;
* pure-anchor floor, if no sport ever has a fixture near kickoff (worst case for
  coverage, best case for spend): H-001's 2 sports at 12h anchor cost up to
  ``2 * 24/12`` = 4/day; the 3 niche sports at 24h cost up to ``3 * 24/24`` = 3/day;
  combined 7/day = ~210/month;
* closing captures add to that floor only on days a sport has a fixture near
  kickoff, and a capture also refreshes that sport's ``last_seen`` (so it partly
  substitutes for, rather than stacks on, the next anchor request). EPL/NBA are
  in-season most days and dominate this extra spend (assume ~1-2/day combined);
  K-League/Liga MX/NCAAF are weekly-cadence leagues and add less (assume ~1/day
  combined on an average week);
* expected steady state: ~7-11 requests/day => **~250-400/month**, inside the
  mission's target band and comfortably under the unchanged 420-430 ceiling. This
  is a design estimate from the planner's own rules, not measured usage.

R2 (``collect_trades``) and R4 (``collect_rewards``), below, read the
``sports_quotes/{polymarket,kalshi}`` streams this module already writes for
MATCHED markets. Niche sports have no ``TEAMS``/``PM_TAG``/``KALSHI_SERIES`` entries
yet: inventing them without an observed Polymarket/Kalshi listing for these leagues
would be a fabricated match, which the existing "no fuzzy fill-in" contract already
forbids, so niche events report unmatched until those tables are populated from real
venue data. ``_venue_quotes`` degrades to an explicit unmatched reason instead of
raising when a sport has no venue mapping at all.
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
#: H-011 ex-ante niche-league list (hard-coded: no key was available in this build to
#: confirm names against GET /v4/sports, which the mission allows as a fallback).
#: ITF tennis is not on the Odds API and is excluded.
NICHE_SPORTS = ("soccer_korea_kleague1", "soccer_mexico_ligamx", "americanfootball_ncaaf")
ALL_SPORTS = SPORTS + NICHE_SPORTS
SPORTS_LISTING_URL = "https://api.the-odds-api.com/v4/sports?apiKey={key}"
ODDS_URL = ("https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey={key}&regions=eu"
            "&markets=h2h&bookmakers=pinnacle&oddsFormat=decimal&dateFormat=iso")
MAX_PER_RUN = 2
DAILY_MAX = 14
MONTHLY_MAX = 430
REMAINING_FLOOR = 25
ANCHOR_HOURS = 12.0
NICHE_ANCHOR_HOURS = 24.0
#: per-sport anchor override for the combined H-001 + H-011 planner (see module
#: docstring "H-011 niche leagues"); ``plan_requests``/``collect`` still default to
#: the flat ``ANCHOR_HOURS`` for backward compatibility with a bare sport list.
ANCHOR_HOURS_BY_SPORT: dict[str, float] = {**{s: ANCHOR_HOURS for s in SPORTS},
                                           **{s: NICHE_ANCHOR_HOURS for s in NICHE_SPORTS}}
CLOSE_WINDOW_MIN = 75       # an event kicking off within this many minutes is "closing"
CLOSE_TARGET_MIN = 60       # ...and needs a snapshot inside its last 60 minutes
CLOSE_LAG_FLAG_MIN = 60     # CLV against a snapshot older than this is flagged
KICKOFF_SKEW_S = 15 * 60
QUOTE_HORIZON_H = 168       # prediction-market quotes for events kicking off within a week

LEDGER = "odds/requests"
PINNACLE = "odds/pinnacle_h2h"
QUOTES_PM = "sports_quotes/polymarket"
QUOTES_KALSHI = "sports_quotes/kalshi"
MATCHES = "sports_quotes/matches"

PM_TAG = {"soccer_epl": "premier-league", "basketball_nba": "nba"}
PM_SLUG = {"soccer_epl": re.compile(r"^epl-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$"),
           "basketball_nba": re.compile(r"^nba-[a-z]+-[a-z]+-\d{4}-\d{2}-\d{2}$")}
PM_EVENTS = ("https://gamma-api.polymarket.com/events?tag_slug={tag}&closed=false"
             "&limit=500&offset={offset}&end_date_min={start}")
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
                  anchor_hours: float | dict[str, float] = ANCHOR_HOURS
                  ) -> tuple[list[tuple[str, str]], dict]:
    """Which sports to request now, and why (pure; ``ledger``/``snapshots`` are records).

    ``ledger`` rows: {fetched_at, sport, charged(bool), remaining(int|None)}.
    ``snapshots`` rows: Pinnacle records {sport, commence_time, observed_at}.
    ``anchor_hours`` is either one value for every sport, or a per-sport mapping
    (missing sports fall back to ``ANCHOR_HOURS``) -- see ``ANCHOR_HOURS_BY_SPORT``,
    used to give H-011's niche leagues a lower anchor frequency than H-001's own
    sports while sharing every cap below globally, across all sports at once.
    """
    def anchor_for(sport: str) -> float:
        return anchor_hours.get(sport, ANCHOR_HOURS) if isinstance(anchor_hours, dict) \
            else anchor_hours
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
    for row in ledger:                      # a fetch that returned no events still counts
        if row.get("status") == "OK" and row.get("sport"):
            seen = parse_time(row["fetched_at"])
            if row["sport"] not in last_seen or seen > last_seen[row["sport"]]:
                last_seen[row["sport"]] = seen
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
            if last is None or now - last >= timedelta(hours=anchor_for(sport)):
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
                out.append({"event_id": event.get("id"), "sport": sport,
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
    except DataUnavailable as exc:
        # Timeout / network / bad JSON after the server may have charged the request:
        # counted as used (no x-requests-used header => charged), never retried free.
        meta = _ledger_row(sport, fetched_at, url, {}, status=f"UNREACHABLE: {exc}"[:120])
        return [], meta
    meta = _ledger_row(sport, fetched_at, url, headers, status="OK")
    try:
        records = parse_pinnacle(payload, sport)
    except (TypeError, KeyError, ValueError) as exc:
        meta["status"] = f"BAD_PAYLOAD: {type(exc).__name__}"
        return [], meta
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
        needed = {home, away} | ({DRAW} if sport.startswith("soccer_") else set())
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
            get: Callable[[str], Any] = get_json, sports: Iterable[str] = SPORTS,
            anchor_hours: float | dict[str, float] = ANCHOR_HOURS
            ) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """Yield ``(stream, key, record)`` for one run; all share the caller's ``observed_at``.

    Raises DataUnavailable when no key is configured (nothing is requested). Pass
    ``sports=ALL_SPORTS, anchor_hours=ANCHOR_HOURS_BY_SPORT`` to also plan H-011's
    niche leagues (this is what ``scripts/fetch_feeds.py`` does); the bare defaults
    keep H-001's own 2-sport, flat-12h-anchor behaviour unchanged.
    """
    key = key if key is not None else os.environ.get("ODDS_API_KEY")
    if not key:
        raise DataUnavailable("ODDS_API_KEY is not configured")
    stamp = now.isoformat(timespec="seconds")
    ledger = [item["record"] for item in read_stream(out, LEDGER)]
    snapshots = [{**item["record"], "observed_at": item["observed_at"]}
                 for item in read_stream(out, PINNACLE)]
    plan, info = plan_requests(now, ledger, snapshots, sports, anchor_hours=anchor_hours)
    yield "odds/plans.jsonl", stamp, {"plan": plan, **info}
    quoted: set[str] = set()
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
            quoted.update(r["event_id"] for r in live)
    # Blue 2026-09-29: venue prices are written EVERY run (no Odds API cost) for matches
    # known from the latest stored Pinnacle snapshot, not only in runs that poll Pinnacle.
    latest: dict[str, dict[str, Any]] = {}
    for row in snapshots:
        if row["event_id"] not in latest or row["observed_at"] > latest[row["event_id"]]["observed_at"]:
            latest[row["event_id"]] = row
    by_sport: dict[str, list[dict[str, Any]]] = {}
    for row in latest.values():
        if row["event_id"] in quoted or row.get("sport") not in set(sports):
            continue
        if now < parse_time(row["commence_time"]) <= now + timedelta(hours=QUOTE_HORIZON_H):
            by_sport.setdefault(row["sport"], []).append(row)
    for sport, rows in by_sport.items():
        yield from _venue_quotes(sport, rows, now, stamp, get)


def _venue_quotes(sport: str, events: list[dict[str, Any]], now: datetime, stamp: str,
                  get: Callable[[str], Any]) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """Polymarket/Kalshi quotes for one sport's ``live`` events.

    ``PM_TAG``/``KALSHI_SERIES`` only cover H-001's own sports today; a sport absent
    from one (a niche H-011 league, until real venue names/tickers are observed and
    added) degrades to an explicit "sport not wired to a venue" unmatched reason
    for that venue instead of a ``KeyError`` -- the whole run must not fail just
    because one sport has no mapping yet.
    """
    start = now.strftime("%Y-%m-%dT%H:%M:%SZ")   # gamma game events end at kickoff
    pm_tag, kalshi_series = PM_TAG.get(sport), KALSHI_SERIES.get(sport)
    pm_events: list[dict[str, Any]] = []
    pm_error = None if pm_tag else "sport not wired to a Polymarket tag"
    if pm_tag:
        try:
            for offset in (0, 500, 1000):      # game events carry many prop sub-events
                page = get(PM_EVENTS.format(tag=pm_tag, start=start, offset=offset)) or []
                pm_events.extend(page)
                if len(page) < 500:
                    break
        except DataUnavailable as exc:
            pm_events, pm_error = [], str(exc)[:200]
    k_markets: list[dict[str, Any]] = []
    k_url = KALSHI_MARKETS.format(series=kalshi_series) if kalshi_series else None
    k_error = None if kalshi_series else "sport not wired to a Kalshi series"
    if kalshi_series:
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
            # Order 12: the public book at entry decides executability (never assume a fill).
            book_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                book = fetch_kalshi_orderbook(market["ticker"], get)
                book_status = "OK" if book else "EMPTY"
            except Exception as exc:  # noqa: BLE001 - malformed book never kills the stream
                book, book_status = None, f"UNAVAILABLE: {type(exc).__name__}: {exc}"[:120]
            record = {**base, "venue": "KALSHI", "outcome": outcome, **kalshi_quote(market),
                      "fetched_at": stamp, "source_url": k_url, "book_status": book_status,
                      "book_fetched_at": book_at,
                      "asks": book["asks"][:5] if book else None,
                      "ask_depth": book["ask_depth"] if book else None}
            # Blue 2026-09-29 diagnostic (no verdict): Kalshi mid - Pinnacle no-vig fair.
            try:
                from ..factory.sportsfair import devig_power
                fair = devig_power(event["prices"]).get(outcome)
            except (KeyError, ValueError, TypeError):
                fair = None
            bid, ask = record.get("best_bid"), record.get("best_ask")
            record.update({"pinnacle_fair": fair,
                           "pinnacle_observed_at": event.get("observed_at", stamp),
                           "mid_minus_fair": ((bid + ask) / 2 - fair) if None not in (bid, ask, fair)
                           else None})
            yield f"{QUOTES_KALSHI}.jsonl", f"{stamp}|{event['event_id']}|{outcome}", record


# --- R2 (H-011): fill data ------------------------------------------------------------
# Trades are retained indefinitely by both venues, so this is a single retrospective
# sweep per matched market rather than a live poll: the first time (and only the
# first time) a market's kickoff falls between TRADE_MIN_AGE_H and TRADE_MAX_AGE_H
# hours in the past, pull its whole trade tape in one paginated pull, covering
# everything from that market's own history through settlement in one go. A market
# outside that window (too soon: trades may still be printing; too late: it never
# got its one sweep) is left alone rather than queued -- a deliberate simplification
# (see the module docstring) that trades a small chance of missing a very late print
# for not polling a settled market's trade tape for three days straight.
TRADES = "sports_quotes/trades"
TRADES_LEDGER = "sports_quotes/trades_ledger"
TRADE_MIN_AGE_H = 1.0
TRADE_MAX_AGE_H = 72.0
POLYMARKET_TRADES = ("https://data-api.polymarket.com/trades?market={market}"
                     "&limit={limit}&offset={offset}")
KALSHI_TRADES = "https://api.elections.kalshi.com/trade-api/v2/markets/trades?ticker={ticker}&limit=1000"


def _latest_matched_markets(out: Path) -> list[tuple[str, str, dict[str, Any]]]:
    """Every distinct matched (venue, market_id) seen in the quotes streams, each with
    its latest record (kickoff/outcome/event id do not change across a market's own
    snapshots, so "latest" is just a convenient, cheap pick). Shared by R2 (trades)
    and R4 (order-book snapshots): both act on "matched markets", which here means
    "appears in sports_quotes/{polymarket,kalshi}" -- those streams are only ever
    written for an outcome that ``_venue_quotes`` actually mapped."""
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for stream, venue, id_field in ((QUOTES_PM, "POLYMARKET", "market_id"),
                                     (QUOTES_KALSHI, "KALSHI", "ticker")):
        for item in read_stream(out, stream):
            record = item["record"]
            market_id = record.get(id_field)
            if market_id:
                seen[(venue, market_id)] = record
    return [(venue, market_id, record) for (venue, market_id), record in seen.items()]


def _as_iso(value: Any) -> str:
    """Accept either unix-seconds or an ISO string (Polymarket's data-api endpoints
    are not consistent with each other about which one they use)."""
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip("-").isdigit()):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat(timespec="seconds")
    return str(value)


def parse_polymarket_trades(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One record per print (ASSUMPTION: field names per Polymarket's public data-api
    docs, not yet verified against a live response). A print with no discoverable id,
    price or size is dropped -- never given a fabricated id -- so a wrong assumption
    here shows up as fewer trades, not corrupted ones."""
    out = []
    for item in payload or []:
        trade_id = item.get("transactionHash") or item.get("id")
        price, size = _float(item.get("price")), _float(item.get("size"))
        traded_at = item.get("timestamp") if item.get("timestamp") is not None else item.get("match_time")
        if not trade_id or price is None or size is None or size <= 0 or traded_at is None:
            continue
        out.append({"trade_id": str(trade_id), "price": price, "size": size,
                    "side": item.get("side"), "outcome": item.get("outcome"),
                    "traded_at": _as_iso(traded_at)})
    return out


def fetch_polymarket_trades(market_id: str, get: Callable[[str], Any] = get_json,
                            page_size: int = 500, max_pages: int = 20) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page_index in range(max_pages):
        offset = page_index * page_size
        page = get(POLYMARKET_TRADES.format(market=market_id, limit=page_size, offset=offset)) or []
        out.extend(parse_polymarket_trades(page))
        if len(page) < page_size:
            break
    return out


def parse_kalshi_trades(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    """One record per print, plus the pagination cursor (Kalshi trade-api v2;
    ASSUMPTION: field names per Kalshi's public docs, not yet verified live)."""
    trades = []
    for item in (payload or {}).get("trades") or []:
        trade_id = item.get("trade_id")
        if not trade_id:
            continue
        trades.append({"trade_id": str(trade_id), "yes_price": _float(item.get("yes_price")),
                       "no_price": _float(item.get("no_price")), "count": _float(item.get("count")),
                       "taker_side": item.get("taker_side"), "traded_at": item.get("created_time")})
    cursor = (payload or {}).get("cursor") or None
    return trades, cursor


def fetch_kalshi_trades(ticker: str, get: Callable[[str], Any] = get_json,
                        max_pages: int = 20) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor = ""
    for _ in range(max_pages):
        url = KALSHI_TRADES.format(ticker=ticker) + (f"&cursor={cursor}" if cursor else "")
        trades, next_cursor = parse_kalshi_trades(get(url))
        out.extend(trades)
        if not next_cursor or not trades or next_cursor == cursor:
            break
        cursor = next_cursor
    return out


def collect_trades(out: Path, now: datetime, get: Callable[[str], Any] = get_json,
                   min_age_h: float = TRADE_MIN_AGE_H, max_age_h: float = TRADE_MAX_AGE_H
                   ) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """R2 (H-011): one paginated trade-tape sweep per matched market, done once, the
    first time its kickoff is between ``min_age_h`` and ``max_age_h`` hours in the
    past. Append-only and deduplicated by ``trade_id`` (the record key); a market
    already in ``TRADES_LEDGER`` (fetched or permanently errored) is never retried.
    """
    stamp = now.isoformat(timespec="seconds")
    fetched = {(row["record"]["venue"], row["record"]["market_id"])
              for row in read_stream(out, TRADES_LEDGER)}
    for venue, market_id, info in _latest_matched_markets(out):
        if (venue, market_id) in fetched:
            continue
        kickoff = parse_time(info["commence_time"])
        age_h = (now - kickoff).total_seconds() / 3600
        if not (min_age_h <= age_h <= max_age_h):
            continue
        try:
            trades = (fetch_polymarket_trades(market_id, get) if venue == "POLYMARKET"
                      else fetch_kalshi_trades(market_id, get))
            status = "OK"
        except DataUnavailable as exc:
            trades, status = [], str(exc)[:200]
        for trade in trades:
            yield (f"{TRADES}.jsonl", f"{venue}|{market_id}|{trade['trade_id']}",
                  {**trade, "venue": venue, "market_id": market_id,
                   "odds_event_id": info.get("odds_event_id"), "outcome": info.get("outcome"),
                   "commence_time": info["commence_time"], "fetched_at": stamp,
                   "source": "polymarket_data_api" if venue == "POLYMARKET" else "kalshi_trade_api"})
        yield (f"{TRADES_LEDGER}.jsonl", f"{venue}|{market_id}",
              {"venue": venue, "market_id": market_id, "odds_event_id": info.get("odds_event_id"),
               "outcome": info.get("outcome"), "commence_time": info["commence_time"],
               "fetched_at": stamp, "status": status, "trade_count": len(trades),
               "age_at_fetch_h": round(age_h, 2)})


# --- R4 (H-013): liquidity rewards ------------------------------------------------------
# The TRUE venue programs sample far more often than this collector can (Polymarket
# ~1/minute, Kalshi LIP ~1/second per the registry S16/S35). A 6-hourly full collect
# can only take a sparse snapshot of the reward-eligible book, so research/fast_rail/
# h013/rewards.py's theoretical reward from these snapshots is a coarse, sparsely-
# sampled proxy for the venue's real daily payout, not a replication of it -- treat it
# as directional. Program-snapshot streams are append-only with restatements kept
# (Stream's default: a changed value under the same key is stored as a restatement,
# never overwrites); order books are always a fresh key (one per run) since a book is
# never "the same value observed twice" in the way a program's terms are.
REWARDS_POLYMARKET = "rewards/polymarket"
REWARDS_KALSHI = "rewards/kalshi"
REWARDS_ORDERBOOKS = "rewards/orderbooks"
ORDERBOOK_HORIZON_H = 48.0
KALSHI_INCENTIVE_PROGRAMS = "https://api.elections.kalshi.com/trade-api/v2/incentive_programs"
POLYMARKET_REWARDS = "https://clob.polymarket.com/rewards/markets/current"
KALSHI_ORDERBOOK = "https://api.elections.kalshi.com/trade-api/v2/markets/{ticker}/orderbook"


def parse_kalshi_incentive_programs(payload: Any) -> list[dict[str, Any]]:
    """One record per program (ASSUMPTION: Kalshi's public docs describe the
    mechanism -- a per-market/day pool, S35 -- but this build has no live key to
    confirm the response's exact field names; every extracted field is best-effort
    and the raw item is kept alongside so a wrong assumption is still recoverable).
    A program with no discoverable identifying key is dropped, not fabricated one."""
    items = payload.get("incentive_programs") if isinstance(payload, dict) else payload
    out = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        key = (item.get("series_ticker") or item.get("market_ticker") or item.get("ticker")
              or item.get("id") or item.get("product_id"))
        if key is None:
            continue
        out.append({"program_key": str(key), "series_ticker": item.get("series_ticker"),
                    "market_ticker": item.get("market_ticker") or item.get("ticker"),
                    "start_date": item.get("start_date"), "end_date": item.get("end_date"),
                    "daily_pool_dollars": _float(item.get("daily_pool_dollars")
                                                 if item.get("daily_pool_dollars") is not None
                                                 else item.get("pool_dollars")),
                    "raw": item})
    return out


def fetch_kalshi_incentive_programs(get: Callable[[str], Any] = get_json) -> list[dict[str, Any]]:
    return parse_kalshi_incentive_programs(get(KALSHI_INCENTIVE_PROGRAMS))


def parse_polymarket_rewards(payload: Any) -> tuple[list[dict[str, Any]], str | None]:
    """One record per rewarded market plus the ``next_cursor`` (ASSUMPTION: field
    names per Polymarket CLOB's public docs -- ``rewards_min_size``/
    ``rewards_max_spread`` govern the quadratic-score band used in
    ``research/fast_rail/h013/rewards.py`` -- not yet verified against a live
    response; the raw item is always kept)."""
    items = payload.get("data") if isinstance(payload, dict) else payload
    out = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        market = item.get("condition_id") or item.get("market") or item.get("id")
        if market is None:
            continue
        rewards = item.get("rewards_config") or item.get("rewards") or {}
        out.append({"market_id": str(market),
                    "min_size": _float(rewards.get("rewards_min_size")
                                       if rewards.get("rewards_min_size") is not None
                                       else item.get("rewards_min_size")),
                    "max_spread": _float(rewards.get("rewards_max_spread")
                                         if rewards.get("rewards_max_spread") is not None
                                         else item.get("rewards_max_spread")),
                    "daily_rate": _float(item.get("rewards_daily_rate")
                                         if item.get("rewards_daily_rate") is not None
                                         else item.get("daily_rate")),
                    "raw": item})
    cursor = payload.get("next_cursor") if isinstance(payload, dict) else None
    return out, (cursor or None)


def fetch_polymarket_rewards(get: Callable[[str], Any] = get_json,
                             max_pages: int = 50) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    cursor, seen_cursors = "", set()
    for _ in range(max_pages):
        url = POLYMARKET_REWARDS + (f"?next_cursor={cursor}" if cursor else "")
        page, next_cursor = parse_polymarket_rewards(get(url))
        out.extend(page)
        if not next_cursor or next_cursor in seen_cursors or next_cursor == "LTE=":
            break                                    # "LTE=" is the CLOB's own end-of-list cursor
        seen_cursors.add(next_cursor)
        cursor = next_cursor
    return out


def parse_kalshi_orderbook(payload: Any, ticker: str) -> dict[str, Any] | None:
    """Normalise Kalshi's complementary yes/no resting-order book (cents, 1-99) into
    the same {best_bid, best_ask, bids, asks, ...} shape ``parse_order_book`` returns
    for Polymarket. Kalshi's ``/orderbook`` publishes each side's own resting BUY
    orders only; a resting no-buy at price ``p`` is a resting yes-SELL at ``1-p``
    (the same complementary-pricing mechanic ``kalshi_quote``/``sportsfair`` already
    assume elsewhere in this codebase, not a new one)."""
    payload = payload or {}
    # Live API (2026): ``orderbook_fp`` with ``yes_dollars``/``no_dollars`` [price $, size];
    # legacy: ``orderbook`` with ``yes``/``no`` [price cents, size].
    fp = payload.get("orderbook_fp")
    book = fp if isinstance(fp, dict) else (payload.get("orderbook") or {})
    scale, suffix = (1.0, "_dollars") if isinstance(fp, dict) else (100.0, "")

    def side(name: str) -> list[tuple[float, float]]:
        levels = [(_float(p), _float(s)) for p, s in (book.get(name + suffix) or [])]
        return [(p / scale, s) for p, s in levels if p is not None and s is not None and s > 0]

    yes_bids = sorted(side("yes"), reverse=True)
    no_bids = sorted(side("no"), reverse=True)
    yes_asks = sorted((round(1 - p, 4), s) for p, s in no_bids)
    if not yes_bids and not yes_asks:
        return None
    return {"venue": "KALSHI", "market": ticker,
            "best_bid": yes_bids[0][0] if yes_bids else None,
            "best_ask": yes_asks[0][0] if yes_asks else None,
            "bid_depth": sum(s for _, s in yes_bids), "ask_depth": sum(s for _, s in yes_asks),
            "bids": yes_bids[:10], "asks": yes_asks[:10]}


def fetch_kalshi_orderbook(ticker: str, get: Callable[[str], Any] = get_json
                           ) -> dict[str, Any] | None:
    return parse_kalshi_orderbook(get(KALSHI_ORDERBOOK.format(ticker=ticker)), ticker)


def collect_rewards(out: Path, now: datetime, get: Callable[[str], Any] = get_json,
                    orderbook_horizon_h: float = ORDERBOOK_HORIZON_H
                    ) -> Iterator[tuple[str, str, dict[str, Any]]]:
    """R4 (H-013): venue-wide reward-program snapshots, every run, plus an order-book
    snapshot of every matched market kicking off within ``orderbook_horizon_h``.

    Program terms (pool size, dates, spread band) change slowly, like the existing
    ``polymarket/rules.jsonl``/``kalshi/rules.jsonl`` streams: each program/market
    keeps ONE stable key (``program_key``/``market_id``) across runs, with NO
    per-run field (a timestamp, a status) inside the record itself -- that field
    would change on every call regardless of the program's real terms and defeat
    the whole point of a stable key, turning every run into a spurious
    "restatement". An unchanged term is then a cheap ``Stream``-level "duplicate"
    and a changed one IS recorded as a real "restatement" (mission: "append-only,
    restatements kept"); "when was this last (re)observed" is exactly what the
    Stream wrapper's own ``observed_at`` (and a restatement's ``#restated@...``
    key suffix) already carries, so it is not duplicated here. A fetch failure
    yields nothing this run (no programs to attach a status to) and is visible in
    fetch_feeds.py's own per-lane run report instead. Order books are the
    opposite: a fresh, timestamped key every run, like ``QUOTES_PM``/
    ``QUOTES_KALSHI``, since a book is never "the same value observed twice".
    """
    stamp = now.isoformat(timespec="seconds")
    try:
        programs = fetch_kalshi_incentive_programs(get)
    except DataUnavailable:
        programs = []
    for program in programs:
        yield f"{REWARDS_KALSHI}.jsonl", program["program_key"], program
    try:
        rewards = fetch_polymarket_rewards(get)
    except DataUnavailable:
        rewards = []
    for reward in rewards:
        yield f"{REWARDS_POLYMARKET}.jsonl", reward["market_id"], reward
    for venue, market_id, info in _latest_matched_markets(out):
        kickoff = parse_time(info["commence_time"])
        if not (now < kickoff <= now + timedelta(hours=orderbook_horizon_h)):
            continue
        try:
            book = (parse_order_book(get(PM_BOOK.format(token=market_id)), "POLYMARKET", market_id)
                    if venue == "POLYMARKET" else fetch_kalshi_orderbook(market_id, get))
        except DataUnavailable:
            book = None
        if book is None:
            continue
        yield (f"{REWARDS_ORDERBOOKS}.jsonl", f"{stamp}|{venue}|{market_id}",
              {**book, "odds_event_id": info.get("odds_event_id"), "outcome": info.get("outcome"),
               "commence_time": info["commence_time"], "fetched_at": stamp})
