"""CP4: strict-timestamp replay per PREREGISTRATION (lanes A-D, rules R1/R2, execution E1/E2/E3).
Run from research/box_office/scripts. Inputs: data/universe_raw.json.gz, film_weekends.json, trades_window.json.gz,
pit_releases.csv. Outputs: data/replay_trades.csv, data/replay_summary.json."""
import json,gzip,csv,datetime as dt,random,math,statistics as st,sys,collections
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
DATA='../data/'
U={r['event_id']:r for r in json.load(gzip.open(DATA+'universe_raw.json.gz','rt'))}
FW=json.load(open(DATA+'film_weekends.json'))
T=json.load(gzip.open(DATA+'trades_window.json.gz','rt'))
PIT=list(csv.DictReader(open(DATA+'pit_releases.csv')))
PRICE_CAP=0.95; MARGIN=0.025; SEED=20260930; NBOOT=10000
INCLUDE_REV='--rev' in sys.argv          # sensitivity: admit Variety REVISABLE rows
OFFSET=int(next((a.split('=')[1] for a in sys.argv if a.startswith('--offset=')),'0'))  # minutes after anchor
FEE_ALL='--fee-all' in sys.argv
TAG=('_rev' if INCLUDE_REV else '')+(f'_off{OFFSET}' if OFFSET else '')+('_feeall' if FEE_ALL else '')
def anchors(w):
    F=dt.date.fromisoformat(w); mk=lambda d,h: dt.datetime(d.year,d.month,d.day,h,tzinfo=ET)
    return {'A':mk(F,16),'B':mk(F+dt.timedelta(1),9),'C':mk(F+dt.timedelta(1),16),'D':mk(F+dt.timedelta(2),16),'X':mk(F+dt.timedelta(3),18)}
NEXT={'A':'B','B':'C','C':'D','D':'X'}
sig={}
for r in PIT:
    if not r['value']: continue
    if (r['strictness']=='REVISABLE' or 'AMBIG' in r['note'].upper()) and not INCLUDE_REV: continue
    sig[(r['wk'],r['film'],r['lane'])]=float(r['value'])
def yes_fills(cond,t0,t1):
    """taker fills that bought YES in (t0,t1]: BUY outcome0 at p, or SELL outcome1 at q -> 1-q. returns [(ts,price,shares)]"""
    out=[]
    for ts,side,oi,p,sz in T.get(cond,{}).get('t',[]):
        if t0<ts<=t1:
            if oi==0 and side==1: out.append((ts,p,sz))
            elif oi==1 and side==-1: out.append((ts,1-p,sz))
    return out
def vwap(f): 
    s=sum(x[2] for x in f); return sum(x[1]*x[2] for x in f)/s if s>0 else None
def bracket_of(ev,W):
    for b in ev['brackets']:
        if b['lo'] is not None and b['lo']<=W<b['hi']: return b
    return None
def fee_rate(b):
    if FEE_ALL: return 0.05
    fs=b.get('fee_schedule') or {}
    return float(fs.get('rate',0)) if b.get('fees_enabled') else 0.0
rows=[]
cov=collections.defaultdict(collections.Counter)
for fw in FW:
    fam='U1' if fw['family']=='OPEN' else 'U2'
    evs=[U[e] for e in fw['events'] if U[e]['closed'] and U[e]['n_winners']==1 and U[e]['unparsed_brackets']==0]
    if not evs: continue
    A=anchors(fw['wk'])
    for lane in 'ABCD':
        if fam=='U2' and lane=='A': continue
        cov[(fam,lane)]['film_weekends']+=1
        W=sig.get((fw['wk'],fw['film'],lane))
        if W is None: continue
        cov[(fam,lane)]['with_signal']+=1
        t0=A[lane].timestamp()+OFFSET*60; tn=A[NEXT[lane]].timestamp()
        got_exec=False
        for ev in evs:
            b=bracket_of(ev,W)
            if b is None: continue
            win=next(x for x in ev['brackets'] if x['won'])
            flip=int(b['market_id']!=win['market_id'])
            f60=yes_fills(b['cond'],t0,t0+3600); ext=0
            if not f60: f60=yes_fills(b['cond'],t0,t0+3*3600); ext=1
            fall=yes_fills(b['cond'],t0,t0+3*3600)
            base={'wk':fw['wk'],'film':fw['film'],'univ':fam,'lane':lane,'event_id':ev['event_id'],'title':ev['title'],'W':W,
                  'bracket':b['label'],'b_lo':b['lo'],'b_hi':b['hi'],'winner':win['label'],'flip':flip,
                  'margin_ok':int(W*(1-MARGIN)>=b['lo'] and W*(1+MARGIN)<b['hi']),'truncated':int(T.get(b['cond'],{}).get('truncated',False))}
            if not f60:
                rows.append({**base,'exec':'NONE'}); continue
            got_exec=True
            p1=vwap(f60); p2=fall[0][1]
            usd60=sum(x[1]*x[2] for x in yes_fills(b['cond'],t0,t0+3600)); usdn=sum(x[1]*x[2] for x in yes_fills(b['cond'],t0,tn))
            nxt=yes_fills(b['cond'],tn,tn+3600); pn=vwap(nxt)
            fr=fee_rate(b); pay=1.0 if b['market_id']==win['market_id'] else 0.0
            def ret(p):
                fee=fr*p*(1-p); return (pay-p-fee)/(p+fee), fee
            r1,fee1=ret(p1); r2,_=ret(p2); r3,_=ret(min(p1+0.01,0.999))
            rows.append({**base,'exec':'EXT180' if ext else 'W60','p_E1':round(p1,4),'p_E2':round(p2,4),'fee_rate':fr,'fee_ps':round(fee1,5),
                         'payoff':pay,'gross_ret':round((pay-p1)/p1,5),'net_E1':round(r1,5),'net_E2':round(r2,5),'net_E3':round(r3,5),
                         'traded':int(p1<=PRICE_CAP),'cap_usd_60m':round(usd60,2),'cap_usd_to_next':round(usdn,2),
                         'p_next_anchor':round(pn,4) if pn else '','n_fills_60':len(f60)})
        if got_exec: cov[(fam,lane)]['with_exec']+=1
flds=sorted({k for r in rows for k in r},key=lambda k:list(rows[0].keys()).index(k) if k in rows[0] else 999)
with open(DATA+f'replay_trades{TAG}.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=flds); w.writeheader(); w.writerows(rows)
# ---- aggregation on film-weekend clusters
def q(w): return f"{w[:4]}Q{(int(w[5:7])-1)//3+1}"
def spearman(x,y):
    n=len(x)
    if n<4: return None
    rk=lambda v: [sorted(v).index(a)+ (sorted(v).count(a)-1)/2 for a in v]
    a,b=rk(x),rk(y); ma,mb=st.mean(a),st.mean(b)
    num=sum((i-ma)*(j-mb) for i,j in zip(a,b)); den=math.sqrt(sum((i-ma)**2 for i in a)*sum((j-mb)**2 for j in b))
    r=num/den if den else 0; return {'rho':round(r,3),'z':round(r*math.sqrt(n-1),2),'n':n}
def boot(vals,seed=SEED):
    if len(vals)<2: return None
    rnd=random.Random(seed); n=len(vals); ms=[]
    for _ in range(NBOOT):
        ms.append(sum(vals[rnd.randrange(n)] for _ in range(n))/n)
    ms.sort()
    return {'lo95':round(ms[int(0.025*NBOOT)],4),'hi95':round(ms[int(0.975*NBOOT)-1],4),'p_one_sided':round(sum(m<=0 for m in ms)/NBOOT,4)}
def summarize(sel,key):
    by=collections.defaultdict(list)
    for r in sel: by[(r['wk'],r['film'])].append(r)
    cl=[]
    for k,v in sorted(by.items()):
        cl.append({'wk':k[0],'film':k[1],'net':st.mean(r[key] for r in v),'gross':st.mean(r['gross_ret'] for r in v),
                   'fee':st.mean(r['fee_ps']/(r['p_E1']+r['fee_ps']) for r in v),'p':st.mean(r['p_E1'] for r in v),
                   'flip':max(r['flip'] for r in v),'cap':sum(r['cap_usd_60m'] for r in v),'capn':sum(r['cap_usd_to_next'] for r in v),'n_ev':len(v)})
    if not cl: return {'n_film_weekends':0}
    nets=[c['net'] for c in cl]; s=sorted(nets); n=len(s)
    tot=sum(abs(x) for x in nets) or 1
    out={'n_film_weekends':n,'n_event_trades':sum(c['n_ev'] for c in cl),'gross_mean':round(st.mean(c['gross'] for c in cl),4),
         'fee_mean_per_$':round(st.mean(c['fee'] for c in cl),4),'net_mean':round(st.mean(nets),4),'net_median':round(st.median(nets),4),
         'p25':round(s[int(0.25*(n-1))],4),'p75':round(s[int(0.75*(n-1))],4),'pos_frac':round(sum(x>0 for x in nets)/n,3),
         'worst':round(min(nets),4),'best':round(max(nets),4),'top3_share_abs':round(sum(sorted((abs(x) for x in nets),reverse=True)[:3])/tot,3),
         'flip_rate':round(st.mean(c['flip'] for c in cl),3),'entry_price_median':round(st.median(c['p'] for c in cl),3),
         'share_entry_ge_0.85':round(sum(c['p']>=0.85 for c in cl)/n,3),'cap_usd_60m_median':round(st.median(c['cap'] for c in cl),1),
         'cap_usd_to_next_median':round(st.median(c['capn'] for c in cl),1),'boot':boot(nets),
         'trend_net':spearman([dt.date.fromisoformat(c['wk']).toordinal() for c in cl],nets),
         'trend_price':spearman([dt.date.fromisoformat(c['wk']).toordinal() for c in cl],[c['p'] for c in cl])}
    qq=collections.defaultdict(list)
    for c in cl: qq[q(c['wk'])].append(c)
    out['by_quarter']={k:{'n':len(v),'net_mean':round(st.mean(c['net'] for c in v),4),'net_median':round(st.median(c['net'] for c in v),4),
        'pos_frac':round(sum(c['net']>0 for c in v)/len(v),3),'entry_price_median':round(st.median(c['p'] for c in v),3),
        'flip_rate':round(st.mean(c['flip'] for c in v),3),'cap_usd_60m_median':round(st.median(c['cap'] for c in v),1),
        'boot':boot([c['net'] for c in v])} for k,v in sorted(qq.items())}
    return out
S={'tag':TAG,'coverage':{f'{k[0]}_{k[1]}':dict(v) for k,v in sorted(cov.items())},'results':{}}
ex=[r for r in rows if r['exec']!='NONE']
for fam in ('U1','U2','U1+U2'):
    for lane in 'ABCD':
        base=[r for r in ex if (fam=='U1+U2' or r['univ']==fam) and r['lane']==lane]
        if not base: continue
        allflip=[r for r in rows if (fam=='U1+U2' or r['univ']==fam) and r['lane']==lane]
        S['results'][f'{fam}_{lane}']={
            'signal_bracket_flip_rate_all_events':round(st.mean(r['flip'] for r in allflip),3) if allflip else None,
            'R1_E1':summarize([r for r in base if r['traded']],'net_E1'),
            'R1_E2':summarize([r for r in base if r['traded']],'net_E2'),
            'R1_E3':summarize([r for r in base if r['traded']],'net_E3'),
            'R2_E1':summarize([r for r in base if r['traded'] and r['margin_ok']],'net_E1'),
            'R1_E1_nocap':summarize(base,'net_E1')}
# Holm on U1 R1_E1 one-sided p
ps=[(l,S['results'].get(f'U1_{l}',{}).get('R1_E1',{}).get('boot') or {}) for l in 'ABCD']
ps=sorted([(l,b['p_one_sided']) for l,b in ps if b],key=lambda x:x[1])
holm={};m=len(ps)
for i,(l,p) in enumerate(ps): holm[l]=round(min(1,max(p*(m-i),holm.get(ps[i-1][0],0) if i else 0)),4)
S['holm_U1_R1_E1']=holm
json.dump(S,open(DATA+f'replay_summary{TAG}.json','w'),indent=1)
print(json.dumps(S['coverage'],indent=0)); print('holm',holm)
for k,v in S['results'].items():
    r=v['R1_E1']; print(k,'N',r.get('n_film_weekends'),'net',r.get('net_mean'),'med',r.get('net_median'),'pos',r.get('pos_frac'),'price',r.get('entry_price_median'),'flip',r.get('flip_rate'),'boot',r.get('boot'))
