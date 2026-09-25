import pickle, pandas as pd, numpy as np
res=pickle.load(open('negrisk.pkl','rb'))
for folder,ev,N,df in res:
    df=df.copy(); fee5=0.05*df.feeA1
    tot=df.dt.sum()
    netA=(1-df.Sa)-fee5  # approx fee: taker on all legs at best
    # sell-all via buying NO at 1-bid: fee uses (1-b)b same p(1-p) ; approximate with feeA1 proxy -> recompute not available; use same proxy
    netB=(df.Sb-1)-fee5
    for name,edge,q in [('buyAll',netA,df.qa),('sellAll',netB,df.qb)]:
        m=edge>0
        if not m.any(): print(f'{ev[:40]:40s} {name}: net>0 none'); continue
        d=df[m]
        # episodes
        mm=m.astype(int).values; st=np.where(np.diff(np.r_[0,mm])==1)[0]
        print(f'{ev[:40]:40s} {name}: net>0 time%={100*df.dt[m].sum()/tot:.2f} episodes={len(st)} medEdge={edge[m].median():.3f} med$cap/ep={np.median([ (edge*q).iloc[s] for s in st]):.2f} sum$ (first tick of each ep)={sum((edge*q).iloc[s] for s in st):.2f}')
    t0=pd.to_datetime(df.t,unit='ms')
    if 'Spain' in ev:
        m=df.Sb>1
        print(' Spain sellAll>1 by hour UTC:', pd.Series(m.values,index=t0).groupby(t0.dt.floor('15min').values).mean().round(2).to_dict())
