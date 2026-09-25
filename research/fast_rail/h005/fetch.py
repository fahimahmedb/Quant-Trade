"""H-005 raw data fetch: Hyperliquid public info API -> gzipped raw responses + provenance.

Paper/shadow research only. Read-only public endpoint, no keys, no orders.
Every response is stored byte-for-byte (gzipped) under data/fast_rail/h005/raw/
with a manifest line: url, request body, fetched_at, sha256 of the raw bytes.
Nothing is filled or synthesised here.

Usage:  python3 research/fast_rail/h005/fetch.py candles   # meta + daily candles for every coin
        python3 research/fast_rail/h005/fetch.py funding   # funding for discovery+validation events only
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "fast_rail" / "h005" / "raw"
MANIFEST = ROOT / "data" / "fast_rail" / "h005" / "manifest.jsonl"
URL = "https://api.hyperliquid.xyz/info"
# Candles from shortly before the venue's first traded day (2023-02-26) keep the
# archive small; older rows are zero-volume backfill, not trading.
CANDLE_START_MS = int(dt.datetime(2023, 2, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
SLEEP_S = 2.5  # public budget is 1200 weight/min; fundingHistory costs ~20 + rows/20


def _post(body: dict) -> bytes:
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:  # 429: back off, never bypass
            if exc.code == 429 and attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def store(name: str, body: dict) -> bytes:
    path = RAW / f"{name}.json.gz"
    if path.exists():
        return gzip.decompress(path.read_bytes())
    raw = _post(body)
    RAW.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw, 9))
    line = {"file": str(path.relative_to(ROOT)), "url": URL, "request": body,
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    with MANIFEST.open("a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")
    time.sleep(SLEEP_S)
    return raw


def fetch_candles(end_ms: int) -> None:
    meta = json.loads(store("meta", {"type": "meta"}))
    for asset in meta["universe"]:
        coin = asset["name"]
        store(f"candles_{coin}", {"type": "candleSnapshot", "req": {
            "coin": coin, "interval": "1d", "startTime": CANDLE_START_MS, "endTime": end_ms}})


def fetch_funding(coin: str, start_ms: int, end_ms: int) -> None:
    """Paginate fundingHistory (500 rows/page) over [start_ms, end_ms]."""
    cursor, page = start_ms, 0
    while cursor <= end_ms:
        rows = json.loads(store(f"funding_{coin}_{start_ms}_p{page}", {
            "type": "fundingHistory", "coin": coin, "startTime": cursor, "endTime": end_ms}))
        if len(rows) < 500:
            break
        cursor, page = rows[-1]["time"] + 1, page + 1


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "candles":
        fetch_candles(int(sys.argv[2]) if len(sys.argv) > 2 else 1790035200000)
    elif what == "funding":
        sys.path.insert(0, str(ROOT))
        from research.fast_rail.h005.run import funding_requests
        for coin, start_ms, end_ms in funding_requests():
            fetch_funding(coin, start_ms, end_ms)
    print("done")
