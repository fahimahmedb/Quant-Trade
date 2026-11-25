#!/usr/bin/env python3
"""Frozen five-hypothesis long-only research batch. Protocol #7149233676."""
import csv,io,json,hashlib,math,statistics as st,random,re,sys,urllib.request,zipfile
BASE="https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES={"US":["F-F_Research_Data_Factors_CSV.zip","6_Portfolios_2x3_CSV.zip","6_Portfolios_ME_OP_2x3_CSV.zip","6_Portfolios_ME_Prior_12_2_CSV.zip"],"EU":["Europe_3_Factors_CSV.zip","Europe_6_Portfolios_ME_BE-ME_CSV.zip","Europe_6_Portfolios_ME_OP_CSV.zip","Europe_6_Portfolios_ME_Prior_12_2_CSV.zip"]}
MONTHS=[f"{y}{m:02d}" for y in range(1991,2026) for m in range(1,13)]
COLS={"US":[[("mktrf",),("rf",)],[("bighibm",),("smallhibm",)],[("bighiop",)],[("bighiprior",)]],"EU":[[("mktrf",),("rf",)],[("bv","bh"),("sv","sh")],[("br",)],[("bw",)]]}
POL={"B":[1,0,0,0,0],"V":[.5,.5,0,0,0],"Q":[.5,0,0,.5,0],"M":[.5,0,0,0,.5],"S":[.5,0,.5,0,0],"X":[.5,1/6,0,1/6,1/6]}
def norm(s):return re.sub(r"[^a-z0-9]","",s.lower())
def parse(s,cols,market=False):
    rows=list(csv.reader(io.StringIO(s)))
    if market:start=0
    else:
        markers=[i for i,r in enumerate(rows) if norm(" ".join(r)) in ("averagevalueweightedreturnsmonthly","valueweightedreturnsmonthly")]
        if len(markers)!=1:raise ValueError("ambiguous monthly value-weighted section "+str(markers))
        start=markers[0]+1
    header=None
    for i in range(start,min(start+15,len(rows))):
        h=[norm(x) for x in rows[i]]
        if all(sum(x in names for x in h)==1 for names in cols):
            header=i;ix=[next(j for j,x in enumerate(h) if x in names) for names in cols];break
    if header is None:raise ValueError("header mismatch "+str(rows[start:start+5]))
    result={};begun=False
    for row in rows[header+1:]:
        if not row or not re.fullmatch(r"\d{6}",row[0].strip()):
            if begun:break
            continue
        begun=True;d=row[0].strip()
        if d not in MONTHS:continue
        if d in result:raise ValueError("duplicate month")
        vals=[float(row[j])/100 for j in ix]
        if not all(math.isfinite(x) and -1<x<2 and x not in (-.9999,-.99,-.999) for x in vals):raise ValueError("invalid return")
        result[d]=[sum(vals)] if market else vals
    if sorted(result)!=MONTHS:raise ValueError("coverage missing "+str(sorted(set(MONTHS)-set(result))))
    print("SCHEMA "+json.dumps(dict(header=rows[header],selected=[rows[header][i] for i in ix],months=len(result))),flush=True)
    return result
def acquire(file):
    url=BASE+file
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QuantTrade public academic research"}),timeout=25) as r:
        if not r.url.startswith(BASE):raise ValueError("unexpected redirect")
        b=r.read(4_000_001)
    if len(b)>4_000_000:raise ValueError("oversize")
    print("SOURCE "+json.dumps(dict(url=url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())),flush=True)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        f=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(f)!=1 or z.getinfo(f[0]).file_size>8_000_000:raise ValueError("zip schema")
        return z.read(f[0]).decode("utf-8-sig")
def path(data,w,bp,drag):
    factor=(1-drag)**(1/12);cost=bp/10000;out=[]
    for i,(d,returns) in enumerate(data):
        r=[returns[0]]+[(1+x)*factor-1 for x in returns[1:]]
        gross=sum(a*(1+b) for a,b in zip(w,r))
        if gross<=0:raise ValueError("nonpositive wealth")
        drift=[a*(1+b)/gross for a,b in zip(w,r)]
        turn=.5*sum(abs(a-b) for a,b in zip(drift,w)) if i+1<len(data) else 0
        fee=cost*turn
        out.append((d,gross*(1-fee)*(1-cost if i==0 else 1),turn+(1 if i==0 else 0),fee+(cost if i==0 else 0)))
    return out
def stats(rows):
    l=0;peak=0;dd=0
    for _,g,_,_ in rows:
        l+=math.log(g);peak=max(peak,l);dd=min(dd,math.exp(l-peak)-1)
    return dict(n=len(rows),wealth=math.exp(l),cagr=math.expm1(12*l/len(rows)),vol=st.stdev(x[1]-1 for x in rows)*math.sqrt(12),dd=dd,turnover_annual=12*sum(x[2] for x in rows)/len(rows),fees_annual_approx=12*sum(x[3] for x in rows)/len(rows))
def boot(diff):
    n=len(diff);rng=random.Random(20261125);v=[]
    for _ in range(10000):
        s=0
        for k in range(0,n,12):
            j=rng.randrange(n)
            s+=sum(diff[(j+h)%n] for h in range(min(12,n-k)))
        v.append(s*12/n)
    v.sort();return [v[24],v[9974]]
def evaluate(data):
    result={}
    for name,bp,drag in [("base",10,.005),("stress",25,.01)]:
        r={k:path(data,w,bp,drag) for k,w in POL.items()};b=r["B"];br=stats(b)
        out={"benchmark":br,"candidates":{}}
        for k in ("V","Q","M","S","X"):
            v=r[k];a=stats(v);diff=[math.log(x[1]/y[1]) for x,y in zip(v,b)]
            periods={str(lo):12*st.mean(d for d,t in zip(diff,MONTHS) if lo<=int(t[:4])<=hi) for lo,hi in [(1991,2005),(2006,2015),(2016,2025)]}
            a.update(cagr_advantage=a["cagr"]-br["cagr"],wealth_delta_per_10000=10000*(a["wealth"]-br["wealth"]),relative_terminal_wealth=a["wealth"]/br["wealth"],annual_log_diff_by_period=periods)
            if name=="base":a["ci_99_5"]=boot(diff)
            a["screen"]=a["cagr_advantage"]>=.005 and a["vol"]<=br["vol"] and a["dd"]>=br["dd"]-.05 and periods["2006"]>0 and periods["2016"]>0 and (name!="base" or a["ci_99_5"][0]>0)
            out["candidates"][k]=a
        result[name]=out
    return result
def self_test():
    fake="Average Value Weighted Returns -- Monthly\n,SMALL LoBM,SMALL HiBM,BIG HiBM\n"+"".join(f"{m},1,2,3\n" for m in MONTHS)+"\nAverage Equal Weighted Returns -- Monthly\n"
    a=parse(fake,[("bighibm",),("smallhibm",)])
    assert a[MONTHS[0]]==[.03,.02] and len(a)==420
    x=path([("199101",[.1,0,0,0,0])],[.5,.5,0,0,0],10,0)
    assert abs(x[0][1]-1.05*.999)<1e-12
    b=path([("199101",[.1,0,0,0,0]),("199102",[-.1,0,0,0,0])],POL["B"],0,0)
    assert abs(stats(b)["wealth"]-.99)<1e-12 and abs(stats(b)["dd"]+.1)<1e-12
    assert all(abs(sum(w)-1)<1e-12 for w in POL.values())
    assert boot([.001]*420)[0]>.01199
    print("SELF_TEST_PASS schema, allocation, costs, compounding, drawdown, bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    result={}
    for region,files in FILES.items():
        try:
            parts=[parse(acquire(f),COLS[region][i],i==0) for i,f in enumerate(files)]
            data=[(m,sum([x[m] for x in parts],[])) for m in MONTHS]
            assert all(len(r)==5 for _,r in data)
            result[region]=evaluate(data);print("REGION_DONE "+region,flush=True)
        except Exception as e:
            result[region]={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+region+" "+str(e),flush=True)
    passes={k:all("base" in result[r] and all(result[r][mode]["candidates"][k]["screen"] for mode in ("base","stress")) for r in FILES) for k in ("V","Q","M","S","X")}
    print("BATCH_RESULT "+json.dumps(dict(regions=result,screen_pass=passes),sort_keys=True,allow_nan=False),flush=True)
