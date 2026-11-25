#!/usr/bin/env python3
"""Fixed four-session turn-of-month hypothesis. Protocol #7149837103."""
import calendar, collections, csv, datetime as dt, hashlib, io, json, math, random, re, statistics as st, sys, urllib.request, zipfile
BASE="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES={"US":"F-F_Research_Data_Factors_daily_CSV.zip","Europe":"Europe_3_Factors_Daily_CSV.zip","Japan":"Japan_3_Factors_Daily_CSV.zip"}
MONTHS={f"{y}{m:02d}" for y in range(1991,2026) for m in range(1,13)}
def acquire(file):
    url=BASE+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade bounded public research"}),timeout=25) as r:
        if not r.url.startswith(BASE):raise ValueError("unexpected redirect")
        b=r.read(5_000_001)
    if len(b)>5_000_000:raise ValueError("oversize")
    print("SOURCE "+json.dumps(dict(file=file,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1 or z.getinfo(names[0]).file_size>10_000_000:raise ValueError("archive schema")
        rows=list(csv.reader(io.StringIO(z.read(names[0]).decode("utf-8-sig"))))
    hi=next(i for i,row in enumerate(rows) if "Mkt-RF" in [x.strip() for x in row] and "RF" in [x.strip() for x in row])
    h=[x.strip() for x in rows[hi]]
    out=[]
    for row in rows[hi+1:]:
        if not row or not re.fullmatch(r"\d{8}",row[0].strip()):continue
        d=row[0].strip()
        if not "19910101"<=d<="20251231":continue
        dt.datetime.strptime(d,"%Y%m%d")
        x=float(row[h.index("Mkt-RF")])/100;f=float(row[h.index("RF")])/100
        if not all(map(math.isfinite,[x,f])) or abs(x)>.5 or abs(f)>.05 or x+f<=-1 or f<=-1:raise ValueError("invalid return")
        out.append((d,x+f,f))
    if len({x[0] for x in out})!=len(out) or out!=sorted(out):raise ValueError("date order/duplicates")
    counts=collections.Counter(x[0][:6] for x in out)
    if set(counts)!=MONTHS or min(counts.values())<10:raise ValueError("coverage")
    print("QA "+json.dumps(dict(rows=len(out),months=len(counts),first=out[0][0],last=out[-1][0],min_sessions=min(counts.values()),header=h)),flush=True)
    return out
def mask(rows):
    by=collections.defaultdict(list)
    for d,_,_ in rows:by[d[:6]].append(d)
    return {d for v in by.values() for d in v[:3]+v[-1:]}
def window(rows,a,b):return [x for x in rows if a<=int(x[0][:4])<=b]
def path(rows,policy,bp):
    w=0.;c=bp/10000;out=[]
    for i,(d,r,f) in enumerate(rows):
        t=policy(d);turn=abs(t-w)
        gross=1+t*r+(1-t)*f
        g=(1-c*turn)*gross
        w=t*(1+r)/gross
        if i==len(rows)-1:
            g*=1-c*w;turn+=w
        out.append((d,g,t,turn))
    return out
def stats(rows):
    l=0.;peak=0.;dd=0.
    for d,g,*_ in rows:
        l+=math.log(g);peak=max(peak,l);dd=min(dd,math.exp(l-peak)-1)
    y=len({x[0][:6] for x in rows})/12
    return dict(n=len(rows),years=y,wealth=math.exp(l),cagr=math.expm1(l/y),vol=st.stdev(x[1]-1 for x in rows)*math.sqrt(252),dd=dd,mean_exposure=st.mean(x[2] for x in rows),annual_turnover=sum(x[3] for x in rows)/y)
def paired(a,b):
    assert [x[0] for x in a]==[x[0] for x in b]
    months=collections.defaultdict(float);years=collections.defaultdict(float)
    for x,y in zip(a,b):
        d=math.log(x[1]/y[1]);months[x[0][:6]]+=d;years[x[0][:4]]+=d
    return list(months.values()),dict(years)
def boot(x):
    n=len(x);rng=random.Random(20261125);v=[]
    for _ in range(20000):
        s=0.
        for k in range(0,n,12):
            j=rng.randrange(n)
            s+=sum(x[(j+h)%n] for h in range(min(12,n-k)))
        v.append(12*s/n)
    v.sort()
    return dict(lower_bonferroni=v[333],median=v[10000],upper_descriptive=v[19666])
def evaluate(rows):
    selected=mask(rows)
    T=lambda d:float(d in selected)
    train=window(rows,1991,2000)
    trainT=stats(path(train,T,5));trainB=stats(path(train,lambda _:1.,5))
    exp=trainT["mean_exposure"];risk=min(1,trainT["vol"]/trainB["vol"])
    policies={"T":T,"B":lambda _:1.,"C":lambda _:exp,"R":lambda _:risk}
    modes={}
    for fee in (5,15):
        cases={}
        for name,lo,hi in [("pooled",2001,2025),("early",2001,2010),("late",2011,2025)]:
            data=window(rows,lo,hi)
            ret={k:path(data,pol,fee) for k,pol in policies.items()}
            z={k:stats(v) for k,v in ret.items()}
            m,y=paired(ret["T"],ret["R"])
            pos=sum(v>.005 for v in y.values());n=sum(v!=.005 for v in y.values())
            z["annual_log_diff"]=12*st.mean(m)
            z["annual_differences"]=y
            z["sign_p_hurdle"]=sum(math.comb(n,k) for k in range(pos,n+1))/2**n
            z["positive_years_above_hurdle"]=pos
            z["cagr_advantage"]=z["T"]["cagr"]-z["R"]["cagr"]
            if name=="pooled" and fee==5:z["bootstrap"]=boot(m)
            cases[name]=z
        v=cases["pooled"];a,b=v["T"],v["R"]
        cases["screen"]=v["cagr_advantage"]>=.005 and a["vol"]<=b["vol"] and a["dd"]>=b["dd"] and all(cases[k]["annual_log_diff"]>0 for k in ("early","late")) and (fee!=5 or v["bootstrap"]["lower_bonferroni"]>.005)
        modes[str(fee)]=cases
    return dict(train_exposure=exp,train_risk_weight=risk,train_T=trainT,train_B=trainB,modes=modes,screen=all(x["screen"] for x in modes.values()))
def self_test():
    a=[("2001010"+str(i),.1,0.) for i in range(1,6)]+[("2001020"+str(i),0.,.001) for i in range(1,6)]
    s=mask(a);assert s=={"20010101","20010102","20010103","20010105","20010201","20010202","20010203","20010205"}
    x=path([("20010101",.1,0.),("20010102",-.5,0.)],lambda d:float(d.endswith("01")),5)
    assert abs(x[0][1]-1.1*.9995)<1e-12 and abs(x[1][1]-.9995)<1e-12
    x=path([("20010101",.1,0.)],lambda _:1.,5);assert abs(x[0][1]-1.1*.9995**2)<1e-12
    assert abs(stats(path([("20010101",.1,0.),("20010102",-.1,0.)],lambda _:1.,0))["dd"]+.1)<1e-12
    assert abs(boot([.001]*300)["lower_bonferroni"]-.012)<1e-10
    print("SELF_TEST_PASS calendar mask, fee timing, terminal liquidation, drawdown, bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    out={}
    for region,file in FILES.items():
        try:out[region]=evaluate(acquire(file));print("REGION_DONE "+region,flush=True)
        except Exception as e:out[region]={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+region+" "+str(e),flush=True)
    print("CALENDAR_RESULT "+json.dumps(dict(regions=out,screen=all(x.get("screen",False) for x in out.values())),sort_keys=True,allow_nan=False),flush=True)
