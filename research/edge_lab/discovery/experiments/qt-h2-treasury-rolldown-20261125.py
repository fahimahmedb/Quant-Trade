#!/usr/bin/env python3
"""Frozen Treasury curve carry/slope historical proxy, #7149399213."""
import csv,io,math,statistics as st,datetime as dt,json,hashlib,random,sys,urllib.request
URL="https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"
N=(2,5,10); COLS=(1,2,4,5,9,10); YEARS=list(range(1990,2026))
def load():
    req=urllib.request.Request(URL,headers={"User-Agent":"QuantTrade public historical research"})
    with urllib.request.urlopen(req,timeout=30) as f:
        if f.url!=URL:raise ValueError("unexpected source redirect")
        b=f.read(20_000_001)
    if len(b)>20_000_000:raise ValueError("source exceeds cap")
    print("SOURCE "+json.dumps(dict(url=URL,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())),flush=True)
    return parse(b.decode("utf-8-sig"))
def parse(s,years=YEARS):
    rows=list(csv.reader(io.StringIO(s,newline="")))
    required=["Date"]+[f"SVENY{n:02d}" for n in COLS]
    hits=[i for i,r in enumerate(rows[:30]) if all(r.count(x)==1 for x in required)]
    if len(hits)!=1:raise ValueError("required unique header missing")
    i=hits[0];ix=[rows[i].index(x) for x in required];out={};prev=None;seen=0
    for row in rows[i+1:]:
        if not row or not row[0].strip():continue
        day=dt.date.fromisoformat(row[ix[0]].strip())
        if prev is not None and day<=prev:raise ValueError("duplicate/unordered date")
        prev=day
        if not years[0]-1<=day.year<=years[-1] or day.month not in (11,12):continue
        try: vals=[float(row[j])/100 for j in ix[1:]]
        except (ValueError,IndexError):continue
        if not all(math.isfinite(v) and -.1<v<.5 for v in vals):continue
        out[day.year,day.month]=(day,dict(zip(COLS,vals)));seen+=1
    need={(y,12) for y in range(years[0]-1,years[-1]+1)}|{(y,11) for y in range(years[0]-1,years[-1])}
    if not need<=out.keys() or any(out[k][0].day<20 for k in need):raise ValueError("missing complete late-month observation")
    print("QA "+json.dumps(dict(header=required,complete_months=len(need),candidate_rows=seen,first=str(out[min(need)][0]),last=str(out[max(need)][0]))),flush=True)
    return out
def choose(y):
    return {"S":10 if y[10]>y[2] else 2,"C":max(N,key=lambda n:n*y[n]-(n-1)*y[n-1])}
def gross(n,entry,exit):return math.exp(n*entry[n]-(n-1)*exit[n-1])
def simulate(data,bp):
    f=(1-bp/10000)**2;out={k:[] for k in ("S","C","B2","B5","B10","Bmix")};picks=[]
    for t in YEARS:
        signal=data[t-1,11];entry=data[t-1,12];exit=data[t,12]
        assert signal[0]<entry[0]<exit[0]
        selected=choose(signal[1]);r={n:gross(n,entry[1],exit[1])*f for n in N}
        picks.append(dict(year=t,signal=str(signal[0]),entry=str(entry[0]),exit=str(exit[0]),**selected))
        for k in ("S","C"):out[k].append(r[selected[k]])
        for n in N:out[f"B{n}"].append(r[n])
        out["Bmix"].append(st.mean(r.values()))
    return out,picks
def stats(g):
    l=0.;peak=0.;dd=0.
    for x in g:l+=math.log(x);peak=max(peak,l);dd=min(dd,math.exp(l-peak)-1)
    return dict(n=len(g),wealth=math.exp(l),cagr=math.expm1(l/len(g)),vol=st.stdev(x-1 for x in g),dd=dd)
def boot(diff):
    n=len(diff);rng=random.Random(20261125);out=[]
    for _ in range(10000):
        s=0.
        for k in range(0,n,3):
            j=rng.randrange(n);s+=sum(diff[(j+h)%n] for h in range(min(3,n-k)))
        out.append(s/n)
    out.sort();return [out[124],out[9874]]
def evaluate(data):
    result={}
    for bp in (10,25):
        paths,picks=simulate(data,bp);m={k:stats(v) for k,v in paths.items()};b=m["Bmix"];candidates={}
        for k in ("S","C"):
            a=m[k];diff=[math.log(x/y) for x,y in zip(paths[k],paths["Bmix"])]
            v=dict(advantage=a["cagr"]-b["cagr"],wealth_delta_per_10000=10000*(a["wealth"]-b["wealth"]),halves=[st.mean(diff[:18]),st.mean(diff[18:])],paired_log_diffs={j:st.mean(math.log(x/y) for x,y in zip(paths[k],paths[j])) for j in ("B2","B5","B10","Bmix")},maturity_counts={str(n):sum(x[k]==n for x in picks) for n in N})
            if bp==10:v["ci_97_5"]=boot(diff)
            v["screen"]=v["advantage"]>=.005 and all(a["cagr"]>m[j]["cagr"] for j in ("B2","B5","B10")) and all(x>0 for x in v["halves"]) and a["vol"]<=b["vol"] and a["dd"]>=b["dd"] and (bp!=10 or v["ci_97_5"][0]>0)
            candidates[k]=v
        result[str(bp)]=dict(metrics=m,candidates=candidates,annual_returns={k:[x-1 for x in v] for k,v in paths.items()},picks=picks)
    return dict(result=result,screen_pass={k:all(x["candidates"][k]["screen"] for x in result.values()) for k in ("S","C")})
def self_test():
    y={n:.04 for n in COLS}
    assert abs(gross(10,y,y)-math.exp(.04))<1e-12
    assert abs(gross(2,y,{n:.05 for n in COLS})-math.exp(.03))<1e-12
    assert choose({n:0. for n in COLS})=={"S":2,"C":2}
    assert choose({n:.001*n for n in COLS})=={"S":10,"C":10}
    assert abs(stats([1.1,.9])["wealth"]-.99)<1e-12
    assert abs(stats([1.1,.9])["dd"]+.1)<1e-12
    assert boot([.01]*36)[0]>.009999
    data={(y,m):(dt.date(y,m,28),{n:0. for n in COLS}) for y in range(1989,2026) for m in (11,12)}
    paths,picks=simulate(data,10)
    assert all(abs(x-.999**2)<1e-12 for v in paths.values() for x in v)
    assert all(x["signal"]<x["entry"]<x["exit"] for x in picks)
    print("SELF_TEST_PASS zero pricing, tie, chronology, annual rolls, fees, drawdown, bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    print("BOND_RESULT "+json.dumps(evaluate(load()),sort_keys=True,allow_nan=False),flush=True)
