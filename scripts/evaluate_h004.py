"""Evaluate H-004 once on data/fast_rail/kalshi_weather_trades.csv.gz.

    PYTHONPATH=src python3 scripts/evaluate_h004.py   -> research/fast_rail/h004_result.json

Trials: the two pre-registered price bands. Threshold required_t_statistic(2).
Falsification (registry): market-clustered t >= threshold, both date-halves
positive, top 10% of markets < 0.5 of P&L, >= 10k$ passive notional/month.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.factory import kalshi_maker as km  # noqa: E402
from quant.factory.evaluate import required_t_statistic  # noqa: E402

DATA = ROOT / "data" / "fast_rail" / "kalshi_weather_trades.csv.gz"
META = ROOT / "data" / "fast_rail" / "kalshi_weather_trades.csv.meta.json"
OUT = ROOT / "research" / "fast_rail" / "h004_result.json"
BANDS = [(1, 99), (10, 90)]
TRIALS = 2
MIN_MONTHLY_NOTIONAL = 10_000.0


def _stats(rows: list[dict]) -> dict:
    by_market = km.aggregate(rows, "ticker")
    by_date = km.aggregate(rows, "event_date")
    m = km.clustered_mean(by_market)
    d = km.clustered_mean(by_date)
    gross = sum(float(r["gross_pnl_cents"]) for r in rows)
    n = sum(float(r["contracts"]) for r in rows)
    return {
        "mean_net_cents_per_contract": m["mean"],
        "se_market_clustered": m["se"], "t_market_clustered": m["t"], "markets": m["clusters"],
        "se_date_clustered": d["se"], "t_date_clustered": d["t"], "event_dates": d["clusters"],
        "mean_gross_cents_per_contract": gross / n if n else float("nan"),
        "mean_fee_cents_per_contract": sum(float(r["fee_cents"]) for r in rows) / n if n else float("nan"),
        "contracts": n, "trades": sum(int(r["n_trades"]) for r in rows),
        "top10pct_market_share": km.top_share(by_market),
    }


def evaluate(rows: list[dict], meta: dict) -> dict:
    required = required_t_statistic(TRIALS)
    weather = [r for r in rows if r["category"] == "weather"]
    comparison = [r for r in rows if r["category"] == "comparison"]
    dates = sorted({r["event_date"] for r in weather})
    split = dates[len(dates) // 2]
    months = sorted({r["event_date"][:7] for r in weather})
    universe = defaultdict(float)
    for key, v in meta["universe_contracts_by_series_month"].items():
        universe[key.split("|")[1]] += v
    out = {"hypothesis": "H-004", "trials": TRIALS, "required_t": required,
           "span": [dates[0], dates[-1]], "split_date": split, "bands": {}}
    for lo, hi in BANDS:
        band = [r for r in weather if lo <= int(r["yes_price"]) <= hi]
        s = _stats(band)
        h1 = _stats([r for r in band if r["event_date"] < split])
        h2 = _stats([r for r in band if r["event_date"] >= split])
        # capacity: maker capital at risk per month in the sample, scaled to the
        # whole seven-series universe by contracts traded (all strikes, all days)
        monthly = {}
        for mo in months:
            rows_mo = [r for r in band if r["event_date"][:7] == mo]
            all_mo = [r for r in weather if r["event_date"][:7] == mo]
            cap = sum(float(r["maker_capital_usd"]) for r in rows_mo)
            sample_contracts = sum(float(r["contracts"]) for r in all_mo)
            scale = universe[mo] / sample_contracts if sample_contracts else float("nan")
            monthly[mo] = {"sample_maker_capital_usd": cap, "universe_scale": scale,
                           "universe_maker_capital_usd": cap * scale}
        sample_min = min(v["sample_maker_capital_usd"] for v in monthly.values())
        checks = {
            "t_market_clustered_ge_required": s["t_market_clustered"] >= required,
            "mean_positive": s["mean_net_cents_per_contract"] > 0,
            "first_half_positive": h1["mean_net_cents_per_contract"] > 0,
            "second_half_positive": h2["mean_net_cents_per_contract"] > 0,
            "top10pct_markets_lt_half": s["top10pct_market_share"] < 0.5,
            "monthly_passive_notional_ge_10k_sample_only": sample_min >= MIN_MONTHLY_NOTIONAL,
        }
        out["bands"][f"{lo}-{hi}"] = {
            **s, "first_half": {k: h1[k] for k in ("mean_net_cents_per_contract", "t_market_clustered", "markets")},
            "second_half": {k: h2[k] for k in ("mean_net_cents_per_contract", "t_market_clustered", "markets")},
            "monthly_capacity": monthly, "min_month_sample_maker_capital_usd": sample_min,
            "checks": checks, "pass": all(checks.values()),
        }
    if comparison:
        out["comparison_descriptive_only"] = {"series": "KXBTCD", **{
            f"{lo}-{hi}": _stats([r for r in comparison if lo <= int(r["yes_price"]) <= hi])
            for lo, hi in BANDS}}
    out["verdict"] = "CANDIDATE" if any(b["pass"] for b in out["bands"].values()) else "REJECT"
    return out


def main() -> None:
    text = gzip.decompress(DATA.read_bytes()).decode()
    rows = list(csv.DictReader(io.StringIO(text)))
    meta = json.loads(META.read_text())
    out = evaluate(rows, meta)
    out["dataset_fingerprint"] = meta["fingerprint_sha256"]
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True, default=float) + "\n")
    brief = {k: {kk: b[kk] for kk in ("mean_net_cents_per_contract", "t_market_clustered", "t_date_clustered",
                                        "trades", "markets", "top10pct_market_share", "pass")}
             for k, b in out["bands"].items()}
    print(json.dumps({"verdict": out["verdict"], "required_t": out["required_t"], "bands": brief}, indent=1))


if __name__ == "__main__":
    main()
