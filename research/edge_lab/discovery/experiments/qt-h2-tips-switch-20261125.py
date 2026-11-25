#!/usr/bin/env python3
"""Frozen nominal/TIPS switch, issue #60 comment 7149456987."""
import csv,io,math,statistics as st,datetime as dt,json,hashlib,random,sys,urllib.request,calendar
YEARS=list(range(2005,2025))
NOM="https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"
REAL="https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv"
CPI="https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS&cosd=2003-01-01&coed=2024-12-31"
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"QuantTrade public historical research"})
    with urllib.request.urlopen(req,timeout=60 if url==CPI else 30) as f:
        if f.url!=url:raise ValueError("unexpected redirect")
        b=f.read(30_000_001)
    if len(b)>30_000_000:raise ValueError("source exceeds cap")
    expected={NOM:"26ae7fccdf348a190b9859e512c6c40190418d3fe84966a7ad1a9d0519404129",REAL:"a205b662458cd10107860f580accf47fdbc894f7b356a75e9f2976a959f5fffc"}
    if url in expected and hashlib.sha256(b).hexdigest()!=expected[url]:raise ValueError("source hash changed")
    print("SOURCE "+json.dumps(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())),flush=True)
    return b.decode("utf-8-sig")
def curve(s,prefix):
    rows=list(csv.reader(io.StringIO(s,newline="")))
    req=["Date",prefix+"09",prefix+"10"]
    hits=[i for i,r in enumerate(rows[:40]) if all(r.count(x)==1 for x in req)]
    if len(hits)!=1:raise ValueError("header missing "+prefix)
    i=hits[0];ix=[rows[i].index(x) for x in req];out={};prev=None
    for row in rows[i+1:]:
        if not row or not row[0].strip():continue
        d=dt.date.fromisoformat(row[ix[0]].strip())
        if prev is not None and d<=prev:raise ValueError("duplicate or unordered date")
        prev=d
        if not 2004<=d.year<=2024 or d.month not in (11,12) or d.day<20:continue
        try:v=[float(row[j])/100 for j in ix[1:]]
        except (ValueError,IndexError):continue
        if all(math.isfinite(x) and -.1<x<.5 for x in v):out[d]=dict(zip((9,10),v))
    return out
def cpi(s):
    r=csv.DictReader(io.StringIO(s,newline=""))
    if r.fieldnames not in (["observation_date","CPIAUCNS"],["DATE","CPIAUCNS"]):raise ValueError("CPI header")
    out={}
    for row in r:
        d=dt.date.fromisoformat(row[r.fieldnames[0]]);k=(d.year,d.month)
        if d.day!=1 or k in out:raise ValueError("CPI date")
        try:v=float(row["CPIAUCNS"])
        except ValueError:continue
        if math.isfinite(v) and v>0:out[k]=v
    return out
def refcpi(d,cp):
    if d.month!=12:raise ValueError("December only")
    a,b=cp[d.year,9],cp[d.year,10]
    return a+(b-a)*(d.day-1)/calendar.monthrange(d.year,d.month)[1]
def choose(n,r,cp,y):
    return "R" if math.log(cp[y,9]/cp[y-1,9])>n[10]-r[10] else "N"
def join(n,r):
    out={}
    for d in sorted(n.keys()&r.keys()):out[d.year,d.month]=(d,n[d],r[d])
    need={(y,12) for y in range(2004,2025)}|{(y,11) for y in range(2004,2024)}
    if not need<=out.keys():raise ValueError("missing common month")
    return out
def gross(a,b):return math.exp(10*a[10]-9*b[9])
def simulate(data,cp,bp):
    f=(1-bp/10000)**2;out={k:[] for k in ("I","N","R","mix")};picks=[]
    for t in YEARS:
        sd,n,r=data[t-1,11];ed,en,er=data[t-1,12];xd,xn,xr=data[t,12]
        assert sd<ed<xd
        pick=choose(n,r,cp,t-1)
        ret={"N":gross(en,xn)*f,"R":gross(er,xr)*refcpi(xd,cp)/refcpi(ed,cp)*f}
        for k in ret:out[k].append(ret[k])
        out["I"].append(ret[pick]);out["mix"].append(st.mean(ret.values()))
        picks.append(dict(year=t,pick=pick,signal=str(sd),entry=str(ed),exit=str(xd),breakeven=n[10]-r[10],trailing=math.log(cp[t-1,9]/cp[t-2,9])))
    return out,picks
def stats(g):
    l=0.;peak=0.;dd=0.
    for x in g:l+=math.log(x);peak=max(peak,l);dd=min(dd,math.exp(l-peak)-1)
    return dict(n=len(g),wealth=math.exp(l),cagr=math.expm1(l/len(g)),vol=st.stdev(x-1 for x in g),dd=dd)
def boot(diff):
    n=len(diff);rng=random.Random(20261125);out=[]
    for _ in range(10000):
        s=0.
        for k in range(0,n,3):
            j=rng.randrange(n);s+=sum(diff[(j+h)%n] for h in range(min(3,n-k)))
        out.append(s/n)
    out.sort();return [out[249],out[9749]]

def evaluate(data,cp):
    result={}
    for bp in (10,25):
        paths,picks=simulate(data,cp,bp);m={k:stats(v) for k,v in paths.items()};a,b=m["I"],m["mix"]
        diff=[math.log(x/y) for x,y in zip(paths["I"],paths["mix"])]
        v=dict(advantage=a["cagr"]-b["cagr"],halves=[st.mean(diff[:10]),st.mean(diff[10:])],ci95=boot(diff),wealth_delta_per_10000=10000*(a["wealth"]-b["wealth"]))
        v["screen"]=v["advantage"]>=.005 and all(a["cagr"]>m[k]["cagr"] for k in ("N","R")) and min(v["halves"])>0 and a["vol"]<=b["vol"] and a["dd"]>=b["dd"] and v["ci95"][0]>0
        result[str(bp)]=dict(metrics=m,candidate=v,annual_returns={k:[x-1 for x in g] for k,g in paths.items()},picks=picks)
    return dict(result=result,screen_pass=all(x["candidate"]["screen"] for x in result.values()))
def self_test():
    n={9:.04,10:.04};r={9:.01,10:.01}
    assert abs(gross(n,n)-math.exp(.04))<1e-12
    assert choose(n,r,{(2004,9):105,(2003,9):100},2004)=="R"
    assert choose(n,r,{(2004,9):102,(2003,9):100},2004)=="N"
    assert refcpi(dt.date(2004,12,16),{(2004,9):100,(2004,10):131})==115
    assert abs(stats([1.1,.9])["wealth"]-.99)<1e-12
    assert boot([.01]*20)[0]>.009999
    print("SELF_TEST_PASS",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    data=join(curve(fetch(NOM),"SVENY"),curve(fetch(REAL),"TIPSY"));cp=cpi(fetch(CPI))
    print("TIPS_RESULT "+json.dumps(evaluate(data,cp),sort_keys=True,allow_nan=False),flush=True)
