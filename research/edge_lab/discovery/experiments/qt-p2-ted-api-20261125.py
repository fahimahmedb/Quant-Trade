"""Frozen TED source qualification, issue #60 comment 7148586004.
No prices, returns, financial forecasts or non-public data.
"""
import argparse, collections, datetime, hashlib, json, re, urllib.request, urllib.error
URL="https://api.ted.europa.eu/v3/notices/search"
FIELDS=["publication-number","publication-date","notice-type","classification-cpv","buyer-name","procedure-identifier"]
QUERIES={"A":"publication-number=59616-2026","B":"classification-cpv=31321220 AND publication-date>=20260101 AND publication-date<20260401"}
def flat(x):
    if isinstance(x,list): return [v for z in x for v in flat(z)]
    if isinstance(x,dict): return [v for z in x.values() for v in flat(z)]
    if isinstance(x,(str,int)) and not isinstance(x,bool): return [str(x)]
    return []
def one(x):
    vals=set(flat(x))
    return next(iter(vals)) if len(vals)==1 else None
def date(x):
    d=one(x)
    if not d:return None
    try:
        if re.fullmatch(r"\d{8}",d):return datetime.datetime.strptime(d,"%Y%m%d").date().isoformat()
        return datetime.date.fromisoformat(d[:10]).isoformat()
    except ValueError:return None
def inspect(key,j):
    rows=j.get("notices")
    total=j.get("totalNoticeCount")
    if not isinstance(rows,list) or type(total) is not int or total<0 or len(rows)>100:
        raise ValueError("unexpected response shape "+str(sorted(j.keys())))
    if not all(isinstance(x,dict) for x in rows):raise ValueError("invalid notice")
    cleaned=[{"number":one(r.get("publication-number")),"date":date(r.get("publication-date")),"types":sorted(set(flat(r.get("notice-type")))),"cpv":sorted(set(flat(r.get("classification-cpv")))),"procedure":sorted(set(flat(r.get("procedure-identifier")))),"buyer_present":bool(flat(r.get("buyer-name")))} for r in rows]
    ids=[r["number"] for r in cleaned]
    unique=len(set(ids))
    known=[r for r in cleaned if r["number"]=="59616-2026"]
    core=all(ids) and unique==len(rows) and total==len(rows) and j.get("timedOut") is False
    known_ok=len(known)==1 and known[0]["date"]=="2026-01-27" and "31321220" in known[0]["cpv"]
    in_window=all(r["date"] and "2026-01-01"<=r["date"]<"2026-04-01" for r in cleaned)
    cpv_match=all("31321220" in r["cpv"] for r in cleaned)
    passed=bool(core and known_ok and (total==1 if key=="A" else in_window and cpv_match))
    counts=collections.Counter(t for r in cleaned for t in r["types"])
    missing={k:sum(not r[k] for r in cleaned) for k in ("number","date","types","cpv","procedure","buyer_present")}
    return {"query":key,"total":total,"returned":len(rows),"unique":unique,"timedOut":j.get("timedOut"),"known":known,"in_window":in_window,"all_cpv_match":cpv_match,"type_counts":dict(counts),"missing":missing,"unique_procedure_ids":len({x for r in cleaned for x in r["procedure"]}),"verdict":("PASS_ACCESS" if key=="A" else "PASS_COHORT_METADATA") if passed else "BLOCK_OR_INCOMPLETE","records":cleaned}
def run(k):
    data=json.dumps({"query":QUERIES[k],"fields":FIELDS,"page":1,"limit":100,"scope":"ALL","paginationMode":"PAGE_NUMBER"}).encode()
    req=urllib.request.Request(URL,data=data,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"QuantTrade public historical data qualification"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            if r.url!=URL:raise ValueError("unexpected redirect")
            raw=r.read(4_000_001)
            if len(raw)>4_000_000:raise ValueError("response exceeds bound")
            status=r.status
        j=json.loads(raw)
        report=inspect(k,j)
        report.update(http=status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),request_sha256=hashlib.sha256(data).hexdigest())
    except urllib.error.HTTPError as e:
        # Do not print arbitrary server-returned content or contact data.
        report={"query":k,"http":e.code,"verdict":"BLOCK_HTTP","error":str(e.reason)[:160]}
    except Exception as e:
        report={"query":k,"verdict":"BLOCK_SCHEMA_OR_ACCESS","error":type(e).__name__+": "+str(e)[:220]}
    print("TED_RESULT "+json.dumps(report,sort_keys=True,ensure_ascii=True),flush=True)
    return report
def test():
    r={"publication-number":"59616-2026","publication-date":"2026-01-27","notice-type":"can-standard","classification-cpv":["31321220"],"buyer-name":{"fra":"Enedis"},"procedure-identifier":"p1"}
    j={"notices":[r],"totalNoticeCount":1,"timedOut":False}
    assert inspect("A",j)["verdict"]=="PASS_ACCESS"
    assert inspect("B",j)["verdict"]=="PASS_COHORT_METADATA"
    assert inspect("B",dict(j,totalNoticeCount=101))["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect("A",dict(j,timedOut=True))["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect("B",dict(j,notices=[r,r],totalNoticeCount=2))["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect("B",dict(j,notices=[dict(r,**{"publication-date":"2026-04-01"})]))["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect("B",dict(j,notices=[dict(r,**{"classification-cpv":["123"]})]))["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert date(["20260127"])=="2026-01-27"
    print("TED_SELF_TEST_PASS 8 assertions")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args()
    if a.self_test:test()
    else:
        a=run("A")
        # A and B are separately frozen requests; a denial/rate limit ends route.
        if a.get("http") not in (401,403,429):run("B")
