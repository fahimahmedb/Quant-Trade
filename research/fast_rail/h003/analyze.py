"""H-003 analysis: buy NO on cheap YES Kalshi contracts (rules fixed in PREREG.md).

Only discovery (first 55%) and validation (next 30%) events are ever evaluated;
the last 15% is split off by close time and never passed to any return code.

    PYTHONPATH=src python3 research/fast_rail/h003/analyze.py
"""

from __future__ import annotations

import gzip
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from quant.factory.evaluate import required_t_statistic  # noqa: E402
from quant.factory.sportsfair import kalshi_taker_fee  # noqa: E402

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "..", "..", "data", "fast_rail", "h003", "markets.jsonl.gz")
GRID = [(thr, hours) for thr in (0.05, 0.10, 0.20) for hours in (24, 1)]
TRIALS = 6
MAX_STALE_S = 24 * 3600
DISCOVERY_FRAC, VALIDATION_FRAC = 0.55, 0.30
MIN_EVENTS = 10
VOLUME_TAKE = 0.10
CAPACITY_TARGET = 10_000.0


def select_candle(candles: list[list], entry_ts: int, max_stale_s: int = MAX_STALE_S) -> list | None:
    """Latest candle that CLOSED at or before entry_ts (and not staler than max_stale_s)."""
    best = None
    for candle in candles:
        end = candle[0]
        if end <= entry_ts and (best is None or end > best[0]):
            best = candle
    if best is None or entry_ts - best[0] > max_stale_s:
        return None
    return best


def no_entry_price(candle: list | None, yes_price_max: float) -> float | None:
    """NO ask (1 - yes_bid) if the YES mid is at or below the threshold; None = no trade."""
    if candle is None:
        return None
    bid, ask = candle[1], candle[2]
    if bid is None or ask is None or not (0.0 < bid <= ask < 1.0):
        return None
    if (bid + ask) / 2.0 > yes_price_max + 1e-12:
        return None
    return round(1.0 - bid, 4)


def contract_net(price: float, result: str, fee_mult: float = 1.0) -> float:
    fee = fee_mult * kalshi_taker_fee(price, 1)
    payout = 1.0 if result == "no" else 0.0
    return (payout - price - fee) / (price + fee)


def trailing_volume(candles: list[list], entry_ts: int, hours: int = 24) -> float:
    return sum(c[3] for c in candles if entry_ts - hours * 3600 < c[0] <= entry_ts)


def group_events(markets: list[dict]) -> dict[str, dict[str, Any]]:
    events: dict[str, dict[str, Any]] = {}
    for m in markets:
        ev = events.setdefault(m["event_ticker"], {"event_ticker": m["event_ticker"], "series": m["series"],
                                                   "close_ts": 0, "markets": []})
        ev["markets"].append(m)
        ev["close_ts"] = max(ev["close_ts"], m["close_ts"])
    return events


def split_events(events: dict[str, dict]) -> tuple[list[dict], list[dict], int]:
    """(discovery, validation, n_holdout). Holdout events are dropped here, never returned."""
    ordered = sorted(events.values(), key=lambda e: (e["close_ts"], e["event_ticker"]))
    n = len(ordered)
    d_end = int(n * DISCOVERY_FRAC)
    v_end = int(n * (DISCOVERY_FRAC + VALIDATION_FRAC))
    return ordered[:d_end], ordered[d_end:v_end], n - v_end


def event_returns(events: list[dict], yes_price_max: float, hours: int, fee_mult: float = 1.0) -> list[dict]:
    out = []
    for ev in events:
        nets, gross, dollars = [], [], 0.0
        for m in ev["markets"]:
            entry_ts = m["close_ts"] - hours * 3600
            candle = select_candle(m["candles"], entry_ts)
            price = no_entry_price(candle, yes_price_max)
            if price is None:
                continue
            nets.append(contract_net(price, m["result"], fee_mult))
            gross.append(contract_net(price, m["result"], 0.0))
            contracts = min(VOLUME_TAKE * trailing_volume(m["candles"], entry_ts), candle[4])
            dollars += contracts * price
        if nets:
            out.append({"event_ticker": ev["event_ticker"], "series": ev["series"], "close_ts": ev["close_ts"],
                        "net": statistics.fmean(nets), "gross": statistics.fmean(gross),
                        "n_contracts": len(nets), "deployable_usd": dollars})
    return out


def t_stat(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    sd = statistics.stdev(values)
    return statistics.fmean(values) / (sd / math.sqrt(len(values))) if sd else 0.0


def concentration(rows: list[dict]) -> dict[str, float]:
    total = sum(r["net"] for r in rows)
    by_series: dict[str, float] = defaultdict(float)
    for r in rows:
        by_series[r["series"]] += r["net"]
    top_n = max(1, math.ceil(0.10 * len(rows)))
    top = sum(sorted((r["net"] for r in rows), reverse=True)[:top_n])
    if total <= 0:
        return {"max_series_share": math.inf, "top10pct_share": math.inf, "top_series": ""}
    top_series = max(by_series, key=by_series.get)
    return {"max_series_share": by_series[top_series] / total, "top10pct_share": top / total,
            "top_series": top_series}


def summarize(rows: list[dict]) -> dict[str, Any]:
    nets = [r["net"] for r in rows]
    return {"n_events": len(rows), "mean_net": statistics.fmean(nets) if nets else 0.0, "t": t_stat(nets),
            "mean_gross": statistics.fmean(r["gross"] for r in rows) if rows else 0.0}


def load(path: str = DATA) -> list[dict]:
    seen, out = set(), []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if line.strip():
                row = json.loads(line)
                if row["ticker"] not in seen:  # a resumed fetch must not double-count a market
                    seen.add(row["ticker"])
                    out.append(row)
    return out


def main() -> int:
    markets = load()
    events = group_events(markets)
    discovery, validation, n_holdout = split_events(events)
    grid = {}
    for thr, hours in GRID:
        grid[f"yes<={thr}@T-{hours}h"] = (thr, hours, summarize(event_returns(discovery, thr, hours)))
    eligible = {k: v for k, v in grid.items() if v[2]["n_events"] >= MIN_EVENTS}
    best_key = max(eligible, key=lambda k: eligible[k][2]["t"]) if eligible else None
    report: dict[str, Any] = {
        "n_markets": len(markets), "n_events": len(events), "n_discovery": len(discovery),
        "n_validation": len(validation), "n_holdout_untouched": n_holdout,
        "discovery_span": [discovery[0]["close_ts"], discovery[-1]["close_ts"]],
        "validation_span": [validation[0]["close_ts"], validation[-1]["close_ts"]],
        "discovery_grid": {k: v[2] for k, v in grid.items()}, "best": best_key,
        "trials": TRIALS, "required_t": required_t_statistic(TRIALS),
    }
    if best_key:
        thr, hours, _ = grid[best_key]
        rows = event_returns(validation, thr, hours)
        rows2 = event_returns(validation, thr, hours, fee_mult=2.0)
        half = len(rows) // 2
        months = max(1e-9, (validation[-1]["close_ts"] - validation[0]["close_ts"]) / (30.44 * 86400))
        deploy = [r["deployable_usd"] for r in rows]
        val = summarize(rows)
        conc = concentration(rows)
        cap_month = sum(deploy) / months
        tests = {
            "mean_net_pos_and_t": val["mean_net"] > 0 and val["t"] >= report["required_t"],
            "fee_x2_mean_pos": summarize(rows2)["mean_net"] > 0,
            "both_halves_pos": bool(rows) and summarize(rows[:half])["mean_net"] > 0
            and summarize(rows[half:])["mean_net"] > 0,
            "series_share_lt_50": conc["max_series_share"] < 0.5,
            "top10_share_lt_50": conc["top10pct_share"] < 0.5,
            "capacity_ge_10k_month": cap_month >= CAPACITY_TARGET,
        }
        by_series: dict[str, list[float]] = defaultdict(list)
        for r in rows:
            by_series[r["series"]].append(r["net"])
        report["validation"] = {
            **val, "fee_drag": val["mean_gross"] - val["mean_net"],
            "fee_x2_mean_net": summarize(rows2)["mean_net"],
            "half1_mean": summarize(rows[:half])["mean_net"], "half2_mean": summarize(rows[half:])["mean_net"],
            **conc, "capacity_usd_per_month": cap_month,
            "median_event_deployable_usd": statistics.median(deploy) if deploy else 0.0,
            "months": months, "tests": tests,
            "by_series": {s: [len(v), statistics.fmean(v)] for s, v in sorted(by_series.items())},
        }
        report["verdict"] = "CANDIDATE" if all(tests.values()) else "REJECT"
    else:
        report["verdict"] = "BLOCKED"
    out = os.path.join(HERE, "results.json")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    print(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
