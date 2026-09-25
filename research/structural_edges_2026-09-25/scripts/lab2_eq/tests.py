import pandas as pd, numpy as np
from scipy import stats
df=pd.read_csv('/home/user/Quant-Trade/data/datasets/us_sector_etf_daily.csv',parse_dates=['date'])
P={s:g.set_index('date').sort_index() for s,g in df.groupby('symbol')}
def prep(s):
    d=P[s].copy(); f=d.adj_close/d.close
    d['cc']=d.adj_close.pct_change()
    d['on']=(d.open*f)/(d.close.shift(1)*f.shift(1))-1   # close t-1 -> open t
    d['id']=d.close/d.open-1                              # open->close t
    return d
spy=prep('SPY'); tlt=prep('TLT')
def rep(name,x,cost_bps_per_trade=0,trades_per_obs=1.0):
    x=pd.Series(x).dropna(); n=len(x); m=x.mean()*1e4; t=stats.ttest_1samp(x,0).statistic
    net=m-cost_bps_per_trade*trades_per_obs
    tn=net/ (x.std()*1e4/np.sqrt(n))
    print(f"{name:55s} n={n:5d} mean={m:7.2f}bp t={t:5.2f} | net({cost_bps_per_trade}bp)={net:7.2f}bp t_net={tn:5.2f}")
    return x
# split halves
H1=spy.index<'2021-09-01'
print("=== 1. Overnight vs intraday SPY ===")
rep("overnight all",spy.on,2,1); rep("intraday all",spy.id,2,1)
rep("overnight 2016-21",spy.on[H1]); rep("overnight 2021-26",spy.on[~H1])
print("=== 2. LETF rebalancing proxy: big day-t cc move, next ON and next ID signed by day-t direction ===")
sig=np.sign(spy.cc)
for q in [0.8,0.9,0.95]:
    thr=spy.cc.abs().rolling(250,min_periods=120).quantile(q).shift(1)
    big=spy.cc.abs()>thr
    on_next=(sig*spy.on.shift(-1))[big]; id_next=(sig*spy.id.shift(-1))[big]; cc_next=(sig*spy.cc.shift(-1))[big]
    rep(f"q{q} continuation next overnight (signed)",on_next,2,1)
    rep(f"q{q} continuation next intraday (signed)",id_next,2,1)
    rep(f"q{q} continuation next close-close (signed)",cc_next,2,1)
    # intraday same-day move: open-to-close signed by overnight gap? the 'last-hour' proxy: id signed by sign(on) on big-gap days
thr=spy.on.abs().rolling(250,min_periods=120).quantile(0.9).shift(1)
big=spy.on.abs()>thr
rep("big overnight gap (q0.9): same-day intraday signed by gap",(np.sign(spy.on)*spy.id)[big],2,1)
print("=== 3. Turn of month (long close of TD-1 to close of TD+3) ===")
s=spy.copy(); s['ym']=s.index.to_period('M')
s['tdm']=s.groupby('ym').cumcount()+1; s['tdr']=s.groupby('ym').cumcount(ascending=False)+1
tom=(s.tdr==1)|(s.tdm<=3)   # daily returns earned on last day and first 3 days (entry close TD-2)
rep("TOM days daily cc (last day + first 3)",s.cc[tom]); rep("non-TOM days daily cc",s.cc[~tom])
print("welch TOM vs other t=%.2f"%stats.ttest_ind(s.cc[tom].dropna(),s.cc[~tom].dropna(),equal_var=False).statistic)
# per-trade window returns
g=[]
ym=s.ym.unique()
for i in range(1,len(ym)):
    prev=s[s.ym==ym[i-1]]; cur=s[s.ym==ym[i]]
    if len(prev)<3 or len(cur)<3: continue
    e=prev.adj_close.iloc[-2]; x=cur.adj_close.iloc[2]; g.append((cur.index[2],x/e-1))
g=pd.Series(dict(g))
rep("TOM per-trade (4d hold), 2bp RT cost",g,2,1)
rep("TOM per-trade 2016-21",g[g.index<'2021-09-01']); rep("TOM per-trade 2021-26",g[g.index>='2021-09-01'])
# benchmark: random 4-day windows
r4=spy.adj_close.pct_change(4).dropna(); rep("any 4-day window (unconditional)",r4)
print("=== 4. Pension rebalancing (Harvey et al): SPY-TLT month-to-date spread -> SPY last 2 days of month ===")
m=pd.DataFrame({'spy':spy.adj_close,'tlt':tlt.adj_close}); m['ym']=m.index.to_period('M')
out=[]
for k,gg in m.groupby('ym'):
    if len(gg)<10: continue
    # MTD up to close of TD(-3), trade last 2 days close(-3)->close(-1)
    base_s=m.spy[m.index<gg.index[0]].iloc[-1] if (m.index<gg.index[0]).any() else None
    if base_s is None: continue
    base_t=m.tlt[m.index<gg.index[0]].iloc[-1]
    spread=(gg.spy.iloc[-3]/base_s)-(gg.tlt.iloc[-3]/base_t)
    ret=gg.spy.iloc[-1]/gg.spy.iloc[-3]-1
    retd=ret-(gg.tlt.iloc[-1]/gg.tlt.iloc[-3]-1)
    out.append((gg.index[-1],spread,ret,retd,k.month%3==0))
o=pd.DataFrame(out,columns=['d','spread','ret','retd','qe']).set_index('d')
sgn=-np.sign(o.spread)
rep("signal -sign(spread)*SPY last2d",sgn*o.ret,2,1)
rep("signal -sign(spread)*(SPY-TLT) last2d",sgn*o.retd,4,1)
big=o.spread.abs()>o.spread.abs().median()
rep("  |spread|>median, SPY-TLT",(sgn*o.retd)[big],4,1)
rep("  quarter-ends only, SPY-TLT",(sgn*o.retd)[o.qe],4,1)
print("corr(spread,retd)=%.3f"%o.spread.corr(o.retd))
print("=== 5. FOMC ===")
F="""2016-09-21 2016-11-02 2016-12-14 2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08 2018-12-19 2019-01-30 2019-03-20 2019-05-01 2019-06-19 2019-07-31 2019-09-18 2019-10-30 2019-12-11
2020-01-29 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16 2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14 2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18 2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29""".split()
F=pd.to_datetime(F); F=F[F.isin(spy.index)]
print("n FOMC",len(F))
rep("FOMC day cc (incl post-2pm)",spy.cc.loc[F],2,1)
rep("FOMC day overnight (pre-announcement part)",spy.on.loc[F],2,1)
prev=[spy.index[spy.index.get_loc(d)-1] for d in F]
rep("day before FOMC cc",spy.cc.loc[prev],2,1)
rep("non-FOMC day cc",spy.cc.drop(F))
