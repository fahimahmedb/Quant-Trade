"""Parse events_full.json into a flat universe table with bracket bounds, winner, weekend dates, fee flags."""
import json,re,datetime as dt,collections
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
evs=json.load(open('events_full.json'))
def num(s):
    s=s.strip().lower().replace('$','').replace(',','')
    mult=1.0
    if s.endswith('m'): s=s[:-1]
    elif s.endswith('b'): s=s[:-1]; mult=1000
    elif s.endswith('k'): s=s[:-1]; mult=0.001
    return float(s)*mult
def bounds(g):
    g=g.strip().replace('–','-').replace(' ','')
    if g.startswith('<'): return (0.0,num(g[1:]))
    if g.startswith('>'): return (num(g[1:]),float('inf'))
    if g.startswith('≥') or g.startswith('>='): return (num(g.lstrip('≥>=')),float('inf'))
    if g.endswith('+'): return (num(g[:-1]),float('inf'))
    m=re.match(r'^\$?([\d.]+[mMkKbB]?)-\$?([\d.]+[mMkKbB]?)$',g)
    if m:
        a,b=m.group(1),m.group(2)
        if a[-1].isdigit() and b[-1].lower()=='m': a+='m'
        return (num(a),num(b))
    return None
def cls(t):
    tl=t.lower()
    if 'opening day' in tl: return 'OPENDAY'
    if 'opening weekend' in tl or 'opening 4-day' in tl or '5-day opening' in tl: return 'OPEN'
    if re.search(r'(second|third|fourth|fifth|2nd|3rd|\dth|\d\dth) (\d-day )?weekend',tl): return 'NTH'
    if 'total domestic' in tl or 'domestic gross' in tl: return 'TOTAL'
    return 'OTHER'
rows=[]
for e in evs:
    t=e['title']; c=cls(t)
    ms=e.get('markets',[])
    desc=(ms[0].get('description','') if ms else '') or e.get('description','')
    m=re.search(r'(\d)-day (?:opening )?(?:weekend )?\((January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})\s*[-–]\s*(?:(January|February|March|April|May|June|July|August|September|October|November|December) )?(\d{1,2})\)',desc)
    ndays=wk_start=wk_end=None
    end=dt.date.fromisoformat(e['endDate'][:10]) if e.get('endDate') else None
    if m:
        ndays=int(m.group(1)); y=end.year if end else 2026
        s=dt.date(y,MON[m.group(2)],int(m.group(3)))
        em=MON[m.group(4)] if m.group(4) else MON[m.group(2)]
        f=dt.date(y,em,int(m.group(5)))
        if s>f: s=dt.date(y-1,s.month,s.day)
        if end and f>end+dt.timedelta(days=30): s=dt.date(y-1,s.month,s.day); f=dt.date(y-1,f.month,f.day)
        wk_start,wk_end=s,f
    src='the-numbers' if 'the-numbers' in desc.lower() or 'the numbers' in desc.lower() else ('boxofficemojo' if 'boxofficemojo' in desc.lower() or 'box office mojo' in desc.lower() else '?')
    film=re.search(r'"([^"]+)"',t); film=film.group(1) if film else t
    brs=[]
    for mk in ms:
        g=mk.get('groupItemTitle') or ''
        b=bounds(g) if g else None
        try: op=json.loads(mk.get('outcomePrices') or '[]')
        except Exception: op=[]
        brs.append({'market_id':mk['id'],'cond':mk.get('conditionId'),'tokens':json.loads(mk.get('clobTokenIds') or '[]'),
            'label':g,'lo':b[0] if b else None,'hi':b[1] if b else None,'won':(op[:1]==['1']),'resolved_prices':op,
            'fees_enabled':mk.get('feesEnabled'),'fee_schedule':mk.get('feeSchedule'),'fee_type':mk.get('feeType'),
            'created':mk.get('createdAt'),'accepting_ts':mk.get('acceptingOrdersTimestamp'),'closed_time':mk.get('closedTime'),
            'uma_status':mk.get('umaResolutionStatuses'),'volume':float(mk.get('volumeNum') or mk.get('volume') or 0),
            'tick':mk.get('orderPriceMinTickSize')})
    rows.append({'event_id':e['id'],'title':t,'family':c,'film':film,'ndays':ndays,'wk_start':str(wk_start) if wk_start else None,
      'wk_end':str(wk_end) if wk_end else None,'created':e.get('creationDate'),'end':e.get('endDate'),'closed':e.get('closed'),
      'res_source':src,'volume':float(e.get('volume') or 0),'neg_risk':e.get('negRisk'),'n_brackets':len(brs),'brackets':brs,
      'n_winners':sum(b['won'] for b in brs),'unparsed_brackets':sum(1 for b in brs if b['lo'] is None)})
json.dump(rows,open('universe_raw.json','w'),indent=0)
C=collections.Counter((r['family'],r['ndays'],r['closed'],r['n_winners']==1) for r in rows)
for k,v in sorted(C.items(),key=str): print(k,v)
for r in rows:
    if r['family'] in('OPEN','NTH') and (r['unparsed_brackets'] or r['ndays'] is None or (r['closed'] and r['n_winners']!=1)):
        print('ISSUE',r['event_id'],r['title'],r['ndays'],r['wk_start'],r['unparsed_brackets'],r['n_winners'],[b['label'] for b in r['brackets']])
