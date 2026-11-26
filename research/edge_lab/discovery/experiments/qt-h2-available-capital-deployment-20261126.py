#!/usr/bin/env python3
"""Predeclared cash deployment comparison, protocol #7180005005."""
import csv,hashlib,io,json,math,random,re,statistics as st,sys,urllib.request,zipfile
BASE="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES={"US":"F-F_Research_Data_Factors_CSV.zip","Europe":"Europe_3_Factors_CSV.zip","Japan":"Japan_3_Factors_CSV.zip"}
MONTHS=[f"{y}{m:02d}" for y in range(1991,2026) for m in range(1,13)]
DRAG=(1-.002)**(1/12)
def parse(text):
    rows=list(csv.reader(io.StringIO(text)))
    h=next(i for i,r in enumerate(rows) if all(k in [s.strip() for s in r] for k in ("Mkt-RF","RF")))
    header=[s.strip() for s in rows[h]]
    ix=[header.index(k) for k in ("Mkt-RF","RF")]
    out={}
    begun=False
    for row in rows[h+1:]:
        if not row or not re.fullmatch(r"\d{6}",row[0].strip()):
            if begun:break
            continue
        begun=True;d=row[0].strip()
        if d not in MONTHS:continue
        if d in out:raise ValueError("duplicate "+d)
        raw=[float(row[j]) for j in ix]
        if any(x in (-99.99,-999.) or not math.isfinite(x) for x in raw):raise ValueError("invalid or missing "+d)
        x,f=[x/100 for x in raw];r=x+f
        if r<=-1 or r>2 or f<=-1 or abs(f)>.1:raise ValueError("invalid total/RF return")
        out[d]=(r,f)
    if list(out)!=MONTHS:raise ValueError("coverage/order: "+str(len(out)))
    return out
def acquire(file):
    url=BASE+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade public academic research"}),timeout=25) as r:
        if not r.url.startswith(BASE):raise ValueError("redirect")
        b=r.read(4000001)
    if len(b)>4000000:raise ValueError("archive size")
    print("SOURCE "+json.dumps(dict(url=url,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(names)!=1 or z.getinfo(names[0]).file_size>8000000:raise ValueError("archive schema")
        data=parse(z.read(names[0]).decode("utf-8-sig"))
    print("QA "+json.dumps(dict(months=len(data),first=next(iter(data)),last=list(data)[-1])),flush=True)
    return data
def path(rows,n,fee):
    cash=[1/n]*n;equity=0.;wealth=[];c=fee/10000
    for i,(r,f) in enumerate(rows):
        if i<n:
            equity+=cash[i]*(1-c);cash[i]=0.
        equity*=((1+r)*DRAG)
        cash=[v*(1+f) for v in cash]
        wealth.append(equity+sum(cash))
    # Endpoint liquidation applied only at 60 months; primary relative wealth
    # at 24 months unaffected by common liquidation once fully deployed.
    wealth[-1]=equity*(1-c)+sum(cash)
    return wealth
def dd(v):
    peak=1.;worst=0.
    for x in v:peak=max(peak,x);worst=min(worst,x/peak-1)
    return worst
def tax(w):return w-.186*max(0,w-1)
def ce(w,g):return st.mean(x**(1-g) for x in w)**(1/(1-g))
def quant(v,p):return sorted(v)[min(len(v)-1,max(0,math.floor(p*len(v))))]
def boot(v):
    rng=random.Random(20261126);n=len(v);z=[]
    for _ in range(20000):
        s=0.
        for k in range(0,n,24):
            j=rng.randrange(n)
            s+=sum(v[(j+h)%n] for h in range(min(24,n-k)))
        z.append(s/n)
    return quant(z,.05/12)
def metrics(a,b,starts,do_boot):
    logs=[math.log(x[23]/y[23]) for x,y in zip(a,b)]
    ratios=[x[23]/y[23]-1 for x,y in zip(a,b)]
    final=[tax(x[-1])-tax(y[-1]) for x,y in zip(a,b)]
    wa=[x[-1] for x in a];wb=[x[-1] for x in b]
    k=max(1,math.ceil(.05*len(ratios)))
    phases={str(lo):st.mean(v for v,d in zip(logs,starts) if lo<=int(d[:4])<=hi) for lo,hi in [(1991,2000),(2001,2010),(2011,2021)]}
    result=dict(n=len(logs),mean_log=st.mean(logs),median_log=st.median(logs),win=st.mean(v>0 for v in logs),q05_ratio=quant(ratios,.05),es05_ratio=st.mean(sorted(ratios)[:k]),mean_net_dollar_delta_10k=10000*st.mean(final),mean_terminal_L=st.mean(wa),mean_terminal_D=st.mean(wb),mean_after_tax_L=st.mean(map(tax,wa)),mean_after_tax_D=st.mean(map(tax,wb)),mean_first_year_dd_L=st.mean(dd(x[:12]) for x in a),mean_first_year_dd_D=st.mean(dd(x[:12]) for x in b),worst_first_year_dd_L=min(dd(x[:12]) for x in a),worst_first_year_dd_D=min(dd(x[:12]) for x in b),loss_1y_L=st.mean(x[11]<1 for x in a),loss_1y_D=st.mean(x[11]<1 for x in b),ce3_L=ce(wa,3),ce3_D=ce(wb,3),ce6_L=ce(wa,6),ce6_D=ce(wb,6),phases=phases,nonoverlap=[dict(start=d,log_delta=logs[i],net_delta_10k=10000*final[i]) for i,d in enumerate(starts) if d in [f"{y}01" for y in range(1991,2022,5)]])
    if do_boot:result["lower_bonferroni"]=boot(logs)
    return result
def evaluate(data):
    values=list(data.values());starts=MONTHS[:361];assert len(values)==420 and starts[-1]=="202101"
    windows=[values[i:i+60] for i in range(len(starts))]
    out={}
    for fee in (10,30):
        l=[path(w,1,fee) for w in windows];m={}
        for n in (3,6,12,24):
            d=[path(w,n,fee) for w in windows]
            assert all(abs(math.log(x[23]/y[23])-math.log(x[-1]/y[-1]))<1e-10 for x,y in zip(l,d))
            v=metrics(l,d,starts,fee==10)
            v["screen"]=v["mean_log"]>.005 and all(x>0 for x in v["phases"].values()) and (fee!=10 or v["lower_bonferroni"]>.005)
            m[str(n)]=v
        out[str(fee)]=m
    return out
def selftest():
    w=[(0.,0.)]*60
    a=path(w,1,10);b=path(w,3,10)
    assert abs(a[0]-.999*DRAG)<1e-12
    assert abs(a[-1]-.999**2*DRAG**60)<1e-12
    assert abs(b[0]-(2/3+.999*DRAG/3))<1e-12
    assert abs(math.log(a[23]/b[23])-math.log(a[-1]/b[-1]))<1e-12
    w=[(.1,.02)]*60
    x=path(w,2,0)
    assert abs(x[0]-(.5*1.1*DRAG+.5*1.02))<1e-12
    assert abs(x[1]-(.5*(1.1*DRAG)**2+.5*1.02*1.1*DRAG))<1e-12
    t=",Mkt-RF,SMB,HML,RF\n"+"\n".join(d+",1,0,0,2" for d in MONTHS)
    assert abs(parse(t)["199101"][0]-.03)<1e-12
    try:parse(t.replace("199101,1,","199101,-99.99,"));raise AssertionError("sentinel accepted")
    except ValueError:pass
    assert abs(boot([.01]*361)-.01)<1e-12
    print("SELF_TEST_PASS cash conservation, timing, cost, common relative wealth, parser and bootstrap",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    out={}
    for region,file in FILES.items():
        try:out[region]=evaluate(acquire(file));print("REGION_DONE "+region,flush=True)
        except Exception as e:out[region]={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+region+" "+str(e),flush=True)
    screens={str(n):all("10" in v and all(v[f][str(n)]["screen"] for f in ("10","30")) for v in out.values()) for n in (3,6,12,24)}
    print("DEPLOYMENT_RESULT "+json.dumps(dict(regions=out,screen=screens),sort_keys=True,allow_nan=False),flush=True)
