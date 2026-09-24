# Vol-managed SPY (Moreira-Muir 2017): weight = target_var / forecast_var, capped at 2x; causal (decided at close t, held t+1).
import pandas as pd, numpy as np
D='research/deep_research_2026-09-24/'
d=pd.read_csv('data/datasets/us_sector_etf_daily.csv',parse_dates=['date'])
p=d[d.symbol=='SPY'].set_index('date').adj_close; r=p.pct_change().dropna()
v=pd.read_csv(D+'vix_daily.csv',parse_dates=['DATE']).set_index('DATE').CLOSE/100
COST=5e-4
def ev(w,name):
    w=w.reindex(r.index).ffill().clip(0,2); net=w.shift(1)*r-COST*w.diff().abs().shift(1)
    net=net.dropna(); sr=net.mean()/net.std()*np.sqrt(252); eq=(1+net).cumprod()
    h=len(net)//2; f=lambda x:x.mean()/x.std()*np.sqrt(252)
    print(f"{name:32s} SR={sr:.2f} SR1={f(net[:h]):.2f} SR2={f(net[h:]):.2f} MDD={(eq/eq.cummax()-1).min():.1%} avgW={w.mean():.2f}")
ev(pd.Series(1.0,index=r.index),'SPY buy&hold')
rv=r.rolling(21).std()*np.sqrt(252); tv=rv.expanding(252).median()   # causal target (full-sample median was look-ahead)
ev((tv/rv)**2,'VolManaged realized 21d (var)')
ev(tv/rv,'VolTarget realized 21d (vol)')
vx=v.reindex(r.index).ffill(); tvx=vx.expanding(252).median()
ev(tv/vx*(tvx/tv),'VolTarget VIX')
ev((vx<vx.rolling(252).quantile(0.8)).astype(float),'Out when VIX>80th pct 1y')
