"""H-006 raw data fetch: football-data.co.uk CSVs + Polymarket gamma match events + CLOB hourly prices.

Paper/shadow research only. Public read-only endpoints, no keys, no orders.
Each response is stored byte-for-byte (gzipped) under data/fast_rail/h006/raw/ (gitignored)
with a committed manifest line: url, fetched_at, sha256 of the raw bytes. Nothing is synthesised.

Usage:  python3 research/fast_rail/h006/fetch.py fd       # 10 league-season CSVs
        python3 research/fast_rail/h006/fetch.py events   # closed match events per league tag
        python3 research/fast_rail/h006/fetch.py prices   # hourly prices for matched events
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "fast_rail" / "h006"
RAW = DATA / "raw"
MANIFEST = DATA / "manifest.jsonl"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
SEASONS = ("2425", "2526")
LEAGUES = {"E0": 306, "SP1": 780, "D1": 1494, "I1": 100618, "F1": 102070}  # fd code -> Polymarket primary tag id
EVENT_TAGS = dict(LEAGUES, I1b=101962)  # Serie A matches carry tag 101962 ("sea"), not 100618
_LOCK = threading.Lock()


def _get(url: str) -> bytes:
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            code = getattr(exc, "code", None)
            if code not in (None, 429, 500, 502, 503, 504) or attempt == 5:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError("unreachable")


def store(name: str, url: str) -> bytes:
    path = RAW / f"{name}.gz"
    if path.exists():
        return gzip.decompress(path.read_bytes())
    raw = _get(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw, 9))
    line = {"file": str(path.relative_to(ROOT)), "url": url,
            "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    with _LOCK, MANIFEST.open("a") as fh:
        fh.write(json.dumps(line, sort_keys=True) + "\n")
    return raw


def fetch_fd() -> None:
    store("notes.txt", "https://www.football-data.co.uk/notes.txt")
    for season in SEASONS:
        for code in LEAGUES:
            store(f"fd_{season}_{code}.csv", f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv")


def _months():
    year, month = 2024, 7
    while (year, month) <= (2026, 7):
        nxt = (year + (month == 12), month % 12 + 1)
        yield f"{year}-{month:02d}-01T00:00:00Z", f"{nxt[0]}-{nxt[1]:02d}-01T00:00:00Z"
        year, month = nxt


def fetch_events() -> None:
    """Closed events per league tag, month by month (gamma caps offset at 2000)."""
    for code, tag in EVENT_TAGS.items():
        count = 0
        for low, high in _months():
            offset = 0
            while True:
                url = (f"https://gamma-api.polymarket.com/events?tag_id={tag}&closed=true&limit=100"
                       f"&offset={offset}&end_date_min={low}&end_date_max={high}")
                page = json.loads(store(f"events_{code}_{low[:7]}_{offset:04d}.json", url))
                count += len(page)
                if len(page) < 100:
                    break
                offset += 100
        print(code, count)


def fetch_prices() -> None:
    sys.path.insert(0, str(ROOT))
    from research.fast_rail.h006 import build
    jobs = []
    for match in build.matched_events():
        start = int(match["collection_ts"]) - 6 * 3600
        end = int(match["kickoff_ts"])
        for outcome, token in match["tokens"].items():
            url = (f"https://clob.polymarket.com/prices-history?market={token}"
                   f"&startTs={start}&endTs={end}&fidelity=60")
            jobs.append((f"px_{match['slug']}_{outcome}.json", url))
    print("price requests", len(jobs))
    with ThreadPoolExecutor(8) as pool:
        list(pool.map(lambda job: store(*job), jobs))


if __name__ == "__main__":
    {"fd": fetch_fd, "events": fetch_events, "prices": fetch_prices}[sys.argv[1]]()
