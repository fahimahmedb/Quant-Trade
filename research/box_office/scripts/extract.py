"""CP3 step 3: candidate 3-day figures per film-weekend x release from labelled Deadline sections
and Variety posts. Outputs data/pit_candidates.csv for manual verification."""
import json,gzip,html,re,datetime as dt,csv,sys
sys.path.insert(0,'.')
from sections import split,txt,flat,UTC,PT
from digest import norm,key   # reuses film key logic (digest.py rebuilds digest when imported; harmless)
D=json.load(gzip.open('../data/deadline_bo.json.gz','rt')); V=json.load(gzip.open('../data/variety_bo.json.gz','rt'))
FW=json.load(open('../data/film_weekends.json'))
NUM=r'\$\s?([\d]+(?:\.\d+)?)\s?(M|million|K)'
RNG=NUM+r'(?:\+|-plus| plus)?(?:\s?(?:-|–|to)\s?'+NUM+r')?'
BAD=re.compile(r'(?i)(preview|friday|today|saturday|sunday|monday|global|ww\b|worldwide|overseas|international|offshore|abroad|cume|total|running|budget|cost|net\b|production|spend|imax|plf|per theater|average|week\b|wk\b|to date|lifetime|year|ytd)')
def val(m,i=1):
    x=float(m.group(i)); u=m.group(i+1)
    return x/1000 if u=='K' else x
def figures(win):
    out=[]
    m=re.search(r'3-day\s*(?:of\s*)?'+RNG,win)
    if m:
        a=val(m,1); b=val(m,3) if m.group(3) else None
        return [('chart',a,b,m.group(0))]
    for m in re.finditer(RNG+r'[^.$]{0,25}?\b(opening|start|weekend|debut|3-day|three-day|bow|frame|launch|second|2nd|third|3rd|fourth|fifth)',win):
        pre=win[max(0,m.start()-25):m.start()]
        if BAD.search(pre+win[m.start():m.end()].split(m.group(len(m.groups())))[0][-25:] if False else pre): continue
        a=val(m,1); b=val(m,3) if m.group(3) else None
        out.append(('text',a,b,win[max(0,m.start()-40):m.end()]))
    for m in re.finditer(r'(?i)(3-day|three-day|weekend|opening|start|debut|projecting|pace for|expected to|should|eyeing|looking at|heading (?:to|for)|shaping up|pull in|gross)[^$.]{0,45}?'+RNG,win):
        g=m.groups(); off=len(g)-4
        a=float(g[off]); a=a/1000 if g[off+1]=='K' else a
        b=None
        if g[off+2]: b=float(g[off+2]); b=b/1000 if g[off+3]=='K' else b
        mid=win[m.start():m.end()]
        if re.search(r'(?i)(preview|friday|today|global|worldwide|overseas|international|budget|cost)',mid): continue
        out.append(('text2',a,b,win[max(0,m.start()-20):m.end()]))
    return out
def windows(text,k,others):
    t=norm(text); res=[]
    for m in re.finditer(re.escape(k),t,flags=re.I):
        end=min(len(t),m.end()+320)
        for o in others:
            j=t.lower().find(o.lower(),m.end()+1)
            if 0<j<end: end=j
        res.append(t[m.start():end])
    return res
rows=[]
byw={}
for fw in FW: byw.setdefault(fw['wk'],[]).append(fw)
for w,fws in byw.items():
    F=dt.date.fromisoformat(w); lo=F-dt.timedelta(days=2); hi=F+dt.timedelta(days=4)
    keys={fw['film']:key(fw['film']) for fw in fws}
    srcs=[]
    for p in D:
        if lo<=dt.date.fromisoformat(p['date_gmt'][:10])<=hi:
            for s in split(p,F):
                if s['day'] in('THURSDAY','FRIDAY','SATURDAY','SUNDAY','MONDAY'):
                    srcs.append(('D',p['id'],s['label'],s['avail_utc'],None,s['text']))
    for p in V:
        if lo<=dt.date.fromisoformat(p['date_gmt'][:10])<=hi:
            tt=html.unescape(p['title']['rendered'])
            if re.search(r'(?i)(china|korea|u\.k\.|ireland|japan|france|india|global|worldwide|overseas|international)',tt): continue
            srcs.append(('V',p['id'],tt[:70],p['date_gmt']+'+00:00',p['modified_gmt']+'+00:00',flat(txt(p))))
    for fw in fws:
        k=keys[fw['film']]; others=[v for f,v in keys.items() if f!=fw['film']]+['Tron','One Battle','Roofman']  # boundaries only
        for src,pid,label,av,mod,text in srcs:
            for win in windows(text,k,[o for o in others if o.lower()!=k.lower()]):
                for kind,a,b,ctx in figures(win):
                    rows.append({'wk':w,'film':fw['film'],'family':fw['family'],'src':src,'post':pid,'label':label,'avail_utc':av,'mod_utc':mod or '',
                                 'kind':kind,'lo':a,'hi':b if b else '','ctx':re.sub(r'\s+',' ',ctx)[:160]})
with open('../data/pit_candidates.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
print(len(rows))
