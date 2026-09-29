"""Step 7: newcomer access (partial identification) + capital economics + weekly decay.

Input: data/newcomer_inputs_<tag>.jsonl.gz (S6), data/fills_<tag>.csv.gz, data/determination_<tag>.csv.gz,
       optional data/live_queue_summary.json (S8) for the live-calibrated central ratio.
Fill models per market for a resting BUY X at the floor posted at t_p (see protocol §5):
  LB      = min(S, cum sub-floor taker flow)                    (back of unobserved queue, no cancel credit)
  CENTRAL = min(S, sub-floor + floor-hits / (k+1))               (equal share with k active floor makers)
  UB      = min(S, sub-floor + floor-hits)                       (first in queue)
Capital sims: EUR 100/500/1000/5000 at ECB EUR/USD 2026-09-28 = 1.1378; bid reserves S*floor from t_p to
T_RES; S = min(free, frac*capital), frac 0.25 (primary) and 1.0; min order 5 shares.
Usage: python3 s07_newcomer.py <tag>
Output: data/newcomer_results_<tag>.json
"""
import collections
import csv
import datetime as dt
import gzip
import json
import os
import statistics as st
import sys

from common import DATA, PRIMARY_END, PRIMARY_START, read_jsonl_gz

EURUSD = 1.1378  # ECB reference rate 2026-09-28
MODELS = ("LB", "CENTRAL", "UB")


def fill(ev, k, shares, model, ratio=None):
    got = 0.0
    for ts, kind, size in ev:
        if got >= shares:
            break
        if kind == 0:
            add = size
        elif model == "LB":
            add = 0.0
        elif model == "UB":
            add = size
        elif ratio is not None:
            add = size * ratio
        else:
            add = size / (k + 1)
        got = min(shares, got + add)
    return got


def reference(inputs, s_usd=100.0, ratio=None):
    out = {}
    elig = [x for x in inputs if x.get("X") is not None and x["t_res"] > x["t_p"]]
    for model in MODELS:
        posted = filled = pnl = 0.0
        n_any = 0
        flow_tot = 0.0
        losses = 0
        for x in elig:
            sh = s_usd / x["floor"]
            f = fill(x["ev"], x["k"], sh, model, ratio if model == "CENTRAL" else None)
            posted += sh
            filled += f
            n_any += f > 0
            flow_tot += sum(e[2] for e in x["ev"])
            p = f * (x["payout_X"] - x["floor"])
            pnl += p
            losses += p < 0
        out[model] = {"eligible_markets": len(elig), "fill_share": filled / posted if posted else None,
                      "fill_probability": n_any / len(elig) if elig else None, "filled_shares": filled,
                      "flow_share": filled / flow_tot if flow_tot else None, "pnl_usd": pnl,
                      "losing_markets": losses}
    return out


def capital_sim(inputs, cap_eur, frac, model, ratio=None):
    cap = cap_eur * EURUSD
    elig = sorted([x for x in inputs if x.get("X") is not None and x["t_res"] > x["t_p"]], key=lambda x: x["t_p"])
    free = cap
    open_pos = []  # (t_res, locked, pnl)
    pnl_tot = 0.0
    n_post = n_fill = 0
    worst = 0.0
    locked_time = 0.0
    fills_usd = 0.0
    t0, t1 = elig[0]["t_p"], max(x["t_res"] for x in elig)
    for x in elig:
        still = []
        for t_res, locked, p in open_pos:
            if t_res <= x["t_p"]:
                free += locked + p
            else:
                still.append((t_res, locked, p))
        open_pos = still
        post = min(free, frac * cap)
        sh = post / x["floor"]
        if sh < 5:
            continue
        f = fill(x["ev"], x["k"], sh, model, ratio if model == "CENTRAL" else None)
        p = f * (x["payout_X"] - x["floor"])
        n_post += 1
        n_fill += f > 0
        fills_usd += f * x["floor"]
        worst = min(worst, p)
        pnl_tot += p
        free -= post
        locked_time += post * (x["t_res"] - x["t_p"])
        open_pos.append((x["t_res"], post, p))
    days = (PRIMARY_END - PRIMARY_START).total_seconds() / 86400  # fixed 30-day window, not data span
    return {"capital_eur": cap_eur, "frac": frac, "model": model, "net_usd": pnl_tot, "net_eur": pnl_tot / EURUSD,
            "net_eur_per_30d": pnl_tot / EURUSD * 30 / days, "return_on_capital_30d": pnl_tot / cap * 30 / days,
            "markets_posted": n_post, "markets_filled": n_fill, "filled_usd": fills_usd,
            "avg_utilization": locked_time / (cap * (t1 - t0)), "worst_market_usd": worst, "days": days}


def main():
    tag = sys.argv[1]
    inputs = list(read_jsonl_gz(os.path.join(DATA, f"newcomer_inputs_{tag}.jsonl.gz")))
    ratio = None
    lq = os.path.join(DATA, "live_queue_summary.json")
    live = json.load(open(lq)) if os.path.exists(lq) else None
    if live and live.get("n_markets_timed", 0) >= 20 and live.get("central_floor_hit_capture_ratio") is not None:
        ratio = live["central_floor_hit_capture_ratio"]
    res = {"n_inputs": len(inputs), "x_method": dict(collections.Counter(x.get("x_method") or "none" for x in inputs)),
           "eurusd": EURUSD, "live_ratio_used": ratio}
    res["reference_S100"] = reference(inputs, 100.0, ratio)
    res["reference_S1000"] = reference(inputs, 1000.0, ratio)
    res["reference_S100_source_side_only"] = reference([x for x in inputs if x.get("x_method") == "source"], 100.0, ratio)
    res["reference_S100_by_family"] = {f: reference([x for x in inputs if x["family"] == f], 100.0, ratio)
                                       for f in sorted({x["family"] for x in inputs})}
    elig = [x for x in inputs if x.get("X") is not None and x["t_res"] > x["t_p"]]
    res["eligible_time_h"] = {"median": st.median((x["t_res"] - x["t_p"]) / 3600 for x in elig),
                              "p90": sorted((x["t_res"] - x["t_p"]) / 3600 for x in elig)[int(0.9 * len(elig))]}
    res["flows_usd"] = {"F999_hits": sum(e[2] * x["floor"] for x in elig for e in x["ev"] if e[1] == 1),
                        "Fsub": sum(e[2] * x["floor"] for x in elig for e in x["ev"] if e[1] == 0),
                        "markets_with_any_Fsub": sum(1 for x in elig if any(e[1] == 0 for e in x["ev"])),
                        "markets_with_any_hit": sum(1 for x in elig if any(e[1] == 1 for e in x["ev"])),
                        "median_k_given_hits": st.median([x["k"] for x in elig if any(e[1] == 1 for e in x["ev"])] or [0])}
    res["capital"] = [capital_sim(inputs, c, fr, mdl, ratio) for c in (100, 500, 1000, 5000) for fr in (0.25, 1.0)
                      for mdl in MODELS]
    # weekly decay
    fills = list(csv.DictReader(gzip.open(os.path.join(DATA, f"fills_{tag}.csv.gz"), "rt")))
    det = {r["conditionId"]: r for r in csv.DictReader(gzip.open(os.path.join(DATA, f"determination_{tag}.csv.gz"), "rt"))}
    wk = lambda t: dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime("%G-W%V")
    weeks = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in fills:
        weeks[wk(det[f["cid"]]["t_res"])]["fills"].append(f)
    for x in elig:
        weeks[wk(x["t_res"])]["elig"].append(x)
    for cid, d in det.items():
        if d["status"] == "VERIFIED" and d["t_res"]:
            weeks[wk(d["t_res"])]["verified"].append(d)
    dec = {}
    for w in sorted(weeks):
        F, E, V = weeks[w]["fills"], weeks[w]["elig"], weeks[w]["verified"]
        notl = sum(float(f["notional"]) for f in F)
        win = [f for f in F if f["win"] == "1"]
        dec[w] = {"verified_markets": len(V), "markets_with_fills": len({f["cid"] for f in F}), "fills": len(F),
                  "notional_usd": notl, "net_usd": sum(float(f["net"]) for f in F),
                  "net_per_notional": sum(float(f["net"]) for f in F) / notl if notl else None,
                  "gross_premium_winners": (sum(float(f["size"]) * (1 - float(f["price"])) for f in win) /
                                            max(sum(float(f["notional"]) for f in win), 1e-9)),
                  "losing_fills": sum(1 for f in F if float(f["payout"]) < float(f["price"])),
                  "median_lock_h": st.median(float(f["lock_s"]) for f in F) / 3600 if F else None,
                  "disputed_verified_markets": sum(1 for d in V if int(d["disputes"] or 0) > 0),
                  "distinct_buyers": len({f["wallet"] for f in F}),
                  "median_k": st.median([x["k"] for x in E]) if E else None,
                  "LB_flow_usd": sum(e[2] * x["floor"] for x in E for e in x["ev"] if e[1] == 0),
                  "UB_flow_usd": sum(e[2] * x["floor"] for x in E for e in x["ev"])}
    res["weekly"] = dec
    json.dump(res, open(os.path.join(DATA, f"newcomer_results_{tag}.json"), "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("reference_S100", "flows_usd", "eligible_time_h")}, indent=1))
    for c in res["capital"]:
        if c["frac"] == 0.25:
            print(c["capital_eur"], c["model"], "net_eur/30d %.2f" % c["net_eur_per_30d"], "posted", c["markets_posted"],
                  "filled", c["markets_filled"], "util %.3f" % c["avg_utilization"], "worst %.2f" % c["worst_market_usd"])


if __name__ == "__main__":
    main()
