"""Build the Hyperliquid new-listing panel (H-006) from the public info API.

    python3 scripts/build_hl_listings_dataset.py --fetch     # network -> data/raw/fast_rail/h006
    python3 scripts/build_hl_listings_dataset.py             # raw -> dataset (offline, stdlib)

Source: ``POST https://api.hyperliquid.xyz/info`` with ``{"type": "meta"}``
(every main-dex perp, including ``isDelisted`` ones), ``candleSnapshot`` 1d and
``fundingHistory``. Every response is stored gzipped under
``data/raw/fast_rail/h006/`` with a manifest line (url, body, fetched_at,
sha256 of the response bytes), so the dataset is rebuilt offline byte for byte.

Output ``data/datasets/hl_listings_daily.csv.gz`` (PricePanel), symbols
``HL.<COIN>`` for every coin in ``meta`` (delisted ones included) plus
``HL.BTC``. Same conventions as ``perp_funding_pairs_daily``; for UTC day d:

* open = close = Hyperliquid's last traded price of day d (daily candle close),
  so a fill "at open(d+1)" happens one full day after the decision;
* ``carry_rate`` = funding paid by longs over day d (sum of the hourly rates
  stamped inside day d);
* volume = daily notional traded on Hyperliquid (base volume x close);
* a day is kept only with >= 22 hourly funding prints and a candle with at
  least one trade (Hyperliquid back-fills pre-listing candles with zero
  trades from other venues; those are not Hyperliquid prices). Nothing filled.

Point-in-time listing features (known at the close of d, only from data dated
<= d):

* ``listing_age_days`` = d - L, where L is the coin's first daily candle with a
  Hyperliquid trade (``n > 0``). L itself is a partial day and normally has
  fewer than 22 funding prints, so the first kept row is usually L+1 (age 1).
* ``listing_eligible`` = 1 when L >= ``ELIGIBLE_FROM``, else 0. The info API's
  funding history starts 2023-05-12 and the daily candles of coins trading at
  Hyperliquid's start are indistinguishable from coins that merely existed
  then, so a coin whose first traded candle precedes ``ELIGIBLE_FROM`` is an
  incumbent at history start, never a new listing.

Coverage (declared before any return was computed, to bound API load): each
coin from L through L + ``COVERAGE_DAYS`` (enough for the longest 30-day
holding window plus the one-day execution lag and exit); ``HL.BTC`` over the
whole funding history (calendar, hedge leg and benchmark).
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import _register  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.dataplane.registry import DatasetRecord, DatasetRegistry  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

DATASET = "hl_listings_daily"
API = "https://api.hyperliquid.xyz/info"
RAW = ROOT / "data" / "raw" / "fast_rail" / "h006"
#: First hourly funding print served by the info API is 2023-05-12; any coin
#: trading on Hyperliquid before this date is an incumbent at history start.
ELIGIBLE_FROM = "2023-06-01"
COVERAGE_DAYS = 45
MIN_FUNDING_PRINTS = 22
DAY_MS = 86_400_000
FUNDING_PAGE = 500


def _day(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date().isoformat()


def _ms(day: str) -> int:
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


# --------------------------------------------------------------------------- fetch
class Fetcher:
    def __init__(self, raw: Path, pause: float):
        self.raw, self.pause = raw, pause
        raw.mkdir(parents=True, exist_ok=True)
        self.manifest = raw / "manifest.jsonl"
        self.done = set()
        if self.manifest.exists():
            for line in self.manifest.read_text().splitlines():
                self.done.add(json.loads(line)["file"])

    def post(self, body: dict, name: str) -> object:
        target = self.raw / name
        if name in self.done and target.exists():
            return json.loads(gzip.decompress(target.read_bytes()))
        data = json.dumps(body).encode()
        for attempt in range(8):
            try:
                request = urllib.request.Request(API, data=data,
                                                 headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = response.read()
                break
            except Exception as error:  # 429 / transient: back off
                wait = 5 * (attempt + 1)
                print(f"retry {name} after {error} in {wait}s", file=sys.stderr)
                time.sleep(wait)
        else:
            raise RuntimeError(f"failed {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
                handle.write(payload)
        entry = {"file": name, "url": API, "method": "POST", "body": body,
                 "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                 "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
        with self.manifest.open("a") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        self.done.add(name)
        time.sleep(self.pause)
        return json.loads(payload)


def fetch(raw: Path, pause: float, end_day: str) -> None:
    fetcher = Fetcher(raw, pause)
    meta = fetcher.post({"type": "meta"}, "meta.json.gz")
    end_ms = _ms(end_day) + DAY_MS - 1
    for asset in meta["universe"]:
        coin = asset["name"]
        candles = fetcher.post({"type": "candleSnapshot",
                                "req": {"coin": coin, "interval": "1d", "startTime": 0,
                                        "endTime": end_ms}},
                               f"candles/{coin}.json.gz")
        traded = [c for c in candles if int(c.get("n", 0)) > 0]
        if not traded:
            continue
        listing = _day(traded[0]["t"])
        start = max(_ms(listing), _ms("2023-05-01"))
        stop = end_ms if coin == "BTC" else min(end_ms, _ms(listing) + (COVERAGE_DAYS + 1) * DAY_MS)
        cursor, page = start, 0
        while cursor < stop:
            rows = fetcher.post({"type": "fundingHistory", "coin": coin, "startTime": cursor,
                                 "endTime": stop}, f"funding/{coin}/{page:04d}.json.gz")
            page += 1
            if not rows:
                break
            cursor = max(int(row["time"]) for row in rows) + 1
            if len(rows) < FUNDING_PAGE:
                break
        print(coin, listing, asset.get("isDelisted", False), len(candles), page, file=sys.stderr)


# --------------------------------------------------------------------------- build
def _load(path: Path) -> object:
    return json.loads(gzip.decompress(path.read_bytes()))


def build(raw: Path) -> tuple[list[dict], list[str], dict]:
    meta = _load(raw / "meta.json.gz")
    rows, symbols, listings = [], [], {}
    for asset in meta["universe"]:
        coin = asset["name"]
        candle_file = raw / "candles" / f"{coin}.json.gz"
        if not candle_file.exists():
            continue
        candles = [c for c in _load(candle_file) if int(c.get("n", 0)) > 0]
        if not candles:
            continue
        listing = _day(candles[0]["t"])
        eligible = listing >= ELIGIBLE_FROM
        prints: dict[str, dict[int, float]] = {}
        for page in sorted((raw / "funding" / coin).glob("*.json.gz")):
            for item in _load(page):
                prints.setdefault(_day(int(item["time"])), {})[int(item["time"])] = \
                    float(item["fundingRate"])
        kept = 0
        for candle in candles:
            day = _day(candle["t"])
            rates = prints.get(day, {})
            close = float(candle["c"])
            if len(rates) < MIN_FUNDING_PRINTS or close <= 0:
                continue
            age = (dt.date.fromisoformat(day) - dt.date.fromisoformat(listing)).days
            if coin != "BTC" and age > COVERAGE_DAYS:
                continue
            rows.append({"date": day, "symbol": f"HL.{coin}", "open": close, "high": close,
                         "low": close, "close": close, "adj_close": close,
                         "volume": float(candle["v"]) * close,
                         "carry_rate": sum(rates.values()), "listing_age_days": float(age),
                         "listing_eligible": 1.0 if eligible else 0.0})
            kept += 1
        listings[coin] = {"listing_date": listing, "eligible": eligible,
                          "delisted": bool(asset.get("isDelisted", False)),
                          "rows": kept,
                          "min_close": min((float(c["c"]) for c in candles), default=None)}
        if kept:
            symbols.append(f"HL.{coin}")
    return rows, symbols, listings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--pause", type=float, default=0.4)
    parser.add_argument("--end-day", default=(dt.datetime.now(dt.timezone.utc).date()
                                              - dt.timedelta(days=1)).isoformat(),
                        help="last complete UTC day to request")
    parser.add_argument("--state", default="var/hl_listings_build")
    args = parser.parse_args()
    if args.fetch:
        fetch(args.raw, args.pause, args.end_day)
    rows, symbols, listings = build(args.raw)
    panel = PricePanel(rows)
    (args.raw / "listings.json").write_text(json.dumps(listings, indent=1, sort_keys=True) + "\n")
    paths = QuantPaths(ROOT, state=args.state).ensure()
    eligible = sum(1 for item in listings.values() if item["eligible"])
    delisted = sum(1 for item in listings.values() if item["delisted"] and item["rows"])
    record = DatasetRecord(
        dataset_id=DATASET,
        source="Hyperliquid public info API (POST https://api.hyperliquid.xyz/info: meta incl. "
               "isDelisted, candleSnapshot 1d, fundingHistory); raw responses and manifest in "
               "data/raw/fast_rail/h006",
        adapter="hl_listings_derivation", path=f"data/datasets/{DATASET}.csv.gz",
        point_in_time={"information_available_at": "00:00 UTC after the dated day",
                       "minimum_decision_lag_days": 1,
                       "fill_convention": "open(d+1) = close(d+1): one full day of execution lag",
                       "listing_feature": "listing_age_days = d - first Hyperliquid-traded "
                                          "daily candle; listing_eligible = listing on or after "
                                          f"{ELIGIBLE_FROM}",
                       "eligibility_cutoff": ELIGIBLE_FROM,
                       "required_symbols": ["HL.BTC"],
                       "min_rows_per_symbol": 1},
        caveats=["main-dex perps only (HIP-3 builder-deployed dexs excluded)",
                 f"coins first traded before {ELIGIBLE_FROM} are incumbents at API history "
                 "start and are never new listings",
                 f"coins covered only from listing to listing + {COVERAGE_DAYS} days; HL.BTC over "
                 "the whole funding history",
                 f"delisted coins included ({delisted} with rows): no survivorship by construction",
                 "listing day itself is partial and usually dropped (< 22 funding prints)",
                 "prices stored with six decimals (PricePanel): sub-cent coins lose precision",
                 "no intraday margin, liquidation, auto-deleveraging or borrow modelling",
                 f"{eligible} eligible listings in meta"],
        license_note="public exchange API; research use")
    registered = _register(DatasetRegistry(paths.dataset_registry, paths.root), record, panel,
                           sorted(set(symbols)), paths.root)
    print(registered.dataset_id, registered.availability, registered.rows,
          len(registered.symbols), registered.first_date, registered.last_date,
          registered.fingerprint, registered.validation.get("problems"))


if __name__ == "__main__":
    main()
