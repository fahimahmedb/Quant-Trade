"""Frozen TED award metadata enrichment, issue #60 comment 7148854840.
One official read-only request; no prices, returns, or personal names in logs.
"""
import argparse, collections, datetime, hashlib, json, math, re, urllib.request, urllib.error
URL="https://api.ted.europa.eu/v3/notices/search"
EXPECTED=[{"number":"2412-2026","date":"2026-01-05","procedure":["bdb870a7-4b3f-4ca1-89a4-8b9b30f6028e"]},{"number":"50316-2026","date":"2026-01-23","procedure":["5921ccd3-eb70-4b36-8d54-ed7ea189eb26"]},{"number":"59616-2026","date":"2026-01-27","procedure":["3bff997e-5498-4ea8-8540-8bf63b6d74eb"]},{"number":"80440-2026","date":"2026-02-04","procedure":["79354278-9fd5-48af-aa66-4a684b4d49c0"]},{"number":"109026-2026","date":"2026-02-16","procedure":["0ecf3365-50ff-401e-a0ba-481d7875f496"]},{"number":"122637-2026","date":"2026-02-20","procedure":["09fd1870-eb9d-46aa-a5fe-02ca6c5dde2d"]},{"number":"134137-2026","date":"2026-02-25","procedure":["5be40ba0-1edd-406a-bec1-f96e22ec0f03"]},{"number":"165472-2026","date":"2026-03-10","procedure":["e95d20e9-788b-4cf0-8925-072fd8b157cd"]},{"number":"168830-2026","date":"2026-03-11","procedure":["dbfcd45f-43d8-4927-84db-a53d8886a237"]},{"number":"171246-2026","date":"2026-03-12","procedure":["21e5207d-9d1f-452c-8055-f1897f7b03fc"]},{"number":"178458-2026","date":"2026-03-16","procedure":["c209002e-a907-4a38-b2b9-411fe84639ac"]},{"number":"196297-2026","date":"2026-03-23","procedure":["e795c3fc-5695-4dc9-82be-8787dfa7b1fa"]},{"number":"204015-2026","date":"2026-03-25","procedure":["dbfcd45f-43d8-4927-84db-a53d8886a237"]},{"number":"211180-2026","date":"2026-03-27","procedure":["394c6e60-42b9-437a-abc8-ac1c65a386c4"]},{"number":"213243-2026","date":"2026-03-27","procedure":["394c6e60-42b9-437a-abc8-ac1c65a386c4"]}]
BASE_FIELDS=["publication-number","publication-date","notice-type","classification-cpv","buyer-name","procedure-identifier"]
EXTRA_FIELDS=["winner-name","winner-selection-status","contract-identifier","contract-conclusion-date","contract-framework-agreement","tender-value","tender-value-cur","result-value-notice","framework-value-notice","change-notice-version-identifier","notice-identifier","notice-version"]
FIELDS=BASE_FIELDS+EXTRA_FIELDS
VALUE_FIELDS={"tender-value","result-value-notice","framework-value-notice"}
def flat(x):
    if isinstance(x,list):return [v for a in x for v in flat(a)]
    if isinstance(x,dict):return [v for a in x.values() for v in flat(a)]
    if isinstance(x,(str,int,float)) and not isinstance(x,bool):return [str(x).strip()]
    return []
def vals(x):return sorted({a for a in flat(x) if a})
def one(x):
    v=vals(x)
    return v[0] if len(v)==1 else None
def dt(x):
    try:
        if re.fullmatch(r"\d{8}",x):return datetime.datetime.strptime(x,"%Y%m%d").date().isoformat()
        return datetime.date.fromisoformat(x[:10]).isoformat()
    except (TypeError,ValueError):return None
def numeric(x):
    try:return math.isfinite(float(x)) and float(x)>=0
    except (TypeError,ValueError):return False
def digest(x):return hashlib.sha256(x.strip().casefold().encode()).hexdigest()
def inspect(j,expected):
    rows=j.get("notices")
    if not isinstance(rows,list) or not all(isinstance(r,dict) for r in rows) or len(rows)>100:raise ValueError("invalid notices list")
    total=j.get("totalNoticeCount")
    ids=[one(r.get("publication-number")) for r in rows]
    em={r["number"]:r for r in expected}
    coverage={k:0 for k in EXTRA_FIELDS}; output=[]
    mismatches=[]; missing_dates=0; after_pub=0
    for n,r in zip(ids,rows):
        rawdate=one(r.get("publication-date"))
        date=dt(rawdate) if rawdate else None
        proc=vals(r.get("procedure-identifier"))
        match=n in em and date==em[n]["date"] and proc==sorted(em[n]["procedure"])
        if not match:mismatches.append(n)
        for k in EXTRA_FIELDS:
            v=vals(r.get(k))
            if (any(numeric(a) for a in v) if k in VALUE_FIELDS else bool(v)):coverage[k]+=1
        names=vals(r.get("winner-name"))
        dates=vals(r.get("contract-conclusion-date")); valid=[dt(d) for d in dates]
        bad=sum(x is None for x in valid); missing_dates+=bad
        after=sum(x is not None and date is not None and x>date for x in valid);after_pub+=after
        contract_ids=vals(r.get("contract-identifier"))
        o={"number":n,"date":date,"procedure":proc,"match":match,"winner_name_distinct_strings":len(names),
           "winner_status":vals(r.get("winner-selection-status")),"known_nexans":any(re.search(r"\bnexans\b",x,re.I) for x in names),
           "known_prysmian":any(re.search(r"\bprysmian\b",x,re.I) for x in names),
           "contract_count":len(contract_ids),"contract_id_hashes":sorted({digest(a) for a in contract_ids}),
           "contract_dates_valid":len(valid)-bad,"contract_date_values":sorted({x for x in valid if x}),
           "contract_dates_after_publication":after,"change_reference_present":bool(vals(r.get("change-notice-version-identifier"))),
           "framework_flag_present":bool(vals(r.get("contract-framework-agreement"))),
           "numeric_value_presence":{k:any(numeric(x) for x in vals(r.get(k))) for k in sorted(VALUE_FIELDS)}}
        output.append(o)
    pairs=[]
    for i,x in enumerate(output):
        for y in output[i+1:]:
            if set(x["procedure"])&set(y["procedure"]):
                a,b=set(x["contract_id_hashes"]),set(y["contract_id_hashes"])
                pairs.append({"a":x["number"],"b":y["number"],"shared":len(a&b),"a_only":len(a-b),"b_only":len(b-a)})
    ok=(type(total) is int and total==len(expected)==len(rows) and set(ids)==set(em) and len(set(ids))==len(ids) and not mismatches and j.get("timedOut") is False)
    return {"total":total,"returned":len(rows),"expected":len(expected),"unique":len(set(ids)),"timedOut":j.get("timedOut"),"mismatches":mismatches,"coverage":coverage,
      "invalid_contract_date_values":missing_dates,"contract_dates_after_publication":after_pub,"same_procedure_pairs":pairs,
      "records":output,"verdict":"PASS_AWARD_METADATA_COVERAGE" if ok else "BLOCK_OR_INCOMPLETE"}
def self_test():
    e=[{"number":"1-2026","date":"2026-01-27","procedure":["p"]}]
    r={"publication-number":"1-2026","publication-date":"2026-01-27","procedure-identifier":["p"],"winner-name":{"fra":["NEXANS"]},"contract-identifier":["A","a"],"tender-value":["10.5"],"contract-conclusion-date":["2026-01-01","2026-01-30"]}
    j={"notices":[r],"totalNoticeCount":1,"timedOut":False}
    v=inspect(j,e)
    assert v["verdict"]=="PASS_AWARD_METADATA_COVERAGE"
    assert v["coverage"]["tender-value"]==1
    assert v["coverage"]["framework-value-notice"]==0
    assert v["records"][0]["known_nexans"]
    assert v["contract_dates_after_publication"]==1
    assert len(v["records"][0]["contract_id_hashes"])==1
    assert inspect(dict(j,totalNoticeCount=2),e)["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect(dict(j,timedOut=True),e)["verdict"]=="BLOCK_OR_INCOMPLETE"
    assert inspect(dict(j,notices=[dict(r,**{"procedure-identifier":["q"]})]),e)["verdict"]=="BLOCK_OR_INCOMPLETE"
    print("ENRICH_SELF_TEST_PASS 9 assertions")
def run():
    query="publication-number IN ("+" ".join(x["number"] for x in EXPECTED)+")"
    data=json.dumps({"query":query,"fields":FIELDS,"page":1,"limit":100,"scope":"ALL","paginationMode":"PAGE_NUMBER"}).encode()
    req=urllib.request.Request(URL,data=data,method="POST",headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"QuantTrade public historical data qualification"})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            if r.url!=URL:raise ValueError("unexpected redirect")
            raw=r.read(4_000_001)
            if len(raw)>4_000_000:raise ValueError("response exceeds bound")
            status=r.status
        report=inspect(json.loads(raw),EXPECTED)
        report.update(http=status,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),request_sha256=hashlib.sha256(data).hexdigest())
    except urllib.error.HTTPError as e:
        report={"http":e.code,"verdict":"BLOCK_HTTP","error":str(e.reason)[:160]}
    except Exception as e:
        report={"verdict":"BLOCK_SCHEMA_OR_ACCESS","error":type(e).__name__+": "+str(e)[:220]}
    print("ENRICH_RESULT "+json.dumps(report,ensure_ascii=True,sort_keys=True),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args()
    self_test() if a.self_test else run()
