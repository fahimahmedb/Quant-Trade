"""Build the Kalshi weather maker-side dataset (H-004) from the public trade API.

    python3 scripts/build_kalshi_weather_trades.py --fetch   # network -> data/raw/fast_rail/h004 (resumable)
    python3 scripts/build_kalshi_weather_trades.py           # raw -> dataset (offline, stdlib)

Source: ``https://api.elections.kalshi.com/trade-api/v2`` (public, unauthenticated):
``/series?category=Climate and Weather``; settled markets from ``/historical/markets``
(settled before the historical cutoff, ``/historical/cutoff``) and
``/markets?status=settled`` (after it); trades from ``/historical/trades`` or
``/markets/trades`` depending on the market's close vs the trades cutoff.

SAMPLE (declared before any trade was fetched or any P&L computed; fixed by
calendar rule, never chosen by outcome):

* series: the seven daily-high series with >= 12 months of settled history at
  the start of the window: KXHIGHNY, KXHIGHCHI, KXHIGHMIA, KXHIGHAUS, KXHIGHLAX,
  KXHIGHDEN, KXHIGHPHIL (the other ~43 KXHIGH* series are younger/thinner);
* event dates 2025-09-01 .. 2026-08-31 (12 months) whose day of month is 5, 15
  or 25 -> 36 dates x 7 series = 252 events; every market of those events
  (all strikes) that settled yes/no;
* the full trade tape of each such market (no trade-level sampling).
* comparison (descriptive only, not a trial): crypto series KXBTCD, the 17:00 ET
  event on the 15th of each month of the same window, every market with volume.

The whole tape is not committed (NYC alone prints ~0.5M trades a month), which is
why events are sampled by date. Capacity is scaled from the sample to the full
seven-series universe with the ``volume_fp`` of every market in the window.

Raw storage: market/series listings are stored verbatim (gzip). Trade pages are
stored as a deterministic projection (created_time, taker_side, yes_price_dollars,
count_fp, is_block_trade) because the verbatim pages are ~5x larger (random
trade ids); the manifest records the sha256 of the verbatim response bytes of
every page *and* the sha256 of the stored projection file.

Derived ``data/fast_rail/kalshi_weather_trades.csv.gz``: one row per
(market, taker_side, yes_price) with trade and contract counts, the maker fee
summed over trade prints (each rounded up to the cent, see
``quant.factory.kalshi_maker``), gross and net maker P&L to settlement (cents)
and maker capital at risk (USD). Excluded before aggregation: block trades,
prints after the market's ``close_time``, markets whose result is not yes/no.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.factory import kalshi_maker as km  # noqa: E402

BASE = "https://api.elections.kalshi.com/trade-api/v2"
RAW = ROOT / "data" / "raw" / "fast_rail" / "h004"
OUT = ROOT / "data" / "fast_rail" / "kalshi_weather_trades.csv.gz"
META = ROOT / "data" / "fast_rail" / "kalshi_weather_trades.csv.meta.json"

SERIES = ["KXHIGHNY", "KXHIGHCHI", "KXHIGHMIA", "KXHIGHAUS", "KXHIGHLAX", "KXHIGHDEN", "KXHIGHPHIL"]
WINDOW = (dt.date(2025, 9, 1), dt.date(2026, 8, 31))
DAYS = (5, 15, 25)
COMPARISON_SERIES = "KXBTCD"
COMPARISON_DAY, COMPARISON_HOUR = 15, "17"
TRADE_FIELDS = ["created_time", "taker_side", "yes_price_dollars", "count_fp", "is_block_trade"]
MIN_INTERVAL = 0.12


# ----------------------------------------------------------------------- fetch

_last = [0.0]


def _get(path: str, params: dict) -> tuple[str, bytes]:
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(10):
        wait = _last[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return url, resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 429 or exc.code >= 500:
                retry = exc.headers.get("Retry-After")
                time.sleep(float(retry) if retry else min(60, 2 ** attempt))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(min(60, 2 ** attempt))
    raise RuntimeError(f"giving up on {url}")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _manifest(entry: dict) -> None:
    with (RAW / "manifest.jsonl").open("a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def _gz(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, compresslevel=9) as fh:
        fh.write(data)
    return buf.getvalue()


def _save_verbatim(rel: str, url: str, body: bytes) -> None:
    path = RAW / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_gz(body))
    _manifest({"url": url, "fetched_at": _now(), "sha256": hashlib.sha256(body).hexdigest(),
               "bytes": len(body), "stored": rel, "stored_as": "verbatim"})


def _paged(path: str, params: dict, key: str, rel_prefix: str,
           stop_before: str | None = None) -> list[dict]:
    """Fetch every page (verbatim) unless already stored; return the items.

    ``stop_before``: listings come newest close first; stop once a page reaches
    markets that closed before this ISO time (the historical listing ignores
    ``min_close_ts``, and older history is outside the declared window).
    """
    items: list[dict] = []
    cursor, page = "", 0
    while True:
        rel = f"{rel_prefix}_p{page:03d}.json.gz"
        if (RAW / rel).exists():
            body = gzip.decompress((RAW / rel).read_bytes())
        else:
            q = dict(params, limit=1000)
            if cursor:
                q["cursor"] = cursor
            url, body = _get(path, q)
            _save_verbatim(rel, url, body)
        data = json.loads(body)
        items += data.get(key, [])
        cursor = data.get("cursor") or ""
        page += 1
        if not cursor or not data.get(key):
            return items
        if stop_before and min(x["close_time"] for x in data[key]) < stop_before:
            return items


def _ts(day: dt.date) -> int:
    return int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())


def _date_or_none(event_ticker: str) -> dt.date | None:
    try:
        return km.event_date(event_ticker)
    except (KeyError, ValueError, IndexError):
        return None  # legacy tickers such as HIGHCHI-2-24FEB28 (outside the window)


def _in_sample(event_ticker: str) -> bool:
    d = _date_or_none(event_ticker)
    return d is not None and WINDOW[0] <= d <= WINDOW[1] and d.day in DAYS


def _in_comparison(event_ticker: str) -> bool:
    code = event_ticker.split("-")[1]
    d = _date_or_none(event_ticker)
    return (d is not None and WINDOW[0] <= d <= WINDOW[1] and d.day == COMPARISON_DAY
            and code[7:] == COMPARISON_HOUR)


def _fetch_trades(ticker: str, endpoint: str) -> None:
    rel = f"trades/{ticker}.json.gz"
    if (RAW / rel).exists():
        return
    rows, cursor, pages = [], "", []
    while True:
        q = {"ticker": ticker, "limit": 1000}
        if cursor:
            q["cursor"] = cursor
        url, body = _get(endpoint, q)
        data = json.loads(body)
        pages.append({"url": url, "fetched_at": _now(), "sha256": hashlib.sha256(body).hexdigest(),
                      "bytes": len(body), "n": len(data.get("trades", []))})
        rows += [[t[f] if f != "is_block_trade" else int(bool(t[f])) for f in TRADE_FIELDS]
                 for t in data.get("trades", [])]
        cursor = data.get("cursor") or ""
        if not cursor or not data.get("trades"):
            break
    stored = json.dumps({"ticker": ticker, "endpoint": endpoint, "fields": TRADE_FIELDS,
                         "trades": rows}, separators=(",", ":")).encode()
    path = RAW / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_bytes(_gz(stored))
    for p in pages:
        _manifest(dict(p, stored=rel, stored_as="projection:" + ",".join(TRADE_FIELDS)))
    _manifest({"stored": rel, "stored_as": "projection_file", "n": len(rows),
               "sha256_stored": hashlib.sha256(stored).hexdigest(), "fetched_at": _now()})
    tmp.rename(path)  # the file's existence marks the market done (resume key)


def fetch() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if not (RAW / "series_weather.json.gz").exists():
        url, body = _get("/series", {"category": "Climate and Weather"})
        _save_verbatim("series_weather.json.gz", url, body)
    cutoff_url, cutoff_body = _get("/historical/cutoff", {})
    if not (RAW / "historical_cutoff.json.gz").exists():
        _save_verbatim("historical_cutoff.json.gz", cutoff_url, cutoff_body)
    cutoff = json.loads(gzip.decompress((RAW / "historical_cutoff.json.gz").read_bytes()))
    trades_cutoff = km.parse_ts(cutoff["trades_created_ts"])
    lo, hi = _ts(WINDOW[0]), _ts(WINDOW[1] + dt.timedelta(days=3))
    todo: list[tuple[str, str]] = []
    for s in SERIES + [COMPARISON_SERIES]:
        if s == COMPARISON_SERIES:
            # the crypto series lists ~100k markets; list only the sampled events
            markets = []
            d = WINDOW[0]
            while d <= WINDOW[1]:
                if d.day == COMPARISON_DAY:
                    ev = f"{s}-{d:%y}{d.strftime('%b').upper()}{d:%d}{COMPARISON_HOUR}"
                    markets += _paged("/historical/markets", {"event_ticker": ev}, "markets",
                                      f"markets/{ev}_hist")
                    markets += _paged("/markets", {"event_ticker": ev, "status": "settled"},
                                      "markets", f"markets/{ev}_live")
                d += dt.timedelta(days=1)
        else:
            markets = _paged("/historical/markets",
                             {"series_ticker": s, "min_close_ts": lo, "max_close_ts": hi},
                             "markets", f"markets/{s}_hist",
                             stop_before=f"{WINDOW[0]}T00:00:00Z")
            markets += _paged("/markets", {"series_ticker": s, "status": "settled",
                                           "min_close_ts": lo, "max_close_ts": hi},
                              "markets", f"markets/{s}_live")
        seen = set()
        for m in markets:
            if m["ticker"] in seen or m.get("result") not in ("yes", "no"):
                continue
            seen.add(m["ticker"])
            keep = (_in_comparison(m["event_ticker"]) and float(m.get("volume_fp") or 0) > 0
                    if s == COMPARISON_SERIES else _in_sample(m["event_ticker"]))
            if keep:
                close = km.parse_ts(m["close_time"])
                opened = km.parse_ts(m["open_time"])
                if opened < trades_cutoff < close:
                    raise RuntimeError(f"{m['ticker']} straddles the trades cutoff; handle explicitly")
                todo.append((m["ticker"], "/historical/trades" if close <= trades_cutoff
                             else "/markets/trades"))
    print(f"{len(todo)} markets to fetch", flush=True)
    for i, (ticker, endpoint) in enumerate(todo):
        _fetch_trades(ticker, endpoint)
        if i % 50 == 0:
            print(f"  {i}/{len(todo)} {ticker}", flush=True)


# ----------------------------------------------------------------------- build

def _markets() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in sorted((RAW / "markets").glob("*.json.gz")):
        for m in json.loads(gzip.decompress(path.read_bytes())).get("markets", []):
            out.setdefault(m["ticker"], m)
    return out


def build() -> dict:
    markets = _markets()
    universe: dict[str, float] = defaultdict(float)  # "SERIES|YYYY-MM" -> contracts
    for m in markets.values():
        s = m["ticker"].split("-")[0]
        if s in SERIES and m.get("result") in ("yes", "no"):
            d = _date_or_none(m["event_ticker"])
            if d is not None and WINDOW[0] <= d <= WINDOW[1]:
                universe[f"{s}|{d:%Y-%m}"] += float(m.get("volume_fp") or 0)
    agg: dict[tuple, list] = {}
    excluded = defaultdict(int)
    for path in sorted((RAW / "trades").glob("*.json.gz")):
        blob = json.loads(gzip.decompress(path.read_bytes()))
        m = markets[blob["ticker"]]
        fields = blob["fields"]
        for raw in blob["trades"]:
            t = dict(zip(fields, raw))
            if t["is_block_trade"]:
                excluded["block_trade"] += 1
                continue
            if not km.trade_is_eligible(t["created_time"], m["close_time"], m["result"], False):
                excluded["after_close_or_unsettled"] += 1
                continue
            try:
                p = km.price_cents(t["yes_price_dollars"])
            except ValueError:
                excluded["sub_cent_price"] += 1
                continue
            if not 1 <= p <= 99:
                excluded["price_outside_1_99"] += 1
                continue
            c = km.to_fraction(t["count_fp"])
            if c <= 0:
                excluded["zero_count"] += 1
                continue
            key = (m["ticker"], t["taker_side"], p)
            a = agg.setdefault(key, [0, Fraction(0), 0])
            a[0] += 1
            a[1] += c
            a[2] += km.maker_fee_cents(c, p)
    header = ["category", "series", "event_ticker", "event_date", "ticker", "close_time", "result",
              "taker_side", "yes_price", "n_trades", "contracts", "fee_cents", "gross_pnl_cents",
              "net_pnl_cents", "maker_capital_usd"]
    lines = [",".join(header)]
    n_trades = 0
    for (ticker, side, p), (n, c, fee) in sorted(agg.items()):
        m = markets[ticker]
        series = ticker.split("-")[0]
        per = km.maker_pnl_cents(side, p, m["result"] == "yes")
        gross = c * per
        capital = c * (p if side == "no" else 100 - p) / 100
        n_trades += n
        lines.append(",".join([
            "comparison" if series == COMPARISON_SERIES else "weather", series, m["event_ticker"],
            km.event_date(m["event_ticker"]).isoformat(), ticker, m["close_time"], m["result"],
            side, str(p), str(n), f"{float(c):.2f}", str(fee), f"{float(gross):.2f}",
            f"{float(gross - fee):.2f}", f"{float(capital):.2f}"]))
    text = ("\n".join(lines) + "\n").encode()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(_gz(text))
    weather = [ln for ln in lines[1:] if ln.startswith("weather,")]
    dates = sorted({ln.split(",")[3] for ln in weather})
    meta = {
        "dataset_id": "kalshi_weather_trades",
        "adapter": "kalshi_weather_trades_derivation",
        "source": BASE,
        "builder": "scripts/build_kalshi_weather_trades.py",
        "fingerprint_sha256": hashlib.sha256(text).hexdigest(),
        "rows": len(lines) - 1,
        "trades_aggregated": n_trades,
        "markets": len({k[0] for k in agg}),
        "weather_event_dates": [dates[0], dates[-1]] if dates else None,
        "sample_rule": {"series": SERIES, "window": [str(WINDOW[0]), str(WINDOW[1])],
                        "days_of_month": list(DAYS),
                        "comparison": f"{COMPARISON_SERIES} {COMPARISON_HOUR}:00 ET event on day "
                                      f"{COMPARISON_DAY} of each month, markets with volume"},
        "fee": {"formula": km.FEE_FORMULA, "source": km.FEE_SOURCE},
        "excluded_prints": dict(excluded),
        "universe_contracts_by_series_month": dict(sorted(universe.items())),
        "caveats": [
            "one row per (market, taker_side, yes_price); trade-level order is not needed for settlement P&L",
            "maker = resting side of each public print; no queue/fill model",
            "maker fee charged on every market and rounded up per print (conservative)",
            "trade pages stored as a field projection; manifest keeps sha256 of verbatim responses",
            "events sampled by calendar rule (days 5/15/25), not the full tape",
        ],
    }
    META.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    meta = build()
    print(json.dumps({k: meta[k] for k in ("rows", "trades_aggregated", "markets",
                                           "weather_event_dates", "excluded_prints")}))


if __name__ == "__main__":
    main()
