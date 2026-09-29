import json,urllib.request,time,datetime as dt,re,concurrent.futures as cf
from zoneinfo import ZoneInfo
def get(u,tries=5):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e: time.sleep(1.5+i)
    return None
# 1) collect NYC + London highest-temperature events over full history (closed)
evs={}
for e in json.load(open('wx_events.json')):
    if re.match(r'Highest temperature in (NYC|London) on',e['title'] or ''): evs[e['id']]=e
d0=dt.date(2026,3,20)
while d0<dt.date(2026,9,29):
    d1=d0+dt.timedelta(days=4)
    off=0
    while True:
        d=get(f"https://gamma-api.polymarket.com/events?tag_slug=weather&closed=true&limit=100&offset={off}&end_date_min={d0}T00:00:00Z&end_date_max={d1}T00:00:00Z")
        if not d: break
        for e in d:
            if re.match(r'Highest temperature in (NYC|London) on',e.get('title') or ''):
                ms=[{'q':m.get('groupItemTitle'),'op':m.get('outcomePrices'),'tok':m.get('clobTokenIds')} for m in e.get('markets',[])]
                evs[e['id']]={'id':e['id'],'title':e['title'],'start':e.get('startDate'),'created':e.get('createdAt'),'end':e.get('endDate'),'vol':e.get('volume'),'markets':ms}
        if len(d)<100: break
        off+=100
    d0=d1
print('events',len(evs),flush=True)
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
MON.update({m[:3]:i for m,i in list(MON.items())})
def target_date(e):
    m=re.search(r'on (\w+) (\d{1,2})',e['title']); end=dt.date.fromisoformat(e['end'][:10])
    mo=MON.get(m.group(1)); day=int(m.group(2)); y=end.year
    d=dt.date(y,mo,day)
    if (d-end).days>200: d=dt.date(y-1,mo,day)
    if (end-d).days>200: d=dt.date(y+1,mo,day)
    return d
def ph(tok,a,b):
    h=get(f"https://clob.polymarket.com/prices-history?market={tok}&startTs={a}&endTs={b}&fidelity=30")
    return sorted((h or {}).get('history',[]),key=lambda x:x['t'])
def at(h,ts):
    v=None
    for x in h:
        if x['t']<=ts: v=x['p']
        else: break
    return v
def do(e):
    city='NYC' if 'NYC' in e['title'] else 'London'
    tz=ZoneInfo('America/New_York' if city=='NYC' else 'Europe/London')
    D=target_date(e)
    base=dt.datetime(D.year,D.month,D.day,tzinfo=tz)
    A={'Dm1_12':base-dt.timedelta(hours=12),'D_00':base,'D_09':base+dt.timedelta(hours=9),'D_15':base+dt.timedelta(hours=15)}
    A={k:int(v.timestamp()) for k,v in A.items()}
    rows=[]
    for m in e['markets']:
        try: op=json.loads(m['op']); tok=json.loads(m['tok'])
        except Exception: continue
        h=ph(tok[0],A['Dm1_12']-86400*2,A['D_15']+3600)
        rows.append({'q':m['q'],'won':op[0]=='1','p':{k:at(h,v) for k,v in A.items()}})
    return {'city':city,'date':str(D),'created':e.get('created'),'vol':float(e.get('vol') or 0),'rows':rows}
out=[]
with cf.ThreadPoolExecutor(12) as ex:
    for i,r in enumerate(ex.map(do,list(evs.values()))):
        out.append(r)
        if i%100==0: print(i,flush=True)
json.dump(out,open('wx_nyc_lon.json','w'))
print('done',len(out))
