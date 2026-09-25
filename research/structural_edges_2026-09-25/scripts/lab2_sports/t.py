import pandas as pd, numpy as np, glob, os, warnings; warnings.filterwarnings("ignore")
B='sf/data/raw/football_data'
fr=[]
for f in sorted(glob.glob(B+'/*/*.csv')):
    s=f.split('/')[-2]
    try: d=pd.read_csv(f,encoding='latin1',on_bad_lines='skip')
    except Exception as e: print(f,e); continue
    d.columns=[c.replace('﻿','').replace('ï»¿','') for c in d.columns]
    for o in 'HDA':
        if 'Max'+o not in d and 'BbMx'+o in d: d['Max'+o]=d['BbMx'+o]
    d=d.copy(); d['season']=s; fr.append(d)
d=pd.concat(fr,ignore_index=True); d=d[d.FTR.isin(list('HDA'))].copy()
print('matches',len(d), 'leagues',d.Div.nunique())
def fair(cols,method='mult'):
    O=d[cols].apply(pd.to_numeric,errors='coerce').values; q=1/O
    if method=='mult': return q/q.sum(1,keepdims=True)
    # power method: find k with sum q^k=1
    k=np.ones(len(q))
    for _ in range(60):
        s=np.nansum(q**k[:,None],1); ds=np.nansum(q**k[:,None]*np.log(q),1)
        k=k-(s-1)/ds
    return q**k[:,None]
def num(c): return pd.to_numeric(d[c],errors='coerce').values if c in d else np.full(len(d),np.nan)
win=np.stack([(d.FTR==o).values for o in 'HDA'],1).astype(float)
def run(name,price_pref,fair_cols,X,comm=0.0,clv_cols=None,method='mult',out=[]):
    P=np.stack([num(price_pref+o) if not price_pref.endswith('>') else None for o in 'HDA'],1)
    p=fair(fair_cols,method)
    Pn=1+(P-1)*(1-comm)
    edge=Pn*p-1
    m=(edge>X)&np.isfinite(edge)&(P>1)
    ret=np.where(win==1,Pn-1,-1.0)[m]
    res={'test':name,'X':X,'n':int(m.sum()),'ROI%':100*ret.mean() if m.sum() else np.nan,
         't':ret.mean()/ret.std()*np.sqrt(len(ret)) if m.sum()>2 else np.nan,'edge%':100*edge[m].mean()}
    if clv_cols:
        pc=fair(clv_cols,method); res['CLV%']=100*np.nanmean((Pn*pc-1)[m])
    ss=pd.Series(ret,index=np.repeat(np.asarray(d.season,dtype=object)[:,None],3,1)[m])
    g=ss.groupby(level=0).agg(['mean','size'])
    res['seasons+']=f"{(g['mean']>0).sum()}/{len(g)}"
    res['seas']=' '.join(f"{i}:{100*r['mean']:+.1f}" for i,r in g.iterrows())
    out.append(res); return res
PO=['PSH','PSD','PSA']; PC=['PSCH','PSCD','PSCA']
R=[]
for X in [0,0.02,0.05]:
    run('B365open vs PinOpen fair (causal)','B365',PO,X,clv_cols=PC,out=R)
    run('MaxOpen vs PinOpen fair (causal)','Max',PO,X,clv_cols=PC,out=R)
    run('AvgOpen vs PinOpen fair (causal)','Avg',PO,X,clv_cols=PC,out=R)
    run('B365open vs PinClose fair (hindsight/CLV check)','B365',PC,X,out=R)
    run('B365close vs PinClose fair','B365C',PC,X,out=R)
    run('MaxClose vs PinClose fair','MaxC',PC,X,out=R)
    run('BFExch close (2%comm) vs PinClose','BFEC',PC,X,comm=0.02,out=R)
    run('BFExch open (2%comm) vs PinOpen','BFE',PO,X,comm=0.02,clv_cols=PC,out=R)
for X in [0.02]:
    run('MaxOpen vs PinOpen POWER devig','Max',PO,X,clv_cols=PC,method='power',out=R)
    run('MaxClose vs PinClose POWER devig','MaxC',PC,X,method='power',out=R)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',200)
r=pd.DataFrame(R); print(r.drop(columns='seas').round(2).to_string())
print(r[r.X==0.02][['test','seas']].to_string())
# Pinnacle open vs close: flat bets on all, log loss
for pref,cols in [('PS',PO),('PSC',PC)]:
    P=np.stack([num(c) for c in cols],1); ok=np.isfinite(P).all(1)
    ret=np.where(win==1,P-1,-1)[ok]; p=fair(cols)[ok]
    ll=-np.mean(np.log((p*win[ok]).sum(1)))
    print(pref,'n',ok.sum(),'flat ROI all sels %.2f%%'%(100*ret.mean()),'logloss %.5f'%ll,'margin %.2f%%'%(100*np.nanmean((1/P[ok]).sum(1)-1)))
# CLV of Pinnacle opening prices vs Pinnacle close; open-price moves predictive? bet side where open fair > close? (hindsight) ; realized ROI by CLV bucket
Po=np.stack([num(c) for c in PO],1); pc=fair(PC); clv=Po*pc-1
ret=np.where(win==1,Po-1,-1.0)
ok=np.isfinite(clv)
b=pd.cut(clv[ok],[-1,-0.05,-0.02,0,0.02,0.05,1])
print(pd.DataFrame({'b':b,'r':ret[ok],'c':clv[ok]}).groupby('b',observed=True).agg(n=('r','size'),ROI=('r','mean'),CLV=('c','mean')).round(4))
# favourite-longshot bias in Pinnacle close
pc_=fair(PC); Pcl=np.stack([num(c) for c in PC],1); r2=np.where(win==1,Pcl-1,-1.0); ok=np.isfinite(Pcl)
bb=pd.cut(Pcl[ok],[1,1.5,2,3,5,8,15,100])
print(pd.DataFrame({'b':bb,'r':r2[ok]}).groupby('b',observed=True).r.agg(['size','mean']).round(4))
# O/U 2.5
if True:
    over=((d.FTHG+d.FTAG)>2.5).astype(float).values; W=np.stack([over,1-over],1)
    for nm,pr,fc,cc in [('OU MaxOpen vs PinOpen',['Max>2.5','Max<2.5'],['P>2.5','P<2.5'],['PC>2.5','PC<2.5']),('OU MaxClose vs PinClose',['MaxC>2.5','MaxC<2.5'],['PC>2.5','PC<2.5'],None),('OU B365open vs PinOpen',['B365>2.5','B365<2.5'],['P>2.5','P<2.5'],['PC>2.5','PC<2.5'])]:
        for X in [0.02,0.05]:
            P=np.stack([num(c) for c in pr],1); p=fair(fc); e=P*p-1; m=(e>X)&np.isfinite(e); rr=np.where(W==1,P-1,-1)[m]
            s=f"{nm} X={X} n={m.sum()} ROI={100*rr.mean():.2f}% t={rr.mean()/rr.std()*np.sqrt(len(rr)):.2f}"
            if cc: s+=f" CLV={100*np.nanmean((P*fair(cc)-1)[m]):.2f}%"
            print(s)
