"""Build the Hyperliquid-vs-dYdX v4 perpetual funding panel from the venues' public APIs.

    python3 scripts/build_perp_funding_hl_dydx.py [--end YYYY-MM-DD] [--offline]

Standard library only. Every raw response is cached (gzip) under
``data/fast_rail/h002/raw/`` keyed by its request, so a rerun is offline and
byte-reproducible; ``data/fast_rail/h002/provenance.jsonl.gz`` records the URL,
request body, fetch time and sha256 of every response the panel was built from.

Sources (public, no keys):

* Hyperliquid ``POST https://api.hyperliquid.xyz/info``: ``meta`` (incl. delisted
  coins), ``fundingHistory`` (hourly rate paid by longs), ``candleSnapshot`` 1d.
* dYdX v4 indexer ``https://indexer.dydx.trade/v4``: ``perpetualMarkets`` (incl.
  FINAL_SETTLEMENT markets), ``historicalFunding/{T}-USD`` (hourly rate, same
  units and sign as Hyperliquid: positive = longs pay; paginated with
  ``effectiveBeforeOrAt``), ``candles/perpetualMarkets/{T}-USD?resolution=1DAY``.

Output ``data/datasets/perp_funding_hl_dydx_daily.csv.gz`` (PricePanel), symbols
``HL.<COIN>`` and ``DY.<COIN>``. For UTC day d:

* open = close = the venue's last price of day d (daily candle close), so a
  fill "at open(d+1)" happens one full day after the decision;
* ``carry_rate`` = funding paid by longs over day d: the sum of the hourly rates
  settled at 01:00 .. 24:00 of d (a settlement at hour H pays for [H-1h, H));
* volume = daily notional traded on that venue (HL: base volume x close; dYdX:
  ``usdVolume``).

A day is kept only when both venues have >= 22 distinct hourly settlements and
a traded (volume > 0) daily candle. Nothing is filled in. Coins are the
intersection of Hyperliquid and dYdX markets, delisted ones included; the six
Hyperliquid ``k``-coins (kPEPE = 1000 PEPE) are paired with the dYdX token.
Prices are expressed per ``price_scale`` tokens (a power of ten chosen per coin
so the smallest close is >= 1; returns are unchanged) because the panel stores
six decimals.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import _register  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.dataplane.registry import DatasetRecord, DatasetRegistry  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

DATASET = "perp_funding_hl_dydx_daily"
HL_INFO = "https://api.hyperliquid.xyz/info"
DYDX = "https://indexer.dydx.trade/v4"
RAW = ROOT / "data" / "fast_rail" / "h002" / "raw"
PROVENANCE = ROOT / "data" / "fast_rail" / "h002" / "provenance.jsonl.gz"
MIN_PRINTS = 22
MIN_DAYS = 60
HOUR_MS = 3_600_000
#: Hyperliquid info weight budget is 1200/min per IP; fundingHistory costs
#: 20 + 1 per 20 items (~45 for a full page), so ~26 pages/min. Stay under it.
HL_PAUSE = 2.6
DYDX_PAUSE = 0.35


class Fetcher:
    def __init__(self, offline: bool):
        self.offline = offline
        self.provenance: dict[str, dict] = {}
        self.last_call: dict[str, float] = {}

    def get(self, url: str, body: dict | None = None) -> object:
        key = json.dumps({"url": url, "body": body}, sort_keys=True)
        digest = hashlib.sha1(key.encode()).hexdigest()
        path = RAW / digest[:2] / f"{digest}.json.gz"
        meta_path = path.with_suffix("").with_suffix(".meta.json")
        if path.exists() and meta_path.exists():
            payload = gzip.decompress(path.read_bytes())
            meta = json.loads(meta_path.read_text())
        else:
            if self.offline:
                raise SystemExit(f"offline and not cached: {key}")
            payload = self._fetch(url, body)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
                    handle.write(payload)
            meta = {"url": url, "body": body,
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
                    "cache": str(path.relative_to(ROOT))}
            meta_path.write_text(json.dumps(meta, sort_keys=True))
        self.provenance[key] = meta
        return json.loads(payload)

    def _fetch(self, url: str, body: dict | None) -> bytes:
        host = "hl" if body is not None else "dydx"
        pause = HL_PAUSE if host == "hl" else DYDX_PAUSE
        for attempt in range(8):
            wait = self.last_call.get(host, 0.0) + pause - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.last_call[host] = time.monotonic()
            data = json.dumps(body).encode() if body is not None else None
            request = urllib.request.Request(url, data=data, headers={
                "Content-Type": "application/json", "User-Agent": "quant-research/1.0"})
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    return response.read()
            except urllib.error.HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504):
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                pass
            time.sleep(min(120.0, 5.0 * 2 ** attempt))
        raise RuntimeError(f"giving up on {url} {body}")


def iso_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def ms_iso(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


def day_of(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).date().isoformat()


def settlement_day(ms: int) -> tuple[str, int]:
    """(day the payment accrues to, settlement hour in ms): a payment settled at
    hour H covers [H-1h, H), so the 00:00 settlement belongs to the previous day."""
    hour = int(round(ms / HOUR_MS)) * HOUR_MS
    return day_of(hour - HOUR_MS), hour


def daily_carry(prints: list[tuple[int, float]]) -> dict[str, float]:
    """Sum of hourly rates per day, only for days with >= MIN_PRINTS distinct hours."""
    by_hour: dict[int, tuple[str, float]] = {}
    for ms, rate in prints:
        day, hour = settlement_day(ms)
        by_hour[hour] = (day, rate)          # one settlement per hour
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for day, rate in by_hour.values():
        sums[day] = sums.get(day, 0.0) + rate
        counts[day] = counts.get(day, 0) + 1
    return {day: value for day, value in sums.items() if counts[day] >= MIN_PRINTS}


def coin_pairs(fetcher: Fetcher) -> list[tuple[str, str, str, float]]:
    """(coin, Hyperliquid name, dYdX ticker, HL tokens per contract)."""
    hl = fetcher.get(HL_INFO, {"type": "meta"})["universe"]
    dy = fetcher.get(f"{DYDX}/perpetualMarkets?limit=1000")["markets"]
    hl_names = {}
    for item in hl:
        name = item["name"]
        if name.startswith("k") and name[1:].isupper():
            hl_names[name[1:]] = (name, 1000.0)
        else:
            hl_names.setdefault(name, (name, 1.0))
    dy_names = {ticker.rsplit("-", 1)[0]: ticker for ticker in dy if ticker.endswith("-USD")}
    return [(coin, *hl_names[coin][:1], dy_names[coin], hl_names[coin][1])
            for coin in sorted(set(hl_names) & set(dy_names))]


def dydx_funding(fetcher: Fetcher, ticker: str, end_ms: int) -> list[tuple[int, float]]:
    prints, cursor = [], end_ms - 1
    while True:
        page = fetcher.get(f"{DYDX}/historicalFunding/{ticker}?limit=1000"
                           f"&effectiveBeforeOrAt={ms_iso(cursor)}")["historicalFunding"]
        prints += [(iso_ms(item["effectiveAt"]), float(item["rate"])) for item in page]
        if len(page) < 1000:
            return prints
        cursor = min(iso_ms(item["effectiveAt"]) for item in page) - 1


def dydx_candles(fetcher: Fetcher, ticker: str, end_ms: int) -> dict[str, tuple[float, float]]:
    bars, cursor = {}, end_ms - 1
    while True:
        page = fetcher.get(f"{DYDX}/candles/perpetualMarkets/{ticker}?resolution=1DAY"
                           f"&limit=1000&toISO={ms_iso(cursor)}")["candles"]
        for item in page:
            started = iso_ms(item["startedAt"])
            if started + 86_400_000 <= end_ms and float(item["usdVolume"]) > 0:
                bars[day_of(started)] = (float(item["close"]), float(item["usdVolume"]))
        if len(page) < 1000:
            return bars
        cursor = min(iso_ms(item["startedAt"]) for item in page) - 1


def hl_funding(fetcher: Fetcher, name: str, start_ms: int, end_ms: int) -> list[tuple[int, float]]:
    prints, cursor = [], start_ms
    while cursor < end_ms:
        page = fetcher.get(HL_INFO, {"type": "fundingHistory", "coin": name,
                                     "startTime": cursor, "endTime": end_ms})
        prints += [(int(item["time"]), float(item["fundingRate"])) for item in page]
        if len(page) < 500:
            return prints
        cursor = max(int(item["time"]) for item in page) + 1
    return prints


def hl_candles(fetcher: Fetcher, name: str, start_ms: int, end_ms: int) -> dict[str, tuple[float, float]]:
    page = fetcher.get(HL_INFO, {"type": "candleSnapshot", "req": {
        "coin": name, "interval": "1d", "startTime": start_ms, "endTime": end_ms}})
    bars = {}
    for item in page:
        close, volume = float(item["c"]), float(item["v"])
        if int(item["t"]) + 86_400_000 <= end_ms and volume > 0:
            bars[day_of(int(item["t"]))] = (close, volume * close)
    return bars


def build(fetcher: Fetcher, end_ms: int, log=print,
          only: set[str] | None = None) -> tuple[list[dict], list[str], dict]:
    rows, symbols, coins = [], [], {}
    pairs = [pair for pair in coin_pairs(fetcher) if not only or pair[0] in only]

    def dydx_side(ticker: str) -> tuple[dict, dict]:
        return daily_carry(dydx_funding(fetcher, ticker, end_ms)), dydx_candles(fetcher, ticker,
                                                                                 end_ms)

    # The dYdX indexer is fetched ahead in a worker thread while the (slower,
    # weight-limited) Hyperliquid requests run here; each host keeps its own pause.
    with ThreadPoolExecutor(max_workers=1) as pool:
        ahead = [pool.submit(dydx_side, pair[2]) for pair in pairs]
        for position, ((coin, hl_name, dy_ticker, per_contract), future) in enumerate(
                zip(pairs, ahead)):
            dy_carry, dy_bars = future.result()
            usable = sorted(set(dy_carry) & set(dy_bars))
            if len(usable) < MIN_DAYS:
                log(f"[{position + 1}/{len(pairs)}] {coin}: {len(usable)} dYdX days, skipped")
                continue
            start_ms = iso_ms(usable[0] + "T00:00:00Z") - 86_400_000
            stop_ms = min(end_ms, iso_ms(usable[-1] + "T00:00:00Z") + 2 * 86_400_000)
            hl_bars = hl_candles(fetcher, hl_name, start_ms, stop_ms)
            hl_carry = {}
            if len(hl_bars) >= MIN_DAYS:
                # Only where Hyperliquid traded: delisted coins keep printing funding.
                hl_carry = daily_carry(hl_funding(
                    fetcher, hl_name, max(start_ms, iso_ms(min(hl_bars) + "T00:00:00Z")),
                    min(stop_ms, iso_ms(max(hl_bars) + "T00:00:00Z") + 2 * 86_400_000)))
            rows_added = _pair_rows(coin, hl_name, dy_ticker, per_contract, dy_carry, dy_bars,
                                    hl_carry, hl_bars, log, f"[{position + 1}/{len(pairs)}]")
            if rows_added:
                rows += rows_added[0]
                coins[coin] = rows_added[1]
                symbols += [f"HL.{coin}", f"DY.{coin}"]
    return rows, symbols, coins


def _pair_rows(coin, hl_name, dy_ticker, per_contract, dy_carry, dy_bars, hl_carry, hl_bars,
               log, tag):
    """Panel rows for one coin, or None when fewer than MIN_DAYS complete days."""
    days = sorted(day for day in set(dy_carry) & set(dy_bars) & set(hl_carry) & set(hl_bars)
                  if hl_bars[day][0] > 0 and dy_bars[day][0] > 0)
    log(f"{tag} {coin}: {len(days)} common days")
    if len(days) < MIN_DAYS:
        return None
    # HL quotes k-coins per 1000 tokens; express both legs per token first.
    low = min([hl_bars[d][0] / per_contract for d in days] + [dy_bars[d][0] for d in days])
    scale = 10.0 ** max(0, math.ceil(-math.log10(low))) if low < 1 else 1.0
    info = {"hyperliquid": hl_name, "dydx": dy_ticker, "hl_tokens_per_contract": per_contract,
            "price_scale_tokens": scale, "first_day": days[0], "last_day": days[-1],
            "days": len(days)}
    rows = []
    for day in days:
        for venue, price, volume, carry in (
                ("HL", hl_bars[day][0] / per_contract * scale, hl_bars[day][1], hl_carry[day]),
                ("DY", dy_bars[day][0] * scale, dy_bars[day][1], dy_carry[day])):
            rows.append({"date": day, "symbol": f"{venue}.{coin}", "open": price,
                         "high": price, "low": price, "close": price, "adj_close": price,
                         "volume": volume, "carry_rate": carry})
    return rows, info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--end", help="exclusive UTC end day (default: today)")
    parser.add_argument("--offline", action="store_true", help="use the raw cache only")
    parser.add_argument("--state", default="var/perp_hl_dydx_build")
    parser.add_argument("--coins", help="comma-separated subset (smoke test only; no registration)")
    args = parser.parse_args()
    end_day = (datetime.fromisoformat(args.end).replace(tzinfo=timezone.utc) if args.end
               else datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0))
    end_ms = int(end_day.timestamp() * 1000)
    fetcher = Fetcher(args.offline)
    only = set(args.coins.split(",")) if args.coins else None
    rows, symbols, coins = build(fetcher, end_ms, log=lambda line: print(line, flush=True),
                                 only=only)
    if only:
        print(json.dumps(coins, indent=1), len(rows))
        return
    panel = PricePanel(rows)
    manifest = sorted(fetcher.provenance.values(), key=lambda item: item["cache"])
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    with PROVENANCE.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as handle:
            handle.write("".join(json.dumps(item, sort_keys=True) + "\n"
                                 for item in manifest).encode())
    (PROVENANCE.parent / "coins.json").write_text(json.dumps(coins, indent=1, sort_keys=True))
    paths = QuantPaths(ROOT, state=args.state).ensure()
    record = DatasetRecord(
        dataset_id=DATASET,
        source="Hyperliquid public info API (meta, fundingHistory, candleSnapshot 1d) + dYdX v4 "
               "public indexer (perpetualMarkets, historicalFunding, candles 1DAY); "
               f"{len(manifest)} responses, sha256 per response in "
               f"{PROVENANCE.relative_to(ROOT)}",
        adapter="perp_funding_hl_dydx_derivation", path=f"data/datasets/{DATASET}.csv.gz",
        point_in_time={"information_available_at": "00:00 UTC after the dated day",
                       "minimum_decision_lag_days": 1,
                       "fill_convention": "open(d+1) = close(d+1): one full day of execution lag",
                       "funding_day": "hourly settlements at 01:00..24:00 UTC of the dated day",
                       "funding_units": "rate per hourly settlement, positive = longs pay; "
                                        "dYdX v4 and Hyperliquid use the same convention",
                       "required_symbols": ["HL.BTC", "DY.BTC", "HL.ETH", "DY.ETH",
                                            "HL.SOL", "DY.SOL"],
                       "min_rows_per_symbol": MIN_DAYS,
                       "fetched_through": end_day.date().isoformat()},
        caveats=["venue APIs queried directly; not independently cross-checked against a "
                 "third-party archive",
                 "delisted coins are included where both venues still serve history "
                 "(Hyperliquid meta isDelisted, dYdX FINAL_SETTLEMENT)",
                 "a day is kept only with >= 22 hourly settlements and a traded daily candle "
                 "on both venues; nothing is filled in",
                 "close is the daily candle's last trade; thin dYdX markets can print stale "
                 "closes, which adds cross-venue price noise to the pair",
                 "prices are per price_scale tokens (data/fast_rail/h002/coins.json) and "
                 "Hyperliquid k-coins are converted to per-token; returns are unaffected",
                 "HL volume notional = base volume x daily close (approximation)",
                 "no intraday margin, liquidation or auto-deleveraging modelling in the data",
                 "coin names are matched by ticker; a re-used ticker would pair different assets"],
        license_note="public venue APIs; research use")
    registered = _register(DatasetRegistry(paths.dataset_registry, paths.root), record, panel,
                           sorted(set(symbols)), paths.root)
    print(registered.dataset_id, registered.availability, registered.rows,
          len(registered.symbols), registered.first_date, registered.last_date,
          registered.fingerprint, registered.validation.get("problems"))


if __name__ == "__main__":
    main()
