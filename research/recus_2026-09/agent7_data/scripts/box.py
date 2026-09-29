import json,urllib.request,datetime as dt,re,concurrent.futures as cf,time
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
def get(u,tries=4):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e:
            time.sleep(1+i)
    return None
ev=json.load(open('box_events.json'))
ev=[e for e in ev if 'opening weekend' in e['title'].lower() and e.get('closed') and e.get('endDate') and e.get('markets')]
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
out=[]
def fri_of(e):
    desc=e['markets'][0].get('description','')
    m=re.search(r'\((January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})\s*[-–]',desc)
    end=dt.date.fromisoformat(e['endDate'][:10])
    if m:
        d=dt.date(end.year,MON[m.group(1)],int(m.group(2)))
        if d>end: d=dt.date(end.year-1,MON[m.group(1)],int(m.group(2)))
        # move to friday if thursday-start etc
        return d, True
    d=end
    while d.weekday()!=4: d-=dt.timedelta(days=1)
    return d, False
def anchors(fri):
    base=dt.datetime(fri.year,fri.month,fri.day,tzinfo=ET)
    A={'thu18':base-dt.timedelta(hours=6),'fri14':base+dt.timedelta(hours=14),'sat14':base+dt.timedelta(days=1,hours=14),
       'sun14':base+dt.timedelta(days=2,hours=14),'mon18':base+dt.timedelta(days=3,hours=18)}
    return {k:int(v.timestamp()) for k,v in A.items()}
def price_at(hist,ts):
    best=None
    for h in hist:
        if h['t']<=ts: best=h['p']
        else: break
    return best
def do(e):
    fri,parsed=fri_of(e); A=anchors(fri)
    rows=[]
    for m in e['markets']:
        try:
            op=json.loads(m['outcomePrices']); toks=json.loads(m['clobTokenIds'])
        except Exception: continue
        h=get(f"https://clob.polymarket.com/prices-history?market={toks[0]}&startTs={A['thu18']-86400*3}&endTs={A['mon18']+3600}&fidelity=60")
        hist=sorted((h or {}).get('history',[]),key=lambda x:x['t'])
        rows.append({'bracket':m.get('groupItemTitle'),'won':op[0]=='1','p':{k:price_at(hist,v) for k,v in A.items()},'npts':len(hist)})
    return {'id':e['id'],'title':e['title'],'fri':str(fri),'parsed':parsed,'vol':float(e.get('volume') or 0),'rows':rows}
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(do,ev): out.append(r)
json.dump(out,open('box_prices.json','w'))
print('done',len(out))
