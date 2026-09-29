import json, glob, statistics as st, datetime as dt, csv, random, sys
P=json.load(open('nmr_coingecko_365d.json'))['prices']
px={}
for t,v in P: px.setdefault(dt.datetime.utcfromtimestamp(t/1000).date().isoformat(),v)  # first (00:00 UTC) print per day
def price(d): return px[d]
def mean_price(a,b): return st.mean(v for k,v in px.items() if a<=k<=b)
WIN={8:('2026-02-27','2026-09-28'),11:('2026-01-02','2026-09-28')}
TIERS=[('<$500',0,500),('$500-2k',500,2000),('$2k-10k',2000,10000),('>$10k',10000,1e18)]
def f(x): return float(x) if x not in (None,'') else 0.0
def q(v,p): 
    v=sorted(v); 
    if not v: return None
    k=(len(v)-1)*p; i=int(k); j=min(i+1,len(v)-1); return v[i]+(v[j]-v[i])*(k-i)
out={}
allrows=[]
for t in (8,11):
    files=sorted(glob.glob('rounds/t%d_r*.json'%t),key=lambda s:int(s.split('_r')[1].split('.')[0]))
    rounds=[json.load(open(fn)) for fn in files]
    if not rounds: continue
    nums=[r['roundNumber'] for r in rounds]; R=len(nums); mid=nums[R//2]
    a,b=WIN[t]; pm=mean_price(a,b); p0=price(a); p1=price(b); pnow=P[-1][1]
    M={}
    missing_settled=0
    for r in rounds:
        n=r['roundNumber']
        for m in r['models']:
            s=f(m['selectedStakeValue']); 
            if m['payoutSettled'] is None and m['payoutPending'] is not None: missing_settled+=1
            pay=f(m['payoutSettled']) if m['payoutSettled'] is not None else f(m['payoutPending'])
            if s<=0 and pay==0: continue
            d=M.setdefault(m['modelName'],{'stakes':[],'pay':0,'neg':0,'pos':0,'h1':0,'h2':0,'s1':[],'s2':[],'first':n,'last':n})
            d['stakes'].append(s); d['pay']+=pay; d['neg']+=pay<0; d['pos']+=pay>0
            d['first']=min(d['first'],n); d['last']=max(d['last'],n)
            if n<mid: d['h1']+=pay; d['s1'].append(s)
            else: d['h2']+=pay; d['s2'].append(s)
    rows=[]
    for name,d in M.items():
        st_=[x for x in d['stakes'] if x>0]
        if not st_: continue
        ms=st.mean(st_); usd=ms*pm
        tier=[tn for tn,lo,hi in TIERS if lo<=usd<hi][0]
        full=len(st_)>=0.9*R
        r_n=d['pay']/ms
        r1=d['h1']/st.mean([x for x in d['s1'] if x>0]) if any(x>0 for x in d['s1']) else None
        r2=d['h2']/st.mean([x for x in d['s2'] if x>0]) if any(x>0 for x in d['s2']) else None
        rows.append(dict(tournament=t,model=name,tier=tier,rounds_staked=len(st_),window_rounds=R,full_window=full,mean_stake_nmr=ms,mean_stake_usd=usd,
            payout_sum_nmr=d['pay'],payout_sum_usd_at_mean_px=d['pay']*pm,ret_nmr=r_n,neg_rounds=d['neg'],pos_rounds=d['pos'],
            ret_usd_hold=(1+r_n)*p1/p0-1 if full else None,ret_usd_hold_now=(1+r_n)*pnow/p0-1 if full else None,ret_h1=r1,ret_h2=r2,first_round=d['first'],last_round=d['last']))
    out[t]=dict(rows=rows,R=R,first=nums[0],last=nums[-1],mid=mid,pm=pm,p0=p0,p1=p1,pnow=pnow,missing_settled=missing_settled,
        tot_payout=sum(f(r['totalPayout']) for r in rounds),mean_at_stake=st.mean(f(r['totalAtStake']) for r in rounds),
        pf=(min(f(r['payoutFactor']) for r in rounds),max(f(r['payoutFactor']) for r in rounds)),
        stakes_per_round=(min(r['totalStakes'] for r in rounds),max(r['totalStakes'] for r in rounds)), mult=rounds[-1]['payoutMultipliers'])
    allrows+=rows
json.dump({str(k):{kk:vv for kk,vv in v.items() if kk!='rows'} for k,v in out.items()},open('census_meta.json','w'),indent=1)
with open('per_model_results.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(allrows[0].keys())); w.writeheader(); [w.writerow(r) for r in allrows]
def pct(x): return '%.1f%%'%(100*x) if x is not None else 'NA'
for t,o in out.items():
    rows=o['rows']
    print('\n######## TOURNAMENT',t,'rounds',o['first'],'-',o['last'],'R=',o['R'],'mid',o['mid'],'meanpx %.3f p0 %.3f p1 %.3f pnow %.3f'%(o['pm'],o['p0'],o['p1'],o['pnow']))
    print('platform window return (sum totalPayout/mean totalAtStake) %.2f%%'%(100*o['tot_payout']/o['mean_at_stake'])); print('pf range',o['pf'],'stakes/round',o['stakes_per_round'],'mean totalAtStake %.0f'%o['mean_at_stake'],'sum totalPayout %.1f'%o['tot_payout'],'missing_settled',o['missing_settled'],o['mult'])
    ms=sorted(r['mean_stake_nmr'] for r in rows)
    print('N models staked>=1 round',len(rows),'full-window',sum(r['full_window'] for r in rows),'sum model payouts %.1f'%sum(r['payout_sum_nmr'] for r in rows))
    print('mean-stake quantiles NMR p10..p90',[round(q(ms,p),2) for p in (.1,.25,.5,.75,.9,.99)],'max %.0f'%ms[-1])
    for sub in ('all','full'):
        print('--',sub)
        print('tier N fracPos medRet meanRet p25 p75 medPayNMR medPayUSD medNegRnds medRndsStaked | medUSDhold fracPosUSD')
        for tn,lo_,hi_ in TIERS+[('  sub:<$50 dust',0,50),('  sub:$50-500',50,500)]:
            g=[r for r in rows if lo_<=r['mean_stake_usd']<hi_ and (sub=='all' or r['full_window'])]
            if not g: print(tn,0); continue
            rr=[r['ret_nmr'] for r in g]; pay=[r['payout_sum_nmr'] for r in g]
            uh=[r['ret_usd_hold'] for r in g if r['ret_usd_hold'] is not None]
            print(tn,len(g),pct(sum(1 for x in pay if x>0)/len(g)),pct(st.median(rr)),pct(st.mean(rr)),pct(q(rr,.25)),pct(q(rr,.75)),
                  '%.3f'%st.median(pay),'%.2f'%(st.median(pay)*o['pm']),st.median([r['neg_rounds'] for r in g]),st.median([r['rounds_staked'] for r in g]),'|',
                  pct(st.median(uh)) if uh else 'NA', pct(sum(1 for x in uh if x>0)/len(uh)) if uh else 'NA',
                  'now:',pct(st.median([r['ret_usd_hold_now'] for r in g if r['ret_usd_hold_now'] is not None])) if uh else 'NA', 'stakeW ret',pct(sum(pay)/sum(r['mean_stake_nmr'] for r in g)))
    # concentration
    pos=sorted([r['payout_sum_nmr'] for r in rows if r['payout_sum_nmr']>0],reverse=True); T=sum(pos)
    neg=sum(r['payout_sum_nmr'] for r in rows if r['payout_sum_nmr']<0)
    print('positive-net models',len(pos),'sum pos %.1f sum neg %.1f'%(T,neg),'top1/5/10/100 share of positive:',[pct(sum(pos[:k])/T) for k in (1,5,10,100)])
    stk=sorted([r['mean_stake_nmr'] for r in rows],reverse=True); S=sum(stk)
    print('stake share top1/5/10/100:',[pct(sum(stk[:k])/S) for k in (1,5,10,100)])
    small=[r for r in rows if r['tier']=='<$500']
    print('small tier share of positive payouts',pct(sum(r['payout_sum_nmr'] for r in small if r['payout_sum_nmr']>0)/T))
    # persistence
    for sub in ('all','full'):
        g=[r for r in rows if (sub=='all' or r['full_window']) and r['ret_h1'] is not None and r['ret_h2'] is not None]
        print('persistence',sub,'N',len(g),'fracPos h1',pct(sum(1 for r in g if r['ret_h1']>0)/len(g)),'h2',pct(sum(1 for r in g if r['ret_h2']>0)/len(g)),
              'medRet h1',pct(st.median([r['ret_h1'] for r in g])),'h2',pct(st.median([r['ret_h2'] for r in g])))
        for tn,_,_ in TIERS:
            gg=[r for r in g if r['tier']==tn]
            if len(gg)<5: continue
            x=[r['ret_h1'] for r in gg]; y=[r['ret_h2'] for r in gg]
            try: c=st.correlation(x,y)
            except Exception: c=None
            # rank persistence: frac of h1-positive that are h2-positive
            hp=[r for r in gg if r['ret_h1']>0]; hn=[r for r in gg if r['ret_h1']<=0]
            print('   ',tn,len(gg),'fracPos h1/h2',pct(sum(1 for v in x if v>0)/len(x)),pct(sum(1 for v in y if v>0)/len(y)),'med h1/h2',pct(st.median(x)),pct(st.median(y)),
                  'corr',None if c is None else round(c,3),'P(h2>0|h1>0)',pct(sum(1 for r in hp if r['ret_h2']>0)/len(hp)) if hp else 'NA','P(h2>0|h1<=0)',pct(sum(1 for r in hn if r['ret_h2']>0)/len(hn)) if hn else 'NA')
