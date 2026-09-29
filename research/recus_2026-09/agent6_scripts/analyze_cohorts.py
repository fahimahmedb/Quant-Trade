"""Agent 6 -- analysis of the pre-declared Polymarket reward cohorts (results_A/B.jsonl).
Run from research/recus_2026-09/agent6_data:  python3 ../agent6_scripts/analyze_cohorts.py
Definitions (fixed at checkpoint cf9db0b, unchanged here):
  trading = user-pnl(D0+90d) - user-pnl(D0)   (validated to exclude REWARD / MAKER_REBATE)
  net     = trading + REWARD + MAKER_REBATE paid in (D0+6h, D0+90d+6h]
  month k = [D0+30k, D0+30(k+1)) for user-pnl marks; subsidy months aligned with +6h offset.
No wallet is excluded on P&L. Only rows without any user-pnl series are unusable (reported).
Flags (descriptive only, never used to drop wallets):
  F_START  user-pnl series has no point <= D0 (start P&L taken as 0)
  F_VOLCAP window TRADE volume hit the 5,000-record cap (volume is a lower bound)
  F_CASH0  cash_d0 (USDC.e + pUSD balance at D0 block) < $10 or unavailable
  F_LB     leaderboard ALL pnl vs user-pnl last value differ by > max($1,000, 20% of larger abs)
"""
import json, statistics as st, sys

FRAME = {"A": {"T1": 552, "T2": 2496, "T3": 938, "T4": 194},
         "B": {"T1": 66, "T2": 2181, "T3": 820, "T4": 192}}
TIERS = ["T1", "T2", "T3", "T4"]


def q(v, p):
    v = sorted(v)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p; f = int(k); c = min(f + 1, len(v) - 1)
    return v[f] + (v[c] - v[f]) * (k - f)


def load(c):
    L = [json.loads(l) for l in open(f"results_{c}.jsonl")]
    return [r for r in L if "net" in r], [r for r in L if "net" not in r]


def flags(r):
    f = []
    if r.get("pnl_start_missing"): f.append("F_START")
    if r.get("vol_status") == "capped": f.append("F_VOLCAP")
    if r.get("cash_d0") is None or r["cash_d0"] < 10: f.append("F_CASH0")
    a, b = r.get("lb_all_pnl"), r.get("pnl_last")
    if a is not None and b is not None and abs(a - b) > max(1000, 0.2 * max(abs(a), abs(b))): f.append("F_LB")
    return f


def monthly(r):
    m = r["pnl_marks"]; base = r["pnl_start"]
    marks = [base] + [x if x is not None else None for x in m[1:]]
    out = []
    for k in range(3):
        a, b = marks[k], marks[k + 1]
        tr = (b - a) if (a is not None and b is not None) else None
        out.append(None if tr is None else tr + r["rewards_m"][k] + r["rebates_m"][k])
    return out


def pct(n, d): return f"{n}/{d} ({(n / d if d else 0):.0%})"


def block(R, label):
    n = len(R)
    tr = [r["trading"] for r in R]; rw = [r["rewards"] for r in R]; rb = [r["rebates"] for r in R]
    nt = [r["net"] for r in R]
    pos = sorted([x for x in nt if x > 0], reverse=True); tp = sum(pos) or 1
    print(f"\n{label}: N usable = {n}")
    print(f"   net>0 {pct(sum(x > 0 for x in nt), n)} | trading>0 {pct(sum(x > 0 for x in tr), n)}"
          f" | trading+rewards>0 {pct(sum(r['trading'] + r['rewards'] > 0 for r in R), n)}"
          f" | trading+rebates>0 {pct(sum(r['trading'] + r['rebates'] > 0 for r in R), n)}")
    print(f"   NET      med {st.median(nt):10.0f}  mean {st.mean(nt):11.0f}  p25 {q(nt, .25):9.0f}  p75 {q(nt, .75):9.0f}")
    print(f"   TRADING  med {st.median(tr):10.0f}  mean {st.mean(tr):11.0f}  p25 {q(tr, .25):9.0f}  p75 {q(tr, .75):9.0f}")
    print(f"   REWARDS  med {st.median(rw):10.1f}  mean {st.mean(rw):11.0f}   | REBATES med {st.median(rb):8.1f}  mean {st.mean(rb):9.0f}")
    print(f"   SUMS     trading {sum(tr):12.0f} + rewards {sum(rw):10.0f} + rebates {sum(rb):10.0f} = net {sum(nt):12.0f}")
    print(f"   positive-net concentration top1/top5/top10 = {100 * sum(pos[:1]) / tp:.0f}% / {100 * sum(pos[:5]) / tp:.0f}% / {100 * sum(pos[:10]) / tp:.0f}%  (n positive {len(pos)})")
    losers = [r for r in R if r["trading"] < 0]
    flip = sum(1 for r in losers if r["net"] > 0)
    print(f"   trading losers {len(losers)}: subsidy flips to net>0 in {flip}; subsidy sum {sum(r['rewards'] + r['rebates'] for r in losers):.0f} vs their trading loss {sum(r['trading'] for r in losers):.0f}")
    # months
    M = [monthly(r) for r in R]
    for k in range(3):
        v = [m[k] for m in M if m[k] is not None]
        rbk = [r["rebates_m"][k] for r in R]; rwk = [r["rewards_m"][k] for r in R]
        print(f"   month{k + 1}: net>0 {pct(sum(x > 0 for x in v), len(v))} med {st.median(v):8.0f} | med reward {st.median(rwk):7.1f} med rebate {st.median(rbk):7.1f} | sum reward {sum(rwk):9.0f} sum rebate {sum(rbk):9.0f}")
    allm = [m for m in M if None not in m]
    print(f"   net>0 in all 3 months {pct(sum(all(x > 0 for x in m) for m in allm), len(allm))}; in 0 of 3 months {pct(sum(all(x <= 0 for x in m) for m in allm), len(allm))}")
    # ratios (defensible subsets)
    rc = [r["net"] / r["cash_d0"] for r in R if r.get("cash_d0") and r["cash_d0"] >= 100]
    rv = [1e4 * r["net"] / r["vol"] for r in R if r["vol_status"] == "complete" and r["vol"] >= 1000]
    rv_tr = [1e4 * r["trading"] / r["vol"] for r in R if r["vol_status"] == "complete" and r["vol"] >= 1000]
    rv_sub = [1e4 * (r["rewards"] + r["rebates"]) / r["vol"] for r in R if r["vol_status"] == "complete" and r["vol"] >= 1000]
    if rc: print(f"   net/cash_d0 (cash>=$100, n={len(rc)}): med {st.median(rc):+.1%}  p25 {q(rc, .25):+.1%}  p75 {q(rc, .75):+.1%}")
    if rv: print(f"   per volume (uncapped, vol>=$1k, n={len(rv)}): net med {st.median(rv):+.0f} bp | trading med {st.median(rv_tr):+.0f} bp | subsidy med {st.median(rv_sub):+.0f} bp")
    cash = [r["cash_d0"] for r in R if r.get("cash_d0") is not None]
    print(f"   cash_d0 med {st.median(cash):.0f} (p25 {q(cash, .25):.0f}, p75 {q(cash, .75):.0f}); window vol med {st.median([r['vol'] for r in R]):.0f}")
    fl = [flags(r) for r in R]
    print("   flags: " + ", ".join(f"{k} {sum(k in f for f in fl)}" for k in ["F_START", "F_VOLCAP", "F_CASH0", "F_LB"]))
    # robustness: same stats without F_LB rows (reported only, primary result unchanged)
    clean = [r for r, f in zip(R, fl) if "F_LB" not in f]
    if len(clean) != n and clean:
        cn = [r["net"] for r in clean]
        print(f"   [robustness, excluding F_LB] n={len(clean)} net>0 {pct(sum(x > 0 for x in cn), len(clean))} med {st.median(cn):.0f} mean {st.mean(cn):.0f}")
    return dict(n=n, fpos=sum(x > 0 for x in nt) / n, med=st.median(nt), tpos=sum(x > 0 for x in tr) / n)


def weighted(c, res):
    W = FRAME[c]; tot = sum(W.values())
    f = sum(W[t] * res[t]["fpos"] for t in TIERS) / tot
    tf = sum(W[t] * res[t]["tpos"] for t in TIERS) / tot
    print(f"\n   FRAME-WEIGHTED population estimate (cohort {c}, frame {tot} wallets): fraction net>0 {f:.0%}; fraction trading>0 {tf:.0%}")


def secondary_cash(R, label):
    """SECONDARY, descriptive: mission's example capital tiers applied to cash_d0 (a LOWER bound on capital).
    Not a redefinition of the pre-declared tiers; not used to select candidates."""
    bands = [("cash<$500", 0, 500), ("$500-2k", 500, 2000), ("$2k-10k", 2000, 10000), (">$10k", 10000, 1e18)]
    print(f"\n   SECONDARY view by cash_d0 ({label}; cash is a lower bound on capital, positions excluded):")
    for name, lo, hi in bands:
        S = [r for r in R if r.get("cash_d0") is not None and lo <= r["cash_d0"] < hi]
        if not S: continue
        nt = [r["net"] for r in S]; tr = [r["trading"] for r in S]
        print(f"     {name:10s} n={len(S):3d} net>0 {sum(x > 0 for x in nt) / len(S):4.0%} med net {st.median(nt):9.0f} mean {st.mean(nt):10.0f} | trading>0 {sum(x > 0 for x in tr) / len(S):4.0%} med trading {st.median(tr):8.0f} | med subsidy {st.median([r['rewards'] + r['rebates'] for r in S]):7.0f}")


if __name__ == "__main__":
    for c in sys.argv[1:] or ["A", "B"]:
        R, bad = load(c)
        print(f"\n######## Cohort {c}: usable {len(R)}, unusable {len(bad)} {[(b['tier'], b['wallet'], b.get('err')) for b in bad]}")
        res = {t: block([r for r in R if r["tier"] == t], f"Cohort {c} {t}") for t in TIERS}
        block(R, f"Cohort {c} ALL (equal 40/tier sample, NOT frame-weighted)")
        weighted(c, res)
        secondary_cash(R, f"cohort {c}")
