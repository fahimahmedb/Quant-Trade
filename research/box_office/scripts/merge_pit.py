"""CP3 final: merge adjudicated_part*.csv -> pit_releases.csv; validate coverage against film_weekends.json."""
import csv,json,glob,collections
FW=json.load(open('../data/film_weekends.json'))
want={(f['wk'],f['film']):f['family'] for f in FW}
rows=[]
for p in sorted(glob.glob('../data/adjudicated_part*.csv')):
    for r in csv.DictReader(open(p)): r['part']=p[-5]; rows.append(r)
def nk(s): return s.replace('’',"'").replace('–','-').strip()
wn={(w,nk(f)):(w,f) for (w,f) in want}
out=[];seen=set();bad=[]
for r in rows:
    k=wn.get((r['wk'],nk(r['film'])))
    if not k: bad.append((r['wk'],r['film'])); continue
    r['film']=k[1]
    if r['value']:
        try: float(r['value'])
        except: bad.append(('nonnumeric',r['wk'],r['film'],r['value'])); r['value']=''
    if (k,r['lane']) in seen: bad.append(('dup',k,r['lane'])); continue
    seen.add((k,r['lane'])); out.append(r)
missing=[(k,l) for k in want for l in 'ABCD' if (k,l) not in seen]
with open('../data/pit_releases.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
c=collections.Counter((want[(r['wk'],r['film'])],r['lane'],bool(r['value']),r['strictness'] if r['value'] else '') for r in out)
for k,v in sorted(c.items()): print(k,v)
print('rows',len(out),'missing',len(missing),missing[:10]); print('bad',bad[:20])
