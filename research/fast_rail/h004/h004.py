"""H-004 analysis: maker P&L of being the counterparty of every taker print.

Measurement only. Pure functions (tested offline) + ``main`` that reads the
stored sample under data/fast_rail/h004/ and writes results.json.

Sign convention: taker_side "yes" means the taker bought YES, so the maker
SOLD YES at p: maker P&L = p - ref. taker_side "no" means the maker BOUGHT YES
at p: maker P&L = ref - p. Prices are YES prices in dollars.
"""
from __future__ import annotations

import bisect
import datetime as dt
import gzip
import json
import math
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h004_config as config  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "fast_rail" / "h004"


@dataclass(frozen=True)
class Print:
    t: float          # epoch seconds
    price: float      # YES price, dollars
    count: float      # contracts
    taker_side: str   # "yes" | "no"


def maker_sign(taker_side: str) -> int:
    """+1 if the maker bought YES (taker sold YES / bought NO), -1 if the maker sold YES."""
    if taker_side == "no":
        return 1
    if taker_side == "yes":
        return -1
    raise ValueError(taker_side)


def maker_pnl(price: float, reference: float, taker_side: str) -> float:
    return maker_sign(taker_side) * (reference - price)


def maker_fee(price: float, rate: float = config.MAKER_FEE_RATE) -> float:
    """Per-contract maker fee (unrounded, see config)."""
    return rate * price * (1.0 - price)


def markout_reference(prints: list[Print], times: list[float], i: int,
                      start_s: float = config.MARKOUT_START_S,
                      end_s: float = config.MARKOUT_END_S) -> float | None:
    """VWAP of prints of the same market in [t_i + start, t_i + end); None if none (no filling)."""
    t0 = prints[i].t
    lo = bisect.bisect_left(times, t0 + start_s)
    hi = bisect.bisect_left(times, t0 + end_s)
    num = den = 0.0
    for j in range(lo, hi):
        num += prints[j].price * prints[j].count
        den += prints[j].count
    return num / den if den > 0 else None


def prior_mid(prints: list[Print], i: int, lookback_s: float = 600.0) -> float | None:
    """Half-spread proxy mid: mean of the last taker-YES (~ask) and last taker-NO (~bid)
    prices strictly before t_i within the lookback. Strictly causal."""
    t0 = prints[i].t
    ask = bid = None
    j = i - 1
    while j >= 0 and (ask is None or bid is None):
        p = prints[j]
        if p.t >= t0:
            j -= 1
            continue
        if t0 - p.t > lookback_s:
            break
        if p.taker_side == "yes" and ask is None:
            ask = p.price
        elif p.taker_side == "no" and bid is None:
            bid = p.price
        j -= 1
    if ask is None or bid is None:
        return None
    return 0.5 * (ask + bid)


@dataclass
class Unit:
    """One event-day: (series, event date). Contract-weighted sums per evaluation."""
    series: str
    category: str
    date: dt.date
    sums: dict = field(default_factory=dict)

    def add(self, key: str, contracts: float, gross: float, fee: float, notional: float) -> None:
        s = self.sums.setdefault(key, {"c": 0.0, "gross": 0.0, "fee": 0.0, "notional": 0.0})
        s["c"] += contracts
        s["gross"] += gross * contracts
        s["fee"] += fee * contracts
        s["notional"] += notional * contracts

    def per_contract(self, key: str, fee_mult: float = 1.0) -> float | None:
        s = self.sums.get(key)
        if not s or s["c"] <= 0:
            return None
        return (s["gross"] - fee_mult * s["fee"]) / s["c"]

    def dollars(self, key: str, fee_mult: float = 1.0) -> float:
        s = self.sums.get(key)
        return 0.0 if not s else s["gross"] - fee_mult * s["fee"]


def process_market(unit: Unit, prints: list[Print], result: str | None) -> None:
    """Accumulate maker P&L of every print of one market into its event-day unit."""
    prints = sorted(prints, key=lambda p: p.t)
    times = [p.t for p in prints]
    settle = {"yes": 1.0, "no": 0.0}.get(result or "")
    for i, p in enumerate(prints):
        fee = maker_fee(p.price)
        notional = p.price if maker_sign(p.taker_side) > 0 else 1.0 - p.price
        if settle is not None:
            unit.add("settlement", p.count, maker_pnl(p.price, settle, p.taker_side), fee, notional)
        ref = markout_reference(prints, times, i)
        if ref is None:
            continue  # no filling: a print without a later window print is skipped
        mk = maker_pnl(p.price, ref, p.taker_side)
        unit.add("markout", p.count, mk, fee, notional)
        mid = prior_mid(prints, i)
        if mid is not None:
            unit.add("hs_proxy", p.count, maker_pnl(p.price, mid, p.taker_side), 0.0, notional)
            unit.add("hs_markout", p.count, mk, 0.0, notional)


def split_dates(dates: list[dt.date]) -> tuple[list[dt.date], list[dt.date], list[dt.date]]:
    ds = sorted(set(dates))
    n = len(ds)
    a = int(round(n * config.DISCOVERY_FRACTION))
    b = int(round(n * (config.DISCOVERY_FRACTION + config.VALIDATION_FRACTION)))
    return ds[:a], ds[a:b], ds[b:]


def t_stat(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    sd = statistics.stdev(xs)
    return statistics.fmean(xs) / (sd / math.sqrt(len(xs))) if sd > 0 else 0.0


def evaluate(units: list[Unit], category: str, key: str) -> dict:
    us = sorted((u for u in units if u.category == category and u.per_contract(key) is not None),
                key=lambda u: (u.date, u.series))
    x1 = [u.per_contract(key) for u in us]
    x2 = [u.per_contract(key, 2.0) for u in us]
    x0 = [u.per_contract(key, 0.0) for u in us]
    out = {"n": len(us), "mean_net_c": 100 * statistics.fmean(x1) if x1 else None,
           "mean_gross_c": 100 * statistics.fmean(x0) if x0 else None,
           "mean_net_fee2x_c": 100 * statistics.fmean(x2) if x2 else None,
           "t_net": t_stat(x1), "t_net_fee2x": t_stat(x2),
           "contracts": sum(u.sums[key]["c"] for u in us)}
    half = len(us) // 2
    out["half_means_c"] = [100 * statistics.fmean(x1[:half]) if x1[:half] else None,
                           100 * statistics.fmean(x1[half:]) if x1[half:] else None]
    dollars = sorted((u.dollars(key) for u in us), reverse=True)
    total = sum(dollars)
    k = max(1, math.ceil(0.10 * len(dollars))) if dollars else 0
    out["net_dollars"] = total
    out["top_decile_share"] = (sum(dollars[:k]) / total) if total > 0 else None
    return out


def build_units(markets: list[dict], trades: dict[str, list[Print]], allowed: set[dt.date]) -> list[Unit]:
    """Only markets whose event date is in ``allowed`` are processed (untouched dates never load)."""
    units: dict[tuple[str, dt.date], Unit] = {}
    for m in markets:
        d = dt.date.fromisoformat(m["event_date"])
        if d not in allowed:
            continue
        key = (m["series"], d)
        u = units.setdefault(key, Unit(m["series"], config.CATEGORY[m["series"]], d))
        process_market(u, trades.get(m["ticker"], []), m.get("result"))
    return list(units.values())


def decode(rec: dict) -> list[Print]:
    out, t = [], 0
    for dtm, p, c, s in zip(rec["t"], rec["p"], rec["c"], rec["s"]):
        t += dtm
        out.append(Print(t / 1000.0, p / 1e4, c / 100.0, "yes" if s == "y" else "no"))
    return out


def load(allowed: set[dt.date]) -> tuple[list[dict], dict[str, list[Print]]]:
    with gzip.open(DATA / "markets.jsonl.gz", "rt") as f:
        markets = [json.loads(line) for line in f]
    markets = [m for m in markets if dt.date.fromisoformat(m["event_date"]) in allowed]
    wanted = {m["ticker"] for m in markets}
    trades: dict[str, list[Print]] = {}
    for path in sorted(DATA.glob("trades_*.jsonl.gz")):
        with gzip.open(path, "rt") as f:
            for line in f:
                rec = json.loads(line)
                if rec["ticker"] in wanted:
                    trades[rec["ticker"]] = decode(rec)
    return markets, trades


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from quant.factory.evaluate import required_t_statistic

    disc, val, untouched = split_dates(config.sampled_dates())
    trials = config.DECLARED_TRIALS + config.RERUNS
    req_t = required_t_statistic(trials)
    markets, trades = load(set(disc) | set(val))
    res: dict = {"split": {"discovery": [str(disc[0]), str(disc[-1]), len(disc)],
                           "validation": [str(val[0]), str(val[-1]), len(val)],
                           "untouched": [str(untouched[0]), str(untouched[-1]), len(untouched)]},
                 "trials": trials, "required_t": req_t, "discovery": {}, "validation": {}}
    units_d = build_units(markets, trades, set(disc))
    units_v = build_units(markets, trades, set(val))
    for cat in ("weather", "other"):
        for key in ("markout", "settlement"):
            res["discovery"][f"{cat}/{key}"] = evaluate(units_d, cat, key)
            res["validation"][f"{cat}/{key}"] = evaluate(units_v, cat, key)
        for name, us in (("discovery", units_d), ("validation", units_v)):
            hs = [u for u in us if u.category == cat and u.per_contract("hs_proxy") is not None]
            c = sum(u.sums["hs_proxy"]["c"] for u in hs)
            res[name][f"{cat}/decomposition"] = {
                "half_spread_proxy_c": 100 * sum(u.sums["hs_proxy"]["gross"] for u in hs) / c if c else None,
                "markout_same_prints_c": 100 * sum(u.sums["hs_markout"]["gross"] for u in hs) / c if c else None,
                "contracts": c}
    best = max((k for k in res["discovery"] if not k.endswith("decomposition")),
               key=lambda k: res["discovery"][k]["t_net"])
    res["best_discovery_expression"] = best
    cat = best.split("/")[0]
    # Capacity: maker notional per sampled date x 30.44 days x maker share (disc+val only).
    all_units = [u for u in units_d + units_v if u.category == cat]
    notional = sum(u.sums.get("settlement", {}).get("notional", 0.0) for u in all_units)
    n_dates = len(disc) + len(val)
    res["capacity_usd_month"] = notional / n_dates * 30.44 * config.MAKER_SHARE_OF_VOLUME
    v = res["validation"][best]
    checks = {
        "t_ge_required": v["t_net"] >= req_t,
        "mean_net_pos": (v["mean_net_c"] or 0) > 0,
        "mean_net_fee2x_pos": (v["mean_net_fee2x_c"] or 0) > 0,
        "both_halves_pos": all((h or 0) > 0 for h in v["half_means_c"]),
        "top_decile_lt_half": v["top_decile_share"] is not None and v["top_decile_share"] < config.MAX_TOP_DECILE_SHARE,
        "capacity_ok": res["capacity_usd_month"] >= config.MIN_MONTHLY_TURNOVER_USD,
    }
    res["checks"] = checks
    res["verdict"] = "CANDIDATE (measurement only)" if all(checks.values()) else "REJECT"
    if res["verdict"] != "REJECT" and not best.endswith("settlement"):
        res["verdict"] += " - markout is diagnostic, not realisable"
    out = Path(__file__).resolve().parent / "results.json"
    out.write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
