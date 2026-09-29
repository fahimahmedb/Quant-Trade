"""CP3 step 2: per film-weekend digest of dated snippets (Deadline sections + Variety posts)."""
import json,gzip,html,re,datetime as dt,collections,sys
sys.path.insert(0,'.')
from sections import split,txt,flat,UTC
D=json.load(gzip.open('../data/deadline_bo.json.gz','rt')); V=json.load(gzip.open('../data/variety_bo.json.gz','rt'))
U=json.load(gzip.open('../data/universe_raw.json.gz','rt'))
def norm(s): return s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-')
def key(film):
    f=norm(film).strip()
    f=re.sub(r'\s*\(\d{4}\)','',f)
    k=re.split(r':| - ',f)[0].strip()
    if len(k)<5: k=f
    k=re.sub(r'^(The|A) ','',k)
    return k
FW=collections.OrderedDict()
for r in sorted(U,key=lambda r:(r['wk_start'] or '',r['film'])):
    if r['family'] not in('OPEN','NTH') or not r['wk_start'] or not ('2025-10-17'<=r['wk_start']<='2026-09-25'): continue
    if r['ndays'] and (dt.date.fromisoformat(r['wk_end'])-dt.date.fromisoformat(r['wk_start'])).days!=2: continue
    fk=(r['wk_start'],norm(r['film']).strip(),r['family'])
    FW.setdefault(fk,[]).append(r['event_id'])
json.dump([{'wk':k[0],'film':k[1],'family':k[2],'events':v} for k,v in FW.items()],open('../data/film_weekends.json','w'),indent=0)
wks=sorted({k[0] for k in FW})
def sents(text,k):
    t=norm(text); out=[]
    for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])',t):
        if k.lower() in s.lower() and '$' in s: out.append(s.strip()[:600])
    return out
outf=open('../data/digest.txt','w')
for w in wks:
    F=dt.date.fromisoformat(w); lo=F-dt.timedelta(days=2); hi=F+dt.timedelta(days=4)
    dsec=[]
    for p in D:
        g=dt.date.fromisoformat(p['date_gmt'][:10])
        if lo<=g<=hi:
            secs=split(p,F)
            if any(s['day'] in('FRIDAY','SATURDAY','SUNDAY','MONDAY','THURSDAY') for s in secs) or '3-day' in flat(txt(p)):
                dsec.append((p,secs))
    vp=[p for p in V if lo<=dt.date.fromisoformat(p['date_gmt'][:10])<=hi and not re.search(r'(?i)(china|korea|u\.k\.|ireland|japan|france|india)',html.unescape(p['title']['rendered']))]
    for k in [k for k in FW if k[0]==w]:
        kk=key(k[1])
        outf.write(f"\n######## {w} | {k[1]} | {k[2]} | key={kk} | events={FW[k]}\n")
        for p,secs in dsec:
            for s in secs:
                ss=sents(s['text'],kk)
                if ss:
                    outf.write(f"-- D{p['id']} [{s['label']}] avail={s['avail_utc']} (post date {p['date_gmt']} mod {p['modified_gmt']})\n")
                    for x in ss[:6]: outf.write('   * '+x+'\n')
        for p in vp:
            ss=sents(flat(txt(p)),kk)
            if ss:
                outf.write(f"-- V{p['id']} pub={p['date_gmt']} mod={p['modified_gmt']} :: {html.unescape(p['title']['rendered'])[:100]}\n")
                for x in ss[:5]: outf.write('   * '+x+'\n')
outf.close()
print(len(FW),collections.Counter(k[2] for k in FW))
