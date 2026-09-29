"""CP3 step 4: lane-tagged digests per quarter for adjudication (only sources that can feed lanes A-D)."""
import json,gzip,html,re,datetime as dt,sys
sys.path.insert(0,'.')
from sections import split,txt,flat
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
D=json.load(gzip.open('../data/deadline_bo.json.gz','rt')); V=json.load(gzip.open('../data/variety_bo.json.gz','rt'))
FW=json.load(open('../data/film_weekends.json'))
def norm(s): return s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"').replace('–','-').replace('—','-')
def key(film):
    f=re.sub(r'\s*\(\d{4}\)','',norm(film).strip()); k=re.split(r':| - ',f)[0].strip()
    if len(k)<5: k=f
    return re.sub(r'^(The|A) ','',k)
def anchors(w):
    F=dt.date.fromisoformat(w); mk=lambda d,h: dt.datetime(d.year,d.month,d.day,h,tzinfo=ET)
    return {'A':mk(F,16),'B':mk(F+dt.timedelta(1),9),'C':mk(F+dt.timedelta(1),16),'D':mk(F+dt.timedelta(2),16)}
def dlane(label):
    L=label.upper(); toks=re.split(r'[ ,.:]+',L)
    am='AM' in toks or 'MORNING' in L or 'EARLY' in L
    if 'FRIDAY' in L: return 'A' if am else 'B'
    if 'SATURDAY' in L: return 'C' if am else None   # Saturday PM sections are after the C anchor
    if 'SUNDAY' in L: return 'D' if am else None
    return None
def vlane(pub,mod,A):
    prev={'A':None,'B':A['A'],'C':A['B'],'D':A['C']}
    for l in 'ABCD':
        if pub<=A[l] and (prev[l] is None or pub>prev[l]):
            return l,('STRICT' if mod<=A[l] else 'REVISABLE(modified after anchor)')
    return None,None
def sents(text,k):
    t=norm(text); out=[]
    for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"\'(])',t):
        if k.lower() in s.lower() and '$' in s: out.append(s.strip()[:500])
    return out
CH=['2025-10-17','2025-12-19','2026-02-27','2026-05-01','2026-06-26','2026-08-07','2099']
Q=lambda w: 'part%d'%max(i for i in range(6) if w>=CH[i])
files={}
byw={}
for fw in FW: byw.setdefault(fw['wk'],[]).append(fw)
for w,fws in byw.items():
    F=dt.date.fromisoformat(w); A=anchors(w); lo=F-dt.timedelta(days=2); hi=F+dt.timedelta(days=3)
    blocks=[]
    for p in D:
        if lo<=dt.date.fromisoformat(p['date_gmt'][:10])<=hi+dt.timedelta(days=1):
            for s in split(p,F):
                l=dlane(s['label']) if s['day'] in('FRIDAY','SATURDAY','SUNDAY') else None
                if l: blocks.append((l,f"Deadline post {p['id']} section [{s['label']}] available by {s['avail_utc']}",s['text']))
    for p in V:
        pub=dt.datetime.fromisoformat(p['date_gmt']+'+00:00'); mod=dt.datetime.fromisoformat(p['modified_gmt']+'+00:00')
        tt=html.unescape(p['title']['rendered'])
        if re.search(r'(?i)(china|korea|u\.k\.|ireland|japan|france|india)',tt): continue
        l,flag=vlane(pub,mod,A)
        if l: blocks.append((l,f"Variety post {p['id']} pub {p['date_gmt']}Z mod {p['modified_gmt']}Z {flag} :: {tt[:90]}",flat(txt(p))))
    fh=files.setdefault(Q(w),open(f'../data/digest_{Q(w)}.txt','w'))
    fh.write(f"\n==================== WEEKEND {w} | anchors ET: A=Fri 16:00, B=Sat 09:00, C=Sat 16:00, D=Sun 16:00\n")
    for fw in fws:
        k=key(fw['film'])
        fh.write(f"\n######## {w} | FILM: {fw['film']} | {fw['family']} | key='{k}'\n")
        for l in 'ABCD':
            for l2,hdr,text in blocks:
                if l2!=l: continue
                ss=sents(text,k)
                if ss:
                    fh.write(f"  [lane {l}] {hdr}\n")
                    for x in ss[:4]: fh.write('     * '+x[:350]+'\n')
for f in files.values(): f.close()
