#!/usr/bin/env python3
from __future__ import annotations
import csv, gzip, hashlib, io, json, re, urllib.request
from pathlib import Path

INDEX='https://ftp.nyse.com/Historical%20Data%20Samples/TAQ%20NYSE%20ORDER%20IMBALANCES/'
OUT=Path('research/research_os/experiments/results/CLOSE_AUCTION_SOURCE_READINESS.json')
UA='Quant-Trade research source-readiness probe/1.0'
REQ_ALIASES={
 'timestamp':('sourcetime','source_time','time'),
 'symbol':('symbol','securitysymbol'),
 'paired_qty':('pairedqty','pairedquantity'),
 'imbalance_qty':('totalimbalanceqty','totalimbalancequantity','unpairedqty'),
 'imbalance_side':('imbalanceside','unpairedside'),
 'reference_price':('referenceprice',),
 'auction_type':('auctiontype',),
}
OPTIONAL_ALIASES={
 'continuous_book_clearing_price':('continuousbookclearingprice',),
 'auction_interest_clearing_price':('auctioninterestclearingprice',),
}

def get(url:str)->bytes:
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=90) as r: return r.read()

def norm(s:str)->str: return re.sub(r'[^a-z0-9]','',s.lower())

def find_col(columns, aliases):
    m={norm(c):c for c in columns}
    for a in aliases:
        if norm(a) in m: return m[norm(a)]
    return None

def inspect_file(name:str):
    raw=get(INDEX+name)
    dec=gzip.decompress(raw)
    text=dec.decode('utf-8-sig',errors='replace')
    first=next((x for x in text.splitlines() if x.strip()),'')
    delim=max(['|','\t',','], key=lambda d:first.count(d))
    if first.count(delim)<2: raise RuntimeError(f'No delimited header detected for {name}')
    reader=csv.DictReader(io.StringIO(text),delimiter=delim)
    cols=reader.fieldnames or []
    mapping={k:find_col(cols,v) for k,v in REQ_ALIASES.items()}
    optional={k:find_col(cols,v) for k,v in OPTIONAL_ALIASES.items()}
    rows=0; closing=0; symbols=set(); timestamps=0
    atype=mapping['auction_type']; sym=mapping['symbol']; ts=mapping['timestamp']
    for row in reader:
        rows+=1
        if sym and row.get(sym): symbols.add(row[sym].strip())
        if ts and row.get(ts): timestamps+=1
        if atype and (row.get(atype) or '').strip().upper() in {'C','P'}: closing+=1
    return {
      'filename':name,'gzip_sha256':hashlib.sha256(raw).hexdigest(),'compressed_bytes':len(raw),
      'columns':cols,'required_mapping':mapping,'optional_mapping':optional,
      'row_count':rows,'closing_auction_rows':closing,'unique_symbols':len(symbols),
      'timestamped_rows':timestamps,
      'required_fields_present':all(mapping.values()),
    }

def main():
    html=get(INDEX).decode('utf-8',errors='replace')
    names=sorted(set(re.findall(r'EQY_US_NYSE_REF_IMBALANCES_\d{8}\.gz',html)))
    selected=names[-2:]
    result={'schema':1,'candidate_id':'QUANT-CLOSE-AUCTION-IMBALANCE-001','assessment_type':'PRE_OUTCOME_SOURCE_READINESS',
            'economic_outcome_accessed':False,'price_or_return_data_accessed':False,'index_url':INDEX,
            'discovered_sample_files':names,'selected_sample_files':selected,'files':[]}
    try:
        if not selected: raise RuntimeError('No official NYSE imbalance sample files discovered')
        result['files']=[inspect_file(x) for x in selected]
        ok=all(x['required_fields_present'] and x['closing_auction_rows']>0 and x['timestamped_rows']>0 for x in result['files'])
        result['status']='PASS_TO_INDEPENDENT_VALIDATION' if ok else 'PARK_DATA'
        result['reason']='Official NYSE sample files expose timestamped closing-auction imbalance fields required for a frozen PIT signal.' if ok else 'Official sample files were reachable but did not expose the full required PIT closing-auction schema.'
    except Exception as exc:
        result['status']='PARK_DATA'; result['reason']=f'Source probe failed: {type(exc).__name__}: {exc}'
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
