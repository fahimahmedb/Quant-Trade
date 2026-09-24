import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
s=pd.read_csv('research/deep_research_2026-09-24/shiller_sp500_monthly.csv',parse_dates=['Date']).set_index('Date')
s=s[s.Dividend>0]
p=s.SP500; r=p.pct_change()+s.Dividend/12/p.shift(1)
cash=(s['Long Interest Rate']/100/12).shift(1)   # crude: long rate as cash proxy (overstates cash)
cash_tb=cash*0.6                                  # haircut proxy for T-bill
def st(x):
    x=x.dropna(); ex=x-cash_tb.reindex(x.index)
    sr=ex.mean()/ex.std()*np.sqrt(12); eq=(1+x).cumprod(); mdd=(eq/eq.cummax()-1).min()
    return sr,mdd
# Shiller prices are monthly AVERAGES -> an extra lag is mandatory to avoid spurious autocorrelation
LAG=2
sig_sma=(p>p.rolling(10).mean()).astype(float).shift(LAG)
sig_ts=(p.pct_change(12)>0).astype(float).shift(LAG)
cost=0.001
strats={'Buy&hold':r,
 'SMA10 timing':sig_sma*r+(1-sig_sma)*cash_tb-cost*sig_sma.diff().abs(),
 'TSMOM12 timing':sig_ts*r+(1-sig_ts)*cash_tb-cost*sig_ts.diff().abs()}
eras=[('1872','1913'),('1914','1945'),('1946','1981'),('1982','2007'),('2008','2026')]
rows={}
for k,v in strats.items():
    row={'SR_full':st(v)[0],'MDD':st(v)[1]}
    for a,b in eras: row[f'SR {a}-{b[2:]}']=st(v[a:b])[0]
    rows[k]=row
print(pd.DataFrame(rows).T.round(2).to_string())
# Power: years needed to reject SR=0 at t=2 for true SR
print('Years of data for t=2 given true annual SR:',{sr:round((2/sr)**2,1) for sr in [0.3,0.5,1,2,3]})
# Bootstrap: P(sub-10y SR<0) for SMA10 excess vs buy&hold
d=(strats['SMA10 timing']-strats['Buy&hold']).dropna().values
rng=np.random.default_rng(0);n=120
b=[d[i:i+n].mean() for i in rng.integers(0,len(d)-n,4000)]
print('SMA10 minus B&H: share of random 10y windows where timing lost:',round(np.mean(np.array(b)<0),2))
