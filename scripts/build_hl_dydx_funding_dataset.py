"""Build the Hyperliquid vs dYdX v4 perpetual funding panel (fast rail H-002).

    python3 scripts/build_hl_dydx_funding_dataset.py fetch-candles   # stage 1 (network)
    python3 scripts/build_hl_dydx_funding_dataset.py select          # stage 2 (offline)
    python3 scripts/build_hl_dydx_funding_dataset.py fetch-funding   # stage 3 (network)
    python3 scripts/build_hl_dydx_funding_dataset.py build           # stage 4 (offline)

Offline research tooling (standard library only). Sources are the venues' own
public APIs, fetched once and kept verbatim (gzip) under
``data/raw/fast_rail/h002/`` with ``manifest.json`` (url, request body,
fetched_at, sha256 of every response body), so ``build`` is reproducible
offline:

* Hyperliquid ``POST https://api.hyperliquid.xyz/info``: ``metaAndAssetCtxs``,
  ``candleSnapshot`` (1d) and ``fundingHistory`` (hourly rate paid by longs);
* dYdX v4 indexer ``https://indexer.dydx.trade/v4``: ``perpetualMarkets``,
  ``candles/perpetualMarkets/<T>-USD?resolution=1DAY`` and
  ``historicalFunding/<T>-USD`` (hourly rate; paginated via
  ``effectiveBeforeOrAt``).

Output: ``data/datasets/perp_funding_hl_dydx_daily.csv.gz`` (PricePanel) with
symbols ``HL.<COIN>`` and ``DX.<COIN>``, same conventions as
``perp_funding_pairs_daily``. For UTC day d:

* open = close = the venue's daily close of day d, so a fill "at open(d+1)"
  happens one full day after the decision;
* ``carry_rate`` = sum of the hourly funding rates longs paid over day d
  (a print stamped in [d 00:00, d+1 00:00) UTC belongs to day d);
* volume = the venue's daily notional (HL: base volume x close; dYdX:
  ``usdVolume``), used by the capacity model.

A (venue, day) is kept only with a complete funding record (>= 22 hourly
prints) and a traded daily candle (volume > 0). Nothing is filled in; a day
is emitted for a coin only when both venues are complete that day.

Universe rule (declared in stage 2, from volume only, before any spread or
return was computed): coins listed today on both venues under the same ticker
(HL not delisted, dYdX ACTIVE), whose *median* daily notional over the days
both venues have a traded candle is >= $1M on each venue; ranked by the
smaller of the two medians, at most ``MAX_COINS``. Survivorship: coins
delisted before the fetch are absent.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DATASET = "perp_funding_hl_dydx_daily"
RAW = ROOT / "data" / "raw" / "fast_rail" / "h002"
HL_URL = "https://api.hyperliquid.xyz/info"
DX_URL = "https://indexer.dydx.trade/v4"
MIN_MEDIAN_NOTIONAL = 1_000_000.0
MAX_COINS = 16
MIN_HOURLY_PRINTS = 22


# --------------------------------------------------------------------- fetch
def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _request(url: str, body: dict | None = None) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                return response.read()
        except Exception as exc:  # noqa: BLE001 - network retry
            if attempt == 5:
                raise
            print("retry", url, body, exc, file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise AssertionError


class Store:
    """Raw responses kept verbatim, one gzip file per (venue, kind, coin)."""

    def __init__(self) -> None:
        RAW.mkdir(parents=True, exist_ok=True)
        self.manifest_path = RAW / "manifest.json"
        self.manifest = (json.loads(self.manifest_path.read_text())
                         if self.manifest_path.exists() else {"files": {}})

    def has(self, name: str) -> bool:
        return name in self.manifest["files"] and (RAW / name).exists()

    def save(self, name: str, pages: list[tuple[str, dict | None, str, bytes]]) -> None:
        texts = [raw.decode("utf-8") for _, _, _, raw in pages]
        blob = gzip.compress(json.dumps({"pages": texts}).encode(), compresslevel=9, mtime=0)
        (RAW / name).write_bytes(blob)
        self.manifest["files"][name] = {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "pages": [{"url": url, "body": body, "fetched_at": at,
                       "sha256": hashlib.sha256(raw).hexdigest()}
                      for url, body, at, raw in pages]}
        self.manifest_path.write_text(json.dumps(self.manifest, indent=1, sort_keys=True))


def load_pages(name: str) -> list:
    blob = json.loads(gzip.decompress((RAW / name).read_bytes()))
    return [json.loads(text) for text in blob["pages"]]


def _hl(body: dict) -> tuple[str, dict, str, bytes]:
    time.sleep(0.25)
    return HL_URL, body, _now(), _request(HL_URL, body)


def _dx(path: str) -> tuple[str, None, str, bytes]:
    time.sleep(0.1)
    url = f"{DX_URL}/{path}"
    return url, None, _now(), _request(url)


def fetch_markets(store: Store) -> None:
    store.save("hl_metaAndAssetCtxs.json.gz", [_hl({"type": "metaAndAssetCtxs"})])
    store.save("dx_perpetualMarkets.json.gz", [_dx("perpetualMarkets")])


def common_coins() -> list[str]:
    meta, ctxs = load_pages("hl_metaAndAssetCtxs.json.gz")[0]
    hl = {asset["name"] for asset in meta["universe"] if not asset.get("isDelisted")}
    markets = load_pages("dx_perpetualMarkets.json.gz")[0]["markets"]
    dx = {ticker[:-4] for ticker, market in markets.items()
          if market["status"] == "ACTIVE" and ticker.endswith("-USD")}
    return sorted(hl & dx)


def fetch_candles(store: Store, coins: list[str]) -> None:
    for coin in coins:
        name = f"hl_candles_{coin}.json.gz"
        if not store.has(name):
            store.save(name, [_hl({"type": "candleSnapshot",
                                   "req": {"coin": coin, "interval": "1d",
                                           "startTime": 1672531200000,
                                           "endTime": 1893456000000}})])
        name = f"dx_candles_{coin}.json.gz"
        if not store.has(name):
            pages, to_iso = [], None
            while True:
                path = f"candles/perpetualMarkets/{coin}-USD?resolution=1DAY&limit=100"
                if to_iso:
                    path += f"&toISO={to_iso}"
                page = _dx(path)
                candles = json.loads(page[3])["candles"]
                pages.append(page)
                if len(candles) < 100:
                    break
                oldest = min(candle["startedAt"] for candle in candles)
                to_iso = (dt.datetime.fromisoformat(oldest.replace("Z", "+00:00"))
                          - dt.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            store.save(name, pages)
        print("candles", coin, flush=True)


def fetch_funding(store: Store, coins: list[str]) -> None:
    for coin in coins:
        name = f"dx_funding_{coin}.json.gz"
        if not store.has(name):
            pages, before = [], None
            while True:
                path = f"historicalFunding/{coin}-USD?limit=1000"
                if before:
                    path += f"&effectiveBeforeOrAt={before}"
                page = _dx(path)
                rows = json.loads(page[3])["historicalFunding"]
                pages.append(page)
                if len(rows) < 1000:
                    break
                oldest = min(row["effectiveAt"] for row in rows)
                before = (dt.datetime.fromisoformat(oldest.replace("Z", "+00:00"))
                          - dt.timedelta(milliseconds=1)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            store.save(name, pages)
        name = f"hl_funding_{coin}.json.gz"
        if not store.has(name):
            pages, start = [], 1672531200000
            while True:
                page = _hl({"type": "fundingHistory", "coin": coin, "startTime": start})
                rows = json.loads(page[3])
                pages.append(page)
                if len(rows) < 500:
                    break
                start = max(row["time"] for row in rows) + 1
            store.save(name, pages)
        print("funding", coin, flush=True)


# --------------------------------------------------------------------- parse
def _day_ms(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).date().isoformat()


def _day_iso(stamp: str) -> str:
    return stamp[:10]


def hl_bars(coin: str) -> dict[str, tuple[float, float]]:
    """day -> (close, daily notional); untraded (backfilled) days dropped."""
    bars = {}
    for candle in load_pages(f"hl_candles_{coin}.json.gz")[0]:
        close, volume = float(candle["c"]), float(candle["v"])
        if volume > 0 and close > 0:
            bars[_day_ms(candle["t"])] = (close, volume * close)
    return bars


def dx_bars(coin: str) -> dict[str, tuple[float, float]]:
    bars = {}
    for page in load_pages(f"dx_candles_{coin}.json.gz"):
        for candle in page["candles"]:
            close, notional = float(candle["close"]), float(candle["usdVolume"])
            if notional > 0 and close > 0:
                bars[_day_iso(candle["startedAt"])] = (close, notional)
    return bars


def _complete(prints: dict[str, dict[str, float]]) -> dict[str, float]:
    """day -> sum of hourly rates, only for days with a complete record."""
    return {day: sum(hours.values()) for day, hours in prints.items()
            if len(hours) >= MIN_HOURLY_PRINTS}


def hl_carry(coin: str) -> dict[str, float]:
    prints: dict[str, dict[str, float]] = {}
    for page in load_pages(f"hl_funding_{coin}.json.gz"):
        for row in page:
            stamp = dt.datetime.fromtimestamp(row["time"] / 1000, dt.timezone.utc)
            prints.setdefault(stamp.date().isoformat(), {})[
                stamp.strftime("%H")] = float(row["fundingRate"])
    return _complete(prints)


def dx_carry(coin: str) -> dict[str, float]:
    prints: dict[str, dict[str, float]] = {}
    for page in load_pages(f"dx_funding_{coin}.json.gz"):
        for row in page["historicalFunding"]:
            stamp = row["effectiveAt"]
            prints.setdefault(stamp[:10], {})[stamp[11:13]] = float(row["rate"])
    return _complete(prints)


def select() -> list[dict]:
    ranked = []
    for coin in common_coins():
        hl, dx = hl_bars(coin), dx_bars(coin)
        days = sorted(set(hl) & set(dx))
        if len(days) < 60:
            continue
        hl_median = statistics.median(hl[day][1] for day in days)
        dx_median = statistics.median(dx[day][1] for day in days)
        ranked.append({"coin": coin, "days": len(days), "hl_median_notional": hl_median,
                       "dx_median_notional": dx_median,
                       "min_leg_median": min(hl_median, dx_median)})
    ranked.sort(key=lambda row: -row["min_leg_median"])
    chosen = [row for row in ranked if row["min_leg_median"] >= MIN_MEDIAN_NOTIONAL][:MAX_COINS]
    (RAW / "selection.json").write_text(json.dumps(
        {"rule": f"listed on both venues today; median daily notional over common traded "
                 f"days >= {MIN_MEDIAN_NOTIONAL:.0f} USD on each venue; top {MAX_COINS} by "
                 f"min-leg median; decided from volume only before any funding was fetched",
         "chosen": [row["coin"] for row in chosen], "ranked": ranked}, indent=1))
    return chosen


def build_rows(coins: list[str]) -> tuple[list[dict], list[str]]:
    rows, symbols = [], []
    for coin in coins:
        hl_b, dx_b, hl_c, dx_c = hl_bars(coin), dx_bars(coin), hl_carry(coin), dx_carry(coin)
        days = sorted(set(hl_b) & set(dx_b) & set(hl_c) & set(dx_c))
        if len(days) < 60:
            continue
        for day in days:
            for venue, (price, notional), carry in (("HL", hl_b[day], hl_c[day]),
                                                    ("DX", dx_b[day], dx_c[day])):
                rows.append({"date": day, "symbol": f"{venue}.{coin}", "open": price,
                             "high": price, "low": price, "close": price,
                             "adj_close": price, "volume": notional, "carry_rate": carry})
        symbols += [f"HL.{coin}", f"DX.{coin}"]
    return rows, symbols


def register(rows: list[dict], symbols: list[str], state: str) -> None:
    from quant.dataplane.ingest import _register
    from quant.dataplane.panel import PricePanel
    from quant.dataplane.registry import DatasetRecord, DatasetRegistry
    from quant.paths import QuantPaths
    panel = PricePanel(rows)
    paths = QuantPaths(ROOT, state=state).ensure()
    record = DatasetRecord(
        dataset_id=DATASET,
        source="api.hyperliquid.xyz/info (fundingHistory, candleSnapshot 1d) + "
               "indexer.dydx.trade/v4 (historicalFunding, candles 1DAY); raw responses in "
               "data/raw/fast_rail/h002 with manifest.json (url, fetched_at, sha256)",
        adapter="perp_funding_hl_dydx_derivation", path=f"data/datasets/{DATASET}.csv.gz",
        point_in_time={"information_available_at": "00:00 UTC after the dated day",
                       "minimum_decision_lag_days": 1,
                       "fill_convention": "open(d+1) = close(d+1): one full day of execution lag",
                       "required_symbols": ["HL.BTC", "DX.BTC", "HL.ETH", "DX.ETH"],
                       "min_rows_per_symbol": 60},
        caveats=["venue APIs fetched once at build time; a later refetch may differ if a "
                 "venue revises history",
                 "survivorship: only coins listed on both venues at fetch time",
                 "universe chosen by trailing median notional on both venues (volume only)",
                 "no intraday margin, liquidation or auto-deleveraging modelling in the data",
                 "dYdX v4 volumes are thin; capacity is bound by the dYdX leg"],
        license_note="public venue APIs; research use")
    registered = _register(DatasetRegistry(paths.dataset_registry, paths.root), record, panel,
                           sorted(set(symbols)), paths.root)
    print(registered.dataset_id, registered.availability, registered.rows,
          len(registered.symbols), registered.first_date, registered.last_date,
          registered.fingerprint, registered.validation.get("problems"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("fetch-candles", "select", "fetch-funding", "build"))
    parser.add_argument("--state", default="var/perp_hl_dydx_build")
    args = parser.parse_args()
    store = Store()
    if args.stage == "fetch-candles":
        fetch_markets(store)
        fetch_candles(store, common_coins())
    elif args.stage == "select":
        for row in select():
            print(row)
    elif args.stage == "fetch-funding":
        chosen = json.loads((RAW / "selection.json").read_text())["chosen"]
        fetch_funding(store, chosen)
    else:
        chosen = json.loads((RAW / "selection.json").read_text())["chosen"]
        rows, symbols = build_rows(chosen)
        register(rows, symbols, args.state)


if __name__ == "__main__":
    main()
