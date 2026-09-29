"""Step 5: fetch trades around the settlement window for every VERIFIED market with a non-empty window.

For each market: data-api /trades?market=<cid>, newest first, pages of 1000 (offset cap 10,000):
  1) takerOnly=true back to t_from = T_DET - PRE (default 2 h, for the in-play contrast); if no taker
     record falls in [T_DET, T_RES) the market has no fills in its window and the maker query is skipped;
  2) takerOnly=false back to t_from; maker records = multiset difference.
Compact record: [ts, outcomeIndex, side(0=BUY,1=SELL), price, size, wallet, tx, is_taker]
Cache: data/raw/trades/<cid>.json.gz (resumable; existing files are skipped).
Usage: python3 s05_fetch_trades.py <tag> [threads] [pre_seconds]
"""
import collections
import concurrent.futures as cf
import csv
import gzip
import json
import os
import sys
import time

from common import DATA, RAW, get

CACHE = os.path.join(RAW, "trades")
os.makedirs(CACHE, exist_ok=True)


def pages(cid, taker_only, t_from):
    out = []
    covered = False
    for off in range(0, 10001, 1000):
        d = get(f"https://data-api.polymarket.com/trades?market={cid}&limit=1000&offset={off}"
                f"&takerOnly={'true' if taker_only else 'false'}")
        if not d:
            covered = True
            break
        out += d
        if min(x["timestamp"] for x in d) < t_from or len(d) < 1000:
            covered = True
            break
    return out, covered


def key(x):
    return (x["transactionHash"], x["proxyWallet"], x["side"], x["asset"], x["price"], x["size"], x["timestamp"])


def fetch(row, pre):
    cid = row["conditionId"]
    fn = os.path.join(CACHE, f"{cid}.json.gz")
    if os.path.exists(fn):
        return "cached"
    t_det, t_res = float(row["t_det"]), float(row["t_res"])
    t_from = t_det - pre
    tk, cov_t = pages(cid, True, t_from)
    in_win = [x for x in tk if t_det <= x["timestamp"] < t_res]
    rec = {"cid": cid, "t_det": t_det, "t_res": t_res, "t_from": t_from, "cov_taker": cov_t,
           "n_taker_window": len(in_win), "fetched": time.time()}
    recs = []
    if in_win:
        al, cov_a = pages(cid, False, t_from)
        rec["cov_all"] = cov_a
        ms = collections.Counter(key(x) for x in tk)
        for x in al:
            if x["timestamp"] < t_from:
                continue
            k = key(x)
            is_t = 1 if ms[k] > 0 else 0
            if is_t:
                ms[k] -= 1
            recs.append([x["timestamp"], x.get("outcomeIndex"), 0 if x["side"] == "BUY" else 1, float(x["price"]),
                         float(x["size"]), x["proxyWallet"], x["transactionHash"], is_t])
        rec["unmatched_taker"] = sum(v for v in ms.values() if v > 0 and True)
    else:
        for x in tk:
            if x["timestamp"] < t_from:
                continue
            recs.append([x["timestamp"], x.get("outcomeIndex"), 0 if x["side"] == "BUY" else 1, float(x["price"]),
                         float(x["size"]), x["proxyWallet"], x["transactionHash"], 1])
        rec["taker_only_file"] = True
    rec["trades"] = recs
    with gzip.open(fn + ".tmp", "wt") as f:
        json.dump(rec, f, separators=(",", ":"))
    os.replace(fn + ".tmp", fn)
    return "ok"


def main():
    tag = sys.argv[1]
    threads = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    pre = float(sys.argv[3]) if len(sys.argv) > 3 else 7200
    rows = list(csv.DictReader(gzip.open(os.path.join(DATA, f"determination_{tag}.csv.gz"), "rt")))
    todo = [r for r in rows if r["status"] == "VERIFIED" and r["window_s"] and float(r["window_s"]) > 0]
    todo.sort(key=lambda r: -float(r["t_res"]))
    print("markets to fetch", len(todo), flush=True)
    t0 = time.time()
    done = collections.Counter()
    with cf.ThreadPoolExecutor(threads) as ex:
        futs = {ex.submit(fetch, r, pre): r for r in todo}
        for i, f in enumerate(cf.as_completed(futs)):
            try:
                done[f.result()] += 1
            except Exception as e:
                done["err"] += 1
                print("err", futs[f]["conditionId"], str(e)[:120], flush=True)
            if i % 500 == 0:
                print(i, dict(done), "%.0fs" % (time.time() - t0), flush=True)
    print("done", dict(done))


if __name__ == "__main__":
    main()
