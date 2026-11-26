#!/usr/bin/env python3
"""Only blocked actual CPI arm, frozen source repair #7180878646."""
import json,hashlib,math,sys,runpy
from pathlib import Path
HERE=Path(__file__).parent
I=runpy.run_path(str(HERE/"qt-h2-real-liability-sequence-20261126.py"))
def cpi():
    raw=(HERE/"qt-h2-real-liability-actual-cpi-20261126.input.json").read_bytes()
    j=json.loads(raw);r=j["rows"]
    assert [x[0] for x in r]==list(range(1927,2026))
    assert all(math.isfinite(x[1]) and x[1]>0 for x in r)
    d=dict(r)
    assert d[1927]==17.3 and d[1970]==39.8 and d[1971]==41.1 and d[2024]==315.605 and d[2025]==324.054
    f={y:d[y]/d[y-1] for y in range(1928,2026)}
    assert abs(math.prod(f.values())-d[2025]/d[1927])<1e-10
    print("CPI_INPUT "+json.dumps(dict(sha256=hashlib.sha256(raw).hexdigest(),n=len(r),first=r[0],last=r[-1],source=j["sources"])),flush=True)
    return f
if __name__=="__main__":
    if "--self-test" in sys.argv:
        I["selftest"]();cpi();print("SELF_TEST_PASS actual CPI endpoints and telescoping");sys.exit(0)
    rows=I["market"]();f=cpi()
    print("ACTUAL_CPI_RESULT "+json.dumps(I["evaluate"](rows,f),allow_nan=False,separators=(",",":")),flush=True)
