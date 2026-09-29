import json,urllib.request,time
def get(u,tries=5):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e:
            time.sleep(1+2*i)
    raise RuntimeError(u)
out=[];off=0
while True:
    b=get(f"https://gamma-api.polymarket.com/events?tag_slug=box-office&limit=100&offset={off}&order=id&ascending=true")
    if not b: break
    out+=b; off+=len(b)
    if len(b)<100: break
json.dump(out,open('events_all.json','w'))
print(len(out))
