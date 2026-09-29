"""Archive Variety (category 20000 box-office) and Deadline (vertical 20000 box-office) posts
2025-10-01 -> 2026-09-30 via public WordPress REST APIs, keeping date_gmt / modified_gmt."""
import json,urllib.request,time,sys
def get(u,tries=6):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
            resp=urllib.request.urlopen(r,timeout=90)
            return json.load(resp), resp.headers
        except urllib.error.HTTPError as e:
            if e.code==400: return [],{}
            time.sleep(2+3*i)
        except Exception as e:
            time.sleep(2+3*i)
    raise RuntimeError(u)
def pull(site,param,out):
    posts=[];page=1
    while True:
        u=(f"https://{site}/wp-json/wp/v2/posts?{param}=20000&after=2025-10-01T00:00:00&before=2026-09-30T00:00:00"
           f"&per_page=100&page={page}&orderby=date&order=asc&_fields=id,date,date_gmt,modified,modified_gmt,link,title,content")
        b,h=get(u)
        if not b: break
        posts+=b; print(site,page,len(posts),h.get('X-WP-TotalPages') if h else None,flush=True)
        if h and page>=int(h.get('X-WP-TotalPages',page)): break
        page+=1
    json.dump(posts,open(out,'w'))
pull('variety.com','categories','variety_bo.json')
pull('deadline.com','vertical','deadline_bo.json')
