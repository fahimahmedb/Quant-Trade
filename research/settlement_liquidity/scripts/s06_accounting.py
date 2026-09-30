"""Step 6: fill accounting (rejection rule 1) + per-market newcomer inputs for S7.

For every VERIFIED market with trades cached by S5:
  qualifying fill = BUY record (maker or taker, either token) with price >= 0.998 and ts in [T_DET, T_RES).
  payout from final outcomePrices; taker fee = size*rate*(p(1-p))^exponent; makers 0; rebates ignored.
  net = size*(payout-price) - fee ; lock = T_RES - ts. Every loser kept.
Contrast (descriptive): same fills in [T_DET-2h, T_DET) ("in-play near-certain").
Newcomer inputs: side X (source det_side, else last-trade consensus before t_p), taker flow events after
t_p = T_DET + L that hit the X floor bid (F999) or trade at winning-equivalent <= floor - tick (Fsub), k.

Usage: python3 s06_accounting.py <tag> [L_seconds]
Outputs: data/fills_<tag>.csv.gz, data/fills_contrast_<tag>.csv.gz, data/newcomer_inputs_<tag>.jsonl.gz,
         data/accounting_summary_<tag>.json
"""
import collections
import csv
import gzip
import json
import os
import random
import statistics as st
import sys

from common import DATA, RAW, iso, parse_ts, write_jsonl_gz

EPS = 1e-9


def fee_of(m, p, size):
    fs = m.get("feeSchedule") or {}
    if not m.get("feesEnabled", True) and not fs:
        return 0.0
    rate = float(fs.get("rate") or 0.0)
    ex = float(fs.get("exponent") or 1.0)
    return size * rate * (p * (1 - p)) ** ex


def main():
    tag = sys.argv[1]
    L = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    det = {r["conditionId"]: r for r in csv.DictReader(gzip.open(os.path.join(DATA, f"determination_{tag}.csv.gz"), "rt"))}
    meta = {}
    for c in csv.DictReader(gzip.open(os.path.join(DATA, f"cohort_{tag}.csv.gz"), "rt")):
        if c["conditionId"] in det:
            meta[c["conditionId"]] = {"outcomes": c["outcomes"], "outcomePrices": c["outcomePrices"],
                                      "feeSchedule": {"rate": c["fee_rate"] or 0, "exponent": c["fee_exp"] or 1},
                                      "feesEnabled": c["feesEnabled"] not in ("False", "false", ""),
                                      "orderPriceMinTickSize": c["tick"], "question": c["question"]}
    fills, contrast, newc = [], [], []
    cov = collections.Counter()
    tdir = os.path.join(RAW, "trades")
    for cid, d in det.items():
        fn = os.path.join(tdir, f"{cid}.json.gz")
        if d["status"] != "VERIFIED" or not d["window_s"] or float(d["window_s"]) <= 0:
            continue
        if not os.path.exists(fn):
            cov["missing_trade_file"] += 1
            continue
        tr = json.load(gzip.open(fn, "rt"))
        m = meta[cid]
        payout = [float(x) for x in json.loads(m["outcomePrices"])]
        t_det, t_res = float(d["t_det"]), float(d["t_res"])
        disputes = int(d["disputes"] or 0)
        win_idx = max(range(len(payout)), key=lambda i: payout[i])
        reversal = ""
        if d["det_side"] != "":
            reversal = int(int(d["det_side"]) != win_idx) if max(payout) == 1.0 else "void_or_split"
        if not tr.get("cov_taker", True) or (tr.get("cov_all") is False):
            cov["coverage_incomplete"] += 1
        recs = tr["trades"]
        for ts, oi, side, p, size, wallet, tx, is_t in recs:
            if side != 0 or p < 0.998 - EPS or oi is None:
                continue
            fee = fee_of(m, p, size) if is_t else 0.0
            row = {"cid": cid, "family": d["family"].split(":")[0], "smt": d["smt"], "ts": ts, "outcome": oi,
                   "price": p, "size": size, "taker": is_t, "wallet": wallet, "payout": payout[oi], "fee": round(fee, 8),
                   "net": size * (payout[oi] - p) - fee, "notional": size * p + fee, "lock_s": t_res - ts,
                   "disputes": disputes, "reversal": reversal, "win": int(payout[oi] == 1.0)}
            if t_det <= ts < t_res:
                fills.append(row)
            elif t_det - 7200 <= ts < t_det:
                contrast.append(row)
        # ---- newcomer inputs ----
        tick = float(m.get("orderPriceMinTickSize") or 0.01)
        if any(r[3] >= 0.991 for r in recs):
            tick = min(tick, 0.001)
        floor = 1 - tick
        t_p = t_det + L
        xs = int(d["det_side"]) if d["det_side"] != "" else None
        xc, cons_age = None, None
        prev = [r for r in recs if r[7] == 1 and r[0] < t_p]
        if prev:
            last = max(prev, key=lambda r: r[0])
            cons_age = t_p - last[0]
            if last[3] >= 0.99 - EPS:
                xc = last[1]
            elif last[3] <= 0.01 + EPS:
                xc = 1 - last[1]
        # protocol rule: source side, else consensus
        X, xm = (xs, "source") if xs is not None else ((xc, "consensus") if xc is not None else (None, ""))
        if X is None:
            newc.append({"cid": cid, "family": d["family"].split(":")[0], "t_p": t_p, "t_res": t_res, "X": None,
                         "x_source": xs, "x_consensus": xc})
            continue
        ev = []
        makers = set()
        for ts, oi, side, p, size, wallet, tx, is_t in sorted(recs, key=lambda r: r[0]):
            if ts < t_p or ts >= t_res or oi is None:
                continue
            wep = p if oi == X else 1 - p
            if is_t:
                if wep <= floor - tick + EPS:
                    ev.append([ts, 0, size])  # sub-floor: X floor bid level empty -> newcomer first
                elif abs(wep - floor) < EPS and ((oi == X and side == 1) or (oi != X and side == 0)):
                    ev.append([ts, 1, size])  # hits the X floor bid level
            else:
                if abs(wep - floor) < EPS and ((oi == X and side == 0) or (oi != X and side == 1)):
                    makers.add(wallet)
        newc.append({"cid": cid, "family": d["family"].split(":")[0], "smt": d["smt"], "t_det": t_det, "t_p": t_p,
                     "t_res": t_res, "X": X, "x_method": xm, "x_source": xs, "x_consensus": xc, "cons_age_s": cons_age,
                     "payout": payout, "payout_X": payout[X], "floor": floor, "k": len(makers),
                     "disputes": disputes, "ev": ev})
    cols = ["cid", "family", "smt", "ts", "outcome", "price", "size", "taker", "wallet", "payout", "fee", "net",
            "notional", "lock_s", "disputes", "reversal", "win"]
    for name, rows in (("fills", fills), ("fills_contrast", contrast)):
        with gzip.open(os.path.join(DATA, f"{name}_{tag}.csv.gz"), "wt", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow({**r, "net": round(r["net"], 6), "notional": round(r["notional"], 6)})
    write_jsonl_gz(os.path.join(DATA, f"newcomer_inputs_{tag}.jsonl.gz"), newc)

    def agg(rows):
        if not rows:
            return {"n": 0}
        notl = sum(r["notional"] for r in rows)
        net = sum(r["net"] for r in rows)
        los = [r for r in rows if r["net"] < 0 and r["payout"] < r["price"]]
        by_m = collections.defaultdict(lambda: [0.0, 0.0])
        for r in rows:
            by_m[r["cid"]][0] += r["net"]
            by_m[r["cid"]][1] += r["notional"]
        keys = list(by_m)
        rnd = random.Random(20260929)
        boots = []
        for _ in range(1000):
            s = [by_m[keys[rnd.randrange(len(keys))]] for _ in keys]
            boots.append(sum(x[0] for x in s) / max(sum(x[1] for x in s), 1e-9))
        boots.sort()
        return {"n_fills": len(rows), "n_markets": len(by_m), "notional": notl,
                "gross_win": sum(r["size"] * (r["payout"] - r["price"]) for r in rows if r["payout"] >= r["price"]),
                "loss": sum(r["size"] * (r["price"] - r["payout"]) for r in rows if r["payout"] < r["price"]),
                "fees": sum(r["fee"] for r in rows), "net": net, "net_per_notional": net / notl if notl else None,
                "ci95_net_per_notional": [boots[25], boots[974]],
                "losing_fills": len(los), "losing_markets": len({r["cid"] for r in los}),
                "median_lock_h": st.median(r["lock_s"] for r in rows) / 3600,
                "p90_lock_h": sorted(r["lock_s"] for r in rows)[int(0.9 * len(rows))] / 3600,
                "distinct_buyers": len({r["wallet"] for r in rows}),
                "maker_share_notional": sum(r["notional"] for r in rows if not r["taker"]) / notl if notl else None,
                "disputed_markets": len({r["cid"] for r in rows if r["disputes"] > 0}),
                "reversal_fills": sum(1 for r in rows if r["reversal"] == 1)}

    summ = {"L_seconds": L, "coverage": dict(cov), "primary_all_ge_0998": agg(fills),
            "at_0998": agg([r for r in fills if abs(r["price"] - 0.998) < EPS]),
            "at_0999": agg([r for r in fills if abs(r["price"] - 0.999) < EPS]),
            "maker_only": agg([r for r in fills if not r["taker"]]), "taker_only": agg([r for r in fills if r["taker"]]),
            "by_family": {f: agg([r for r in fills if r["family"] == f]) for f in sorted({r["family"] for r in fills})},
            "contrast_pre_det_2h": agg(contrast),
            "losing_fill_list": [{**r, "ts_iso": iso(r["ts"])} for r in fills if r["payout"] < r["price"]][:500]}
    json.dump(summ, open(os.path.join(DATA, f"accounting_summary_{tag}.json"), "w"), indent=1, default=str)
    p = summ["primary_all_ge_0998"]
    print(json.dumps({k: v for k, v in p.items()}, default=str, indent=1))
    print("contrast", json.dumps(summ["contrast_pre_det_2h"], default=str))
    print("coverage", dict(cov))


if __name__ == "__main__":
    main()
