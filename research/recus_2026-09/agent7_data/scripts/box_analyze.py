# M3 analysis: winner price at release anchors by quarter, Spearman trends, favourite diagnostic, statistical latency.
# Input: box_prices.json produced by box.py (gamma box-office events + clob prices-history, anchors in ET).
import json, math, statistics as st, datetime as dt, collections, random
random.seed(7)
d = json.load(open("box_prices.json"))
A = ["thu18", "fri14", "sat14", "sun14", "mon18"]

def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v)
    for k, i in enumerate(o):
        r[i] = k
    return r

def spearman(x, y):
    idx = [i for i in range(len(x)) if y[i] is not None]
    x = [x[i] for i in idx]; y = [y[i] for i in idx]
    rx, ry = rank(x), rank(y); n = len(x)
    return 1 - 6 * sum((a - b) ** 2 for a, b in zip(rx, ry)) / (n * (n * n - 1)), n

ev = []
for e in d:
    rs = [r for r in e["rows"] if r["p"]["sat14"] is not None and r["p"]["sun14"] is not None]
    if sum(r["won"] for r in rs) != 1:
        continue
    ev.append((e["fri"], e["vol"], rs))
ev.sort(key=lambda x: x[0])
g = collections.defaultdict(list)
for f, v, rs in ev:
    y, m = int(f[:4]), int(f[5:7])
    g["2023-11..2025-09" if (y, m) < (2025, 10) else f"{y}Q{(m - 1) // 3 + 1}"].append((v, rs))
print("period | n | median vol | winner median by anchor | winner=fav sat14/sun14")
for k in sorted(g):
    L = g[k]
    meds = []
    for a in A:
        vals = [[r for r in rs if r["won"]][0]["p"][a] for _, rs in L]
        vals = [x for x in vals if x is not None]
        meds.append("%.2f" % st.median(vals) if vals else "na")
    fs = sum(max(rs, key=lambda r: r["p"]["sat14"])["won"] for _, rs in L) / len(L)
    fu = sum(max(rs, key=lambda r: r["p"]["sun14"])["won"] for _, rs in L) / len(L)
    print(k, len(L), "%.0fk" % (st.median(v for v, _ in L) / 1e3), "/".join(meds), "%.0f%%/%.0f%%" % (100 * fs, 100 * fu))

reg = [(f, rs) for f, v, rs in ev if f >= "2025-10-01"]
t = [(dt.date.fromisoformat(f) - dt.date(2025, 10, 1)).days for f, _ in reg]
for a in ["fri14", "sat14", "sun14"]:
    y = [[r for r in rs if r["won"]][0]["p"][a] for _, rs in reg]
    rho, n = spearman(t, y)
    print(a, "spearman(time, winner price) %.3f z %.2f n %d" % (rho, rho * math.sqrt(n - 1), n))

def fav_ret(rs, a):
    f = max(rs, key=lambda r: r["p"][a]); p = f["p"][a]
    if p <= 0.02 or p >= 0.995:
        return None
    return (1.0 if f["won"] else 0.0) / (p + 0.05 * p * (1 - p)) - 1

q = collections.defaultdict(list)
for f, rs in reg:
    q[f"{f[:4]}Q{(int(f[5:7]) - 1) // 3 + 1}"].append((f, rs))
for a in ["sat14", "sun14"]:
    allr = []
    for k in sorted(q):
        R = [x for x in (fav_ret(rs, a) for _, rs in q[k]) if x is not None]; allr += R
        bs = sorted(st.mean(random.choices(R, k=len(R))) for _ in range(2000))
        print(a, k, "fav ret %.3f [%.3f, %.3f] n=%d" % (st.mean(R), bs[50], bs[1949], len(R)))
    bs = sorted(st.mean(random.choices(allr, k=len(allr))) for _ in range(2000))
    print(a, "ALL %.3f [%.3f, %.3f] n=%d" % (st.mean(allr), bs[50], bs[1949], len(allr)))
R = [(dt.date.fromisoformat(f), fav_ret(rs, "sat14")) for f, rs in reg]
R = [(x, y) for x, y in R if y is not None]
rho, n = spearman([(x - dt.date(2025, 10, 1)).days for x, _ in R], [y for _, y in R])
sd = st.pstdev([y for _, y in R]); weeks = (max(x for x, _ in R) - min(x for x, _ in R)).days / 7
print("sat14 fav return trend spearman %.3f z %.2f; sd %.3f; events/week %.2f" % (rho, rho * math.sqrt(n - 1), sd, n / weeks))
for eff in [0.05, 0.10, 0.15, 0.25]:
    N = (2.486 * sd / eff) ** 2
    print("effect %.2f/$ -> events %.0f -> weeks %.0f" % (eff, N, N / (n / weeks)))
