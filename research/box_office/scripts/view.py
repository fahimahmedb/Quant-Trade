"""Compact adjudication view of pit_candidates.csv, grouped by film-weekend; lane tag by source timing."""
import csv,datetime as dt,sys
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
R=list(csv.DictReader(open('../data/pit_candidates.csv')))
def anchors(w):
    F=dt.date.fromisoformat(w)
    mk=lambda d,h: dt.datetime(d.year,d.month,d.day,h,tzinfo=ET)
    return {'A':mk(F,16),'B':mk(F+dt.timedelta(1),9),'C':mk(F+dt.timedelta(1),16),'D':mk(F+dt.timedelta(2),16)}
def lane(r):
    A=anchors(r['wk']); av=dt.datetime.fromisoformat(r['avail_utc'])
    if r['src']=='D':
        L=r['label'].upper()
        if 'FRIDAY' in L and ('AM' in L.split() or 'MORNING' in L) : return 'A'
        if 'FRIDAY' in L: return 'B'
        if 'SATURDAY' in L: return 'C' if ('AM' in L.split() or 'MORNING' in L) else 'C?'
        if 'SUNDAY' in L: return 'D'
        return None
    mod=dt.datetime.fromisoformat(r['mod_utc'])
    for l in 'ABCD':
        prev={'A':None,'B':A['A'],'C':A['B'],'D':A['C']}[l]
        if av<=A[l] and (prev is None or av>prev):
            return l+('' if mod<=A[l] else '~REV')
    return None
lo,hi=(sys.argv[1],sys.argv[2]) if len(sys.argv)>2 else ('0','9')
cur=None;seen=set()
for r in R:
    if not (lo<=r['wk']<=hi): continue
    l=lane(r)
    if not l: continue
    if (r['wk'],r['film'])!=cur:
        cur=(r['wk'],r['film']); print(f"\n## {r['wk']} {r['film']} [{r['family']}]")
    k=(r['wk'],r['film'],l,r['src'],r['post'],r['lo'],r['hi'])
    if k in seen: continue
    seen.add(k)
    print(f"{l:6}{r['src']}{r['post'][-4:]} {r['label'][:22]:22} {r['lo']}{'-'+r['hi'] if r['hi'] else ''} | {r['ctx'][:120]}")
