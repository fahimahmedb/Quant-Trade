#!/usr/bin/env python3
"""Frozen four-expression industry allocation test, issue #60 comment 7179466861."""
import csv,io,math,statistics as st,random,json,hashlib,zipfile,urllib.request,re,sys
BASE="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
MONTHS=[f"{y}{m:02d}" for y in range(1970,2026) for m in range(1,13)]
def acquire(file):
    url=BASE+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade bounded academic research"}),timeout=25) as r:
        if not r.url.startswith(BASE):raise ValueError("unexpected redirect")
        b=r.read(8_000_001)
    if len(b)>8_000_000:raise ValueError("oversize")
    print("SOURCE "+json.dumps({"file":file,"url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1 or z.getinfo(names[0]).file_size>16_000_000:raise ValueError("archive schema")
        return z.read(names[0]).decode("utf-8-sig")
def norm(s):return re.sub(r"[^a-z0-9]","",s.lower())
def parse(text,n):
    rows=list(csv.reader(io.StringIO(text)))
    if n:
        markers=[i for i,r in enumerate(rows) if "averagevalueweightedreturnsmonthly" in norm(" ".join(r))]
        if len(markers)!=1:raise ValueError("monthly value-weighted section mismatch")
        start=markers[0]+1
    else:start=0
    header=None
    for i in range(start,min(len(rows),start+25)):
        r=[x.strip() for x in rows[i]]
        if n:
            if len(r)==n+1 and not r[0] and all(r[1:]) and len(set(r[1:]))==n:header=i;indices=list(range(1,n+1));break
        elif all(r.count(k)==1 for k in ("Mkt-RF","SMB","HML","RF")):
            header=i;indices=[r.index(k) for k in ("Mkt-RF","SMB","HML","RF")];break
    if header is None:raise ValueError("header missing")
    out={};begun=False
    for row in rows[header+1:]:
        if not row or not re.fullmatch(r"\d{6}",row[0].strip()):
            if begun:break
            continue
        begun=True;d=row[0].strip()
        if d not in MONTHS:continue
        if d in out:raise ValueError("duplicate "+d)
        v=[float(row[j])/100 for j in indices]
        if not all(math.isfinite(x) and -1<x<5 and x not in (-.9999,-.99,-.999) for x in v):raise ValueError("invalid or missing "+d)
        if not n and (v[0]+v[3]<=-1 or abs(v[3])>.1):raise ValueError("market/RF invalid")
        out[d]=v
    if list(out)!=MONTHS:raise ValueError("missing or out-of-order months: "+str(sorted(set(MONTHS)-set(out))[:20]))
    print("QA "+json.dumps({"universe":n or "market","header":rows[header],"months":len(out),"first":next(iter(out)),"last":list(out)[-1]}),flush=True)
    return out
def simulate(data,kind,fee,drag,risk=1):
    """Weights before current month's return; transaction fees on pre-fee wealth."""
    n=len(data[0][1]);industry=kind in ("M","A","D")
    target=[1/n]*n+[0.] if industry else [risk,1-risk]
    w=[0.]*(len(target)-1)+[1.]
    cost=fee/10000
    monthly_drag=(1-drag)**(1/12)
    out=[]
    for i,(d,ind,factors) in enumerate(data):
        mk,sm,hml,rf=factors
        returns=[(1+r)*monthly_drag-1 for r in ind]+[rf] if industry else [mk+rf,rf]
        rebalance=i==0 or kind in ("M","B","R") or (kind=="A" and d.endswith("01"))
        turn=sum(abs(x-y) for x,y in zip(w[:-1],target[:-1])) if rebalance else 0.
        if rebalance:w=list(target)
        gross=sum(a*(1+b) for a,b in zip(w,returns))
        g=(1-cost*turn)*gross
        if gross<=0 or g<=0:raise ValueError("nonpositive wealth")
        w=[a*(1+b)/gross for a,b in zip(w,returns)]
        if i==len(data)-1:
            liquidate=sum(w[:-1]);g*=1-cost*liquidate;turn+=liquidate
        out.append((d,g,turn))
    return out
def stats(z):
    log=peak=0.;dd=0.
    for _,g,_ in z:log+=math.log(g);peak=max(peak,log);dd=min(dd,math.exp(log-peak)-1)
    years=len(z)/12
    wealth=math.exp(log)
    return dict(n=len(z),wealth=wealth,cagr=math.expm1(log/years),vol=st.stdev(x[1]-1 for x in z)*math.sqrt(12),dd=dd,turnover_annual=sum(x[2] for x in z)/years,terminal_tax_scenario=wealth-.186*max(0,wealth-1))
def paired(a,b):
    assert [x[0] for x in a]==[x[0] for x in b]
    return [math.log(x[1]/y[1]) for x,y in zip(a,b)]
def boot(v):
    rng=random.Random(20261126);n=len(v);out=[]
    for _ in range(20000):
        s=0.
        for k in range(0,n,12):
            j=rng.randrange(n)
            s+=sum(v[(j+h)%n] for h in range(min(12,n-k)))
        out.append(12*s/n)
    out.sort()
    return {"lower_bonferroni":out[124],"median":out[10000],"upper_descriptive":out[19874]}
def ols(z,data):
    # Gaussian elimination on the normal equations, descriptive only.
    x=[[1.,f[0],f[1],f[2]] for _,_,f in data]
    y=[r[1]-1-f[3] for r,(_,_,f) in zip(z,data)]
    a=[[sum(t[i]*t[j] for t in x) for j in range(4)]+[sum(t[i]*v for t,v in zip(x,y))] for i in range(4)]
    for i in range(4):
        k=max(range(i,4),key=lambda j:abs(a[j][i]));a[i],a[k]=a[k],a[i]
        if abs(a[i][i])<1e-12:return {"status":"singular"}
        z0=a[i][i];a[i]=[t/z0 for t in a[i]]
        for j in range(4):
            if j!=i:
                z1=a[j][i];a[j]=[v-z1*w for v,w in zip(a[j],a[i])]
    beta=[r[-1] for r in a]
    return dict(alpha_annual_linear=12*beta[0],beta_market=beta[1],beta_size=beta[2],beta_value=beta[3])
def evaluate(data):
    train=[r for r in data if r[0]<"199001"];test=[r for r in data if r[0]>="199001"]
    assert len(train)==240 and len(test)==432
    vb=stats(simulate(train,"B",10,0))["vol"]
    out={}
    for kind in ("M","A"):
        vr=stats(simulate(train,kind,10,.0025))["vol"]
        risk=min(1.,vr/vb);modes={}
        for fee,drag in [(10,.0025),(30,.0075)]:
            z={k:simulate(test,k,fee,drag,risk if k=="R" else 1.) for k in (kind,"B","R","D")}
            s={k:stats(v) for k,v in z.items()}
            a=s[kind];b=s["B"];r=s["R"];d=s["D"]
            dr=paired(z[kind],z["R"]);dd=paired(z[kind],z["D"]);db=paired(z[kind],z["B"])
            phases={str(lo):12*st.mean(v for v,t in zip(dr,test) if lo<=int(t[0][:4])<=hi) for lo,hi in [(1990,2001),(2002,2013),(2014,2025)]}
            m=dict(stats=s,annual_log_diff_R=12*st.mean(dr),annual_log_diff_D=12*st.mean(dd),annual_log_diff_B=12*st.mean(db),phases_R=phases,wealth_advantage_B_10k=10000*(a["wealth"]-b["wealth"]),wealth_advantage_R_10k=10000*(a["wealth"]-r["wealth"]),tax_scenario_advantage_B_10k=10000*(a["terminal_tax_scenario"]-b["terminal_tax_scenario"]),factor_diagnostic=ols(z[kind],test))
            if fee==10:m["bootstrap_R"]=boot(dr);m["bootstrap_D"]=boot(dd)
            checks={"cagr_R":a["cagr"]-r["cagr"]>=.005,"cagr_B":a["cagr"]>b["cagr"],"vol_B":a["vol"]<=b["vol"],"drawdown_B":a["dd"]>=b["dd"]-.02,"all_periods_R":all(v>0 for v in phases.values()),"cagr_D":a["cagr"]>d["cagr"]}
            if fee==10:checks.update(stat_R=m["bootstrap_R"]["lower_bonferroni"]>.005,stat_D=m["bootstrap_D"]["lower_bonferroni"]>0)
            m["checks"]=checks;m["screen"]=all(checks.values());modes[str(fee)]=m
        out[kind]={"train_risk_weight":risk,"modes":modes,"screen":all(m["screen"] for m in modes.values())}
    return out
def self_test():
    t="Average Value Weighted Returns -- Monthly\n,A,B\n"+"\n".join(d+",1,2" for d in MONTHS)+"\n\nAverage Equal Weighted Returns -- Monthly\n"
    assert parse(t,2)["197001"]==[.01,.02]
    bad=t.replace("197002,1,2","197002,-99.99,2")
    try:parse(bad,2);raise AssertionError("missing sentinel accepted")
    except ValueError:pass
    a=[("200001",[.1,0.],[0.,0.,0.,0.]),("200002",[-.1,0.],[0.,0.,0.,0.])]
    d=simulate(a,"D",0,0);m=simulate(a,"M",0,0)
    assert abs(math.prod(x[1] for x in d)-.995)<1e-12
    assert abs(math.prod(x[1] for x in m)-.9975)<1e-12
    assert simulate(a,"A",0,0)==d
    assert abs(simulate(a[:1],"M",10,0)[0][1]-1.05*.999**2)<1e-12
    assert abs(m[1][2]-(2*.55/1.05-1+1))<1e-12
    assert abs(boot([.001]*432)["lower_bonferroni"]-.012)<1e-10
    print("SELF_TEST_PASS parser, missingness, drift, rebalance, entry/exit fees, block bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    market=parse(acquire("F-F_Research_Data_Factors_CSV.zip"),0)
    out={}
    for n in (12,49):
        try:
            ind=parse(acquire(f"{n}_Industry_Portfolios_CSV.zip"),n)
            data=[(d,ind[d],market[d]) for d in MONTHS]
            out[str(n)]=evaluate(data)
            print("UNIVERSE_DONE "+str(n),flush=True)
        except Exception as e:
            out[str(n)]={"BLOCK_DATA":str(e)}
            print("BLOCK_DATA "+str(n)+" "+str(e),flush=True)
    print("INDUSTRY_RESULT "+json.dumps(out,sort_keys=True,allow_nan=False),flush=True)
