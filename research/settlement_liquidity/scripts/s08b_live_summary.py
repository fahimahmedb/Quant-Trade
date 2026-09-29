"""Step 8b: summarize the read-only live queue monitor into a FIFO shadow-bid experiment.

For each tracked market that has closed:
  t_p = t_seen_final + 60 s ("timed" sample: final first observed by the monitor during its run), or the
        first snapshot for games already final when the monitor started ("late" sample);
  X   = token whose best bid >= 0.99 in the first snapshot at/after t_p (skip if ambiguous);
  Q0  = depth at the X floor = X bids at 0.999 + not-X asks at 0.001 (shares), first snapshot >= t_p;
  flows after t_p from data-api taker records: hits (sell X@0.999 / buy notX@0.001) and sub-floor (wep<=0.998).
FIFO shadow bid of S=100 USDC:
  conservative: queue ahead only shrinks by hits (no cancellation credit);
  optimistic  : queue ahead also capped by observed depth at each snapshot (all cancellations ahead of us).
Usage: python3 s08b_live_summary.py
Output: data/live_queue_summary.json, data/live_queue_markets.csv.gz
"""
import collections
import csv
import gzip
import json
import os
import statistics as st

from common import DATA, RAW, get

LIVE = os.path.join(RAW, "live")
EPS = 1e-9


def trades(cid):
    fn = os.path.join(LIVE, f"trades_{cid}.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    out = []
    for off in range(0, 10001, 1000):
        d = get(f"https://data-api.polymarket.com/trades?market={cid}&limit=1000&offset={off}&takerOnly=true")
        if not d:
            break
        out += d
        if len(d) < 1000:
            break
    json.dump(out, open(fn, "w"))
    return out


def main(S_usd=100.0):
    meta, closed = {}, {}
    for l in open(os.path.join(LIVE, "tracked.jsonl")):
        r = json.loads(l)
        if "closed_seen" in r:
            closed[r["conditionId"]] = r
        else:
            meta.setdefault(r["conditionId"], r)
    snaps = collections.defaultdict(list)
    for l in open(os.path.join(LIVE, "books.jsonl")):
        r = json.loads(l)
        if r.get("gone"):
            continue
        snaps[r["c"]].append(r)
    rows = []
    for cid, m in meta.items():
        if cid not in closed or cid not in snaps:
            continue
        timed = not m.get("first_poll")
        s_all = sorted(snaps[cid], key=lambda r: r["ts"])
        t_p = (m["t_seen_final"] + 60) if timed else s_all[0]["ts"]
        after = [r for r in s_all if r["ts"] >= t_p]
        if not after:
            continue
        t0 = after[0]["ts"]
        first = {r["i"]: r for r in after if r["ts"] - t0 < 15}
        if len(first) < 2:
            continue
        hi = [i for i, r in first.items() if r["bb"] is not None and r["bb"] >= 0.99]
        if len(hi) != 1:
            continue
        X = hi[0]

        def depth(snapgroup):
            dx = sum(sz for p, sz in (snapgroup.get(X, {}).get("hb") or []) if p >= 0.999 - EPS)
            dn = sum(sz for p, sz in (snapgroup.get(1 - X, {}).get("la") or []) if p <= 0.001 + EPS)
            return dx, dn
        q_bid, q_mirror = depth(first)
        Q0 = q_bid + q_mirror
        # depth path (one value per snapshot time)
        groups = collections.defaultdict(dict)
        for r in after:
            groups[round(r["ts"])][r["i"]] = r
        path = sorted((t, sum(depth(g))) for t, g in groups.items() if len(g) == 2)
        t_res = closed[cid].get("closedTime")
        tr = trades(cid)
        ev = []
        for x in tr:
            ts = x["timestamp"]
            if ts < t_p:
                continue
            oi = x.get("outcomeIndex")
            p = float(x["price"])
            wep = p if oi == X else 1 - p
            side = x["side"]
            if wep <= 0.998 + EPS:
                ev.append((ts, 0, float(x["size"])))
            elif abs(wep - 0.999) < EPS and ((oi == X and side == "SELL") or (oi != X and side == "BUY")):
                ev.append((ts, 1, float(x["size"])))
        ev.sort()
        S = S_usd / 0.999
        res = {}
        for mode in ("conservative", "optimistic"):
            ahead, got = Q0, 0.0
            pi = 0
            for ts, kind, z in ev:
                if mode == "optimistic":
                    while pi < len(path) and path[pi][0] <= ts:
                        ahead = min(ahead, path[pi][1])
                        pi += 1
                if got >= S:
                    break
                if kind == 0:
                    got = min(S, got + z)
                else:
                    if ahead >= z:
                        ahead -= z
                    else:
                        got = min(S, got + z - ahead)
                        ahead = 0.0
            res[mode] = got
        H = sum(z for _, k, z in ev if k == 1)
        Sub = sum(z for _, k, z in ev if k == 0)
        rows.append({"cid": cid, "event": m.get("event"), "smt": m.get("smt"), "timed": int(timed), "X": X,
                     "t_p": t_p, "Q0_shares": Q0, "Q0_bid": q_bid, "Q0_mirror": q_mirror, "hits": H, "sub": Sub,
                     "fill_cons": res["conservative"], "fill_opt": res["optimistic"], "S": S,
                     "n_snaps": len(path), "closedTime": t_res})
    out = os.path.join(DATA, "live_queue_markets.csv.gz")
    if rows:
        with gzip.open(out, "wt", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    def summ(rs):
        if not rs:
            return {"n": 0}
        posted = sum(r["S"] for r in rs)
        H = sum(r["hits"] for r in rs)
        return {"n": len(rs), "fill_share_conservative": sum(r["fill_cons"] for r in rs) / posted,
                "fill_share_optimistic": sum(r["fill_opt"] for r in rs) / posted,
                "fill_prob_conservative": sum(1 for r in rs if r["fill_cons"] > 0) / len(rs),
                "fill_prob_optimistic": sum(1 for r in rs if r["fill_opt"] > 0) / len(rs),
                "median_Q0_shares": st.median(r["Q0_shares"] for r in rs),
                "p90_Q0_shares": sorted(r["Q0_shares"] for r in rs)[int(0.9 * len(rs))],
                "median_hits_shares": st.median(r["hits"] for r in rs),
                "share_markets_Q0_gt_hits": sum(1 for r in rs if r["Q0_shares"] > r["hits"]) / len(rs),
                "sum_hits": H, "sum_sub": sum(r["sub"] for r in rs),
                "hit_capture_ratio_conservative": (sum(max(0.0, r["fill_cons"] - min(r["S"], r["sub"])) for r in rs) / H) if H else None}
    timed = [r for r in rows if r["timed"]]
    late = [r for r in rows if not r["timed"]]
    s = {"timed": summ(timed), "late": summ(late), "all": summ(rows), "n_markets_timed": len(timed),
         "central_floor_hit_capture_ratio": summ(timed).get("hit_capture_ratio_conservative") if len(timed) >= 20 else None,
         "note": "READ-ONLY public book snapshots every ~20 s; queue position of a hypothetical order simulated; no orders placed."}
    json.dump(s, open(os.path.join(DATA, "live_queue_summary.json"), "w"), indent=1)
    print(json.dumps(s, indent=1))


if __name__ == "__main__":
    main()
