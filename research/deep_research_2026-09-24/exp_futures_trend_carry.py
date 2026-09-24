# Trend (EWMAC) + carry on the pysystemtrade futures panel (public, git clone github.com/pst-group/pysystemtrade).
# Causal: forecasts from data through day t, position held on t+1. Costs from spreadcosts.csv (half spread per unit traded).
import pandas as pd, numpy as np, glob, os, sys, warnings; warnings.filterwarnings('ignore')
ROOT=sys.argv[1] if len(sys.argv)>1 else 'pst/data/futures'
cfg=pd.read_csv(f'{ROOT}/csvconfig/instrumentconfig.csv').set_index('Instrument')
sc=pd.read_csv(f'{ROOT}/csvconfig/spreadcosts.csv').set_index('Instrument').iloc[:,0]
def mon(c): c=int(c)//100; return (c//100)*12+c%100
R={};T={};C={};K={}
for f in sorted(glob.glob(f'{ROOT}/adjusted_prices_csv/*.csv')):
    ins=os.path.basename(f)[:-4]
    if any(x in ins.lower() for x in ['_micro','_mini','_small','_e-mini']): continue   # avoid duplicate exposures
    p=pd.read_csv(f,index_col=0,parse_dates=True).price
    p=p.groupby(p.index.normalize()).last().loc['1980':]
    if len(p)<750: continue
    d=p.diff(); sig=d.ewm(span=35).std()
    sig=sig.clip(lower=0.2*sig.rolling(512,min_periods=60).median()).replace(0,np.nan)  # vol floor: stale/flat prices otherwise give inf
    s=sig.shift(1)
    R[ins]=(d/s).clip(-15,15)                        # return of 1 unit of risk
    tr=sum((p.ewm(span=f).mean()-p.ewm(span=4*f).mean())/sig for f in (16,32,64))/3
    T[ins]=tr
    mp=f'{ROOT}/multiple_prices_csv/{ins}.csv'
    if os.path.exists(mp):
        m=pd.read_csv(mp,index_col=0,parse_dates=True); m=m.groupby(m.index.normalize()).last()
        yrs=(m.CARRY_CONTRACT.dropna().map(mon)-m.PRICE_CONTRACT.map(mon))/12
        ac=((m.PRICE-m.CARRY)/yrs).replace([np.inf,-np.inf],np.nan).ffill(limit=5)
        K[ins]=(ac.reindex(p.index).ffill(limit=5)/(sig*16)).ewm(span=90).mean()  # annual carry / annual vol
    C[ins]=1.3*sc.get(ins,np.nan)/2/sig   # half-spread +~30% for commissions (review fix)
R=pd.DataFrame(R);T=pd.DataFrame(T);K=pd.DataFrame(K).reindex(columns=R.columns);Cc=pd.DataFrame(C)
def norm(F):  # per-instrument causal scalar: forecast / expanding median |forecast| (robust to outliers), cap +-2
    s=F.abs().expanding(min_periods=250).median().shift(1)
    return (F/s).clip(-2,2)
def port(F,name):
    pos=F.shift(1); G=pos*R
    cc=Cc.fillna(Cc.stack().median())
    pnl=G-(pos.diff().abs()*cc).fillna(0).where(G.notna())-(8/256*pos.abs()*cc).fillna(0).where(G.notna())  # + ~4 rolls/yr x 2 legs
    n=pnl.notna().sum(axis=1); pr=pnl.sum(axis=1)/np.sqrt(n.clip(lower=1))  # equal risk, sqrt-N diversification scaling
    pr=pr[n>=5]
    f=lambda x:(lambda w:w.mean()/w.std()*np.sqrt(52))(x.resample('W').sum())  # weekly SR: daily rows include holidays (review fix)
    out={'SR':f(pr),'t':f(pr)*np.sqrt((pr.index[-1]-pr.index[0]).days/365.25),'N_avg':n[n>=5].mean()}
    for a,b in [('1980','1999'),('2000','2012'),('2013','2019'),('2020','2026')]: out[f'SR {a}-{b[2:]}']=f(pr[a:b])
    gross=G.sum(axis=1)[n>=5]/np.sqrt(n[n>=5]); out['cost_drag_SR']=f(gross)-out['SR']
    eq=(pr*0.10/np.sqrt(256)/pr.std()).cumsum(); out['MDD@10%vol']=(eq-eq.cummax()).min()
    return name,out
T=T.replace([np.inf,-np.inf],np.nan);K=K.replace([np.inf,-np.inf],np.nan).clip(-5,5);Cc=Cc.replace([np.inf,-np.inf],np.nan).clip(upper=1)
Tn=norm(T);Kn=norm(K)
rows=dict([port(Tn,'Trend EWMAC 16/32/64'),port(Kn,'Carry'),port(((Tn+Kn.fillna(0))/2),'Trend+Carry 50/50'),
           port(np.sign(T),'Trend sign only (binary)'),port(Tn.where(K.notna()),'Trend (same sample as carry)')])
print(pd.DataFrame(rows).T.round(2).to_string())
print('instruments used:',R.shape[1],' with carry:',K.notna().any().sum(),' span',R.index.min().date(),R.index.max().date())
# Breadth curve: SR of Trend+Carry on random subsets of N instruments (only instruments with data since 2000), 2000-2024
X=((Tn+Kn.fillna(0))/2); pos=X.shift(1); G=(pos*R).loc['2000':]
cc=Cc.fillna(Cc.stack().median()); pnl=(G-((pos.diff().abs()+8/256*pos.abs())*cc).fillna(0).loc['2000':].where(G.notna()))
ok=[c for c in pnl.columns if pnl[c].loc[:'2001'].notna().sum()>200]
rng=np.random.default_rng(1); f=lambda x:(lambda w:w.mean()/w.std()*np.sqrt(52))(x.resample('W').sum())
print('Breadth curve (Trend+Carry, 2000-2024, instruments live since 2000:',len(ok),')')
for N in [1,3,5,10,20,40,len(ok)]:
    srs=[f(pnl[list(rng.choice(ok,N,replace=False))].mean(axis=1).dropna()) for _ in range(40 if N<len(ok) else 1)]
    print(f'  N={N:3d}  median SR={np.median(srs):.2f}  p10={np.percentile(srs,10):.2f}  p90={np.percentile(srs,90):.2f}')
