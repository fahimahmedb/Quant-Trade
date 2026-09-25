import pandas as pd, numpy as np
df=pd.read_parquet('markout.parquet')
df['ev2']=df.ev.str.split('-2026').str[0].str.replace('bitcoin-5m-15m-hourly','btc-updown')
for h in [60,300]: df[f'mo{h}']=df.d*(df.p-df[f'm{h}'])*100
df['hs']=df.d*(df.p-df.m0)*100
df['big']=df.s>=df.groupby('ev2').s.transform(lambda x:x.quantile(.9))
rows=[]
for ev,g in list(df.groupby('ev2'))+[('ALL',df)]:
    r={'ev':ev}
    for c in ['hs','mo60','mo300']:
        x=g.dropna(subset=[c]); per=x.groupby('mkt')[c].mean()
        r[c+'_trade']=round(x[c].mean(),2); r[c+'_shw']=round(np.average(x[c],weights=x.s),2)
        r[c+'_mktT']=round(per.mean()/(per.std()/np.sqrt(len(per))),1)
    x=g.dropna(subset=['mo300']); r['mo300_top10%size']=round(x[x.big].mo300.mean(),2); r['mo300_rest']=round(x[~x.big].mo300.mean(),2)
    rows.append(r)
pd.set_option('display.width',250); print(pd.DataFrame(rows).to_string(index=False))
