#!/usr/bin/env python3
"""Frozen information-flow and accounting economic batch, #7149506623."""
import datetime as dt,hashlib,importlib.util,io,json,math,pathlib,random,statistics as st,sys,urllib.request,urllib.parse
HERE=pathlib.Path(__file__).parent
spec=importlib.util.spec_from_file_location("premia",HERE/"qt-h2-long-only-premia-20261125.py")
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
SIGNALS=("EarningsSurprise","RevenueSurprise","AnalystRevision","Accruals","NetEquityFinance")
MONTHS=[f"{y}{m:02d}" for y in range(2007,2025) for m in range(1,13)]
REV="57a99733a1885ffcb4b5055a92729a4c3e45d1f7"
URL="https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/"+REV+"/Portfolios/Full%20Sets%20Alt/PredictorAltPorts_QuintilesVW.parquet"
FIELDS=("signalname","port","date","ret","Nlong","Nshort")
def month(value):
    if isinstance(value,(dt.date,dt.datetime)):return value.strftime("%Y%m")
    if isinstance(value,str):
        try:return dt.date.fromisoformat(value[:10]).strftime("%Y%m")
        except ValueError:
            if len(value)==6 and value.isdigit() and 1<=int(value[4:])<=12:return value
    raise ValueError("invalid date type")
def parse(rows):
    out={s:{} for s in SIGNALS};errors={s:[] for s in SIGNALS};seen=set()
    for r in rows:
        s=r["signalname"]
        if s not in out or r["port"] not in ("05",5):continue
        m=month(r["date"])
        if m not in MONTHS:continue
        if (s,m) in seen:errors[s].append("duplicate "+m);continue
        seen.add((s,m))
        try:
            x=float(r["ret"]);n=float(r["Nlong"]);short=float(r["Nshort"])
            if not all(map(math.isfinite,(x,n,short))) or x<=-100 or x>=200 or x in (-99.99,-99,-99.9) or n<20 or n!=int(n) or short!=0:raise ValueError("invalid return/holdings")
            out[s][m]=(x/100,int(n))
        except (ValueError,TypeError,OverflowError):errors[s].append("invalid "+m)
    for s in SIGNALS:
        missing=sorted(set(MONTHS)-out[s].keys())
        if missing:errors[s].append("missing "+",".join(missing))
    return out,errors
def load():
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    import pyarrow as pa
    req=urllib.request.Request(URL,headers={"User-Agent":"QuantTrade public academic research"})
    with urllib.request.urlopen(req,timeout=60) as r:
        host=urllib.parse.urlparse(r.url).hostname or ""
        if not (host=="huggingface.co" or host.endswith(".huggingface.co") or host.endswith(".hf.co") or host.endswith(".xethub.hf.co")):raise ValueError("unexpected redirect host "+host)
        b=r.read(40_000_001)
    if len(b)>40_000_000 or b[:4]!=b"PAR1" or b[-4:]!=b"PAR1":raise ValueError("not bounded parquet")
    print("SOURCE "+json.dumps(dict(url=URL,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())),flush=True)
    pf=pq.ParquetFile(io.BytesIO(b))
    if not all(k in pf.schema_arrow.names for k in FIELDS):raise ValueError("missing expected schema "+str(pf.schema_arrow.names))
    t=pf.read(columns=list(FIELDS))
    a=t.filter(pc.is_in(t["signalname"],value_set=pa.array(SIGNALS)))
    print("SCHEMA "+json.dumps(dict(columns=pf.schema_arrow.names,rows=pf.metadata.num_rows,selected_rows=a.num_rows)),flush=True)
    return parse(a.to_pylist())
def bootstrap(diff):
    n=len(diff);rng=random.Random(20261125);res=[]
    for _ in range(10000):
        z=0.
        for k in range(0,n,12):
            j=rng.randrange(n)
            z+=sum(diff[(j+h)%n] for h in range(min(12,n-k)))
        res.append(z*12/n)
    res.sort()
    return [res[41],res[9957]]
def compare(market,tilts,errors):
    names=list(SIGNALS)+["MIX"];out={};complete=[s for s in SIGNALS if not errors[s]]
    if len(complete)<5:errors["MIX"]=["one or more component series blocked"]
    for mode,bp,drag in (("base",10,.01),("stress",25,.02)):
        b=old.path([(m,[market[m][0]]) for m in MONTHS],[1.],bp,0);br=old.stats(b);res={}
        for s in names:
            if errors.get(s):
                res[s]={"BLOCK_DATA":errors[s]};continue
            ss=list(SIGNALS) if s=="MIX" else [s]
            data=[(m,[market[m][0]]+[tilts[k][m][0] for k in ss]) for m in MONTHS]
            v=old.path(data,[.5]+[.5/len(ss)]*len(ss),bp,drag)
            z=old.stats(v);diff=[math.log(x[1]/y[1]) for x,y in zip(v,b)]
            z.update(cagr_advantage=z["cagr"]-br["cagr"],wealth_delta_per_10000=10000*(z["wealth"]-br["wealth"]),
                     relative_terminal_wealth=z["wealth"]/br["wealth"],min_holdings={k:min(n for _,n in tilts[k].values()) for k in ss},
                     annual_log_diff_halves=[12*st.mean(diff[:108]),12*st.mean(diff[108:])])
            if mode=="base":z["ci_99_1667"]=bootstrap(diff)
            z["screen"]=z["cagr_advantage"]>=.005 and z["vol"]<=br["vol"] and z["dd"]>=br["dd"]-.05 and all(x>0 for x in z["annual_log_diff_halves"]) and (mode!="base" or z["ci_99_1667"][0]>0)
            res[s]=z
        out[mode]={"benchmark":br,"candidates":res}
    return dict(results=out,screen_pass={s:all(x["candidates"][s].get("screen",False) for x in out.values()) for s in names})
def self_test():
    fake=[dict(signalname=s,port="05",date=dt.date(int(m[:4]),int(m[4:]),1),ret=2.,Nlong=30,Nshort=0) for s in SIGNALS for m in MONTHS]
    a,e=parse(fake);assert not any(e.values()) and a[SIGNALS[0]][MONTHS[0]]==(.02,30)
    fake.append(dict(fake[0]));_,e=parse(fake);assert "duplicate" in e[SIGNALS[0]][0]
    fake.pop();fake[0]["Nshort"]=1;_,e=parse(fake);assert "invalid" in e[SIGNALS[0]][0];fake[0]["Nshort"]=0
    fake[0]["Nlong"]=19;_,e=parse(fake);assert "invalid" in e[SIGNALS[0]][0]
    fake[0]["Nlong"]=30;fake[0]["ret"]=-999.;_,e=parse(fake);assert "invalid" in e[SIGNALS[0]][0]
    assert bootstrap([.001]*216)[0]>.011999
    b=old.path([(MONTHS[0],[.1,0.])],[.5,.5],10,0);assert abs(b[0][1]-1.05*.999)<1e-12
    assert abs(old.stats(old.path([(MONTHS[0],[.1]),(MONTHS[1],[-.1])],[1],0,0))["wealth"]-.99)<1e-12
    print("SELF_TEST_PASS source schema, percent conversion, chronology, coverage, holdings, no short, cost, bootstrap")
if __name__=="__main__":
    if "--self-test" in sys.argv:self_test();sys.exit(0)
    market=old.parse(old.acquire(old.FILES["US"][0]),old.COLS["US"][0],True)
    tilts,errors=load()
    print("INFO_RESULT "+json.dumps(compare(market,tilts,errors),sort_keys=True,allow_nan=False),flush=True)
