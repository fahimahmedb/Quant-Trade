#!/usr/bin/env python3
"""Frozen #7180517321, matched capital, actual tax brackets, known archival return paths."""
import math,statistics as st,runpy,json,hashlib,zipfile,urllib.request,io,sys
from pathlib import Path
SRC=runpy.run_path(str(Path(__file__).with_name("qt-h2-available-capital-deployment-20261126.py")))
HASH={"US":"b03d39e4bb253dda0f14893db3b78e64b40b8d6549a0fc0fd4111dae84c98618","Europe":"842332540d9c86681cbda628c6acc9d75d0c1563e364a2bf6a535072f651471e","Japan":"525605ffa42317b6a66389fb5911d5b2a7f34359b5cecdfa1c3aa52f63a6a15d"}
PROFILES=[(30000,20000),(35000,15000),(35000,20000),(35000,28000)]
def gross(x):
    return sum(max(0,min(x,b)-a)*r for a,b,r in [(11600,29579,.11),(29579,84577,.3),(84577,181917,.41),(181917,float("inf"),.45)])
def afterdec(g):
    a=max(0,g-max(0,897-.4525*g));return a if a>=61 else 0.
def tax(x):return afterdec(gross(x))
def incremental(x,p,q=False):
    return afterdec(gross(x)+4*(gross(x+p/4)-gross(x)))-tax(x) if q else tax(x+p)-tax(x)
def net(v,b,rate=.186):return v-rate*max(0,v-b)
def pernet(v,b,x,q):return net(v,b,.314)-incremental(x,min(v,b),q)
def factor(path,extra=0):
    return .999**2*math.prod(1+r for r in path)*(.998*(1-extra))**(len(path)/12)
def allocation(path,E,X,cap,extra,q,match=None,peeextra=0,shock=0,useper=True):
    # Same 5k initial cash; any employer capital and tax refund are external benefits.
    emp=1000. if match is not None else 0.
    fee=10. if useper else 0.
    c=min(cap,5000-emp-fee) if useper else 0.
    p=5000-emp-fee-c
    assert abs(emp+fee+c+p-5000)<1e-9
    a=factor(path);b=factor(path[12:])
    refund=tax(E)-tax(E-c) if useper else 0.
    pea_v=p*a+refund*b;pea_basis=p+refund
    if emp:
        start=emp*(1+.903*match)
        proceeds=net(start*factor(path[:60],peeextra)*(1+shock),start)
        pea_v+=proceeds*factor(path[60:])
        pea_basis+=proceeds
    per=pernet(c*factor(path,extra),c,X,q) if c else 0.
    pea=net(pea_v,pea_basis)
    return dict(wealth=per+pea,per=per,pea=pea,contrib=c,refund=refund)
def A(path,E,X,cap,fee,q):
    base=net(5000*factor(path),5000)
    return allocation(path,E,X,cap,fee,q)["wealth"]-base
def C(path,E,X,m,stress,q,shock):
    f=.01 if stress else .005;pf=.015 if stress else .005
    P=net(5000*factor(path),5000)
    R=allocation(path,E,X,4710,f,q)["wealth"]
    M=allocation(path,E,X,4710,f,q,m,pf,shock,False)["wealth"]
    H=allocation(path,E,X,4710,f,q,m,pf,shock,True)["wealth"]
    return [P,R,M,H]
def stats(v):
    a=sorted(v);n=len(a);q=a[math.floor(.05*n)];w=sum(x>0 for x in a)/n
    return dict(n=n,mean=st.mean(a),median=st.median(a),q05=q,worst=a[0],win=w,robust=w>=.9 and q>0)
def B(v,b,x,g,years,qfirst=True):
    # t0 initial payout, final common time t4. Withdrawal based on remaining equal fractions.
    cash=0.;ir=0.;pf=0.;prev=None
    for i,t in enumerate(years):
        if prev is not None:
            v*= (1+g)**(t-prev);cash*=1.03**(t-prev)
        n=len(years)-i
        w=v/n;basis=b/n;principal=min(w,basis)
        quot=qfirst and (prev is None or t-prev>=4)
        a=incremental(x,principal,quot);z=.314*max(0,w-basis)
        cash+=w-a-z;ir+=a;pf+=z
        v-=w;b-=basis;prev=t
    assert abs(v)<1e-8 and abs(b)<1e-8
    return dict(wealth=cash*1.03**(4-prev),ir=ir,pfu=pf)
POL=[("ordinary",[0],False),("quotient",[0],True),("annual2",[0,1],True),("annual3",[0,1,2],True),("annual5",[0,1,2,3,4],True),("spaced2",[0,4],True)]
def D(age,old,friction):
    v=50000.;g=1.05*.998;h=10;new=.005
    wait=max(0,5-age)
    initial=.01 if age<5 else 0.
    paths={"retain":v*(g*(1-old))**h,"now":v*(1-initial)*(1-friction)*(g*(1-new))**h,"wait":v*(g*(1-old))**wait*(1-friction)*(g*(1-new))**(h-wait)}
    return {k:pernet(w,30000,20000,False) for k,w in paths.items()}
def deterministic():
    bb=[];cc=[];dd=[]
    for v,b in [(50000,30000),(100000,60000)]:
        for x in (15000,20000,30000,40000):
            for g in (-.1,0,.03,.07):
                base=B(v,b,x,g,[0])["wealth"]
                for label,years,q in POL:
                    y=B(v,b,x,g,years,q)
                    bb.append(dict(v=v,b=b,x=x,g=g,policy=label,delta=y["wealth"]-base,**y))
    for E,X in [(30000,20000),(35000,20000)]:
        for g in (-.02,0,.05,.07):
            path=[(1+g)**(1/12)-1]*120
            for match in (0,.5,1,2):
                for stress in (False,True):
                    for shock in (0,-.5):
                        for q in (False,True):
                            w=C(path,E,X,match,stress,q,shock)
                            cc.append(dict(E=E,X=X,g=g,match=match,stress=stress,shock=shock,q=q,w=w,delta=w[3]-w[0],increment=w[3]-max(w[:3])))
    for age in (0,2,4,5):
        for old in (.0075,.01,.015):
            for friction in (0,.03):
                w=D(age,old,friction)
                dd.append(dict(age=age,old=old,friction=friction,**w))
    assert (len(bb),len(cc),len(dd))==(192,256,24)
    return dict(B=bb,C=cc,D=dd)
def acquire(region,file):
    url=SRC["BASE"]+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade bounded academic research"}),timeout=25) as r:
        if not r.url.startswith(SRC["BASE"]):raise ValueError("redirect")
        raw=r.read(4000001)
    h=hashlib.sha256(raw).hexdigest()
    if h!=HASH[region] or len(raw)>4000000:raise ValueError("frozen archive hash mismatch "+h)
    print("SOURCE "+json.dumps(dict(region=region,url=url,sha256=h,bytes=len(raw))),flush=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        f=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(f)!=1 or z.getinfo(f[0]).file_size>8000000:raise ValueError("schema")
        d=SRC["parse"](z.read(f[0]).decode("utf-8-sig"))
    assert len(d)==420
    print("QA "+json.dumps(dict(region=region,n=len(d),start=next(iter(d)),end=list(d)[-1])),flush=True)
    return [r for r,f in d.values()]
def historical(vals):
    windows=[vals[i:i+120] for i in range(301)];aa=[];cc=[]
    for E,X in PROFILES:
        for cap in (4710,4990):
            for fee in (.005,.01):
                for q in (False,True):
                    aa.append(dict(E=E,X=X,cap=cap,fee=fee,q=q,**stats([A(w,E,X,cap,fee,q) for w in windows])))
    for E,X in [(30000,20000),(35000,20000)]:
        for match in (.5,1):
            for stress in (False,True):
                for shock in (0,-.5):
                    for q in (False,True):
                        w=[C(p,E,X,match,stress,q,shock) for p in windows]
                        cc.append(dict(E=E,X=X,match=match,stress=stress,shock=shock,q=q,vs_pea=stats([a[3]-a[0] for a in w]),vs_best=stats([a[3]-max(a[:3]) for a in w])))
    assert len(aa)==len(cc)==32
    return dict(A=aa,C=cc)
def selftest():
    assert abs(gross(30000)-2103.99)<1e-8
    assert abs(afterdec(1400)-1136.5)<1e-8
    assert abs(tax(30000)-tax(25010)-858.40725)<1e-8
    assert abs(incremental(20000,4990)-797.27725)<1e-8
    assert abs(incremental(20000,4990,True)-797.27725)<1e-8
    assert incremental(28000,30000,True)<incremental(28000,30000)
    # BOFiP fractional basis example
    assert 4500*15000/18000==3750
    x=B(50000,30000,20000,0,[0]);assert abs(x["wealth"]-(50000-incremental(20000,30000,True)-6280)*1.03**4)<1e-8
    a=allocation([0.]*120,35000,20000,4710,.005,True)
    assert a["contrib"]==4710 and abs(a["refund"]-1413)<1e-8
    assert abs(D(5,.01,0)["now"]-D(5,.01,0)["wait"])<1e-8
    deterministic()
    print("SELF_TEST_PASS tax bracket, decote, quotient, basis, withdrawal timing, budget and transfer",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    d=deterministic()
    for k,v in d.items():print("DETERMINISTIC_"+k+" "+json.dumps(v,separators=(",",":"),allow_nan=False),flush=True)
    out={}
    for reg,f in SRC["FILES"].items():
        try:out[reg]=historical(acquire(reg,f));print("REGION_DONE "+reg,flush=True)
        except Exception as e:out[reg]={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+reg+" "+str(e),flush=True)
    for reg,rows in out.items():print("HIST_"+reg+" "+json.dumps(rows,separators=(",",":"),allow_nan=False),flush=True)
