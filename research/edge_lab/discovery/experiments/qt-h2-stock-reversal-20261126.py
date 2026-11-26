#!/usr/bin/env python3
"""Frozen #7180194122, stock-level loser sleeves, not industry reversal."""
import csv,io,math,statistics as st,random,json,hashlib,zipfile,urllib.request,re,sys
BASE="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
MONTHS=[f"{y}{m:02d}" for y in range(1991,2026) for m in range(1,13)]
def norm(x):return re.sub("[^a-z0-9]","",x.lower())
def load(file):
    url=BASE+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade academic research"}),timeout=25) as r:
        if not r.url.startswith(BASE):raise ValueError("redirect")
        b=r.read(4000001)
    if len(b)>4000000:raise ValueError("oversize")
    print("SOURCE "+json.dumps(dict(url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        f=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(f)!=1 or z.getinfo(f[0]).file_size>8000000:raise ValueError("archive")
        return z.read(f[0]).decode("utf-8-sig")
def parse(s,market=False):
    rows=list(csv.reader(io.StringIO(s)))
    markers=[i for i,r in enumerate(rows) if "averagevalueweightedreturnsmonthly" in norm(" ".join(r))]
    if not market and len(markers)!=1:raise ValueError("monthly weighted section")
    start=0 if market else markers[0]+1; head=None
    for i in range(start,min(len(rows),start+25)):
        h=[norm(x) for x in rows[i]]
        if market and all(h.count(k)==1 for k in ("mktrf","rf")):
            head=i;ix=[h.index(k) for k in ("mktrf","rf")];break
        if not market and len(h)==7 and h[0]=="":
            # explicit full size/prior ordering; accept only exact names.
            allowed=[["smallloprior","me1prior2","smallhiprior","bigloprior","me2prior2","bighiprior"],["me1prior1","me1prior2","me1prior3","me2prior1","me2prior2","me2prior3"],["smallloprior","smallme2","smallhiprior","bigloprior","bigme2","bighiprior"]]
            # Known Fama-French header uses ME1 PRIOR2, ME2 PRIOR2 in the middle.
            if h[1:] in allowed:
                head=i;ix=[1,2,4,5];break
    if head is None:raise ValueError("unexpected header "+str(rows[start:start+6]))
    out={};begun=False
    for r in rows[head+1:]:
        if not r or not re.fullmatch(r"\d{6}",r[0].strip()):
            if begun:break
            continue
        begun=True;d=r[0].strip()
        if d not in MONTHS:continue
        if d in out:raise ValueError("duplicate")
        raw=[float(r[j]) for j in ix]
        if any(x in (-99.99,-999.) or not math.isfinite(x) for x in raw):raise ValueError("sentinel "+d)
        v=[x/100 for x in raw]
        if not all(-1<x<3 for x in v):raise ValueError("invalid return")
        if market:
            if v[0]+v[1]<=-1 or abs(v[1])>.1:raise ValueError("market")
            v=[sum(v)]
        out[d]=v
    if list(out)!=MONTHS:raise ValueError("coverage")
    print("QA "+json.dumps(dict(header=rows[head],selected=[rows[head][i] for i in ix],months=len(out))),flush=True)
    return out
def simulate(data,fee,drag,tilt):
    cost=fee/10000;d=(1-drag)**(1/12);out=[]
    for i,(date,m,s) in enumerate(data):
        if tilt:
            a=.5*(1+m);b=.5*(1+s)*d;gross=a+b
            turn=abs(a/gross-.5)+abs(b/gross-.5) if i<len(data)-1 else 0
        else:gross=1+m;turn=0.
        g=gross*(1-cost*turn)
        if i==0:g*=1-cost
        if i==len(data)-1:g*=1-cost
        out.append((date,g,turn+(i==0)+(i==len(data)-1)))
    return out
def stats(z):
    l=peak=0.;dd=0.
    for _,g,_ in z:l+=math.log(g);peak=max(peak,l);dd=min(dd,math.exp(l-peak)-1)
    wealth=math.exp(l);years=len(z)/12
    return dict(wealth=wealth,cagr=math.expm1(l/years),vol=st.stdev(x[1]-1 for x in z)*math.sqrt(12),dd=dd,turnover=sum(x[2] for x in z)/years,tax=wealth-.186*max(wealth-1,0))
def boot(v):
    rng=random.Random(20261126);n=len(v);res=[]
    for _ in range(20000):
        s=0.
        for k in range(0,n,12):
            j=rng.randrange(n);s+=sum(v[(j+h)%n] for h in range(min(12,n-k)))
        res.append(12*s/n)
    res.sort();return res[124]
def evaluate(m,other,kind):
    result={}
    for size,lo,mid in [("small",0,1),("big",2,3)]:
        out={}
        for fee,drag in [(10,.02 if kind=="ST" else .005),(30,.04 if kind=="ST" else .01)]:
            z={k:simulate([(d,m[d][0],other[d][j]) for d in MONTHS],fee,drag,k!="B") for k,j in [("B",lo),("L",lo),("N",mid)]}
            s={k:stats(v) for k,v in z.items()}
            a,b,n=s["L"],s["B"],s["N"]
            diffs={k:[math.log(x[1]/y[1]) for x,y in zip(z["L"],z[k])] for k in ("B","N")}
            phases={str(i):12*st.mean(v for v,d in zip(diffs["B"],MONTHS) if i<=int(d[:4])<=j) for i,j in [(1991,2005),(2006,2015),(2016,2025)]}
            lower={k:boot(v) for k,v in diffs.items()} if fee==10 else {}
            checks=[a["cagr"]-b["cagr"]>=.005,a["cagr"]>n["cagr"],a["vol"]<=b["vol"],a["dd"]>=b["dd"]-.02,phases["2006"]>0,phases["2016"]>0]
            if fee==10:checks += [lower["B"]>.005,lower["N"]>0]
            out[str(fee)]=dict(stats=s,phases=phases,lower=lower,annual_log={k:12*st.mean(v) for k,v in diffs.items()},screen=all(checks),checks=checks)
        result[size]=dict(modes=out,screen=all(x["screen"] for x in out.values()))
    return result
def selftest():
    t="Average Value Weighted Returns -- Monthly\n,SMALL LoPRIOR,ME1 PRIOR2,SMALL HiPRIOR,BIG LoPRIOR,ME2 PRIOR2,BIG HiPRIOR\n"+"\n".join(d+",1,2,3,4,5,6" for d in MONTHS)
    assert parse(t)["199101"]==[.01,.02,.04,.05]
    try:parse(t.replace("199101,1,","199101,-99.99,"));raise AssertionError("sentinel")
    except ValueError:pass
    z=simulate([("199101",.1,0)],10,0,True)
    assert abs(z[0][1]-1.05*.999**2)<1e-12
    assert abs(boot([.001]*420)-.012)<1e-10
    print("SELF_TEST_PASS schema sentinel costs and bootstrap",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit()
    m=parse(load("F-F_Research_Data_Factors_CSV.zip"),True);out={}
    for k,f in [("ST","6_Portfolios_ME_Prior_1_0_CSV.zip"),("LT","6_Portfolios_ME_Prior_60_13_CSV.zip")]:
        try:out[k]=evaluate(m,parse(load(f)),k);print("FAMILY_DONE "+k,flush=True)
        except Exception as e:out[k]={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+k+" "+str(e),flush=True)
    print("REVERSAL_RESULT "+json.dumps(out,allow_nan=False,sort_keys=True),flush=True)
