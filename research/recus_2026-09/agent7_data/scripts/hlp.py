# M1: HLP vault period returns, half-year summary, quarterly half-life fit.
# Public endpoint: POST https://api.hyperliquid.xyz/info {"type":"vaultDetails","vaultAddress":HLP}
import json, math, statistics as st, datetime as dt, urllib.request, collections

HLP = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
req = urllib.request.Request("https://api.hyperliquid.xyz/info",
                             data=json.dumps({"type": "vaultDetails", "vaultAddress": HLP}).encode(),
                             headers={"Content-Type": "application/json"})
d = json.load(urllib.request.urlopen(req, timeout=60))
p = dict((k, v) for k, v in d["portfolio"])["allTime"]
av = [(int(t), float(x)) for t, x in p["accountValueHistory"]]
pn = [(int(t), float(x)) for t, x in p["pnlHistory"]]
rows = []
for i in range(1, len(av)):
    t0, a0 = av[i - 1]; t1, _ = av[i]
    if a0 <= 0:
        continue
    dp = pn[i][1] - pn[i - 1][1]
    rows.append((dt.datetime.utcfromtimestamp(t1 / 1000).date(), dp, a0, dp / a0, (t1 - t0) / 86400000))
json.dump([(str(r[0]),) + r[1:] for r in rows], open("hlp_periods.json", "w"))

half = collections.defaultdict(list)
for r in rows:
    half[f"{r[0].year}H{1 if r[0].month <= 6 else 2}"].append(r)
print("half | median AV M$ | ann. all | ann. ex-best period | median bp/day | best share")
for k in sorted(half):
    L = half[k]; days = sum(x[4] for x in L)
    G = math.prod(1 + x[3] for x in L)
    top = max(L, key=lambda x: x[1])
    Gx = math.prod(1 + x[3] for x in L if x is not top); dx = days - top[4]
    tot = sum(x[1] for x in L)
    print(k, "%.0f" % (st.median(x[2] for x in L) / 1e6), "%.1f%%" % ((G ** (365 / days) - 1) * 100),
          "%.1f%%" % ((Gx ** (365 / dx) - 1) * 100), "%.2f" % st.median(x[3] / x[4] * 1e4 for x in L),
          "%.0f%%" % (100 * top[1] / tot if tot > 0 else float("nan")), top[0])

q = collections.defaultdict(list)
for r in rows:
    q[(r[0].year, (r[0].month - 1) // 3)].append(r)
xs, ys, lav = [], [], []
for k in sorted(q):
    L = q[k]; med = st.median(x[3] / x[4] * 1e4 for x in L)
    mid = L[len(L) // 2][0]
    if med > 0 and k >= (2023, 3):
        xs.append((mid - dt.date(2023, 5, 10)).days / 365); ys.append(math.log(med))
        lav.append(math.log(st.median(x[2] for x in L)))
n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
res = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
se = math.sqrt(sum(e * e for e in res) / (n - 2) / sum((x - mx) ** 2 for x in xs))
print("slope/yr %.2f +- %.2f; half-life months %.1f (95%% CI %.1f-%.1f)" % (
    b, se, -math.log(2) / b * 12, -math.log(2) / (b - 1.96 * se) * 12, -math.log(2) / (b + 1.96 * se) * 12))
ma = sum(lav) / n
print("elasticity of median return to AV %.2f" % (sum((a - ma) * (y - my) for a, y in zip(lav, ys)) / sum((a - ma) ** 2 for a in lav)))
