#!/usr/bin/env python3
"""Frozen annual regional rebalancing comparison; #7149351486."""
import json,math,statistics as st,random,runpy,sys
from pathlib import Path
shared=runpy.run_path(str(Path(__file__).with_name("qt-h2-long-only-premia-20261125.py")))
MONTHS=shared["MONTHS"]
FILES=["Developed_3_Factors_CSV.zip","North_America_3_Factors_CSV.zip","Europe_3_Factors_CSV.zip","Japan_3_Factors_CSV.zip","Asia_Pacific_ex_Japan_3_Factors_CSV.zip"]
W0=[1,0,0,0,0]
WREG=[0,.25,.25,.25,.25]
def simulate(data,policy,bp,drag):
    target=W0 if policy=="B0" else WREG
    w=list(target); cost=bp/10000; f=(1-drag)**(1/12); out=[]
    for i,(d,returns) in enumerate(data):
        rr=[returns[0]]+[(1+x)*f-1 for x in returns[1:]]
        gross=sum(a*(1+b) for a,b in zip(w,rr))
        if gross<=0: raise ValueError("nonpositive wealth")
        w=[a*(1+b)/gross for a,b in zip(w,rr)]
        turnover=0.
        if policy=="R" and d[-2:]=="12" and i+1<len(data):
            turnover=.5*sum(abs(a-b) for a,b in zip(w,target))
            w=list(target)
        fee=cost*turnover
        g=gross*(1-fee)*(1-cost if i==0 else 1)
        out.append((d,g,turnover+(1 if i==0 else 0),fee+(cost if i==0 else 0)))
    return out
def boot(diff):
    n=len(diff);rng=random.Random(20261125);vals=[]
    for _ in range(10000):
        s=0.
        for k in range(0,n,12):
            j=rng.randrange(n);s+=sum(diff[(j+h)%n] for h in range(min(12,n-k)))
        vals.append(12*s/n)
    vals.sort();return [vals[124],vals[9874]]
def evaluate(data):
    assert [x[0] for x in data]==MONTHS and all(len(x[1])==5 for x in data)
    result={}
    for mode,bp,drag in [("base",10,.002),("stress",25,.005)]:
        paths={k:simulate(data,k,bp,drag) for k in ("B0","B1","R")}
        metrics={k:shared["stats"](v) for k,v in paths.items()}
        r=metrics["R"];b0=metrics["B0"];comps={}
        for b in ("B0","B1"):
            bm=metrics[b]
            diff=[math.log(x[1]/y[1]) for x,y in zip(paths["R"],paths[b])]
            periods={str(lo):12*st.mean(d for d,t in zip(diff,MONTHS) if lo<=int(t[:4])<=hi) for lo,hi in [(1991,2005),(2006,2015),(2016,2025)]}
            v=dict(cagr_advantage=r["cagr"]-bm["cagr"],wealth_delta_per_10000=10000*(r["wealth"]-bm["wealth"]),annual_log_difference=12*st.mean(diff),periods=periods)
            if mode=="base": v["ci_97_5"]=boot(diff)
            v["pass"]=v["cagr_advantage"]>=.005 and periods["2006"]>0 and periods["2016"]>0 and (mode!="base" or v["ci_97_5"][0]>0)
            comps[b]=v
        result[mode]=dict(metrics=metrics,comparisons=comps,risk_pass=r["vol"]<=b0["vol"] and r["dd"]>=b0["dd"])
    passed=all(v["risk_pass"] and all(x["pass"] for x in v["comparisons"].values()) for v in result.values())
    return dict(result=result,verdict="PASS_HISTORICAL_CANDIDATE" if passed else "FAIL_FROZEN_EXPRESSION")
def self_test():
    assert shared["parse"]("Date,Mkt-RF,RF\n"+"".join(f"{m},1,0.1\n" for m in MONTHS),[("mktrf",),("rf",)],True)[MONTHS[0]]==[.011]
    d=[("199112",[0,1,0,0,0]),("199201",[0,-.5,0,0,0])]
    a=simulate(d,"R",0,0);b=simulate(d,"B1",0,0)
    assert abs(a[0][1]-1.25)<1e-12 and abs(a[0][2]-1.15)<1e-12
    assert abs(a[1][1]-.875)<1e-12 and abs(b[1][1]-.8)<1e-12
    assert abs(math.prod(x[1] for x in b)-1)<1e-12
    assert abs(simulate(d,"B0",10,.005)[0][1]-.999)<1e-12
    z=[("199101",[0,0,0,0,0])]; assert abs(simulate(z,"B1",0,.005)[0][1]-(1-.005)**(1/12))<1e-12
    assert boot([.001]*420)[0]>.01199
    print("SELF_TEST_PASS reused schema, drift, December rebalancing, common cost, sleeve drag, bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv: self_test();sys.exit(0)
    parts=[shared["parse"](shared["acquire"](file),[("mktrf",),("rf",)],True) for file in FILES]
    data=[(m,[part[m][0] for part in parts]) for m in MONTHS]
    print("GEO_RESULT "+json.dumps(evaluate(data),sort_keys=True,allow_nan=False),flush=True)
