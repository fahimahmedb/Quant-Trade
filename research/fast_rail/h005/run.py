"""H-005 runner: stored raw data -> events -> discovery selection -> validation verdict.

The final 15% of events (by listing date) is UNTOUCHED: no funding is fetched for
it and no return is computed on it; only its count and date range are reported.

    python3 research/fast_rail/h005/run.py   ->  research/fast_rail/h005/results.json
"""
from __future__ import annotations

import gzip
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from quant.factory.evaluate import required_t_statistic  # noqa: E402
from research.fast_rail.h005 import analysis as A  # noqa: E402

RAW = ROOT / "data" / "fast_rail" / "h005" / "raw"
OUT = Path(__file__).resolve().parent / "results.json"
MAX_H = max(h for h, _ in A.GRID)
RERUNS = 0  # full-grid reruns on the same dataset; each adds 6 trials


def _load(name: str):
    return json.loads(gzip.decompress((RAW / f"{name}.json.gz").read_bytes()))


def load_universe():
    meta = _load("meta")
    delisted = {a["name"] for a in meta["universe"] if a.get("isDelisted")}
    universe = {}
    for a in meta["universe"]:
        rows = A.parse_candles(_load(f"candles_{a['name']}"))
        if rows:
            universe[a["name"]] = rows
    return universe, delisted


def _studied():
    universe, delisted = load_universe()
    events, info = A.build_events(universe, delisted)
    disc, val, untouched = A.split_events(events)
    return universe, disc, val, untouched, info


def _fund_window(ev):
    t0 = A.day_ms(ev["listing_day"]) + A.DAY_MS
    return t0, t0 + (MAX_H + 1) * A.DAY_MS


def funding_requests():
    """(coin, start_ms, end_ms) for discovery+validation events and BTC over their span."""
    _, disc, val, _, _ = _studied()
    reqs = [(e["coin"], *_fund_window(e)) for e in disc + val]
    lo = min(r[1] for r in reqs)
    hi = max(r[2] for r in reqs)
    return reqs + [("BTC", lo, hi)]


def _load_funding(coin, start_ms):
    rows, page = [], 0
    while (RAW / f"funding_{coin}_{start_ms}_p{page}.json.gz").exists():
        rows += _load(f"funding_{coin}_{start_ms}_p{page}")
        page += 1
    return rows


def compute(cost_mult: float = 1.0):
    universe, disc, val, untouched, info = _studied()
    btc = universe["BTC"]
    btc_start = funding_requests()[-1][1]
    btc_f = _load_funding("BTC", btc_start)
    out = {}
    for name, evs in (("discovery", disc), ("validation", val)):
        per_h = {}
        for h in sorted({h for h, _ in A.GRID}):
            rows, skipped = [], []
            for e in evs:
                r = A.event_returns(e, universe[e["coin"]], _load_funding(e["coin"], _fund_window(e)[0]),
                                    btc, btc_f, h, cost_mult)
                (rows.append(r) if r else skipped.append(e["coin"]))
            per_h[h] = {"rows": rows, "skipped": skipped}
        out[name] = per_h
    return out, disc, val, untouched, info


def main():
    base, disc, val, untouched, info = compute(1.0)
    dbl, *_ = compute(2.0)
    trials = len(A.GRID) * (1 + RERUNS)
    req_t = required_t_statistic(trials)
    key = {"none": "short_net", "btc": "hedged_net"}
    discovery = {}
    for h, hedge in A.GRID:
        discovery[f"H{h}_{hedge}"] = A.summarize(base["discovery"][h]["rows"], key[hedge])
    best = max(discovery, key=lambda k: discovery[k]["t"])
    bh, bhedge = int(best.split("_")[0][1:]), best.split("_")[1]
    vrows = base["validation"][bh]["rows"]
    vs = A.summarize(vrows, key[bhedge])
    xs = [r[key[bhedge]] for r in vrows]
    half = len(xs) // 2
    halves = [statistics.fmean(xs[:half]), statistics.fmean(xs[half:])]
    x2 = [r[key[bhedge]] for r in dbl["validation"][bh]["rows"]]
    unhedged = [r["short_net"] for r in vrows]
    short_btc = [r["short_btc_net"] for r in vrows]
    diff = [a - b for a, b in zip(unhedged, short_btc)]
    caps = [r["capacity_usd"] for r in vrows]
    worst = min(vrows, key=lambda r: r[key[bhedge]])
    top = A.top_decile_share(xs)
    checks = {
        "t_ge_required": vs["t"] >= req_t,
        "mean_pos_2x_costs": statistics.fmean(x2) > 0,
        "both_halves_positive": all(m > 0 for m in halves),
        "top10pct_lt_50pct_of_gains": top < 0.5,
        "unhedged_beats_short_btc": statistics.fmean(diff) > 0,
        "capacity_median_ge_10k": statistics.median(caps) >= 10_000,
    }
    result = {
        "hypothesis": "H-005", "dataset_key": "hl_new_listings_events", **info,
        "n_events": {"discovery": len(disc), "validation": len(val), "untouched": len(untouched)},
        "untouched_range": [untouched[0]["listing_day"].isoformat(), untouched[-1]["listing_day"].isoformat()] if untouched else None,
        "validation_range": [val[0]["listing_day"].isoformat(), val[-1]["listing_day"].isoformat()],
        "discovery_range": [disc[0]["listing_day"].isoformat(), disc[-1]["listing_day"].isoformat()],
        "trials": trials, "required_t": req_t, "discovery": discovery, "best": best,
        "validation": {**vs, "mean_2x_costs": statistics.fmean(x2), "halves": halves,
                       "top10pct_share": top, "skipped": base["validation"][bh]["skipped"],
                       "exit_kinds": {k: sum(r["exit_kind"] == k for r in vrows) for k in {r["exit_kind"] for r in vrows}},
                       "unhedged_mean": statistics.fmean(unhedged), "short_btc_mean": statistics.fmean(short_btc),
                       "unhedged_minus_short_btc": A.summarize([{**r, "d": d} for r, d in zip(vrows, diff)], "d"),
                       "capacity_median_usd": statistics.median(caps),
                       "capacity_frac_ge_10k": sum(c >= 10_000 for c in caps) / len(caps),
                       "worst_event": {k: worst[k] for k in ("coin", "listing_day", "exit_kind", "gross_short", "funding_short", key[bhedge])},
                       "best_event": max(xs), "mean_funding_short": statistics.fmean(r["funding_short"] for r in vrows)},
        "checks": checks, "verdict": "CANDIDATE" if all(checks.values()) else "REJECTED",
        "oi_caps": "unknown: HL applies open-interest caps to new listings; historical cap levels are not in the public info API",
        "events_validation": vrows,
    }
    OUT.write_text(json.dumps(result, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("events_validation",)}, indent=1, default=str))


if __name__ == "__main__":
    main()
