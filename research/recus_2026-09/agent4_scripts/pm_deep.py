import json, re, sys, time, urllib.request, collections, datetime
BASE="https://data-api.polymarket.com"; H={"User-Agent":"curl/8.5.0","Accept":"*/*"}
def get(url, tries=3):
    err=None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as r: return json.load(r)
        except Exception as e: err=e; time.sleep(1.5*(i+1))
    return {"_err":str(err)}
exec(open("classes.py").read())
W=json.load(open("focus_wallets.json"))
out={}
for a,label in W.items():
    pos=[]; off=0
    while off<3000:
        page=get(f"{BASE}/closed-positions?user={a}&limit=50&offset={off}")
        if not isinstance(page,list) or not page: break
        pos+=page; off+=50
        if len(page)<50: break
    pnl=get(f"https://user-pnl-api.polymarket.com/user-pnl?user_address={a}&interval=all&fidelity=1d")
    rew=get(f"{BASE}/activity?user={a}&type=REWARD&limit=500"); reb=get(f"{BASE}/activity?user={a}&type=MAKER_REBATE&limit=500")
    def s(x): return round(sum(float(e.get("usdcSize") or e.get("size") or 0) for e in x),0) if isinstance(x,list) else None
    recs=[{"t":p.get("title"),"c":classify(p.get("title") or ""),"ap":float(p.get("avgPrice") or 0),"b":float(p.get("totalBought") or 0),"r":float(p.get("realizedPnl") or 0),"ts":p.get("timestamp"),"o":p.get("outcome")} for p in pos]
    out[a]={"label":label,"n":len(pos),"truncated":len(pos)>=3000,"positions":recs,"user_pnl":pnl if isinstance(pnl,list) else None,"reward_sum":s(rew),"reward_n":len(rew) if isinstance(rew,list) else None,"rebate_sum":s(reb),"rebate_n":len(reb) if isinstance(reb,list) else None}
    print(a[:10],label,len(pos),round(sum(r["r"] for r in recs)),"rew",s(rew),"reb",s(reb),file=sys.stderr)
json.dump(out,open("pm_deep.json","w"))
