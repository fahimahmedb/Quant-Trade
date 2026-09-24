import sys; sys.path.insert(0,'.')
from crypto_edges import *
perp, spot, fund, turn, mp = load_bybit()
pairs=[s for s in perp if s in fund and mp.get(s) in spot]
P=pd.DataFrame({s:perp[s] for s in pairs}); S=pd.DataFrame({s:spot[mp[s]] for s in pairs})
F=pd.DataFrame({s:fund[s] for s in pairs}).reindex(P.index).fillna(0.0); T=pd.DataFrame({s:turn[s] for s in pairs}).reindex(P.index)
B=np.log(P/S); avail=P.notna()&S.notna(); F=F.where(avail)
print('median |basis|', B.abs().median().describe())
trail=F.rolling(7,min_periods=7).sum()/7*365; liq=T.rolling(30,min_periods=20).mean()
fu=[];ba=[];to=[];names=[]
W=None;wp=pd.Series(0.0,index=pairs)
for i,d in enumerate(P.index[:-1]):
    if i%7==0:
        ok=avail.loc[d]&avail.iloc[i+1]; el=trail.loc[d][ok&(liq.loc[d]>2e6)].dropna(); top=el[el>0.1].nlargest(10)
        W=pd.Series(0.0,index=pairs); W[top.index]=0.1; names+=list(top.index)
    fu.append((W*F.shift(-1).loc[d].fillna(0)).sum()); ba.append(-(W*(B.shift(-1)-B).loc[d].fillna(0)).sum()); to.append((W-wp).abs().sum()); wp=W
n=len(fu)/365
print('ann funding %.1f%% basis %.1f%% turnover/yr %.1f cost %.1f%% (per unit notional)'%(sum(fu)/n*100,sum(ba)/n*100,sum(to)/n,sum(to)/n*0.00305*100))
idx=P.index[:-1]
s=pd.DataFrame({'f':fu,'b':ba},index=idx); print(s.groupby(s.index.year).sum()*100)
print(pd.Series(names).value_counts().head(10))
