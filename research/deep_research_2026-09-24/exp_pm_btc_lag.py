"""Does Polymarket 'BTC Up or Down' lag Binance? Tests the X-post 'latency arbitrage' claim on real order books.
Data: git clone https://github.com/marketlenstrade/polymarket-historical-data (folder bitcoin-5m-15m-hourly-2026-06-15:
408 markets, 1 day, full L2 book deltas + Binance BTC trade tape). Book = the 'Up' token (assumption checked below).
Model (causal): P(Up) = Phi( ln(S_t/S_open) / (sigma*sqrt(tau)) ), sigma from trailing 30 min of Binance 1s returns.
Caveat: Polymarket resolves on Chainlink BTC/USD, not Binance; S_open = Binance price at open_time.
Trade rule: one taker entry per market at the first decision time where edge > threshold; hold to resolution.
Latency L: decide with Binance data up to t, fill at the book as of t+L. Fee: 0.07*P*(1-P) per share (crypto taker).
"""
import pandas as pd, numpy as np, json, glob, os, sys
from math import erf, sqrt, log
D=sys.argv[1]
m=pd.read_csv(f'{D}/markets.csv')
ref=pd.read_parquet(f'{D}/reference-BTC.parquet'); ref['price']=ref.price.astype(float)
ref['s']=ref.timestamp//1000; px=ref.groupby('s').price.last()
px=px.reindex(range(px.index.min(),px.index.max()+1)).ffill()
lr=np.log(px).diff(); sig=lr.rolling(1800,min_periods=300).std().shift(1)      # per-second vol, causal
Phi=lambda z:0.5*(1+erf(z/sqrt(2)))
def book_grid(f,t0,t1):
    h=pd.read_parquet(f); bids={};asks={}; out={}; grid=t0
    for et,t,p,s,side,b,a in zip(h.event_type,h.t,h.price,h['size'],h.side,h.bids,h.asks):
        while grid<=t1 and t>=grid*1000:
            if bids and asks: out[grid]=(max(bids),min(asks))
            grid+=1
        if et=='snapshot':
            bids={float(x['price']):float(x['size']) for x in json.loads(b)}; asks={float(x['price']):float(x['size']) for x in json.loads(a)}
        elif et=='delta':
            d=bids if side=='BUY' else asks
            if s==0: d.pop(p,None)
            else: d[p]=s
    return out
rows=[]
for _,r in m.iterrows():
    f=glob.glob(f"{D}/history-{r.market_id}-*.parquet")
    if not f: continue
    t0=int(pd.Timestamp(r.open_time).timestamp()); t1=int(pd.Timestamp(r.close_time).timestamp())
    if t0 not in px.index or t1 not in px.index: continue
    g=book_grid(f[0],t0,t1); y=1.0 if r.winning_outcome=='Up' else 0.0
    S0=px[t0]
    for t in range(t0+15,t1-5):
        if t not in g: continue
        tau=t1-t; z=log(px[t]/S0)/(sig[t]*sqrt(tau)) if sig[t]>0 else 0
        rows.append((r.market_id,r.series,t,tau,Phi(z),g[t][0],g[t][1],y))
X=pd.DataFrame(rows,columns=['mk','series','t','tau','p','bid','ask','y']); X['mid']=(X.bid+X.ask)/2
print('markets',X.mk.nunique(),'obs',len(X),' Up-token check corr(mid,y)=',round(X[['mid','y']].corr().iloc[0,1],2))
# 1) Information test: Brier of market mid vs model vs blend, and does model add info beyond mid? (per-market clustered)
b=lambda q:((q-X.y)**2).groupby(X.mk).mean().mean()
print(f"Brier mid={b(X.mid):.4f} model={b(X.p):.4f} blend50={b((X.mid+X.p)/2):.4f}")
# 2) Trading test
fee=lambda q:0.07*q*(1-q)
res=[]
for L in [0,1,3,5]:
    Y=X.copy(); Y[['bidL','askL']]=Y.groupby('mk')[['bid','ask']].shift(-L)
    for th in [0.02,0.05,0.10]:
        pnl=[]
        for mk,gm in Y.dropna().groupby('mk'):
            up=gm[gm.p-gm.askL-fee(gm.askL)>th]; dn=gm[(1-gm.p)-(1-gm.bidL)-fee(1-gm.bidL)>th]
            c=[]
            if len(up): u=up.iloc[0]; c.append((u.t,(u.y-u.askL-fee(u.askL))/u.askL))
            if len(dn): d_=dn.iloc[0]; q=1-d_.bidL; c.append((d_.t,((1-d_.y)-q-fee(q))/q))
            if c: pnl.append(min(c)[1])
        pnl=np.array(pnl)
        res.append(dict(latency_s=L,threshold=th,n=len(pnl),ret_per_usd=pnl.mean() if len(pnl) else np.nan,
                        t=pnl.mean()/pnl.std()*np.sqrt(len(pnl)) if len(pnl)>2 else np.nan,hit=(pnl>0).mean() if len(pnl) else np.nan))
print(pd.DataFrame(res).round(3).to_string(index=False)); print('trials=',len(res))
