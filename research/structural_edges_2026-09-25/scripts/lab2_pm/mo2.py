import pandas as pd, numpy as np
df=pd.read_parquet('markout.parquet')
print('side check: BUY at/above ask frac', (df[df.d==1].atask).mean().round(3),' SELL at/below bid frac',(df[df.d==-1].atbid).mean().round(3), ' BUY at bid', (df[df.d==1].atbid).mean().round(3))
df['hs']=df.d*(df.p-df.m0)*100
for h in [5,60,300,1800]: df[f'mo{h}']=df.d*(df.p-df[f'm{h}'])*100
df['moS']=df.d*(df.p-df.settle)*100
rate={'mlb-2026-07-05':.05,'counter-strike-2026-09-10':.05,'world-cup-final-2026-07-19':.05,'ufc-330-2026-08-16':.05,'nyc-weather-2026-07-16':.05,'apple-weekly-2026-06-12':.04,'bitcoin-5m-15m-hourly-2026-06-15':.07}
df['takerfee']=df.ev.map(rate)*df.p*(1-df.p)*100
df['w']=df.s
def wm(g,c):
    x=g[[c,'w','mkt']].dropna(); 
    if len(x)==0: return np.nan,np.nan
    mu=np.average(x[c],weights=x.w)
    # cluster t by market
    per=x.groupby('mkt').apply(lambda z: np.average(z[c],weights=z.w)); t=per.mean()/(per.std(ddof=1)/np.sqrt(len(per))) if len(per)>2 else np.nan
    return mu,t
out=[]
df['ev2']=df.ev.str.split('-2026').str[0]
df.loc[(df.ev2=='bitcoin-5m-15m-hourly'),'ev2']='btc-updown'
for ev,g in list(df.groupby('ev2'))+[('ALL',df)]:
    r={'ev':ev,'trades':len(g),'mkts':g.mkt.nunique(),'med_spread_c':round(g.spr.median()*100,2)}
    for c in ['hs','mo5','mo60','mo300','mo1800','moS']:
        mu,t=wm(g,c); r[c]=f'{mu:+.2f}({t:+.1f})'
    r['takerfee_c']=round(np.average(g.takerfee,weights=g.w),2)
    out.append(r)
print(pd.DataFrame(out).to_string(index=False))
# pre-event vs in-play for sports: use tte? close_time is end; skip. Split by price bucket ALL
df['pb']=pd.cut(df.p,[0,.1,.3,.7,.9,1])
print(df.groupby('pb',observed=True).apply(lambda g: pd.Series({'n':len(g),'hs':np.average(g.hs,weights=g.w),'mo60':np.average(g.mo60.fillna(0),weights=g.w),'moS':np.average(g.moS.dropna(),weights=g.w[g.moS.notna()])})).round(2))
