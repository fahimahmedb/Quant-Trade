"""Agent 6 -- bounded Polymarket reward / maker-rebate daily pool series (on-chain, public RPC).
Block numbers are interpolated piecewise between VERIFIED anchors (blocks whose timestamps were read
on-chain during this mission); each window [D-3h, D+4h] is then checked against real block timestamps
and must cover D 00:00-01:15 UTC (all observed payouts happen 00:00-01:00), else the date is UNKNOWN.
Sums all transfers from the known reward payers and rebate payers (USDC.e and pUSD) in the window.
(Attempt 1 used a binary search whose bracket failed before April; its output is kept only as
decay_series_attempt1_INVALID.log.)  Run from agent6_data/.  Output: decay_series.json
"""
import json, calendar, time, statistics, sys
sys.path.insert(0, "../agent6_scripts")
import rpc
rpc.RPCS = ["https://polygon-bor-rpc.publicnode.com", "https://polygon.drpc.org"]
from rpc import call, TRANSFER, PUSD, pad, block_ts
from collections import Counter

USDCE = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
REW = ["0xc288480574783bd7615170660d71753378159c47", "0xf7cd89be08af4d4d6b1522852ced49fc10169f64",
       "0x2c2795ea295d5eb51f9121b728ed2ea4e936a709", "0xdd8db71ce3be8d71ff148b2163d64da181a29e8b"]
REB = ["0x3a9418b2651c8164db5ebc56f12008137865e0f7", "0xfdb1b8dc7f5789a0c9a398026585b8b10fba5507"]
T = lambda *a: calendar.timegm(a)
ANCHORS = [(84939882, T(2026, 3, 31, 23, 30, 0)), (85544678, T(2026, 4, 14, 23, 30, 0)),
           (89438137, T(2026, 6, 30, 23, 30, 0)), (94620840, T(2026, 9, 28, 23, 0, 0)),
           (94662513, T(2026, 9, 29, 16, 21, 50))]


def est_block(ts):
    for (b0, t0), (b1, t1) in zip(ANCHORS, ANCHORS[1:]):
        if t0 <= ts <= t1:
            return int(b0 + (ts - t0) * (b1 - b0) / (t1 - t0)), (t1 - t0) / (b1 - b0)
    raise ValueError("date outside anchors")


def retry(fn, n=6):
    for i in range(n):
        try:
            return fn()
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError("retries exhausted")


def logs(tok, payers, b0, b1, step=4000):
    out = []; b = b0
    while b <= b1:
        e = min(b + step, b1)
        out += retry(lambda: call("eth_getLogs", [{"address": tok, "topics": [TRANSFER, [pad(p) for p in payers]],
                                                   "fromBlock": hex(b), "toBlock": hex(e)}], tries=2))
        b = e + 1
    return out


if __name__ == "__main__":
    dates = [(2026, 4, 1), (2026, 4, 15)] + [(2026, m, d) for m in (5, 6, 7, 8, 9) for d in (1, 15)] + [(2026, 9, 29)]
    only = sys.argv[1:]
    try: out = json.load(open("decay_series.json"))
    except Exception: out = {}
    for (y, m, d) in dates:
        if only and "%d-%02d-%02d" % (y, m, d) not in only: continue
        k = "%d-%02d-%02d" % (y, m, d)
        try:
            ts = T(y, m, d, 0, 0, 0)
            e, spb = est_block(ts)
            for _ in range(5):  # correct the interpolation with real block timestamps
                err = retry(lambda: block_ts(e)) - ts
                if abs(err) < 600: break
                e = int(e - err / spb)
            b0, b1 = int(e - 3 * 3600 / spb), int(e + 4 * 3600 / spb)
            t0, t1 = retry(lambda: block_ts(b0)), retry(lambda: block_ts(b1))
            if not (ts - 5 * 3600 <= t0 <= ts and ts + 4500 <= t1 <= ts + 6 * 3600):
                raise RuntimeError(f"window {t0 - ts:+d}s..{t1 - ts:+d}s does not cover payout hour")
            res = {"blocks": [b0, b1], "window_s_rel_midnight": [t0 - ts, t1 - ts]}
            for name, payers in [("reward", REW), ("rebate", REB)]:
                L = logs(USDCE, payers, b0, b1) + logs(PUSD, payers, b0, b1)
                a = Counter()
                for l in L: a["0x" + l["topics"][2][-40:]] += int(l["data"], 16) / 1e6
                v = sorted(a.values(), reverse=True); tot = sum(v)
                res[name] = dict(n=len(v), total=round(tot), median=round(statistics.median(v), 2) if v else None,
                                 top10=round(100 * sum(v[:10]) / tot, 1) if tot else None,
                                 payers=dict(Counter("0x" + l["topics"][1][-40:] for l in L)))
        except Exception as ex:
            res = {"UNKNOWN": str(ex)[:200]}
        out[k] = res
        json.dump(out, open("decay_series.json", "w"), indent=1)
        if "UNKNOWN" in res: print(k, "UNKNOWN", res["UNKNOWN"], flush=True)
        else: print(k, "REWARD n=%(n)s $%(total)s med=%(median)s top10=%(top10)s%%" % res["reward"],
                    "| REBATE n=%(n)s $%(total)s med=%(median)s top10=%(top10)s%%" % res["rebate"], flush=True)
