"""H-004 fetcher: settled markets + every trade print for the frozen sample.

Public, unauthenticated Kalshi endpoints only; a global limiter keeps us well
under the published basic-tier read limit and 429s back off (never bypassed).

Storage (data/fast_rail/h004/):
  markets.jsonl.gz          one line per settled market in the sample
  trades_<SERIES>.jsonl.gz  one line per market, prints stored column-wise:
                            t = epoch-ms deltas, p = YES price in 1e-4 $,
                            c = contracts x100, s = taker side string (y/n)
                            plus provenance: urls, fetched_at, sha256 of the raw
                            page bodies, n_prints
  manifest.json             sha256 of every stored file + fetch parameters

Usage: python3 research/fast_rail/h004/fetch.py [--series KXHIGHNY ...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h004_config as config  # noqa: E402

BASE = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "fast_rail" / "h004"
MIN_INTERVAL_S = 1.0 / 6.0  # <= 6 requests/second across all threads

_lock = threading.Lock()
_last = [0.0]
_MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}
_DATE_RE = re.compile(r"^(\d{2})([A-Z]{3})(\d{2})")


def event_date(event_ticker: str) -> dt.date | None:
    parts = event_ticker.split("-", 1)
    if len(parts) != 2:
        return None
    m = _DATE_RE.match(parts[1])
    if not m or m.group(2) not in _MONTHS:
        return None
    return dt.date(2000 + int(m.group(1)), _MONTHS[m.group(2)], int(m.group(3)))


def get(path: str) -> tuple[dict, bytes]:
    for attempt in range(8):
        with _lock:
            wait = _last[0] + MIN_INTERVAL_S - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.monotonic()
        try:
            with urllib.request.urlopen(BASE + path, timeout=60) as r:
                body = r.read()
            return json.loads(body), body
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {}, b""
            time.sleep(min(30, 2 ** attempt))
        except Exception:
            time.sleep(min(30, 2 ** attempt))
    raise RuntimeError(f"failed: {path}")


def list_markets(series: str, dates: set[dt.date]) -> list[dict]:
    min_ts = int(dt.datetime.combine(config.WINDOW_START - dt.timedelta(days=2),
                                     dt.time(), dt.timezone.utc).timestamp())
    max_ts = int(dt.datetime.combine(config.WINDOW_END + dt.timedelta(days=3),
                                     dt.time(), dt.timezone.utc).timestamp())
    seen: dict[str, dict] = {}
    for source, prefix, extra in (("historical", "/historical", ""), ("live", "", "&status=settled")):
        cursor = ""
        while True:
            q = (f"{prefix}/markets?series_ticker={series}&limit=1000&min_close_ts={min_ts}"
                 f"&max_close_ts={max_ts}{extra}" + (f"&cursor={cursor}" if cursor else ""))
            d, _ = get(q)
            ms = d.get("markets", [])
            for m in ms:
                ed = event_date(m["event_ticker"])
                if ed not in dates or m["ticker"] in seen:
                    continue
                seen[m["ticker"]] = {
                    "series": series, "ticker": m["ticker"], "event_ticker": m["event_ticker"],
                    "event_date": ed.isoformat(), "result": m.get("result"),
                    "status": m.get("status"), "close_time": m.get("close_time"),
                    "volume_fp": m.get("volume_fp"), "source": source,
                    "strike_type": m.get("strike_type"), "floor_strike": m.get("floor_strike"),
                    "cap_strike": m.get("cap_strike"),
                }
            cursor = d.get("cursor")
            if not cursor or not ms:
                break
    return sorted(seen.values(), key=lambda m: m["ticker"])


def fetch_trades(market: dict) -> dict:
    prefix = "/historical/trades" if market["source"] == "historical" else "/markets/trades"
    urls, h, rows, ids = [], hashlib.sha256(), [], set()
    fetched_at = dt.datetime.now(dt.timezone.utc).isoformat()
    if float(market.get("volume_fp") or 0) > 0:
        cursor = ""
        while True:
            q = f"{prefix}?ticker={market['ticker']}&limit=1000" + (f"&cursor={cursor}" if cursor else "")
            d, body = get(q)
            urls.append(BASE + q)
            h.update(body)
            tr = d.get("trades", [])
            for t in tr:
                if t["trade_id"] in ids:
                    continue
                ids.add(t["trade_id"])
                ts = dt.datetime.fromisoformat(t["created_time"].replace("Z", "+00:00"))
                rows.append((int(ts.timestamp() * 1000), round(float(t["yes_price_dollars"]) * 1e4),
                             round(float(t["count_fp"]) * 100), "y" if t["taker_side"] == "yes" else "n"))
            cursor = d.get("cursor")
            if not cursor or not tr:
                break
    rows.sort()
    t_delta, prev = [], 0
    for r in rows:
        t_delta.append(r[0] - prev)
        prev = r[0]
    return {"ticker": market["ticker"], "n_prints": len(rows), "t": t_delta,
            "p": [r[1] for r in rows], "c": [r[2] for r in rows], "s": "".join(r[3] for r in rows),
            "provenance": {"urls_first": urls[:1], "n_pages": len(urls), "fetched_at": fetched_at,
                           "sha256_raw_pages": h.hexdigest()}}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", nargs="*", default=list(config.WEATHER_SERIES + config.OTHER_SERIES))
    ap.add_argument("--step", type=int, default=config.SAMPLE_STEP_DAYS)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    dates = set(config.sampled_dates(args.step))
    mpath = OUT / "markets.jsonl.gz"
    markets: dict[str, dict] = {}
    if mpath.exists():
        with gzip.open(mpath, "rt") as f:
            for line in f:
                m = json.loads(line)
                markets[m["ticker"]] = m
    for series in args.series:
        tpath = OUT / f"trades_{series}.jsonl.gz"
        if tpath.exists():
            print(series, "exists, skip", flush=True)
            continue
        ms = list_markets(series, dates)
        print(series, "markets", len(ms), flush=True)
        with ThreadPoolExecutor(4) as ex:
            recs = list(ex.map(fetch_trades, ms))
        tmp = tpath.with_suffix(".tmp")
        with gzip.open(tmp, "wt", compresslevel=9) as f:
            for r in recs:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
        os.replace(tmp, tpath)  # atomic: a crash never leaves a half file under the real name
        for m in ms:
            markets[m["ticker"]] = m
        tmpm = mpath.with_suffix(".tmp")
        with gzip.open(tmpm, "wt", compresslevel=9) as f:
            for m in sorted(markets.values(), key=lambda x: x["ticker"]):
                f.write(json.dumps(m, separators=(",", ":")) + "\n")
        os.replace(tmpm, mpath)
        print(series, "prints", sum(r["n_prints"] for r in recs), "bytes", tpath.stat().st_size, flush=True)
    manifest = {"hypothesis": config.HYPOTHESIS_ID, "dataset_key": config.DATASET_KEY,
                "base_url": BASE, "sample_step_days": args.step,
                "window": [config.WINDOW_START.isoformat(), config.WINDOW_END.isoformat()],
                "written_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "files": {p.name: {"sha256": sha256_file(p), "bytes": p.stat().st_size}
                          for p in sorted(OUT.glob("*.jsonl.gz"))}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print("total bytes", sum(v["bytes"] for v in manifest["files"].values()))


if __name__ == "__main__":
    main()
