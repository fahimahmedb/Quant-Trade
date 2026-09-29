"""CP2: pull all taker trades (data-api /trades, takerOnly default) for every bracket of U1+U2 candidate events.
Run from research/box_office/data. Output: trades_u.json.gz {conditionId: [trade,...]}"""
import json,gzip,urllib.request,time,concurrent.futures as cf,os
def get(u,tries=6):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=90))
        except Exception:
            time.sleep(1+2*i)
    raise RuntimeError(u)
U=json.load(gzip.open('universe_raw.json.gz','rt'))
conds=[b['cond'] for r in U if r['family'] in('OPEN','NTH') and r['closed'] and r['wk_start'] and '2025-10-10'<=r['wk_start']<='2026-09-25' for b in r['brackets']]
KEEP=('side','asset','conditionId','size','price','timestamp','outcomeIndex','proxyWallet','transactionHash')
def pull(c):
    out=[];off=0
    while True:
        b=get(f"https://data-api.polymarket.com/trades?market={c}&limit=500&offset={off}")
        if not isinstance(b,list) or not b: break
        out+=[{k:t.get(k) for k in KEEP} for t in b]; off+=len(b)
        if len(b)<500: break
        if off>=10000: out.append({'TRUNCATED':True}); break
    return c,out
res={}
with cf.ThreadPoolExecutor(8) as ex:
    for c,o in ex.map(pull,conds): res[c]=o
json.dump(res,gzip.open('trades_u.json.gz','wt'))
print(len(res),sum(len(v) for v in res.values()),'truncated',sum(1 for v in res.values() if v and 'TRUNCATED' in v[-1]))
