# M2: decompose the Polymarket maker-rebate payer transfers by recipient for A6's 13 dates,
# then fetch the dominant recipient's full MAKER_REBATE history from the public data-api.
# Inputs: Agent 6's decay_series.json (block windows per date), rpc.py (public Polygon RPC helpers).
#   git show fff0cca0773f542e9039be726d9b49519fe2b56e:research/recus_2026-09/agent6_data/decay_series.json > decay_series.json
import json, collections, urllib.request, datetime as dt
from rpc import logs_range, TRANSFER, PUSD, REBATE_EOA, pad

USDCE = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"
REB_OLD = "0x3a9418b2651c8164db5ebc56f12008137865e0f7"
d = json.load(open("decay_series.json"))
out = {}
for day in sorted(d):
    b0, b1 = d[day]["blocks"]
    a = collections.Counter()
    for tok in (USDCE, PUSD):
        for l in logs_range(tok, [TRANSFER, [pad(REB_OLD), pad(REBATE_EOA)]], b0, b1, step=3000):
            a["0x" + l["topics"][2][-40:]] += int(l["data"], 16) / 1e6
    out[day] = dict(a)
    top = a.most_common(3)
    print(day, "n", len(a), "total %.0f" % sum(a.values()), "top3", [(k[:8], round(v)) for k, v in top])
json.dump(out, open("rebate_by_wallet.json", "w"))

DOM = "0x2d507657ca4ebcc8f9a38f6764c07310b66dea54"   # dominant recipient (no trades/positions/P&L in public API)
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
reb, end = [], None
while True:
    page = get(f"https://data-api.polymarket.com/activity?user={DOM}&type=MAKER_REBATE&limit=500" + (f"&end={end}" if end else ""))
    if not page:
        break
    reb += page; end = min(x["timestamp"] for x in page) - 1
    if len(page) < 500:
        break
by = collections.Counter()
for x in reb:
    by[dt.datetime.utcfromtimestamp(x["timestamp"]).strftime("%Y-%m")] += x["usdcSize"]
print("dominant recipient payments", len(reb), "total %.1f M$" % (sum(by.values()) / 1e6), dict(sorted(by.items())))
