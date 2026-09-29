"""CP3 step 1: split Deadline weekend articles into labelled sections with strict availability times,
and collect Variety posts; emit per film-weekend digests of candidate snippets."""
import json,gzip,html,re,datetime as dt,collections
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York'); PT=ZoneInfo('America/Los_Angeles'); UTC=dt.timezone.utc
DAYS=['MONDAY','TUESDAY','WEDNESDAY','THURSDAY','FRIDAY','SATURDAY','SUNDAY']
LAB=re.compile(r'(?m)^[ \t]*((?:(?:UPDATED?|REFRESHED?|PREVIOUS(?:LY)?|WRITETHRU|EXCLUSIVE|FINAL)[ ,:]*)*(?:THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY|TUESDAY|WEDNESDAY)\b[A-Z ,.0-9\-–/’\']{0,50}?|EXCLUSIVE|PREVIOUS(?:LY)?(?: EXCLUSIVE)?|UPDATE[A-Z ,0-9]{0,40})\s*:')
def txt(p):
    t=re.sub(r'<[^>]+>','\n',p['content']['rendered']); t=html.unescape(t)
    t=re.sub(r'[ \t]*\n[ \t]*','\n',t); t=re.sub(r'\n+','\n',t)
    # join inline-split lines (film titles in <em> produce breaks); keep line starts for labels
    return t
def flat(s): return re.sub(r'\s*\n\s*',' ',s)
def avail(label,friday):
    """end of labelled window in PT -> UTC; None if no day label."""
    L=label.upper()
    day=next((d for d in DAYS if d in L),None)
    if day is None: return None,'nolabel'
    # map day to date relative to weekend Friday (Thu..Tue)
    off={'THURSDAY':-1,'FRIDAY':0,'SATURDAY':1,'SUNDAY':2,'MONDAY':3,'TUESDAY':4,'WEDNESDAY':-2}[day]
    D=friday+dt.timedelta(days=off)
    if re.search(r'\bAM\b|MORNING|EARLY',L): h,m=12,0
    elif re.search(r'MIDDAY|NOON|AFTERNOON',L): h,m=17,0
    else: h,m=23,59
    t=dt.datetime(D.year,D.month,D.day,h,m,tzinfo=PT)
    return t.astimezone(UTC),day
def split(p,friday):
    t=txt(p); secs=[]
    ms=list(LAB.finditer(t))
    pub=dt.datetime.fromisoformat(p['date_gmt']+'+00:00')
    if not ms or ms[0].start()>40:
        # unlabelled top: available at date_gmt (re-dated post) but content revisable -> label TOP
        secs.append({'label':'TOP(unlabelled)','start':0,'end':ms[0].start() if ms else len(t)})
    for i,m in enumerate(ms):
        secs.append({'label':m.group(1).strip(),'start':m.end(),'end':ms[i+1].start() if i+1<len(ms) else len(t)})
    out=[]
    for s in secs:
        a,day=avail(s['label'],friday) if not s['label'].startswith('TOP') else (None,'top')
        out.append({'label':s['label'],'day':day,'avail_utc':a.isoformat() if a else None,'text':flat(t[s['start']:s['end']])})
    return out
