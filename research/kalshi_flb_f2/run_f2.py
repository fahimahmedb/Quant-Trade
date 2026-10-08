"""F2 KALSHI-FLB-OOS-001 analysis harness (Revision 1 of the pre-registration).

Pure analysis: no network. Input directory layout (written by the acquisition
stage, hashed there):
    markets.jsonl           one raw market object per line (historical list)
    candles/{ticker}.json   response body of the signal-candle request
    event_series.json       {event_ticker: series_ticker}
    series_category.json    {series_ticker: category}
    fee_table.json          {"default_multiplier": 1.0, "changes": [[iso_ts, multiplier], ...]}
Fails closed: any missing/unrecognised field raises before a result is written.

    python3 -I run_f2.py DATA_DIR RESULT_PATH
"""
import datetime as dt
import json
import math
import os
import sys
from collections import defaultdict

sys.dont_write_bytecode = True

WIN_LO = dt.datetime(2025, 5, 1, tzinfo=dt.timezone.utc)
WIN_HI = dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc)  # exclusive
Z_GATE = 2.128045  # one-sided, alpha = 0.05/3, m = 1
MIN_CLUSTERS = 250
ASK_MIN = 0.80
SPREAD_MAX = 0.20
OI_MIN = 1000.0
FINAL_VOL_MIN = 1000.0
TARGET = 0.01
H = 3600


class FormatError(RuntimeError):
    pass


def ts(s):
    if not isinstance(s, str) or not s:
        raise FormatError("missing timestamp")
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def num(x):
    if x is None:
        return None
    return float(x)


def ceil6(x):
    return math.ceil(round(x * 1e6, 6)) / 1e6


def ceil_cent(x):
    return math.ceil(round(x * 100, 9)) / 100


def fee_mult(table, series, when):
    """Multiplier in force on `when` for `series` (latest change with scheduled_ts <= when).
    None if the governing fee type is not 'quadratic'; fails closed outside [0.1, 3]."""
    changes = sorted(table.get("series", {}).get(series, []), key=lambda x: (ts(x[0]), str(x[2]), x[1]))
    m, ftype = table.get("default_multiplier", 1.0), "quadratic"
    for t, v, ft in changes:
        if ts(t) <= when:
            m, ftype = v, ft
    if ftype != "quadratic":
        return None
    if not (0.1 <= m <= 3.0):
        raise FormatError(f"fee multiplier {m} outside the pre-declared sanity range")
    return m


def ticks(x):
    """Exact integer ticks of 1/10000 from a FixedPointDollars string."""
    return int(round(float(x) * 10000))


def signal_candle(body, close_time):
    """Exactly one candle with end_period_ts in (T-25h, T-24h]; else None."""
    if "candlesticks" not in body:
        raise FormatError("candles body without candlesticks")
    hi = int((close_time - dt.timedelta(hours=24)).timestamp())
    lo = int((close_time - dt.timedelta(hours=25)).timestamp())
    sel = [c for c in body["candlesticks"] if lo < int(c["end_period_ts"]) <= hi]
    return sel[0] if len(sel) == 1 else None


def evaluate_market(m, candle, fees, cat_ok, series=None, mode="favourite"):
    """Return (reason_excluded | None, record). mode 'longshot' buys the cheap side (ask <= 0.20)."""
    if not isinstance(m.get("can_close_early"), bool):
        raise FormatError("can_close_early missing or not boolean")
    close_t, open_t = ts(m["close_time"]), ts(m["open_time"])
    bc, ac = candle["yes_bid"]["close"], candle["yes_ask"]["close"]
    if bc is None or ac is None:
        return "no_quote", None
    bid_t, ask_t = ticks(bc), ticks(ac)
    if not (0 < bid_t <= ask_t < 10000):
        return "bad_quote", None
    if ask_t - bid_t > 2000:
        return "spread", None
    ask_yes_t, ask_no_t = ask_t, 10000 - bid_t
    if mode == "favourite":
        if ask_yes_t >= 8000:
            side, pt = "yes", ask_yes_t
        elif ask_no_t >= 8000:
            side, pt = "no", ask_no_t
        else:
            return "no_signal", None
    else:
        if ask_yes_t <= 2000:
            side, pt = "yes", ask_yes_t
        elif ask_no_t <= 2000:
            side, pt = "no", ask_no_t
        else:
            return "no_signal", None
    p = pt / 10000.0
    oi = num(candle["open_interest"])
    win = (m["result"] == side)
    sig_end = close_t - dt.timedelta(hours=24)
    when = ts(m["settlement_ts"])
    if when <= sig_end:
        return "settlement_before_signal", None
    k = fee_mult(fees, series, close_t)
    if k is None:
        return "fee_type_not_quadratic", None
    fee = ceil6(0.07 * p * (1.0 - p) * k)
    fee_s = ceil_cent(0.07 * p * (1.0 - p) * k)
    payoff = 1.0 if win else 0.0
    rec = {"ticker": m["ticker"], "event": m["event_ticker"], "close": close_t, "price": p, "side": side,
           "fee": fee, "payoff": payoff,
           "net": (payoff - p - fee) / (p + fee), "net_stress": (payoff - p - fee_s) / (p + fee_s),
           "pnl": payoff - p - fee,
           "capital_days": (p + fee) * (when - sig_end).total_seconds() / 86400.0,
           "spread": (ask_t - bid_t) / 10000.0, "oi": oi, "final_vol": num(m.get("volume_fp")),
           "early": m["can_close_early"], "cat": cat_ok}
    return None, rec


def event_level(recs, cluster_key):
    ev = defaultdict(list)
    for r in recs:
        ev[r["event"]].append(r)
    rows = []
    for e, rs in ev.items():
        first = min(r["close"] for r in rs)
        rows.append((cluster_key(first), sum(r["net"] for r in rs) / len(rs), sum(r["net_stress"] for r in rs) / len(rs)))
    return rows


def cluster_stat(rows, idx=1):
    n = len(rows)
    if n < 2:
        return {"n_events": n, "n_clusters": n, "mean": None, "se": None, "t": None}
    mu = sum(r[idx] for r in rows) / n
    cl = defaultdict(float)
    for r in rows:
        cl[r[0]] += r[idx] - mu
    g = len(cl)
    if g < 2:
        return {"n_events": n, "n_clusters": g, "mean": mu, "se": None, "t": None}
    se = math.sqrt(g / (g - 1.0) * sum(v * v for v in cl.values())) / n
    return {"n_events": n, "n_clusters": g, "mean": mu, "se": se, "t": (mu / se if se > 0 else None)}


def classify(primary, stress):
    g, t, se, mu = primary["n_clusters"], primary["t"], primary["se"], primary["mean"]
    if g < MIN_CLUSTERS or t is None:
        return "INCONCLUSIVE_UNDERPOWERED"
    if t >= Z_GATE and stress["mean"] is not None and stress["mean"] > 0:
        return "CONFIRMED"
    if mu + 1.645 * se < TARGET:
        return "NOT_CONFIRMED_EXCLUDES_+1.0%"
    return "INCONCLUSIVE_UNDERPOWERED"


def day_key(t):
    return t.date().isoformat()


def week_key(t):
    y, w, _ = t.isocalendar()
    return f"{y}-W{w:02d}"


def month_key(t):
    return f"{t.year}-{t.month:02d}"


def load(data_dir):
    def jl(name):
        with open(os.path.join(data_dir, name)) as fh:
            return json.load(fh)

    with open(os.path.join(data_dir, "markets.jsonl")) as fh:
        markets = [json.loads(l) for l in fh if l.strip()]
    return markets, jl("event_series.json"), jl("series_category.json"), jl("fee_table.json")


def nw_se(x, lags):
    n = len(x)
    mu = sum(x) / n
    e = [v - mu for v in x]
    g = sum(v * v for v in e) / n
    for L in range(1, lags + 1):
        g += 2.0 * (1.0 - L / (lags + 1.0)) * sum(e[i] * e[i - L] for i in range(L, n)) / n
    return math.sqrt(max(g, 0.0) / n)


def evaluate_all(markets, ev_series, cats, fees, data_dir, mode, excl):
    recs = []
    for m in markets:
        s = ts(m["settlement_ts"]) if m.get("settlement_ts") else None
        if s is None or not (WIN_LO <= s < WIN_HI):
            continue
        series = ev_series.get(m["event_ticker"])
        cat = cats.get(series) if series else None
        if not cat:
            continue
        p = os.path.join(data_dir, "candles", m["ticker"] + ".json")
        if not os.path.exists(p):
            continue
        with open(p) as fh:
            body = json.load(fh)
        c = signal_candle(body, ts(m["close_time"]))
        if c is None:
            continue
        why, rec = evaluate_market(m, c, fees, cat, series, mode)
        if why:
            excl[why] += 1
            continue
        recs.append(rec)
    return recs


def tail_structure(rs):
    wins = [r["payoff"] - r["price"] - r["fee"] for r in rs if r["payoff"] == 1.0]
    losses = [r["payoff"] - r["price"] - r["fee"] for r in rs if r["payoff"] == 0.0]
    mw = sum(wins) / len(wins) if wins else None
    ml = sum(losses) / len(losses) if losses else None
    return {"n_wins": len(wins), "n_losses": len(losses), "mean_win": mw, "mean_loss": ml,
            "wins_offset_by_one_loss": (-ml / mw if (mw and ml) else None)}


def run(data_dir, result_path):
    markets, ev_series, cats, fees = load(data_dir)
    tickers = [m.get("ticker") for m in markets]
    if len(tickers) != len(set(tickers)):
        raise FormatError("duplicate tickers in markets.jsonl")
    excl = defaultdict(int)
    recs = []
    for m in markets:
        for k in ("ticker", "event_ticker", "market_type", "result", "open_time", "close_time", "settlement_ts", "can_close_early"):
            if k not in m:
                raise FormatError(f"market missing {k}")
        if not m["settlement_ts"]:
            excl["no_settlement"] += 1
            continue
        s = ts(m["settlement_ts"])
        if not (WIN_LO <= s < WIN_HI):
            excl["outside_window"] += 1
            continue
        if m["market_type"] != "binary":
            excl["not_binary"] += 1
            continue
        if m["result"] not in ("yes", "no"):
            excl["void_or_scalar_result"] += 1
            continue
        if (ts(m["close_time"]) - ts(m["open_time"])).total_seconds() < 24 * H:
            excl["open_lt_24h"] += 1
            continue
        series = ev_series.get(m["event_ticker"])
        cat = cats.get(series) if series else None
        if not cat:
            excl["category_unresolved"] += 1
            continue
        p = os.path.join(data_dir, "candles", m["ticker"] + ".json")
        if not os.path.exists(p):
            excl["no_candle_file"] += 1
            continue
        with open(p) as fh:
            body = json.load(fh)
        c = signal_candle(body, ts(m["close_time"]))
        if c is None:
            excl["candle_count_not_one"] += 1
            continue
        why, rec = evaluate_market(m, c, fees, cat, series)
        if why:
            excl[why] += 1
            continue
        recs.append(rec)

    def sel(r):
        return (not r["early"]) and r["cat"] != "Sports" and r["oi"] is not None and r["oi"] >= OI_MIN

    primary = [r for r in recs if sel(r)]
    rows = event_level(primary, day_key)
    p_stat, s_stat = cluster_stat(rows, 1), cluster_stat(rows, 2)
    status = classify(p_stat, s_stat)

    def sens(rs):
        rr = event_level(rs, day_key)
        return {"base": cluster_stat(rr, 1), "stress": cluster_stat(rr, 2)}

    # non-gating: mirror longshot side on the primary universe
    excl_l = defaultdict(int)
    longs = [r for r in evaluate_all(markets, ev_series, cats, fees, data_dir, "longshot", excl_l)
             if r["oi"] is not None and r["oi"] >= OI_MIN and not r["early"] and r["cat"] != "Sports"]
    daily = defaultdict(list)
    for d, v, _ in rows:
        daily[d].append(v)
    series_days = [sum(v) / len(v) for _, v in sorted(daily.items())]
    cum, peak, mdd = 0.0, 0.0, 0.0
    by_day_pnl = defaultdict(float)
    for r_ in primary:
        by_day_pnl[day_key(r_["close"])] += r_["pnl"]
    for _, v in sorted(by_day_pnl.items()):
        cum += v
        peak = max(peak, cum)
        mdd = max(mdd, peak - cum)
    gross = sum(r["payoff"] - r["price"] for r in primary)
    fee_sum = sum(r["fee"] for r in primary)
    overrides = os.path.join(data_dir, "event_overrides.json")
    n_over = None
    if os.path.exists(overrides):
        with open(overrides) as fh:
            ov = json.load(fh)
        n_over = len({r["event"] for r in primary if r["event"] in ov})
    out = {
        "n_markets_input": len(markets), "exclusions": dict(excl), "n_signals_all": len(recs),
        "n_primary_markets": len(primary), "primary": p_stat, "primary_stress": s_stat, "status": status,
        "power": ({"se": p_stat["se"], "mde_t_gate": Z_GATE * p_stat["se"],
                   "mde_80pct_power": (Z_GATE + 0.8416) * p_stat["se"]} if p_stat["se"] else None),
        "sensitivities": {
            "weekly_clusters": cluster_stat(event_level(primary, week_key), 1),
            "newey_west_daily_cluster_means": ({"lags7_se": nw_se(series_days, 7), "n_days": len(series_days),
                                                 "mean": sum(series_days) / len(series_days)} if len(series_days) > 8 else None),
            "spread_le_0.05": sens([r for r in primary if r["spread"] <= 0.05]),
            "final_volume_filter": sens([r for r in recs if (not r["early"]) and r["cat"] != "Sports"
                                         and r["final_vol"] is not None and r["final_vol"] >= FINAL_VOL_MIN]),
            "sports": sens([r for r in recs if r["cat"] == "Sports" and not r["early"]
                            and r["oi"] is not None and r["oi"] >= OI_MIN]),
            "early_close_capable": sens([r for r in recs if r["early"] and r["cat"] != "Sports"
                                         and r["oi"] is not None and r["oi"] >= OI_MIN]),
            "mirror_longshot_primary_universe": sens(longs),
        },
        "tail_structure": tail_structure(primary),
        "fee_share_of_gross": (fee_sum / gross if gross > 0 else None),
        "max_drawdown_cum_pnl_per_contract": mdd,
        "n_primary_events_with_fee_override": n_over,
        "dollars": {"pnl_per_contract_sum": sum(r["pnl"] for r in primary),
                    "return_per_capital_day": (sum(r["pnl"] for r in primary) / sum(r["capital_days"] for r in primary)
                                               if primary else None)},
    }
    by_month = defaultdict(list)
    for d, v, _ in rows:
        by_month[d[:7]].append(v)
    out["by_month_mean_net_event_level"] = {k: [sum(v) / len(v), len(v)] for k, v in sorted(by_month.items())}
    out["by_price_bucket"] = {}
    for lo, hi in ((0.80, 0.90), (0.90, 0.95), (0.95, 1.01)):
        xs = [r["net"] for r in primary if lo <= r["price"] < hi]
        out["by_price_bucket"][f"{lo:.2f}-{min(hi, 1.0):.2f}"] = [sum(xs) / len(xs) if xs else None, len(xs)]
    bc = defaultdict(list)
    for r_ in recs:
        if (not r_["early"]) and r_["oi"] is not None and r_["oi"] >= OI_MIN:
            bc[r_["cat"]].append(r_["net"])
    out["by_category_oi_filtered"] = {k: [sum(v) / len(v), len(v)] for k, v in sorted(bc.items())}
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    tmp = result_path + ".tmp"
    with open(tmp, "x") as f:
        json.dump(out, f, sort_keys=True, indent=1, default=str)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.link(tmp, result_path)
    finally:
        os.remove(tmp)
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
    print(json.dumps({"written": sys.argv[2]}))
