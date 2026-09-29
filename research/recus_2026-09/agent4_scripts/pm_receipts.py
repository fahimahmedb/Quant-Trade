import json, re, sys, time, urllib.request, collections, datetime
BASE="https://data-api.polymarket.com"
def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"curl/8.5.0","Accept":"*/*"}), timeout=40) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(1.5*(i+1)); err=e
    return {"_err":str(err)}
CLASSES=[
 ("TWEETS", r"tweet|posts? on x\b|# of posts|elon.*post|trump.*post|truth social"),
 ("BOXOFFICE", r"box office|opening weekend|gross"),
 ("MUSIC", r"spotify|billboard|streams|monthly listeners|#1 song|album"),
 ("SCREEN", r"rotten tomatoes|imdb|netflix|top 10|metacritic|episode"),
 ("APP_RANK", r"app store|top app|google trends|downloads"),
 ("MENTIONS", r"\bsay|\bsays?\b|mention|utter|speech|press conference|state of the union|debate"),
 ("ECON_DATA", r"cpi|inflation|jobs report|payroll|unemployment|gdp|fed |fomc|rate cut|interest rate|bps|initial claims|pce"),
 ("CORP_EVENT", r"microstrategy|strategy .*btc|buy.*bitcoin|earnings|ipo|announce|launch|release|acquire|merger|8-k|filing|listed|listing"),
 ("AI_TECH", r"\bai\b|openai|gpt|model|chatbot|lmarena|arena|benchmark|apple|iphone|tesla|spacex|starship|nvidia"),
 ("CRYPTO_PRICE", r"bitcoin|btc|ethereum|\beth\b|solana|\bsol\b|price|above|below|\$\d"),
 ("SPORTS", r"\bvs\.?\b|win the|nfl|nba|mlb|nhl|ufc|f1|grand prix|match|game|champion|premier league|world cup|series"),
 ("POLITICS", r"election|president|senate|house|governor|nominee|poll|approval|impeach|shutdown|bill|congress|prime minister|parliament"),
 ("WEATHER", r"temperature|°|highest temp|lowest temp|rain|snow|hurricane|storm"),
]
def classify(t):
    tl=t.lower()
    for name,rx in CLASSES:
        if re.search(rx, tl): return name
    return "OTHER"
cats=sys.argv[1].split(",")
windows=sys.argv[2].split(",")
topn=int(sys.argv[3]); maxpos=int(sys.argv[4])
wallets=collections.OrderedDict()
for cat in cats:
    for w in windows:
        lb=get(f"{BASE}/v1/leaderboard?category={cat}&timePeriod={w}&orderBy=PNL&limit={topn}&offset=0")
        if not isinstance(lb,list): print("LB ERR",cat,w,lb); continue
        for e in lb:
            a=e.get("proxyWallet") or e.get("user") or e.get("address")
            if not a: continue
            wallets.setdefault(a,{"name":e.get("userName") or e.get("name") or e.get("pseudonym"),"lb":[]})
            wallets[a]["lb"].append((cat,w,e.get("pnl"),e.get("vol")))
print("wallets:",len(wallets),file=sys.stderr)
out=[]
for a,meta in wallets.items():
    pos=[]; off=0
    while off<maxpos:
        page=get(f"{BASE}/closed-positions?user={a}&limit=500&offset={off}")
        if not isinstance(page,list) or not page: break
        pos+=page; off+=500
        if len(page)<500: break
    agg=collections.defaultdict(lambda:[0,0.0,0.0,None,None])  # n, realized, fees, first, last
    for p in pos:
        c=classify(p.get("title","") or p.get("eventTitle","") or "")
        r=agg[c]; r[0]+=1; r[1]+=float(p.get("realizedPnl") or 0); r[2]+=float(p.get("entryFeesUsdc") or 0)
        ts=p.get("endDate") or p.get("timestamp") or p.get("closedAt")
        if ts:
            r[3]=min(r[3],ts) if r[3] else ts; r[4]=max(r[4],ts) if r[4] else ts
    tot=sum(v[1] for v in agg.values())
    hi=[q for q in pos if float(q.get("avgPrice") or 0)>=0.9]
    hi_r=sum(float(q.get("realizedPnl") or 0) for q in hi); hi_b=sum(float(q.get("totalBought") or 0) for q in hi)
    lo=[q for q in pos if float(q.get("avgPrice") or 0)<=0.1]
    lo_r=sum(float(q.get("realizedPnl") or 0) for q in lo)
    out.append({"wallet":a,"name":meta["name"],"lb":meta["lb"],"n_pos":len(pos),"realized_total":round(tot,0),"hi90":{"n":len(hi),"realized":round(hi_r),"bought":round(hi_b)},"lo10":{"n":len(lo),"realized":round(lo_r)},
                "by_class":{k:{"n":v[0],"realized":round(v[1],0),"fees":round(v[2],0),"first":v[3],"last":v[4]} for k,v in sorted(agg.items(),key=lambda kv:-kv[1][1])}})
    print(a[:10],meta["name"],len(pos),round(tot),{k:(v[0],round(v[1])) for k,v in list(agg.items())[:4]},file=sys.stderr)
json.dump(out,open(f"pm_receipts_{'_'.join(cats)}.json","w"),indent=1)
