#!/usr/bin/env python3
"""Frozen #7180593121, same previously exposed return paths, three fixed policies."""
import math,statistics as st,runpy,json,sys
from pathlib import Path
I=runpy.run_path(str(Path(__file__).with_name("qt-h2-integrated-wealth-20261126.py")))
def evaluate(path,E,X,fee,q):
    c=min(4710,max(0,E-29579))
    assert c in (421,2421)
    baseline=I["net"](5000*I["factor"](path),5000)
    full=I["allocation"](path,E,X,4710,fee,q)["wealth"]
    rule=I["allocation"](path,E,X,c,fee,q)["wealth"]
    return rule-baseline,rule-full,rule-max(baseline,full)
def summarize(v):
    s=I["stats"](v)
    s["nonoverlap_n"]=len(v[::120]);s["nonoverlap_positive"]=sum(x>0 for x in v[::120])
    return s
def hist(vals):
    assert len(vals)==420
    windows=[vals[i:i+120] for i in range(301)]
    out=[]
    for E in (30000,32000):
        for X in (15000,20000,28000):
            for fee in (.005,.01):
                for q in (False,True):
                    z=[evaluate(w,E,X,fee,q) for w in windows]
                    out.append(dict(E=E,X=X,fee=fee,q=q,vs_pea=summarize([r[0] for r in z]),vs_full=summarize([r[1] for r in z]),vs_best=summarize([r[2] for r in z])))
    assert len(out)==24
    return out
def selftest():
    path=[1.05**(1/12)-1]*120
    a,b,c=evaluate(path,32000,20000,.005,True)
    assert abs(a-322.13644424046)<1e-8 and abs(b-141.21518072370)<1e-8
    assert abs(c-min(a,b))<1e-8
    a,b,c=evaluate(path,32000,20000,.01,True)
    assert abs(a-198.47736916053)<1e-8 and abs(b-258.13200140026)<1e-8
    assert summarize([1.]*301)["nonoverlap_n"]==3
    print("SELF_TEST_PASS fixed contribution, prior independent deterministic examples, matched comparator",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    for reg,f in I["SRC"]["FILES"].items():
        try:
            out=hist(I["acquire"](reg,f));print("REGION_DONE "+reg,flush=True)
        except Exception as e:
            out={"BLOCK_DATA":str(e)};print("BLOCK_DATA "+reg+" "+str(e),flush=True)
        print("MARGINAL_"+reg+" "+json.dumps(out,separators=(",",":"),allow_nan=False),flush=True)
