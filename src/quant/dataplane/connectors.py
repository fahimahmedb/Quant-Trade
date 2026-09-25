"""External data connectors: ready to plug in the moment a network path exists.

Every connector is two layers:

* a **pure parser** that turns one documented response shape into normalised
  records. Parsers are unit-tested offline against fixtures that mirror the
  public response formats, and never invent a value: a missing or malformed
  field drops the record;
* a thin **fetch** that performs the HTTP call through the standard library
  (so ``HTTPS_PROXY`` and the system CA bundle apply) and raises
  ``DataUnavailable`` on any transport failure, which the Control Plane already
  turns into a named BLOCKED dependency.

``TERMS`` records, per connector, what the provider's terms say about this use.
"grey" means a public endpoint used without circumventing any access control,
but outside the provider's documented or commercial API (for example Yahoo's
chart JSON). No connector here scrapes behind a login, rotates identities or
defeats rate limits; those are deliberately out of scope.

Collected records are written by ``scripts/fetch_feeds.py`` as append-only
JSONL under ``data/feeds/<connector>/``, keyed so a re-run never duplicates a
row. The GitHub Actions workflow ``data-feeds.yml`` runs that script on a
runner with internet access and commits the files to a data branch, which is
how this sandboxed repository receives external data.
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Callable

from .adapters import DataUnavailable

USER_AGENT = "quant-research/1.0 (paper/shadow research; contact via repository owner)"


# --- transport ----------------------------------------------------------------
def _request(url: str, *, method: str = "GET", body: Any = None,
             headers: dict[str, str] | None = None, timeout: float = 30.0,
             retries: int = 2, backoff: float = 2.0) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    merged = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if body is not None:
        merged["Content-Type"] = "application/json"
    merged.update(headers or {})
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(url, data=data, headers=merged, method=method)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503, 504):
                break                      # 4xx other than rate-limit: do not hammer
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
        if attempt < retries:
            time.sleep(backoff * (2 ** attempt))
    raise DataUnavailable(f"{url.split('?')[0]}: {type(last).__name__}: {last}")


def get_json(url: str, **kwargs: Any) -> Any:
    raw = _request(url, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DataUnavailable(f"{url.split('?')[0]}: invalid JSON: {exc}") from exc


def get_text(url: str, **kwargs: Any) -> str:
    return _request(url, **kwargs).decode("utf-8", errors="replace")


def _float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number == number and abs(number) != float("inf") else None


def _iso_day(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).date().isoformat()


# --- equities / ETFs ------------------------------------------------------------
YAHOO_CHART = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"


def parse_yahoo_chart(payload: dict[str, Any], symbol: str) -> list[dict[str, Any]]:
    """Daily bars from Yahoo's chart JSON. Dates are the exchange-local session."""
    chart = payload.get("chart") or {}
    if chart.get("error") or not chart.get("result"):
        return []
    result = chart["result"][0]
    offset = (result.get("meta") or {}).get("gmtoffset", 0) or 0
    quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    adjusted = (((result.get("indicators") or {}).get("adjclose") or [{}])[0]).get("adjclose")
    rows = []
    for index, stamp in enumerate(result.get("timestamp") or []):
        values = {name: _float((quote.get(name) or [None] * (index + 1))[index])
                  for name in ("open", "high", "low", "close", "volume")}
        adj = _float(adjusted[index]) if adjusted and index < len(adjusted) else None
        if None in (values["open"], values["close"], adj) or values["close"] <= 0:
            continue                         # incomplete bar: dropped, never filled
        rows.append({"date": _iso_day(stamp + offset), "symbol": symbol,
                     "open": values["open"], "high": values["high"] or values["close"],
                     "low": values["low"] or values["close"], "close": values["close"],
                     "adj_close": adj, "volume": values["volume"] or 0.0})
    return rows


def fetch_yahoo(symbol: str, range_: str = "1mo") -> list[dict[str, Any]]:
    url = YAHOO_CHART.format(symbol=urllib.parse.quote(symbol)) + f"?range={range_}&interval=1d"
    return parse_yahoo_chart(get_json(url, headers={"User-Agent": "Mozilla/5.0"}), symbol)


STOOQ_CSV = "https://stooq.com/q/d/l/?s={symbol}&i=d"


def parse_stooq_csv(text: str, symbol: str) -> list[dict[str, Any]]:
    """Stooq daily CSV (Date,Open,High,Low,Close,Volume). Not dividend-adjusted."""
    rows = []
    for record in csv.DictReader(io.StringIO(text)):
        values = {key: _float(record.get(key.capitalize()))
                  for key in ("open", "high", "low", "close", "volume")}
        if not record.get("Date") or None in (values["open"], values["close"]):
            continue
        rows.append({"date": record["Date"], "symbol": symbol, **values,
                     "adj_close": values["close"], "volume": values["volume"] or 0.0})
    return rows


def fetch_stooq(symbol: str) -> list[dict[str, Any]]:
    return parse_stooq_csv(get_text(STOOQ_CSV.format(symbol=symbol.lower())), symbol)


# --- macro / calendars ------------------------------------------------------------
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"


def parse_fred_csv(text: str, series: str) -> list[dict[str, Any]]:
    """FRED graph CSV. '.' marks a missing observation and is dropped."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    if not header:
        return []
    out = []
    for row in reader:
        if len(row) < 2:
            continue
        value = _float(row[1])
        if value is not None:
            out.append({"series": series, "date": row[0], "value": value})
    return out


def fetch_fred(series: str) -> list[dict[str, Any]]:
    return parse_fred_csv(get_text(FRED_CSV.format(series=series)), series)


FOMC_CALENDAR = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
_MONTHS = {name: number for number, name in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}


def _month(token: str) -> int:
    prefix = token.strip()[:3]
    return next((number for name, number in _MONTHS.items()
                 if prefix and name.startswith(prefix)), 0)


def parse_fomc_calendar(html: str) -> list[dict[str, Any]]:
    """Scheduled FOMC decision days (the last day of each meeting).

    The Federal Reserve page groups meetings under "<year> FOMC Meetings"
    headings, each with a month cell (e.g. "Jan/Feb") and a day cell
    (e.g. "31-1*"). Unscheduled meetings, notation votes and cancelled
    meetings are excluded: they are not known in advance, so a strategy may
    not condition on them.
    """
    meetings = []
    sections = re.split(r"(\d{4})\s+FOMC\s+Meetings", html)
    for position in range(1, len(sections) - 1, 2):
        year, body = int(sections[position]), sections[position + 1]
        cells = re.findall(r'fomc-meeting__month[^>]*>(.*?)</div>.*?fomc-meeting__date[^>]*>(.*?)</div>',
                           body, flags=re.S | re.I)
        for month_cell, day_cell in cells:
            month_text = re.sub(r"<[^>]+>", " ", month_cell).strip().lower()
            day_text = re.sub(r"<[^>]+>", " ", day_cell).strip().lower()
            if any(word in day_text for word in ("unscheduled", "notation", "cancel")):
                continue
            months = [_month(part) for part in month_text.split("/")]
            days = [int(value) for value in re.findall(r"\d+", day_text)]
            if not months or not months[-1] or not days:
                continue
            decision_month = months[-1]
            decision_year = year + 1 if (months[0] == 12 and decision_month == 1) else year
            meetings.append({"decision_date": date(decision_year, decision_month,
                                                   days[-1]).isoformat(),
                             "projections": "*" in day_text})
    return sorted({item["decision_date"]: item for item in meetings}.values(),
                  key=lambda item: item["decision_date"])


def fetch_fomc_calendar() -> list[dict[str, Any]]:
    return parse_fomc_calendar(get_text(FOMC_CALENDAR, headers={"User-Agent": "Mozilla/5.0"}))


# --- crypto perpetual funding ------------------------------------------------------
HYPERLIQUID_INFO = "https://api.hyperliquid.xyz/info"


def parse_hyperliquid_funding(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hyperliquid ``fundingHistory``: hourly rate paid by longs (fraction)."""
    out = []
    for item in payload or []:
        rate, stamp = _float(item.get("fundingRate")), _float(item.get("time"))
        if rate is None or stamp is None or not item.get("coin"):
            continue
        out.append({"venue": "HYPERLIQUID", "coin": item["coin"], "time_ms": int(stamp),
                    "rate": rate, "interval_hours": 1})
    return out


def fetch_hyperliquid_funding(coin: str, start_ms: int) -> list[dict[str, Any]]:
    return parse_hyperliquid_funding(get_json(HYPERLIQUID_INFO, method="POST", body={
        "type": "fundingHistory", "coin": coin, "startTime": start_ms}))


def parse_hyperliquid_universe(payload: Any) -> list[dict[str, Any]]:
    """``metaAndAssetCtxs``: [meta, contexts] with daily notional volume per coin."""
    if not isinstance(payload, list) or len(payload) != 2:
        return []
    universe = (payload[0] or {}).get("universe") or []
    out = []
    for asset, context in zip(universe, payload[1] or []):
        volume, mark = _float(context.get("dayNtlVlm")), _float(context.get("markPx"))
        if asset.get("name") and volume is not None and mark is not None:
            out.append({"venue": "HYPERLIQUID", "coin": asset["name"], "mark": mark,
                        "day_notional_volume": volume,
                        "funding_now": _float(context.get("funding"))})
    return out


def fetch_hyperliquid_universe() -> list[dict[str, Any]]:
    return parse_hyperliquid_universe(get_json(HYPERLIQUID_INFO, method="POST",
                                               body={"type": "metaAndAssetCtxs"}))


BYBIT_FUNDING = ("https://api.bybit.com/v5/market/funding/history?category=linear"
                 "&symbol={symbol}&limit=200")


def parse_bybit_funding(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if (payload or {}).get("retCode") not in (0, None):
        return []
    out = []
    for item in ((payload.get("result") or {}).get("list") or []):
        rate, stamp = _float(item.get("fundingRate")), _float(item.get("fundingRateTimestamp"))
        symbol = item.get("symbol") or ""
        if rate is None or stamp is None or not symbol.endswith("USDT"):
            continue
        out.append({"venue": "BYBIT", "coin": symbol[:-4], "time_ms": int(stamp),
                    "rate": rate, "interval_hours": 8})
    return out


def fetch_bybit_funding(coin: str) -> list[dict[str, Any]]:
    return parse_bybit_funding(get_json(BYBIT_FUNDING.format(symbol=f"{coin}USDT")))


BINANCE_FUNDING = "https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit=1000"


def parse_binance_funding(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for item in payload or []:
        rate, stamp = _float(item.get("fundingRate")), _float(item.get("fundingTime"))
        symbol = item.get("symbol") or ""
        if rate is None or stamp is None or not symbol.endswith("USDT"):
            continue
        out.append({"venue": "BINANCE", "coin": symbol[:-4], "time_ms": int(stamp),
                    "rate": rate, "interval_hours": 8})
    return out


def fetch_binance_funding(coin: str) -> list[dict[str, Any]]:
    return parse_binance_funding(get_json(BINANCE_FUNDING.format(symbol=f"{coin}USDT")))


# --- prediction markets -------------------------------------------------------------
POLYMARKET_MARKETS = ("https://gamma-api.polymarket.com/markets?active=true&closed=false"
                      "&limit={limit}&offset={offset}")
POLYMARKET_BOOK = "https://clob.polymarket.com/book?token_id={token}"


def parse_polymarket_markets(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for item in payload or []:
        try:
            tokens = json.loads(item.get("clobTokenIds") or "[]")
            outcomes = json.loads(item.get("outcomes") or "[]")
            prices = [_float(value) for value in json.loads(item.get("outcomePrices") or "[]")]
        except (TypeError, json.JSONDecodeError):
            continue
        if not item.get("conditionId") or len(tokens) != len(outcomes):
            continue
        out.append({"venue": "POLYMARKET", "market_id": item["conditionId"],
                    "question": item.get("question"), "category": item.get("category"),
                    "end_date": item.get("endDate"), "neg_risk": bool(item.get("negRisk")),
                    "event_slug": ((item.get("events") or [{}])[0] or {}).get("slug"),
                    "resolution_source": item.get("resolutionSource"),
                    "description": item.get("description"),
                    "tokens": [{"token_id": token, "outcome": outcome, "price": price}
                               for token, outcome, price in zip(tokens, outcomes, prices)],
                    "volume_24h": _float(item.get("volume24hr")),
                    "liquidity": _float(item.get("liquidity"))})
    return out


def fetch_polymarket_markets(limit: int = 500, offset: int = 0) -> list[dict[str, Any]]:
    return parse_polymarket_markets(get_json(POLYMARKET_MARKETS.format(limit=limit,
                                                                       offset=offset)))


def parse_order_book(payload: dict[str, Any], venue: str, market: str) -> dict[str, Any] | None:
    """Top of book and depth from a {bids:[{price,size}], asks:[...]} book."""
    def levels(side: str) -> list[tuple[float, float]]:
        parsed = [(_float(level.get("price")), _float(level.get("size")))
                  for level in (payload or {}).get(side) or []]
        return [(p, s) for p, s in parsed if p is not None and s is not None and s > 0]
    bids = sorted(levels("bids"), reverse=True)
    asks = sorted(levels("asks"))
    if not bids and not asks:
        return None
    return {"venue": venue, "market": market,
            "best_bid": bids[0][0] if bids else None, "best_ask": asks[0][0] if asks else None,
            "bid_depth": sum(size for _, size in bids), "ask_depth": sum(size for _, size in asks),
            "bids": bids[:10], "asks": asks[:10]}


def fetch_polymarket_book(token_id: str) -> dict[str, Any] | None:
    return parse_order_book(get_json(POLYMARKET_BOOK.format(token=token_id)),
                            "POLYMARKET", token_id)


KALSHI_MARKETS = "https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit={limit}"


def parse_kalshi_markets(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for item in (payload or {}).get("markets") or []:
        if not item.get("ticker"):
            continue
        cents = {key: _float(item.get(key)) for key in ("yes_bid", "yes_ask", "no_bid", "no_ask")}
        out.append({"venue": "KALSHI", "market_id": item["ticker"],
                    "event_ticker": item.get("event_ticker"), "title": item.get("title"),
                    "close_time": item.get("close_time"),
                    "rules_primary": item.get("rules_primary"),
                    "yes_bid": cents["yes_bid"] / 100 if cents["yes_bid"] is not None else None,
                    "yes_ask": cents["yes_ask"] / 100 if cents["yes_ask"] is not None else None,
                    "volume_24h": _float(item.get("volume_24h")),
                    "open_interest": _float(item.get("open_interest"))})
    return out


def fetch_kalshi_markets(limit: int = 1000) -> list[dict[str, Any]]:
    return parse_kalshi_markets(get_json(KALSHI_MARKETS.format(limit=limit)))


# --- sports odds ------------------------------------------------------------------
ODDS_API = ("https://api.the-odds-api.com/v4/sports/{sport}/odds?apiKey={key}&regions=eu,us"
            "&markets=h2h&oddsFormat=decimal")


def parse_odds_api(payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The Odds API v4 h2h: one record per event x bookmaker with decimal prices."""
    out = []
    for event in payload or []:
        for book in event.get("bookmakers") or []:
            for market in book.get("markets") or []:
                if market.get("key") != "h2h":
                    continue
                prices = {outcome.get("name"): _float(outcome.get("price"))
                          for outcome in market.get("outcomes") or []}
                if not prices or any(value is None or value <= 1 for value in prices.values()):
                    continue
                out.append({"event_id": event.get("id"), "sport": event.get("sport_key"),
                            "commence_time": event.get("commence_time"),
                            "home": event.get("home_team"), "away": event.get("away_team"),
                            "bookmaker": book.get("key"),
                            "quote_time": market.get("last_update") or book.get("last_update"),
                            "prices": prices})
    return out


def fetch_odds(sport: str) -> list[dict[str, Any]]:
    key = os.environ.get("ODDS_API_KEY")
    if not key:
        raise DataUnavailable("ODDS_API_KEY is not configured (paid/free-tier key required)")
    return parse_odds_api(get_json(ODDS_API.format(sport=sport, key=key)))


# --- registry ------------------------------------------------------------------------
@dataclass(frozen=True)
class ConnectorSpec:
    name: str
    domain: str
    terms: str            # "documented" | "grey" | "keyed"
    note: str
    probe: Callable[[], Any]
    requires_env: tuple[str, ...] = field(default_factory=tuple)


CONNECTORS: dict[str, ConnectorSpec] = {spec.name: spec for spec in [
    ConnectorSpec("yahoo_chart", "query2.finance.yahoo.com", "grey",
                  "undocumented public JSON; Yahoo terms restrict automated/commercial use; "
                  "personal research only, low request rate", lambda: fetch_yahoo("SPY", "5d")),
    ConnectorSpec("stooq", "stooq.com", "grey",
                  "free CSV download; informal terms; unadjusted prices",
                  lambda: fetch_stooq("spy.us")),
    ConnectorSpec("fred", "fred.stlouisfed.org", "documented",
                  "public CSV; attribution requested", lambda: fetch_fred("DGS3MO")),
    ConnectorSpec("fomc_calendar", "www.federalreserve.gov", "documented",
                  "public government page (HTML layout may change)", fetch_fomc_calendar),
    ConnectorSpec("hyperliquid", "api.hyperliquid.xyz", "documented",
                  "public info API; geo terms apply to trading, not to reading",
                  fetch_hyperliquid_universe),
    ConnectorSpec("bybit", "api.bybit.com", "documented",
                  "public market API; blocked from some jurisdictions (e.g. US IPs)",
                  lambda: fetch_bybit_funding("BTC")),
    ConnectorSpec("binance_futures", "fapi.binance.com", "documented",
                  "public market API; HTTP 451 from US IPs", lambda: fetch_binance_funding("BTC")),
    ConnectorSpec("polymarket", "gamma-api.polymarket.com", "documented",
                  "public read API; trading restricted by jurisdiction",
                  lambda: fetch_polymarket_markets(5)),
    ConnectorSpec("kalshi", "api.elections.kalshi.com", "documented",
                  "public market data; trading requires a KYC account",
                  lambda: fetch_kalshi_markets(5)),
    ConnectorSpec("odds_api", "api.the-odds-api.com", "keyed",
                  "commercial API with a free tier; key in ODDS_API_KEY",
                  lambda: fetch_odds("soccer_epl"), ("ODDS_API_KEY",)),
]}


def probe_all() -> dict[str, dict[str, Any]]:
    """Reachability of every connector; never raises."""
    report = {}
    for name, spec in CONNECTORS.items():
        missing = [variable for variable in spec.requires_env if not os.environ.get(variable)]
        if missing:
            report[name] = {"status": "NOT_CONFIGURED", "missing": missing, "terms": spec.terms}
            continue
        started = time.time()
        try:
            result = spec.probe()
            count = len(result) if hasattr(result, "__len__") else 1
            report[name] = {"status": "OK" if count else "EMPTY", "records": count,
                            "seconds": round(time.time() - started, 2), "terms": spec.terms}
        except DataUnavailable as exc:
            report[name] = {"status": "UNREACHABLE", "error": str(exc)[:200],
                            "terms": spec.terms}
        except Exception as exc:  # a parser/shape change must be visible, not fatal
            report[name] = {"status": "PARSE_ERROR", "error": f"{type(exc).__name__}: {exc}"[:200],
                            "terms": spec.terms}
    return report
