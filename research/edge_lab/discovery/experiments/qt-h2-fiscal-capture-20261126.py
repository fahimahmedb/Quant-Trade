#!/usr/bin/env python3
"""Frozen #7180371113 A: same cash budget; tax refund at month 12; no trade."""
import math,json,statistics as st,runpy,sys
from pathlib import Path
SOURCE=runpy.run_path(str(Path(__file__).with_name("qt-h2-available-capital-deployment-20261126.py")))
BUDGET=5000.;CONTRIB=4990.;FEE=.001;PS=.186;PFU=.314
def net_pea(value,basis):
    return value-PS*max(0,value-basis)
def calc(path,extra,entry,exit):
    n=len(path)
    assert n>=72 and all(x>-1 for x in path)
    gross=math.prod(1+x for x in path)
    gross_side=math.prod(1+x for x in path[12:])
    a=(1-FEE)**2*gross*(1-.002)**(n/12)
    b=a*(1-extra)**(n/12)
    side=(1-FEE)**2*gross_side*(1-.002)**((n-12)/12)
    p=BUDGET*a;v=CONTRIB*b
    refund=CONTRIB*entry
    per=v-exit*min(v,CONTRIB)-PFU*max(0,v-CONTRIB)
    side_net=net_pea(refund*side,refund)
    pea=net_pea(p,BUDGET)
    total=per+side_net
    break_entry=(pea-per)/net_pea(CONTRIB*side,CONTRIB)
    break_exit=(v-PFU*max(0,v-CONTRIB)+side_net-pea)/min(v,CONTRIB)
    return dict(pea=pea,per=total,delta=total-pea,break_entry=break_entry,break_exit=break_exit,refund=refund,per_net=per,side_net=side_net)
def scenarios():
    out=[]
    for h in (10,20,30):
        for g in (-.02,0,.05,.07):
            path=[(1+g)**(1/12)-1]*(12*h)
            for fee in (.005,.01):
                for entry in (0,.11,.30,.41,.45):
                    for exit in (0,.11,.30,.41,.45):
                        out.append(dict(h=h,g=g,fee=fee,entry=entry,exit=exit,**calc(path,fee,entry,exit)))
    assert len(out)==600
    return out
def hist(data):
    vals=[r for r,f in data.values()]
    assert len(vals)==420
    out=[]
    for h in (10,20,30):
        n=12*h;N=len(vals)-n+1
        for fee in (.005,.01):
            for entry,exit in ((.11,.11),(.30,.11),(.41,.30)):
                ds=[calc(vals[i:i+n],fee,entry,exit)["delta"] for i in range(N)]
                ordered=sorted(ds)
                disjoint=ds[::n]
                q=ordered[math.floor(.05*N)]
                win=sum(x>0 for x in ds)/N
                out.append(dict(h=h,fee=fee,entry=entry,exit=exit,n=N,mean=st.mean(ds),median=st.median(ds),q05=q,win=win,worst=min(ds),best=max(ds),nonoverlap_n=len(disjoint),nonoverlap_positive=sum(x>0 for x in disjoint),robust=win>=.90 and q>0))
    return out
def selftest():
    x=calc([0.]*120,.005,0,0)
    assert abs(x["pea"]-5000*.999**2*.998**10)<1e-8
    assert abs(x["per"]-4990*.999**2*.998**10*.995**10)<1e-8
    y=calc([0.]*120,.005,.30,.11)
    assert abs(y["side_net"]-4990*.30*.999**2*.998**9)<1e-8
    z=calc([0.]*120,.005,y["break_entry"],.11)
    assert abs(z["delta"])<1e-8
    z=calc([0.]*120,.005,.30,y["break_exit"])
    assert abs(z["delta"])<1e-8
    p=[1.]+[0.]*119
    q=calc(p,.005,.30,.11)
    assert abs(q["side_net"]-y["side_net"])<1e-8
    r=calc([.01]*120,.005,.30,.11)
    assert r["pea"]>5000 and r["per_net"]>0
    assert len(scenarios())==600
    print("SELF_TEST_PASS common cash, refund lag, tax basis, two break-even identities, grid")
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    grid=scenarios()
    print("GRID_RESULT "+json.dumps(grid,allow_nan=False,separators=(",",":")),flush=True)
    result={}
    for region,file in SOURCE["FILES"].items():
        try:
            data=SOURCE["acquire"](file)
            result[region]=hist(data)
            print("REGION_DONE "+region,flush=True)
        except Exception as e:
            result[region]={"BLOCK_DATA":str(e)}
            print("BLOCK_DATA "+region+" "+str(e),flush=True)
    print("FISCAL_RESULT "+json.dumps(result,allow_nan=False,separators=(",",":")),flush=True)
