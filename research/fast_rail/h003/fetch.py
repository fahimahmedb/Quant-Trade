"""H-003 dataset builder: settled Kalshi binary markets + hourly candles (stdlib only).

Public, unauthenticated Kalshi API. Paced requests with backoff on 429; no bypass.
Sampling rule is fixed in PREREG.md and in SERIES below (outcome-blind hash order).
Resumable: markets already in markets.jsonl.gz are skipped.

    python3 research/fast_rail/h003/fetch.py
"""

from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import http.client
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.elections.kalshi.com/trade-api/v2"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "fast_rail", "h003")
PACE_S = 0.15
MAX_MARKETS_PER_EVENT = 25
CANDLE_LOOKBACK_H = 49  # 24h entry + 24h trailing volume + 1h slack

WEATHER = ["KXHIGHNY", "KXHIGHCHI", "KXHIGHMIA", "KXHIGHAUS", "KXHIGHDEN", "KXHIGHLAX", "KXHIGHPHIL"]
INDEX_CRYPTO = ["KXINX", "KXINXU", "KXNASDAQ100", "KXNASDAQ100U", "KXBTC", "KXBTCD", "KXETH", "KXETHD"]
MACRO = ["KXFED", "KXCPI", "KXCPIYOY", "KXPAYROLLS", "KXU3", "KXGDP"]
SERIES = {**{s: 120 for s in WEATHER}, **{s: 60 for s in INDEX_CRYPTO}, **{s: 120 for s in MACRO}}


def sample_key(ticker: str) -> str:
    return hashlib.sha256(("H-003|" + ticker).encode()).hexdigest()


def select_events(event_tickers: list[str], n: int) -> list[str]:
    return sorted(set(event_tickers), key=sample_key)[:n]


def select_markets(market_tickers: list[str], n: int = MAX_MARKETS_PER_EVENT) -> list[str]:
    return sorted(set(market_tickers), key=sample_key)[:n]


_last = [0.0]
_lock = threading.Lock()


def get(path: str, **query) -> tuple[dict, str, str]:
    url = BASE + path + ("?" + urllib.parse.urlencode(query) if query else "")
    for attempt in range(8):
        with _lock:  # global pacer shared by worker threads: <= 1/PACE_S requests per second
            wait = PACE_S - (time.monotonic() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read()
            return json.loads(raw), url, hashlib.sha256(raw).hexdigest()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return {}, url, ""
            if exc.code in (429, 500, 502, 503, 504):
                time.sleep(min(60, 2 ** attempt))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException):
            time.sleep(min(60, 2 ** attempt))
    raise RuntimeError(f"gave up on {url}")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(text: str) -> int:
    return int(dt.datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp())


def _num(block: dict | None, *keys: str) -> float | None:
    for key in keys:
        if block and block.get(key) not in (None, ""):
            return float(block[key])
    return None


def trim_candle(c: dict) -> list:
    """[end_ts, yes_bid_close, yes_ask_close, volume, open_interest]; live and historical formats."""
    return [int(c["end_period_ts"]),
            _num(c.get("yes_bid"), "close_dollars", "close"),
            _num(c.get("yes_ask"), "close_dollars", "close"),
            _num(c, "volume_fp", "volume") or 0.0,
            _num(c, "open_interest_fp", "open_interest") or 0.0]


def list_events(series: str) -> list[dict]:
    events, cursor = [], ""
    while True:
        data, _, _ = get("/events", series_ticker=series, status="settled", limit=200, cursor=cursor)
        batch = data.get("events", [])
        events += batch
        cursor = data.get("cursor") or ""
        if not cursor or not batch:
            return events


def event_markets(event_ticker: str) -> tuple[list[dict], str, str, str]:
    data, url, digest = get("/markets", event_ticker=event_ticker, limit=200)
    if data.get("markets"):
        return data["markets"], url, digest, "live"
    data, url, digest = get("/historical/markets", event_ticker=event_ticker, limit=200)
    return data.get("markets", []), url, digest, "historical"


def fetch_event(series: str, event_ticker: str) -> tuple[list[dict], dict]:
    markets, murl, mdigest, source = event_markets(event_ticker)
    binary = {m["ticker"]: m for m in markets
              if m.get("market_type", "binary") == "binary" and m.get("result") in ("yes", "no")}
    keep = select_markets(list(binary))
    rows = []
    for ticker in keep:
        m = binary[ticker]
        close_ts = parse_ts(m["close_time"])
        q = {"period_interval": 60, "start_ts": close_ts - CANDLE_LOOKBACK_H * 3600, "end_ts": close_ts}
        qt = urllib.parse.quote(ticker, safe="")
        path = (f"/historical/markets/{qt}/candlesticks" if source == "historical"
                else f"/series/{series}/markets/{qt}/candlesticks")
        cdata, curl, cdigest = get(path, **q)
        rows.append({
            "ticker": ticker, "event_ticker": event_ticker, "series": series,
            "close_time": m["close_time"], "close_ts": close_ts, "result": m["result"],
            "strike_type": m.get("strike_type"), "volume": _num(m, "volume_fp", "volume"),
            "candles": [trim_candle(c) for c in cdata.get("candlesticks", [])],
            "provenance": {"market_url": murl, "market_sha256": mdigest, "candles_url": curl,
                           "candles_sha256": cdigest, "source": source, "fetched_at": now()},
        })
    return rows, {"event_ticker": event_ticker, "series": series, "n_markets_listed": len(binary),
                  "n_markets_kept": len(keep), "sample_key": sample_key(event_ticker), "fetched_at": now()}


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    events_path = os.path.join(OUT, "events.jsonl.gz")
    markets_path = os.path.join(OUT, "markets.jsonl.gz")
    done_events: set[str] = set()
    if os.path.exists(events_path):
        with gzip.open(events_path, "rt") as fh:
            done_events = {json.loads(line)["event_ticker"] for line in fh if line.strip()}
    only = set(sys.argv[1:])
    for series, n_events in SERIES.items():
        if only and series not in only:
            continue
        listing = list_events(series)
        chosen = select_events([e["event_ticker"] for e in listing], n_events)
        meta = {e["event_ticker"]: e for e in listing}
        todo = [e for e in chosen if e not in done_events]
        print(f"{series}: {len(listing)} settled events, {len(chosen)} sampled, {len(todo)} to fetch", flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            # Written only after an event is complete, so a crash never leaves a half event.
            for rows, ev_line in pool.map(lambda e: fetch_event(series, e), todo):
                with gzip.open(markets_path, "at") as fh:
                    for row in rows:
                        fh.write(json.dumps(row, separators=(",", ":")) + "\n")
                ev_line["mutually_exclusive"] = meta[ev_line["event_ticker"]].get("mutually_exclusive")
                with gzip.open(events_path, "at") as fh:
                    fh.write(json.dumps(ev_line, separators=(",", ":")) + "\n")
                done_events.add(ev_line["event_ticker"])
        print(f"{series}: done", flush=True)
    return 0


def finalize() -> int:
    """Rewrite both files as single gzip members (deduplicated) and write MANIFEST.json."""
    manifest = {"hypothesis": "H-003", "dataset_key": "kalshi_settled_markets_candles",
                "source": BASE, "sampling": "see research/fast_rail/h003/PREREG.md",
                "series": SERIES, "max_markets_per_event": MAX_MARKETS_PER_EVENT,
                "candle_lookback_h": CANDLE_LOOKBACK_H, "finalized_at": now(), "files": {}}
    for name, key in (("events.jsonl.gz", "event_ticker"), ("markets.jsonl.gz", "ticker")):
        path = os.path.join(OUT, name)
        with gzip.open(path, "rt") as fh:
            rows = {}
            for line in fh:
                if line.strip():
                    row = json.loads(line)
                    rows.setdefault(row[key], row)
        ordered = sorted(rows.values(), key=lambda r: r[key])
        with gzip.GzipFile(path, "wb", mtime=0) as fh:
            for row in ordered:
                fh.write((json.dumps(row, separators=(",", ":")) + "\n").encode())
        with open(path, "rb") as fh:
            manifest["files"][name] = {"rows": len(ordered), "sha256": hashlib.sha256(fh.read()).hexdigest()}
    with open(os.path.join(OUT, "MANIFEST.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print(json.dumps(manifest["files"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(finalize() if sys.argv[1:] == ["finalize"] else main())
