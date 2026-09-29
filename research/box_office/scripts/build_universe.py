"""Build the frozen box-office universe: every box-office event (tag box-office ∪ series box-office-openings)
created on/after 2025-10-01, with full market details (brackets, tokens, fee schedule, resolution)."""
import json,urllib.request,time,re,datetime as dt,concurrent.futures as cf
def get(u,tries=6):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e:
            time.sleep(1+2*i)
    raise RuntimeError(u)
ev=json.load(open('events_all.json'))
ids={e['id'] for e in ev}
off=0
while True:
    b=get(f"https://gamma-api.polymarket.com/events?series_slug=box-office-openings&limit=100&offset={off}")
    if not b: break
    for e in b:
        if e['id'] not in ids: ev.append(e); ids.add(e['id'])
    off+=len(b)
    if len(b)<100: break
ev=[e for e in ev if (e.get('creationDate') or e.get('startDate') or '')>='2025-10-01']
def full(e):
    d=get(f"https://gamma-api.polymarket.com/events/{e['id']}")
    return d
with cf.ThreadPoolExecutor(6) as ex:
    evs=list(ex.map(full,ev))
json.dump(evs,open('events_full.json','w'))
print(len(evs))
