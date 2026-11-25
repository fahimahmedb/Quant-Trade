#!/usr/bin/env python3
"""One predeclared historical economic test. No live orders."""
import csv, io, math, statistics as st, random, json, hashlib, zipfile, urllib.request, re, sys, collections
URL="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
def load():
    req=urllib.request.Request(URL,headers={"User-Agent":"QuantTrade public research"})
    with urllib.request.urlopen(req,timeout=35) as f:
        if not f.url.startswith("https://mba.tuck.dartmouth.edu/"): raise ValueError("unexpected redirect")
        b=f.read(8_000_001)
    if len(b)>8_000_000: raise ValueError("oversize")
    print("SOURCE "+json.dumps(dict(url=URL,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        n=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(n)!=1 or z.getinfo(n[0]).file_size>10_000_000: raise ValueError("archive schema")
        lines=list(csv.reader(io.StringIO(z.read(n[0]).decode("utf-8-sig"))))
    header=next(i for i,row in enumerate(lines) if "Mkt-RF" in [x.strip() for x in row] and "RF" in [x.strip() for x in row])
    h=[x.strip() for x in lines[header]]
    out=[]
    for row in lines[header+1:]:
        if not row or not re.fullmatch(r"\d{8}",row[0].strip()): continue
        d=row[0].strip()
        if "19640101"<=d<="20251231":
            x=float(row[h.index("Mkt-RF")])/100; f=float(row[h.index("RF")])/100
            if not all(map(math.isfinite,[x,f])) or x+f<=-1 or f<=-1 or abs(x)>0.5 or abs(f)>0.05: raise ValueError("invalid return")
            out.append((d,x+f,f))
    assert len({d for d,_,_ in out})==len(out) and out==sorted(out)
    expected={f"{y}{m:02d}" for y in range(1964,2026) for m in range(1,13)}
    assert {d[:6] for d,_,_ in out}==expected
    print("QA "+json.dumps(dict(rows=len(out),first=out[0][0],last=out[-1][0],months=len(expected),header=h)),flush=True)
    return out
def sig(rows):
    groups=collections.defaultdict(list)
    for d,r,f in rows: groups[d[:6]].append(r)
    months=sorted(groups)
    return {m:min(1,.10/(st.stdev(groups[months[i-1]])*math.sqrt(252))) if st.stdev(groups[months[i-1]])>0 else 1 for i,m in enumerate(months) if i>0}
def step(w,r,f,target,cost):
    gross=1+w*r+(1-w)*f
    held=w*(1+r)/gross
    turn=abs(target-held) if target is not None else 0
    # proportional fee on traded risky weight, approximate as fraction of pre-fee wealth
    factor=gross*(1-cost*turn)
    return factor, target if target is not None else held, turn, cost*turn
def simulate(rows,policy,cost):
    w=0.; last=None; out=[]
    for d,r,f in rows:
        if d<"19650101": continue
        m=d[:6]
        target=policy(m) if m!=last else None
        factor,w,turn,fee=step(w,r,f,target,cost)
        out.append((d,factor,w,turn,fee));last=m
    return out
def stats(rows):
    log=0.; peak=0.; dd=0.
    for d,g,*_ in rows:
        log+=math.log(g);peak=max(peak,log);dd=min(dd,math.exp(log-peak)-1)
    years=len({r[0][:6] for r in rows})/12
    return dict(days=len(rows),years=years,wealth=math.exp(log),cagr=math.expm1(log/years),vol=st.stdev(r[1]-1 for r in rows)*math.sqrt(252),drawdown=dd,mean_weight=st.mean(r[2] for r in rows),annual_turnover=sum(r[3] for r in rows)/years,annual_fee_fraction=sum(r[4] for r in rows)/years)
def window(rows,a,b): return [r for r in rows if a<=r[0][:4]<=b]
def bootstrap(v,b):
    by=collections.defaultdict(float)
    assert [x[0] for x in v]==[x[0] for x in b]
    for x,y in zip(v,b): by[x[0][:6]]+=math.log(x[1])-math.log(y[1])
    x=list(by.values());n=len(x); rng=random.Random(20261125); res=[]
    for _ in range(10000):
        s=0.;k=0
        while k<n:
            j=rng.randrange(n)
            for h in range(min(12,n-k)): s+=x[(j+h)%n]
            k+=12
        res.append(12*s/n)
    res.sort()
    return [res[249],res[9749]]
def evaluate(rows):
    weights=sig(rows)
    v=lambda m:weights[m];full=lambda m:1.;eighty=lambda m:.8
    training_v=stats(window(simulate(rows,v,.001),"1965","1984"))
    training_m=stats(window(simulate(rows,full,.001),"1965","1984"))
    scale=min(1,training_v["vol"]/training_m["vol"])
    policies={"V":v,"M":full,"80":eighty,"R":lambda m:scale}
    periods={"pooled":("1985","2025"),"early":("1985","2004"),"middle":("2005","2016"),"late":("2017","2025")}
    res={}
    for bp in (10,25):
        rr={k:simulate(rows,f,bp/10000) for k,f in policies.items()}
        result={}
        for name,(a,b) in periods.items():
            subset={k:window(z,a,b) for k,z in rr.items()}
            s={k:stats(z) for k,z in subset.items()}
            s["delta_log_annual"]=math.log(s["V"]["wealth"]/s["R"]["wealth"])/s["V"]["years"]
            result[name]=s
            if name=="pooled" and bp==10:
                result["bootstrap_95"]=bootstrap(subset["V"],subset["R"])
        annual={}
        for year in range(1985,2026):
            a=window(rr["V"],str(year),str(year)); b=window(rr["R"],str(year),str(year))
            annual[str(year)]=[math.prod(x[1] for x in a)-1,math.prod(x[1] for x in b)-1]
        result["annual_V_R"]=annual
        res[str(bp)]=result
    def meets(s):
        a,b=s["pooled"]["V"],s["pooled"]["R"]
        return a["cagr"]-b["cagr"]>=.005 and a["vol"]<=b["vol"] and a["drawdown"]>=b["drawdown"] and all(s[k]["delta_log_annual"]>0 for k in ("early","middle","late"))
    passed=all(meets(res[str(bp)]) for bp in (10,25)) and res["10"]["bootstrap_95"][0]>0
    return dict(risk_matched_static_weight=scale,train_V=training_v,train_M=training_m,results=res,verdict="PASS_HISTORICAL_CANDIDATE" if passed else "FAIL_FROZEN_EXPRESSION")
def selftest():
    g,w,t,f=step(0,.1,.001,1,.001);assert abs(g-1.001*.999)<1e-12 and w==1 and t==1
    g,w,t,f=step(.5,.10,0,None,.001);assert abs(g-1.05)<1e-12 and abs(w-.55/1.05)<1e-12 and t==0
    g,w,t,f=step(1,-.1,.01,0,.0025);assert abs(g-.9*.9975)<1e-12 and w==0
    sample=[("19641201",.01,0),("19641202",-.01,0),("19650101",.2,0),("19650102",-.3,0)]
    assert abs(sig(sample)["196501"]-min(1,.1/(st.stdev([.01,-.01])*math.sqrt(252))))<1e-12
    a=simulate(sample,lambda _:1.,0)
    assert a[0][1]==1 and abs(a[1][1]-.7)<1e-12
    assert stats(a)["drawdown"]<-.29
    print("SELF_TEST_PASS accounting, costs, lag, cash, no leverage, drawdown")
if __name__=="__main__":
    if "--self-test" in sys.argv: selftest()
    else: print("ECON_RESULT "+json.dumps(evaluate(load()),allow_nan=False,sort_keys=True),flush=True)
