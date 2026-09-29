import json,time,urllib.request,datetime
H={"User-Agent":"curl/8.5.0","Accept":"*/*"}
def get(u,tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40) as r: return json.load(r)
        except Exception as e: time.sleep(2*(i+1))
    return None
cut=datetime.datetime(2025,9,29).timestamp(); out={}
for a,fam in json.load(open("surv_wallets.json")).items():
    s=get(f"https://user-pnl-api.polymarket.com/user-pnl?user_address={a}&interval=all&fidelity=1d")
    pts=[(int(x["t"]),float(x["p"])) for x in (s or []) if x.get("t") is not None]
    if not pts: out[a]=None; continue
    last=pts[-1][1]; v12=[p for t,p in pts if t>=cut]
    out[a]={"fam":fam,"first":datetime.datetime.utcfromtimestamp(pts[0][0]).strftime("%Y-%m-%d"),"all":round(last),"m12":round(last-v12[0]) if v12 else None,"n":len(pts)}
json.dump(out,open("pm_userpnl_surv.json","w"),indent=0); print("userpnl done",len(out),"missing",sum(1 for v in out.values() if v is None))
