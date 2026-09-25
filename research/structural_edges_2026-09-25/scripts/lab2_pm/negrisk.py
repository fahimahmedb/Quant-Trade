import sys, pandas as pd, numpy as np, pickle
from book import replay, D
def fee(p, rate):  # Polymarket-style taker fee per share: rate*p*(1-p)  (assumption; param)
    return rate*p*(1-p)
groups=[('nyc-weather-2026-07-16',None),('apple-weekly-2026-06-12',None),('world-cup-final-2026-07-19','Exact Score')]
res=[]
for folder,flt in groups:
    m=pd.read_csv(D+folder+'/markets.csv')
    if flt: m=m[m.event.str.contains(flt)]
    for ev,g in m.groupby('event'):
        series={}
        for r in g.itertuples():
            rows,_=replay(D+folder+'/'+r.file,K=10)
            series[r.market_id]=rows
        ids=list(series)
        # union timeline
        ts=sorted(set(t for s in series.values() for (t,_,_,_) in s))
        idx={k:0 for k in ids}; cur={k:None for k in ids}
        recs=[]
        for t in ts:
            for k in ids:
                s=series[k]; i=idx[k]
                while i<len(s) and s[i][0]<=t:
                    cur[k]=s[i]; i+=1
                idx[k]=i
            if any(cur[k] is None for k in ids): continue
            asks=[cur[k][3] for k in ids]; bids=[cur[k][2] for k in ids]
            if all(len(a)>0 for a in asks):
                Sa=sum(a[0][0] for a in asks); qa=min(a[0][1] for a in asks)
            else: Sa=np.nan; qa=0
            if all(len(b)>0 for b in bids):
                Sb=sum(b[0][0] for b in bids); qb=min(b[0][1] for b in bids)
            else: Sb=np.nan; qb=0
            # ladder walk for buy-all: increase q in steps until marginal cost>=1
            prof_walk=0.0; 
            if Sa==Sa and Sa<1:
                lad=[list(a) for a in asks]; ptr=[0]*len(lad); rem=[lad[j][0][1] for j in range(len(lad))]
                while True:
                    try: pr=[lad[j][ptr[j]][0] for j in range(len(lad))]
                    except IndexError: break
                    c=sum(pr)
                    if c>=1: break
                    step=min(rem); prof_walk+=(1-c)*step
                    for j in range(len(lad)):
                        rem[j]-=step
                        if rem[j]<=1e-9:
                            ptr[j]+=1
                            if ptr[j]<len(lad[j]): rem[j]=lad[j][ptr[j]][1]
                            else: rem[j]=0
                    if any(ptr[j]>=len(lad[j]) for j in range(len(lad))): break
            feeA = sum(fee(a[0][0],1.0) for a in asks) if Sa==Sa else np.nan  # per share at rate=1; scale later
            recs.append((t,Sa,qa,Sb,qb,prof_walk,feeA))
        df=pd.DataFrame(recs,columns=['t','Sa','qa','Sb','qb','prof_walk','feeA1'])
        df['dt']=df.t.shift(-1).fillna(df.t.iloc[-1]).sub(df.t)/1000
        res.append((folder,ev,len(ids),df))
        tot=df.dt.sum()
        def ep(mask):
            m=mask.astype(int).values; starts=np.where(np.diff(np.r_[0,m])==1)[0]; ends=np.where(np.diff(np.r_[m,0])==-1)[0]
            durs=[df.t.iloc[min(e+1,len(df)-1)]/1000-df.t.iloc[s]/1000 for s,e in zip(starts,ends)]
            return len(starts), (np.median(durs) if durs else np.nan)
        A=df.Sa<1; B=df.Sb>1
        na,da=ep(A); nb,db=ep(B)
        print(f"{ev[:45]:45s} N={len(ids)} hrs={tot/3600:.1f} medSa={df.Sa.median():.3f} medSb={df.Sb.median():.3f} "
              f"buyAll:<1 time%={100*df.dt[A].sum()/tot:.2f} episodes={na} medDur={da:.1f}s maxEdge={1-df.Sa.min():.3f} "
              f"$atBest(max)={(df[A].qa*(1-df[A].Sa)).max() if A.any() else 0:.2f} $walk(max)={df.prof_walk.max():.2f} | "
              f"sellAll:>1 time%={100*df.dt[B].sum()/tot:.2f} episodes={nb} medDur={db:.1f}s maxEdge={df.Sb.max()-1:.3f} $atBest(max)={(df[B].qb*(df[B].Sb-1)).max() if B.any() else 0:.2f}",flush=True)
pickle.dump(res,open('negrisk.pkl','wb'))
