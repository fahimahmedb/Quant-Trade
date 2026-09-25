import pandas as pd, numpy as np, random, sys, json
from book import D
H=[5,60,300,1800]
def mids(path):
    f=pd.read_parquet(path)
    bids={}; asks={}; T=[];BB=[];BA=[]; tr=[]
    for r in f.itertuples(index=False):
        et=r.event_type
        if et=='snapshot':
            bids={float(x['price']):float(x['size']) for x in json.loads(r.bids)} if isinstance(r.bids,str) else {}
            asks={float(x['price']):float(x['size']) for x in json.loads(r.asks)} if isinstance(r.asks,str) else {}
        elif et=='delta':
            b=bids if r.side=='BUY' else asks
            if r.size==0: b.pop(r.price,None)
            else: b[r.price]=r.size
        elif et=='trade':
            # record book state BEFORE trade (last recorded)
            tr.append((r.t,r.price,r.size,r.side, BB[-1] if BB else np.nan, BA[-1] if BA else np.nan)); continue
        T.append(r.t); BB.append(max(bids) if bids else np.nan); BA.append(min(asks) if asks else np.nan)
    return np.array(T),np.array(BB),np.array(BA),tr
rows=[]
random.seed(0)
for folder,cap in [('mlb-2026-07-05',300),('counter-strike-2026-09-10',200),('world-cup-final-2026-07-19',200),('ufc-330-2026-08-16',80),('nyc-weather-2026-07-16',40),('apple-weekly-2026-06-12',20),('bitcoin-5m-15m-hourly-2026-06-15',60)]:
    m=pd.read_csv(D+folder+'/markets.csv'); m=m.sample(min(cap,len(m)),random_state=0)
    for r in m.itertuples():
        T,BB,BA,tr=mids(D+folder+'/'+r.file)
        if len(tr)==0 or len(T)<2: continue
        valid=(BB>0)&(BA>0)&(BA-BB<=0.10)
        mid=np.where(valid,(BB+BA)/2,np.nan)
        settle=1.0 if r.winning_outcome=='Yes' else (0.0 if r.winning_outcome=='No' else np.nan)
        for (t,p,s,side,bb,ba) in tr:
            if not(bb>0 and ba>0) or ba-bb>0.10: continue
            m0=(bb+ba)/2
            d=1 if side=='BUY' else -1   # taker direction (verify)
            rec=dict(ev=folder,mkt=r.market_id,t=t,p=p,s=s,d=d,m0=m0,spr=ba-bb,atask=p>=ba-1e-9,atbid=p<=bb+1e-9,settle=settle,tte=(pd.Timestamp(r.close_time).value//10**6-t)/3.6e6)
            for h in H:
                j=np.searchsorted(T,t+h*1000,side='right')-1
                rec[f'm{h}']=mid[j] if j>=0 else np.nan
            rows.append(rec)
    print(folder,len(rows),flush=True)
df=pd.DataFrame(rows); df.to_parquet('markout.parquet')
