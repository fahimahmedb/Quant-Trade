"""Build the cross-venue perpetual funding panel from public GitHub snapshots.

    python3 scripts/build_perp_funding_dataset.py --hyperliquid DIR --bybit DIR

Offline research tooling (needs pandas + pyarrow); the product itself stays
standard-library. Sources (clone them first; they are third-party snapshots):

* https://github.com/guibvieira/freqtrade-hyperliquid-data
  ``user_data/data/hyperliquid/futures/<COIN>_USDC_USDC-{1h-funding_rate,1d-futures}.feather``
* https://github.com/LorenzoBaggi/funding_arb
  ``funding_analysis/raw_data/<SYM>_funding.csv`` and ``kline_data/<SYM>_1h_linear_kline.csv``

Output: ``data/datasets/perp_funding_pairs_daily.csv.gz`` (PricePanel) with
symbols ``HL.<COIN>`` and ``BY.<COIN>``. For UTC day d:

* open = close = the venue's last price of day d (Hyperliquid daily close;
  Bybit close of the 23:00 hourly bar), so a fill "at open(d+1)" happens one
  full day after the decision (conservative for a 24/7 market);
* ``carry_rate`` = funding paid by longs over day d (sum of the venue's rates;
  a Bybit settlement at 00:00 pays for the previous day);
* volume = daily notional traded on that venue (used by the capacity model).

A day is kept for a venue only with a complete funding record (Hyperliquid
>= 22 hourly prints; Bybit >= 3 eight-hourly prints). Nothing is filled in.
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.dataplane.ingest import _register  # noqa: E402
from quant.dataplane.panel import PricePanel  # noqa: E402
from quant.dataplane.registry import DatasetRecord, DatasetRegistry  # noqa: E402
from quant.events import EventLog  # noqa: E402
from quant.paths import QuantPaths  # noqa: E402

DATASET = "perp_funding_pairs_daily"


def bybit_symbol(coin: str) -> str:
    return ("1000" + coin[1:] if coin.startswith("k") and coin[1:].isupper() else coin) + "USDT"


def build(hyperliquid: Path, bybit: Path) -> tuple[list[dict], list[str]]:
    rows, symbols = [], []
    for path in sorted(glob.glob(str(hyperliquid / "*_USDC_USDC-1h-funding_rate.feather"))):
        coin = os.path.basename(path).split("_")[0]
        sym = bybit_symbol(coin)
        funding_file = bybit / "funding_analysis" / "raw_data" / f"{sym}_funding.csv"
        kline_file = bybit / "kline_data" / f"{sym}_1h_linear_kline.csv"
        daily_file = hyperliquid / f"{coin}_USDC_USDC-1d-futures.feather"
        if not (funding_file.exists() and daily_file.exists()):
            continue
        hl_rates = pd.read_feather(path).set_index("date")["open"]
        hl_day = hl_rates.groupby(hl_rates.index.floor("D"))
        hl_carry = hl_day.sum()[hl_day.count() >= 22]
        hl_bar = pd.read_feather(daily_file).set_index("date")
        hl_bar = hl_bar[hl_bar.volume > 0]                      # drop backfilled rows
        by_rates = pd.read_csv(funding_file)
        stamp = pd.to_datetime(by_rates.fundingRateTimestamp, utc=True)
        by_day_index = (stamp - pd.Timedelta(seconds=1)).dt.floor("D")
        by_group = by_rates.fundingRate.groupby(by_day_index.values)
        by_carry = by_group.sum()[by_group.count() >= 3]
        by_carry.index = pd.to_datetime(by_carry.index, utc=True)
        proxy = not kline_file.exists()
        if proxy:
            # The Bybit kline snapshot only covers some coins: value the Bybit leg
            # at the Hyperliquid close (flagged price_proxy=1). This assumes a
            # perfect price hedge; measured cross-venue price drift was ~+1%/yr.
            by_close = hl_bar.close.copy()
            by_volume = hl_bar.volume * hl_bar.close
        else:
            kline = pd.read_csv(kline_file)
            kline["t"] = pd.to_datetime(kline.timestamp, utc=True)
            kline = kline.set_index("t")
            by_close = kline.close[kline.index.hour == 23].rename(lambda t: t.floor("D"))
            by_volume = (kline.volume * kline.close).groupby(kline.index.floor("D")).sum()
        days = (hl_carry.index.intersection(by_carry.index).intersection(hl_bar.index)
                .intersection(by_close.index))
        if len(days) < 60:
            continue
        for day in days:
            label = day.date().isoformat()
            for venue, price, volume, carry in (
                    ("HL", float(hl_bar.close[day]), float(hl_bar.volume[day] * hl_bar.close[day]),
                     float(hl_carry[day])),
                    ("BY", float(by_close[day]), float(by_volume.get(day, 0.0)),
                     float(by_carry[day]))):
                if price <= 0:
                    continue
                row = {"date": label, "symbol": f"{venue}.{coin}", "open": price,
                       "high": price, "low": price, "close": price, "adj_close": price,
                       "volume": volume, "carry_rate": carry}
                if proxy and venue == "BY":
                    row["price_proxy"] = 1.0
                rows.append(row)
        symbols += [f"HL.{coin}", f"BY.{coin}"]
    return rows, symbols


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hyperliquid", type=Path, required=True,
                        help=".../freqtrade-hyperliquid-data/user_data/data/hyperliquid/futures")
    parser.add_argument("--bybit", type=Path, required=True, help=".../funding_arb")
    parser.add_argument("--state", default="var/perp_build")
    args = parser.parse_args()
    rows, symbols = build(args.hyperliquid, args.bybit)
    panel = PricePanel(rows)
    paths = QuantPaths(ROOT, state=args.state).ensure()
    record = DatasetRecord(
        dataset_id=DATASET,
        source="github.com/guibvieira/freqtrade-hyperliquid-data (Hyperliquid 1h funding, "
               "1d bars) + github.com/LorenzoBaggi/funding_arb (Bybit funding, 1h klines)",
        adapter="perp_funding_pairs_derivation", path=f"data/datasets/{DATASET}.csv.gz",
        point_in_time={"information_available_at": "00:00 UTC after the dated day",
                       "minimum_decision_lag_days": 1,
                       "fill_convention": "open(d+1) = close(d+1): one full day of execution lag",
                       # staggered listings: anchors must be current, others may start
                       # late or be delisted (keeping them avoids survivorship)
                       "required_symbols": ["HL.BTC", "BY.BTC", "HL.ETH", "BY.ETH", "HL.SOL", "BY.SOL"],
                       "min_rows_per_symbol": 60},
        caveats=["third-party snapshots, not verified against the venues",
                 "survivorship: only coins still listed when the snapshots were taken",
                 "no intraday margin, liquidation or auto-deleveraging modelling in the data",
                 "Bybit coverage ends 2025-05; forward data comes from data/feeds/funding",
                 "where the Bybit kline snapshot is missing the Bybit leg is valued at the "
                 "Hyperliquid close (price_proxy=1): cross-venue price divergence is then "
                 "not modelled for that coin"],
        license_note="third-party public repositories; research use")
    registered = _register(DatasetRegistry(paths.dataset_registry, paths.root), record, panel,
                           sorted(set(symbols)), paths.root)
    print(registered.dataset_id, registered.availability, registered.rows, len(registered.symbols),
          registered.first_date, registered.last_date, registered.fingerprint,
          registered.validation.get("problems"))


if __name__ == "__main__":
    main()
