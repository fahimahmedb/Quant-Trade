import requests, time, json, os
S=requests.Session()
DA="https://data-api.polymarket.com"
def get(url, params=None, tries=5):
    for i in range(tries):
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code==200: return r.json()
            if r.status_code in (429,500,502,503,504): time.sleep(2*(i+1)); continue
            return {"__error__":r.status_code,"text":r.text[:300]}
        except Exception as e:
            time.sleep(2*(i+1))
    return {"__error__":"exhausted"}
def activity_all(user, start=None, end=None, types=None, max_records=60000):
    """page backwards by time using end=, dedupe by (tx,asset,type,size)."""
    out=[]; seen=set(); cur_end=end
    while True:
        p={"user":user,"limit":500,"sortBy":"TIMESTAMP","sortDirection":"DESC"}
        if start: p["start"]=start
        if cur_end: p["end"]=cur_end
        if types: p["type"]=types
        page=None
        for off in range(0,5001,500):
            p["offset"]=off
            pg=get(DA+"/activity",p)
            if isinstance(pg,dict): return out, f"error {pg}"
            new=0
            for x in pg:
                k=(x["transactionHash"],x.get("asset"),x["type"],x.get("size"),x.get("side"),x["timestamp"])
                if k in seen: continue
                seen.add(k); out.append(x); new+=1
            if len(pg)<500: return out, "complete"
            if len(out)>=max_records: return out, "capped"
            last_ts=pg[-1]["timestamp"]
        # offset exhausted: move end back
        if cur_end==last_ts: return out, "stuck"
        cur_end=last_ts
def pnl_series(user):
    j=get("https://user-pnl-api.polymarket.com/user-pnl",{"user_address":user,"interval":"all","fidelity":"1d"})
    return j if isinstance(j,list) else []
def value(user):
    j=get(DA+"/value",{"user":user})
    try: return float(j[0]["value"])
    except Exception: return None
