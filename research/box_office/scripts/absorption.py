"""Market-only diagnostics (no information signal): winner-bracket executable YES price at anchors A-D,
and weekend taker volume per film-weekend, by quarter. Descriptive only."""
import json,gzip,datetime as dt,statistics as st,collections,sys
sys.argv=[sys.argv[0]]
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
U={r['event_id']:r for r in json.load(gzip.open('../data/universe_raw.json.gz','rt'))}
FW=json.load(open('../data/film_weekends.json'))
T=json.load(gzip.open('../data/trades_window.json.gz','rt'))
def anchors(w):
    F=dt.date.fromisoformat(w); mk=lambda d,h: dt.datetime(d.year,d.month,d.day,h,tzinfo=ET)
    return {'A':mk(F,16),'B':mk(F+dt.timedelta(1),9),'C':mk(F+dt.timedelta(1),16),'D':mk(F+dt.timedelta(2),16)}
def yes_vwap(c,t0,t1):
    f=[(p if oi==0 else 1-p,sz) for ts,side,oi,p,sz in T[c]['t'] if t0<ts<=t1 and ((oi==0 and side==1) or (oi==1 and side==-1))]
    s=sum(x[1] for x in f); return sum(a*b for a,b in f)/s if s else None
q=lambda w: f"{w[:4]}Q{(int(w[5:7])-1)//3+1}"
res=collections.defaultdict(lambda: collections.defaultdict(list)); vol=collections.defaultdict(list)
for fw in FW:
    evs=[U[e] for e in fw['events'] if U[e]['closed'] and U[e]['n_winners']==1]
    if not evs: continue
    A=anchors(fw['wk']); fam='U1' if fw['family']=='OPEN' else 'U2'
    for l,t in A.items():
        ps=[yes_vwap(b['cond'],t.timestamp(),t.timestamp()+3600) for e in evs for b in e['brackets'] if b['won']]
        ps=[p for p in ps if p is not None]
        if ps: res[(fam,q(fw['wk']))][l].append(st.mean(ps))
    F=dt.datetime.fromisoformat(fw['wk']+'T00:00:00').replace(tzinfo=ET)
    v=sum(p*sz for e in evs for b in e['brackets'] for ts,side,oi,p,sz in T[b['cond']]['t'] if F.timestamp()-86400<=ts<=F.timestamp()+4*86400)
    vol[(fam,q(fw['wk']))].append(v)
out={}
for k in sorted(res):
    out[f'{k[0]}_{k[1]}']={'winner_price_median':{l:round(st.median(v),3) for l,v in res[k].items()},'n':{l:len(v) for l,v in res[k].items()},
        'weekend_taker_usd_median':round(st.median(vol[k]),0),'weekend_taker_usd_sum':round(sum(vol[k]),0),'n_fw':len(vol[k])}
json.dump(out,open('../data/absorption_market_only.json','w'),indent=1)
for k,v in out.items(): print(k,v)
