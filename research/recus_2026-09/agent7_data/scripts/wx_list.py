import json,urllib.request,time,collections
def get(u,tries=5):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e: time.sleep(2+i)
    return []
out=[];off=0
while True:
    d=get(f"https://gamma-api.polymarket.com/events?tag_slug=weather&closed=true&limit=100&offset={off}&order=endDate&ascending=true")
    if not d: break
    for e in d:
        ms=[]
        for m in e.get('markets',[]):
            ms.append({'q':m.get('groupItemTitle'),'op':m.get('outcomePrices'),'tok':m.get('clobTokenIds'),'cid':m.get('conditionId'),'vol':m.get('volume'),'fee':m.get('feeSchedule') or m.get('feeType'),'created':m.get('createdAt'),'tick':m.get('orderPriceMinTickSize')})
        out.append({'id':e['id'],'title':e.get('title'),'start':e.get('startDate'),'created':e.get('createdAt'),'end':e.get('endDate'),'vol':e.get('volume'),'tags':[t.get('slug') for t in e.get('tags',[])],'markets':ms})
    off+=100
    if len(d)<100: break
    if off%5000==0: print(off,flush=True)
json.dump(out,open('wx_events.json','w'))
print('done',len(out))
