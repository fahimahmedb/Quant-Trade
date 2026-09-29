# M6: monthly volume of Elon-Musk post-count events (gamma).
# M7: monthly user-pnl deltas and weather-only realized P&L for already-public wallets (named in A1/A3/A4).
import json, urllib.request, time, re, collections, datetime as dt

def get(u):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60))
        except Exception:
            time.sleep(2)
    return None

# ---- M6
evs = {}
for tag in ["tweets-markets", "elon-tweets", "elon-musk"]:
    for closed in ["true", "false"]:
        off = 0
        while off <= 2000:
            d = get(f"https://gamma-api.polymarket.com/events?tag_slug={tag}&closed={closed}&limit=100&offset={off}&order=endDate&ascending=true")
            if not d:
                break
            for e in d:
                t = e.get("title") or ""
                if re.search(r"(elon|musk).*(tweet|post)|# of tweets|number of tweets", t, re.I) and not re.search(r"trump", t, re.I):
                    evs[e["id"]] = {"title": t, "end": e.get("endDate"), "vol": float(e.get("volume") or 0)}
            if len(d) < 100:
                break
            off += 100
mon = collections.Counter()
for e in evs.values():
    if e["end"]:
        mon[e["end"][:7]] += e["vol"]
print("tweet-count events", len(evs))
for m in sorted(mon):
    print(m, "%.1f M$" % (mon[m] / 1e6))

# ---- M7
W = {"b00k13": "0x1c5575dc20e4ea54d1bb09ccda72ccf8a3b684ce", "gopfan2": "0xf2f6af4f27ec2dcf4072095ab804016e14cd5817",
     "aenews2": "0x44c1dfe43260c94ed4f1d00de2e1f80fb113ebc1", "BeefSlayer": "0x331bf91c132af9d921e1908ca0979363fc47193f",
     "russell110320": "0x118689b24aead1d6e9507b8068d056b2ec4f051b", "HighTempTation": "0x6011655c4afb76f36dd1b08a137a1ba73466b31e",
     "Bilberry": "0xbf13934a1fec7d3211fc15c138d84ac2a691b91a"}
for n, a in W.items():
    s = get(f"https://user-pnl-api.polymarket.com/user-pnl?user_address={a}&interval=all&fidelity=1d") or []
    last = collections.OrderedDict()
    for x in s:
        last[dt.datetime.utcfromtimestamp(x["t"]).strftime("%Y-%m")] = x["p"]
    prev, deltas = 0, {}
    for k, v in last.items():
        deltas[k] = v - prev; prev = v
    print(n, " ".join(f"{k}:{v/1e3:+.1f}k" for k, v in deltas.items() if k >= "2025-06"))
# word-boundary filter (a loose filter matched "Ukraine"/"Bahrain"/"Miami Heat"; corrected after review)
WX = re.compile(r"\btemperature\b|°[CF]|\bweather\b|\brain(fall)?\b|\bsnow(fall)?\b|\bhurricanes?\b|\bheat ?wave\b|\bhottest\b|\bdegrees\b|\bnamed storms\b", re.I)
for n in ("gopfan2", "aenews2"):
    allp, off = [], 0
    while off < 10000:
        d = get(f"https://data-api.polymarket.com/closed-positions?user={W[n]}&limit=50&offset={off}&sortBy=TIMESTAMP&sortDirection=DESC")
        if not d:
            break
        allp += d; off += 50
        if len(d) < 50:
            break
    by, cnt = collections.Counter(), collections.Counter()
    for p in allp:
        if WX.search(p.get("title", "")):
            m = dt.datetime.utcfromtimestamp(p.get("timestamp") or 0).strftime("%Y-%m")
            by[m] += float(p.get("realizedPnl") or 0); cnt[m] += 1
    print(n, "weather realized by month:", " ".join(f"{k}:{by[k]/1e3:+.1f}k({cnt[k]})" for k in sorted(by)))
