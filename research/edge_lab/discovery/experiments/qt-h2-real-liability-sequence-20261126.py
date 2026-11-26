#!/usr/bin/env python3
"""Frozen #7180839999; fixed real withdrawals, no live transactions."""
import csv,io,hashlib,json,math,statistics as st,sys,urllib.request,runpy
from pathlib import Path
I=runpy.run_path(str(Path(__file__).with_name("qt-h2-credit-diversification-20261126.py")))
HASH="127c772f0fea8763391dbf2c1c7d3ecd3a07ca2b23f81ab47af58b529e2b5647"
CPI="https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS&cosd=1927-12-01&coed=2025-12-01"
W={"B":(.6,.4,0.),"S":(.6,.3,.1),"K":(.6,.3,.1),"D":(.4,.6,0.)}
def fetch(url,host):
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade bounded academic research"}),timeout=25) as r:
        if not r.url.startswith(host):raise ValueError("unexpected redirect")
        b=r.read(4000001);encoding=r.headers.get_content_charset() or "windows-1252"
    if len(b)>4000000:raise ValueError("oversize")
    h=hashlib.sha256(b).hexdigest();print("SOURCE "+json.dumps(dict(url=url,sha256=h,bytes=len(b))),flush=True)
    return b.decode(encoding,errors="strict"),h
def market():
    s,h=fetch(I["URL"],"https://pages.stern.nyu.edu/")
    if h!=HASH:raise ValueError("prior pinned market hash changed")
    return I["parse"](s)
def inflation():
    s,h=fetch(CPI,"https://fred.stlouisfed.org/")
    r=csv.DictReader(io.StringIO(s))
    if r.fieldnames not in (["observation_date","CPIAUCNS"],["DATE","CPIAUCNS"]):raise ValueError("CPI header")
    d={}
    for x in r:
        t=x[r.fieldnames[0]]
        if t[5:]!="12-01":continue
        y=int(t[:4])
        if not 1927<=y<=2025:continue
        v=float(x["CPIAUCNS"])
        if y in d or not math.isfinite(v) or v<=0:raise ValueError("invalid CPI")
        d[y]=v
    if list(d)!=list(range(1927,2026)):raise ValueError("CPI December coverage")
    print("CPI_QA "+json.dumps(dict(n=len(d),first=d[1927],last=d[2025])),flush=True)
    return {y:d[y]/d[y-1] for y in range(1928,2026)}
def rebalance(h,w,c):
    V=sum(h)
    if V<=0:return [0.]*3,0.
    lo,hi=0.,V
    for _ in range(60):
        x=(lo+hi)/2
        turnover=sum(abs(a-x*b) for a,b in zip(h,w))
        if x+c*turnover>V:hi=x
        else:lo=x
    x=(lo+hi)/2
    t=sum(abs(a-x*b) for a,b in zip(h,w))
    assert abs(x+c*t-V)<1e-7*max(1,V)
    return [x*b for b in w],t
def withdraw(h,amount,c,bucket):
    V=sum(h);sale=min(V,amount/(1-c))
    if sale==0:return h[:],0.,0.
    if not bucket:
        z=[a*(1-sale/V) for a in h]
    else:
        cash=min(h[2],sale);left=sale-cash;v=h[0]+h[1]
        z=[max(0,h[i]*(1-left/v)) if v else 0. for i in (0,1)]+[h[2]-cash]
    assert min(z)>=-1e-7 and abs(sum(z)+sale-V)<1e-7*max(1,V)
    return z,sale*(1-c),sale
def path(rows,infl,policy,payout,bp):
    c=bp/10000;w=W[policy];start=100000
    h=[start*x/(1+c) for x in w];turn=sum(h)
    total=0.;short=0.;first=None;minimum=sum(h);exposure=[]
    for i,(y,e,rf,t,b) in enumerate(rows):
        V=sum(h);minimum=min(minimum,V)
        h,paid,sale=withdraw(h,payout,c,policy=="K");turn+=sale
        total+=paid;short+=max(0,payout-paid)
        if paid<payout-1e-7 and first is None:first=i+1
        V=sum(h);exposure.append(h[0]/V if V else 0.)
        h=[a*g*.998/infl[y] for a,g in zip(h,(1+e,1+t,1+rf))]
        if i<len(rows)-1 and (policy!="K" or e>=0):
            h,tr=rebalance(h,w,c);turn+=tr
    terminal=sum(h)*(1-c);turn+=sum(h)
    return dict(terminal=terminal,payout=total,shortfall=short,first_shortfall=first,minwealth=minimum,turnover=turn/len(rows)/start,exposure=st.mean(exposure))
def q05(x):return sorted(x)[math.floor(.05*len(x))]
def summary(x):
    return dict(n=len(x),failed=sum(a["first_shortfall"] is not None for a in x),mean_shortfall=st.mean(a["shortfall"] for a in x),max_shortfall=max(a["shortfall"] for a in x),mean_terminal=st.mean(a["terminal"] for a in x),median_terminal=st.median(a["terminal"] for a in x),q05_terminal=q05([a["terminal"] for a in x]),worst_terminal=min(a["terminal"] for a in x),mean_exposure=st.mean(a["exposure"] for a in x),mean_turnover=st.mean(a["turnover"] for a in x))
def compare(a,b):
    d=[x["terminal"]-y["terminal"] for x,y in zip(a,b)];s=[x["shortfall"]-y["shortfall"] for x,y in zip(a,b)]
    return dict(mean=st.mean(d),q05=q05(d),min=min(d),wins=sum(x>1e-7 for x in d),shortfall_worse=sum(x>1e-7 for x in s),shortfall_better=sum(x< -1e-7 for x in s),screen=max(s)<=1e-7 and st.mean(d)>=-1e-7 and q05(d)>=-1e-7 and (max(d)>1e-7 or min(s)<-1e-7))
def evaluate(rows,infl):
    out=[]
    for payout in (3000,4000,5000):
        for bp in (10,30):
            z={p:[path(rows[i:i+20],infl,p,payout,bp) for i in range(79)] for p in W}
            out.append(dict(payout=payout,bp=bp,stats={p:summary(v) for p,v in z.items()},compare={a+"_"+b:compare(z[a],z[b]) for a,b in [("K","S"),("S","B"),("D","B")]}))
    return out
def selftest():
    h,t=rebalance([60.,40.,0.],(.5,.5,0.),.001)
    assert abs(sum(h)+t*.001-100)<1e-10
    h,p,t=withdraw([60.,30.,10.],15.,.001,True)
    assert h[2]==0 and abs(p-15)<1e-10
    rows=[(y,0.,0.,0.,0.) for y in range(20)]
    z=path(rows,{y:1. for y in range(20)},"B",4000,0)
    v=100000.
    for _ in rows:v=(v-4000)*.998
    assert abs(z["terminal"]-v)<1e-7 and abs(z["payout"]-80000)<1e-7
    z=path(rows,{y:1. for y in range(20)},"K",20000,10)
    assert z["shortfall"]>0 and z["terminal"]==0 and abs(z["payout"]+z["shortfall"]-400000)<1e-7
    print("SELF_TEST_PASS rebalance accounting, cash-first, equal spending, depletion",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    rows=market()
    try:actual=inflation()
    except Exception as e:actual=None;print("BLOCK_CPI "+type(e).__name__+": "+str(e),flush=True)
    for name,inf in [("fixed2",{y:1.02 for y,*_ in rows}),("fixed4",{y:1.04 for y,*_ in rows}),("actual",actual)]:
        if inf is not None:print("SEQUENCE_"+name+" "+json.dumps(evaluate(rows,inf),separators=(",",":"),allow_nan=False),flush=True)
