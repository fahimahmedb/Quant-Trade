import pandas as pd, numpy as np
d=pd.read_csv('data/datasets/us_sector_etf_daily.csv',parse_dates=['date'])
P=d.pivot(index='date',columns='symbol',values='adj_close').dropna()
O=d.pivot(index='date',columns='symbol',values='open').reindex(P.index)
C=d.pivot(index='date',columns='symbol',values='close').reindex(P.index)
R=P.pct_change().fillna(0)
SECT=['XLB','XLE','XLF','XLI','XLK','XLP','XLU','XLV','XLY']
COST=5e-4  # 5bp per unit turnover (ETF spread+slip, conservative for retail)
def run(W,name):
    W=W.reindex(R.index).ffill().fillna(0)
    Wl=W.shift(1).fillna(0)                 # decide at close t, hold t+1: causal
    gross=(Wl*R).sum(axis=1); to=(W-W.shift(1)).abs().sum(axis=1).shift(1).fillna(0)
    net=gross-COST*to
    return name,net,to
def stats(net,to):
    ann=252; sr=net.mean()/net.std()*np.sqrt(ann); eq=(1+net).cumprod()
    mdd=(eq/eq.cummax()-1).min(); cagr=eq.iloc[-1]**(ann/len(net))-1
    h=len(net)//2; s1=net[:h].mean()/net[:h].std()*np.sqrt(ann); s2=net[h:].mean()/net[h:].std()*np.sqrt(ann)
    return dict(SR=round(sr,2),CAGR=f"{cagr:.1%}",MDD=f"{mdd:.1%}",SR_1st=round(s1,2),SR_2nd=round(s2,2),TO_yr=round(to.mean()*ann,1),t=round(sr*np.sqrt(len(net)/ann),2))
res={}
# 1 baseline
res['SPY buy&hold']=run(pd.DataFrame({'SPY':1.0},index=R.index),'')
# 2 60/40-ish equal weight 12
res['EqualWeight 12 (monthly)']=run(pd.DataFrame(1/12,index=R.index,columns=R.columns).resample('ME').last().reindex(R.index).ffill(),'')
# vol
vol=R.rolling(60).std()*np.sqrt(252)
me=P.resample('ME').last()
# 3 TSMOM 12m vol-target 10%/asset /N
sig=np.sign(me.pct_change(12)).reindex(R.index).ffill()
W=(sig*(0.10/vol)/12).clip(-0.5,0.5); W=W.resample('ME').last().reindex(R.index).ffill()
res['TSMOM 12m long/short volT']=run(W,'')
W2=W.clip(lower=0); res['TSMOM 12m long-only volT']=run(W2,'')
# 4 SPY 200d SMA
f=(P.SPY>P.SPY.rolling(200).mean()).astype(float); res['SPY>SMA200 else cash']=run(pd.DataFrame({'SPY':f}),'')
# 5 Inverse-vol SPY/TLT/GLD
iv=(1/vol[['SPY','TLT','GLD']]); iv=iv.div(iv.sum(axis=1),axis=0).resample('ME').last().reindex(R.index).ffill()
res['InvVol SPY/TLT/GLD']=run(iv,'')
# 6 Sector XS momentum top3 of 9 (12-1)
m=me[SECT].shift(1).pct_change(11); rk=m.rank(1,ascending=False); Wx=(rk<=3).astype(float)/3; Wx[m.isna().any(axis=1)]=0
res['Sector mom top3 (12-1)']=run(Wx.reindex(R.index).ffill(),'')
# 7 Sector 1-week reversal: long bottom3 weekly
wk=P[SECT].resample('W-FRI').last(); r5=wk.pct_change(); rk=r5.rank(1); Wr=(rk<=3).astype(float)/3
res['Sector 1w reversal bottom3']=run(Wr.reindex(R.index).ffill(),'')
# 8 Turn of month SPY: last 1 + first 3 trading days
idx=R.index; mo=idx.to_period('M'); pos=pd.Series(range(len(idx)),index=idx)
first=pos.groupby(mo).transform('min'); last=pos.groupby(mo).transform('max')
k=pos-first; kl=last-pos
hold=((k<=2)|(kl==0)).astype(float)   # return day t held if in window; weights set at t-1 -> shift -1
res['SPY turn-of-month']=run(pd.DataFrame({'SPY':hold.shift(-1).fillna(0)}),'')
# 9 overnight vs intraday SPY (raw, ignoring divs)
on=(O.SPY/C.SPY.shift(1)-1).dropna(); intr=(C.SPY/O.SPY-1)
for nm,s in [('SPY overnight only (2 trades/day)',on-2*COST/2),('SPY intraday only',intr-2*COST/2)]:
    res[nm]=('',s.dropna(),pd.Series(2.0,index=s.index))
out=pd.DataFrame({k:stats(v[1],v[2]) for k,v in res.items()}).T
print(out.to_string()); print('N trials=',len(res),' sample',R.index[0].date(),R.index[-1].date())
