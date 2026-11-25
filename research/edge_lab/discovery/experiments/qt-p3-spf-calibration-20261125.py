#!/usr/bin/env python3
"""Frozen historical SPF probability benchmark, issue #60 comment 7148473179.
Not a trading experiment. No parameter search or revised GDP labels.
"""
import argparse, hashlib, io, json, math, random, re, statistics, urllib.request, zipfile
from xml.etree import ElementTree as ET

URLS = {
    "spf": "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/data-files/files/Mean_RECESS_Level.xlsx?hash=177B473A08F05FE5EF62292B36352526&sc_lang=en",
    "gdp": "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/real-time-data/data-files/xlsx/routput_first_second_third.xlsx?hash=AB8BB59BBBF6840DE1448851E90D7A80&sc_lang=en",
}
NS={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
def acquire(key):
    req=urllib.request.Request(URLS[key],headers={"User-Agent":"QuantTrade historical public data research"})
    with urllib.request.urlopen(req,timeout=30) as r:
        if not r.url.startswith("https://www.philadelphiafed.org/"):
            raise ValueError("unexpected source redirect")
        b=r.read(8_000_001)
    if len(b)>8_000_000 or not b.startswith(b"PK"):
        raise ValueError("not a bounded XLSX payload")
    print("SOURCE "+json.dumps({"key":key,"url":URLS[key],"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}),flush=True)
    return b
def workbook(b):
    sheets=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        strings=[]
        if "xl/sharedStrings.xml" in z.namelist():
            strings=["".join(n.itertext()) for n in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("x:si",NS)]
        for name in sorted(n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml",n)):
            rows=[]
            for row in ET.fromstring(z.read(name)).findall(".//x:sheetData/x:row",NS):
                vals={}
                for cell in row.findall("x:c",NS):
                    col=re.match(r"[A-Z]+",cell.attrib["r"]).group()
                    node=cell.find("x:v",NS)
                    v=node.text if node is not None else ""
                    if cell.get("t")=="s" and v: v=strings[int(v)]
                    if cell.get("t")=="inlineStr":
                        v="".join(t.text or "" for t in cell.findall(".//x:t",NS))
                    vals[col]=v
                rows.append(vals)
            sheets.append((name,rows))
    return sheets
def norm(x): return re.sub(r"[^a-z0-9]","",str(x).lower())
def quarter(x):
    m=re.fullmatch(r"\s*(\d{4})\s*[:. -]?\s*[Qq]?\s*([1-4])\s*",str(x))
    if m: return int(m[1])*4+int(m[2])-1
    return None
def yearq(y,q):
    try:
        yy,qq=int(float(y)),int(float(q))
        if float(y)==yy and float(q)==qq and 1900<=yy<=2100 and 1<=qq<=4: return yy*4+qq-1
    except (TypeError,ValueError): pass
    return None
def qname(t): return f"{t//4}Q{t%4+1}"
def value(x):
    try:
        v=float(x)
        return v if math.isfinite(v) else None
    except (TypeError,ValueError): return None
def extract(sheets,kind):
    matches=[]
    for sheet,rows in sheets:
        for idx,row in enumerate(rows[:30]):
            heads={col:norm(v) for col,v in row.items()}
            def cols(names): return [col for col,v in heads.items() if v in names]
            target=cols({"recess2"} if kind=="spf" else {"first","firstrelease","firstreleasevalue","firstreleasevalues","firstreleasegrowth","firstreleasegrowthrate","1strelease","1streleasevalue"})
            yc,qc=cols({"year"}),cols({"quarter","qtr"})
            dc=cols({"date","quarter","period","observation","observationdate","time","yearquarter","observationquarter","quarterlydate"})
            # A first-release file can leave the date header empty; accept only
            # a uniquely identifiable column of quarter-formatted observations.
            if kind=="gdp" and not (len(yc)==len(qc)==1) and len(dc)!=1:
                dc=[col for col in rows[idx+1] if sum(quarter(r.get(col)) is not None for r in rows[idx+1:idx+21])>=5] if idx+1<len(rows) else []
            if len(target)==1 and ((len(yc)==len(qc)==1) or (kind=="gdp" and len(dc)==1)):
                matches.append((sheet,rows,idx,target[0],yc,qc,dc,row))
    if len(matches)!=1:
        print("SCHEMA_HEADERS "+json.dumps({"kind":kind,"matches":len(matches),"headers":[[name,[r for r in rows[:5]]] for name,rows in sheets]},ensure_ascii=True)[:6000],flush=True)
        raise ValueError("unambiguous frozen source header not found")
    sheet,rows,idx,col,yc,qc,dc,header=matches[0]
    out={}; missing=[]
    for row in rows[idx+1:]:
        t=yearq(row.get(yc[0]),row.get(qc[0])) if len(yc)==len(qc)==1 else quarter(row.get(dc[0]))
        if t is None: continue
        if kind=="spf": t+=1
        if t in out or t in missing: raise ValueError("duplicate quarter "+qname(t))
        v=value(row.get(col))
        if v is None: missing.append(t); continue
        if kind=="spf" and not 0<=v<=100: raise ValueError("probability outside 0..100")
        out[t]=v/100 if kind=="spf" else int(v<0)
    return out,{"sheet":sheet,"header":header,"numeric_rows":len(out),"missing_count":len(missing)}
def losses(p,y):
    q=max(1e-6,min(1-1e-6,p))
    return (p-y)**2, -math.log(q if y else 1-q)
def evaluate(f,g):
    tr=list(range(1992*4+1,2010*4))
    te=list(range(2011*4,2026*4))
    train=[t for t in tr if t in f and t in g]
    test=[t for t in te if t in f and t in g]
    result={"training_n":len(train),"training_expected":len(tr),"test_n":len(test),"test_expected":len(te),
            "missing_training":[qname(t) for t in tr if t not in train],"missing_test":[qname(t) for t in te if t not in test]}
    if len(train)<.9*len(tr) or len(test)<.9*len(te):
        return dict(result,verdict="PARK_DATA_COVERAGE")
    base=(sum(g[t] for t in train)+1)/(len(train)+2)
    pred={"B0":[base for t in test],"B1":[f[t] for t in test],"C1":[.5*base+.5*f[t] for t in test]}
    labels=[g[t] for t in test]
    ls={k:[losses(p,y) for p,y in zip(v,labels)] for k,v in pred.items()}
    def metric(indices):
        return {k:{name:statistics.mean(ls[k][i][j] for i in indices) for j,name in enumerate(("brier","logloss"))} for k in pred}
    overall=metric(list(range(len(test))))
    halves=[metric([i for i,t in enumerate(test) if (t//4<=2017)==early]) for early in (True,False)]
    diffs={(b,j):[ls["C1"][i][j]-ls[b][i][j] for i in range(len(test))] for b in ("B0","B1") for j in (0,1)}
    rng=random.Random(20261125); n=len(test); samples={k:[] for k in diffs}
    for _ in range(10000):
        idx=[]
        while len(idx)<n:
            a=rng.randrange(n); idx.extend((a+k)%n for k in range(4))
        idx=idx[:n]
        for k,v in diffs.items(): samples[k].append(sum(v[i] for i in idx)/n)
    ci={}
    for (b,j),v in samples.items():
        v.sort(); name=("brier","logloss")[j]
        ci[b+"_"+name]={"delta":statistics.mean(diffs[b,j]),"lo":v[249],"hi":v[9749]}
    bins={}
    for k,v in pred.items():
        bins[k]=[]
        for lo,hi in [(0,.1),(.1,.2),(.2,.4),(.4,1)]:
            ids=[i for i,x in enumerate(v) if lo<=x and (x<hi or (hi==1 and x==1))]
            bins[k].append({"lo":lo,"hi":hi,"n":len(ids),"mean_p":statistics.mean(v[i] for i in ids) if ids else None,
                            "frequency":statistics.mean(labels[i] for i in ids) if ids else None})
    passed=all(m["C1"][name]<m[b][name] for m in [overall,*halves] for b in ("B0","B1") for name in ("brier","logloss")) and all(v["hi"]<0 for v in ci.values())
    verdict="DESCRIPTIVE_ONLY_RARE_EVENTS" if sum(labels)<3 else "PASS_HISTORICAL_CANDIDATE" if passed else "FAIL_FROZEN_CANDIDATE"
    return dict(result,training_positive=sum(g[t] for t in train),test_positive=sum(labels),base=base,
                mean_probabilities={k:statistics.mean(v) for k,v in pred.items()},
                scores=overall,halves=halves,paired_block_bootstrap=ci,bins=bins,
                bootstrap_assumption="consecutive quarters" if len(test)==len(te) else "missing quarters; block adjacency approximate",
                verdict=verdict)
def self_test():
    assert quarter("1992:Q1")==1992*4
    assert quarter("1992.4")==1992*4+3
    assert yearq("1992","2")==1992*4+1
    assert losses(0,0)[0]==0 and math.isfinite(losses(0,1)[1])
    s=[("sheet", [{"A":"YEAR","B":"QUARTER","C":"RECESS2"},{"A":"1992","B":"1","C":"25"}])]
    g=[("sheet", [{"A":"DATE","B":"First","C":"Most Recent"},{"A":"1992:Q2","B":"-1","C":"2"}])]
    assert extract(s,"spf")[0]=={1992*4+1:.25}
    assert extract(g,"gdp")[0]=={1992*4+1:1}
    assert evaluate({}, {})["verdict"]=="PARK_DATA_COVERAGE"
    f={t:.15 for t in range(1992*4+1,2026*4)}
    labels={t:int(t%11==0) for t in f}
    r=evaluate(f,labels)
    assert r["test_n"]==60 and r["training_n"]==71 and r["test_positive"]>=3
    assert r["base"]==(r["training_positive"]+1)/73
    assert len(r["paired_block_bootstrap"])==4
    print("SELF_TEST_PASS: source schema, horizon, first-release label, missingness, proper scores, paired bootstrap")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
    if a.self_test: self_test()
    else:
        f,fmeta=extract(workbook(acquire("spf")),"spf")
        g,gmeta=extract(workbook(acquire("gdp")),"gdp")
        print("SCHEMA "+json.dumps({"spf":fmeta,"gdp":gmeta}),flush=True)
        print("P3_RESULT "+json.dumps(evaluate(f,g),sort_keys=True,allow_nan=False),flush=True)
