import json, sys, time, urllib.request, collections
BASE="https://data-api.polymarket.com"; H={"User-Agent":"curl/8.5.0","Accept":"*/*"}
def get(url, tries=3):
    err=None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(1.5*(i+1))
    return {"_err":str(err)}
exec(open("classes.py").read())
ge=json.load(open("gamma_events.json"))
targets={"BOXOFFICE":["forgotten-island-opening-weekend-box-office","heart-of-the-beast-opening-weekend-box-office","primetime-opening-weekend-box-office"],
         "TWEETS":["elon-musk-of-tweets-in-september-2026"]}
out={}
for fam,slugs in targets.items():
    parts=collections.Counter()
    for q,evs in ge.items():
        for e in evs:
            if e["slug"] in slugs:
                for cid in e["cids"]:
                    off=0
                    while off<2000:
                        tr=get(f"{BASE}/trades?market={cid}&limit=500&offset={off}")
                        if not isinstance(tr,list) or not tr: break
                        for t in tr: parts[t.get("proxyWallet")]+=1
                        off+=500
                        if len(tr)<500: break
    parts.pop(None,None)
    print(fam,"participants",len(parts),file=sys.stderr)
    # sample: up to 70 participants, stratified: all with >=5 trades first, then random rest
    ranked=[a for a,_ in parts.most_common()]
    sample=ranked[:70]
    rows=[]
    for a in sample:
        pos=[]; off=0
        while off<300:
            page=get(f"{BASE}/closed-positions?user={a}&limit=50&offset={off}")
            if not isinstance(page,list) or not page: break
            pos+=page; off+=50
            if len(page)<50: break
        fam_pos=[p for p in pos if classify(p.get("title") or "")==fam]
        r=sum(float(p.get("realizedPnl") or 0) for p in fam_pos); b=sum(float(p.get("totalBought") or 0) for p in fam_pos)
        fee_n=sum(1 for p in pos if p.get("entryFeesUsdc") is not None); fee_s=sum(float(p.get("entryFeesUsdc") or 0) for p in pos)
        rows.append({"w":a,"fee_n":fee_n,"fee_sum":round(fee_s,2),"trades_in_event":parts[a],"n_pos_total":len(pos),"trunc":len(pos)>=300,"n_fam":len(fam_pos),"fam_realized":round(r,2),"fam_bought":round(b,2),
                     "all_realized":round(sum(float(p.get("realizedPnl") or 0) for p in pos),2)})
        print(fam,a[:8],parts[a],len(pos),len(fam_pos),round(r),file=sys.stderr)
    out[fam]={"n_participants":len(parts),"sample":rows}
json.dump(out,open("pm_surv.json","w"),indent=0)
