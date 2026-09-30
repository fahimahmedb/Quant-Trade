"""Step 9: queue competition diagnostics from historical maker records (outcome-independent of the newcomer).

For every eligible market (newcomer inputs, protocol side X) and the X floor bid level after T_DET:
  - maker wallets filled at the X floor (maker BUY X @floor or maker SELL notX @1-floor), notional by wallet;
  - time from T_DET to the first floor maker fill; share of floor-hit volume executed before t_p = T_DET + 60 s;
  - whether the filled makers already had floor fills on this market before T_DET (bids resting through the game);
  - seller side: distinct taker wallets hitting the floor.
Usage: python3 s09_competition.py <tag>
Output: data/competition_<tag>.json
"""
import collections
import gzip
import json
import os
import statistics as st
import sys

from common import DATA, RAW, read_jsonl_gz

EPS = 1e-9


def main():
    tag = sys.argv[1]
    inputs = [x for x in read_jsonl_gz(os.path.join(DATA, f"newcomer_inputs_{tag}.jsonl.gz"))
              if x.get("X") is not None and x["t_res"] > x["t_p"]]
    by_wallet = collections.Counter()
    first_fill_delay = []
    pre_tp_share_num = pre_tp_share_den = 0.0
    resting_through = collections.Counter()
    sellers = set()
    per_market_top_share = []
    n_markets_hits = 0
    wallet_markets = collections.defaultdict(set)
    for x in inputs:
        fn = os.path.join(RAW, "trades", f"{x['cid']}.json.gz")
        if not os.path.exists(fn):
            continue
        tr = json.load(gzip.open(fn, "rt"))
        X, floor, t_det, t_res = x["X"], x["floor"], x["t_det"], x["t_res"]
        pre_makers = set()
        mk = collections.Counter()
        first = None
        for ts, oi, side, p, size, wallet, tx, is_t in tr["trades"]:
            if oi is None:
                continue
            wep = p if oi == X else 1 - p
            at_floor = abs(wep - floor) < EPS
            if not at_floor:
                continue
            maker_bid = (not is_t) and ((oi == X and side == 0) or (oi != X and side == 1))
            taker_hit = is_t and ((oi == X and side == 1) or (oi != X and side == 0))
            if maker_bid and ts < t_det:
                pre_makers.add(wallet)
            if ts < t_det or ts >= t_res:
                continue
            if maker_bid:
                mk[wallet] += size * floor
                first = ts if first is None else min(first, ts)
            if taker_hit:
                sellers.add(wallet)
                pre_tp_share_den += size
                if ts < x["t_p"]:
                    pre_tp_share_num += size
        if mk:
            n_markets_hits += 1
            tot = sum(mk.values())
            per_market_top_share.append(max(mk.values()) / tot)
            for w, v in mk.items():
                by_wallet[w] += v
                wallet_markets[w].add(x["cid"])
                resting_through["resting_before_T_DET" if w in pre_makers else "new_after_T_DET"] += v
            first_fill_delay.append(first - t_det)
    tot = sum(by_wallet.values())
    top = by_wallet.most_common(20)
    res = {"markets_with_floor_maker_fills": n_markets_hits,
           "floor_maker_notional_usd": tot,
           "distinct_floor_makers": len(by_wallet),
           "top1_share": top[0][1] / tot if tot else None,
           "top5_share": sum(v for _, v in top[:5]) / tot if tot else None,
           "top10_share": sum(v for _, v in top[:10]) / tot if tot else None,
           "top10": [{"wallet": w, "notional_usd": round(v, 2), "share": v / tot, "markets": len(wallet_markets[w])}
                     for w, v in top[:10]],
           "median_top_maker_share_per_market": st.median(per_market_top_share) if per_market_top_share else None,
           "first_floor_fill_delay_s": {"median": st.median(first_fill_delay),
                                        "p10": sorted(first_fill_delay)[len(first_fill_delay) // 10],
                                        "share_within_60s": sum(1 for d in first_fill_delay if d < 60) / len(first_fill_delay)},
           "floor_hit_volume_share_before_t_p": pre_tp_share_num / pre_tp_share_den if pre_tp_share_den else None,
           "maker_notional_by_resting_status": dict(resting_through),
           "distinct_floor_sellers": len(sellers)}
    json.dump(res, open(os.path.join(DATA, f"competition_{tag}.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "top10"}, indent=1))
    for t in res["top10"][:5]:
        print(t)


if __name__ == "__main__":
    main()
