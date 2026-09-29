import json, sys, time, urllib.request, datetime
BASE="https://data-api.polymarket.com"; H={"User-Agent":"curl/8.5.0","Accept":"*/*"}
def get(url, tries=4):
    err=None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(2*(i+1))
    return {"_err":str(err)}
exec(open("classes.py").read())
W=json.load(open(sys.argv[1])); outp=sys.argv[2]
cut=datetime.datetime(2025,9,29).timestamp()
out={}
first=True
for a,label in W.items():
    pos=[]; off=0
    while off<5000:
        page=get(f"{BASE}/positions?user={a}&limit=500&offset={off}&sizeThreshold=0")
        if not isinstance(page,list) or not page: break
        pos+=page; off+=500
        if len(page)<500: break
    if first and pos: print("POS KEYS:",sorted(pos[0].keys()),file=sys.stderr); print(json.dumps(pos[0])[:600],file=sys.stderr); first=False
    dead=[p for p in pos if float(p.get("curPrice") or 0)<=0.001]
    live=[p for p in pos if float(p.get("curPrice") or 0)>0.001]
    def agg(L):
        return {"n":len(L),"initial":round(sum(float(p.get("initialValue") or 0) for p in L)),"current":round(sum(float(p.get("currentValue") or 0) for p in L)),
                "cashPnl":round(sum(float(p.get("cashPnl") or 0) for p in L)),"realized_field":round(sum(float(p.get("realizedPnl") or 0) for p in L))}
    def by_class(L):
        d={}
        for p in L:
            c=classify(p.get("title") or ""); d.setdefault(c,[0,0.0]); d[c][0]+=1; d[c][1]+=float(p.get("cashPnl") or 0)
        return {k:[v[0],round(v[1])] for k,v in sorted(d.items(),key=lambda kv:kv[1][1])}
    out[a]={"label":label,"n_open":len(pos),"dead":agg(dead),"dead_by_class":by_class(dead),"live":agg(live),"live_by_class":by_class(live)}
    print(a[:10],label,"open",len(pos),"DEAD",out[a]["dead"],"LIVE",out[a]["live"],file=sys.stderr)
json.dump(out,open(outp,"w"),indent=0)
