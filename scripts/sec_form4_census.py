#!/usr/bin/env python3
"""Acquire official SEC ownership bytes and build the V2-A1 deterministic census."""
from __future__ import annotations
import argparse, csv, gzip, io, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from quant.dataplane.sec_form4 import (  # noqa:E402
    DEFAULT_SEC_RATE_PER_SECOND, END_DATE, PARSER_VERSION, RateLimiter, SessionCalendar,
    SourceRecord, _http_get, _sha256_bytes, _stable_hash, acceptance_header_url,
    build_census, build_mapping_ledger, candidate_to_dict, census_summary, event_to_dict,
    jsonl_bytes, loss_to_dict, normalize_accession, normalize_cik, observation_to_dict,
    parse_edgar_header, probe_yahoo_symbols, quarter_specs, resolve_event_times,
    source_url_candidates, write_atomic,
)

Q3_MASTER_URL='https://www.sec.gov/Archives/edgar/full-index/2026/QTR3/master.idx'

def deterministic_gzip(data:bytes)->bytes:return gzip.compress(data,compresslevel=9,mtime=0)
def write_json(path:Path,payload):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def sec_fetch(url:str,limiter:RateLimiter|None=None)->bytes:
    return _http_get(url,limiter=limiter)

def preflight()->int:
    limiter=RateLimiter(DEFAULT_SEC_RATE_PER_SECOND);last=None
    for url in source_url_candidates(2020,1):
        try:data=sec_fetch(url,limiter)
        except Exception as exc:last=exc;continue
        if not data.startswith(b'PK'):raise SystemExit('official SEC preflight payload is not ZIP')
        print(f'official SEC acquisition-path preflight ok: {url} {len(data)} bytes');return 0
    raise SystemExit(f'official SEC preflight failed: {last}')

def acquire(raw_dir:Path,expected_manifest=None,limiter=None):
    raw_dir.mkdir(parents=True,exist_ok=True);payloads=[];records=[]
    for year,q in quarter_specs():
        period=f'{year}Q{q}';path=raw_dir/f'{year}q{q}_form345.zip';used=None
        if path.exists():
            data=path.read_bytes();used=((expected_manifest or {}).get(period) or {}).get('source_url') or source_url_candidates(year,q)[0]
        else:
            last=None
            for url in source_url_candidates(year,q):
                try:data=sec_fetch(url,limiter);used=url;break
                except Exception as exc:
                    import urllib.error
                    if isinstance(exc,urllib.error.HTTPError) and exc.code==404:last=exc;continue
                    raise
            else:raise RuntimeError(f'no official SEC root served {period}: {last}')
            write_atomic(path,data)
        digest=_sha256_bytes(data);expected=(expected_manifest or {}).get(period)
        if expected and digest!=expected.get('sha256'):raise SystemExit(f'source drift {period}: {digest} != {expected.get("sha256")}')
        records.append(SourceRecord(period,used,digest,len(data),datetime.now(timezone.utc).isoformat(),local_path=str(path.relative_to(ROOT))))
        payloads.append((period,data))
    return payloads,records

def generate_calendar(path:Path)->None:
    import exchange_calendars as xcals
    cal=xcals.get_calendar('XNYS',start='2019-11-25',end='2026-08-07');sessions=cal.sessions_in_range('2019-12-02','2026-07-31')
    version=getattr(xcals,'__version__','unknown');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as h:
        h.write('session,source,version\n')
        for ts in sessions:h.write(f'{ts.date().isoformat()},exchange_calendars:XNYS,{version}\n')

def _q3_master_rows(payload:bytes):
    text=payload.decode('latin-1');rows=[];started=False
    for line in text.splitlines():
        if line.startswith('-----'):started=True;continue
        if not started or '|' not in line:continue
        parts=line.split('|')
        if len(parts)!=5:continue
        cik,name,form,filed,filename=[x.strip() for x in parts]
        if form!='4':continue
        accession=normalize_accession(Path(filename).stem)
        if not accession:raise ValueError(f'invalid accession in Q3 master: {filename}')
        rows.append({'master_cik':normalize_cik(cik),'company_name':name,'form_type':form,'filed_date':filed,'filename':filename,'accession':accession})
    return sorted(rows,key=lambda r:(r['filed_date'],r['accession']))

def _period_from_header(payload:bytes):
    text=payload.decode('utf-8',errors='replace');m=re.search(r'(?im)^\s*CONFORMED PERIOD OF REPORT\s*:\s*(\d{8})',text)
    return datetime.strptime(m.group(1),'%Y%m%d').date().isoformat() if m else None

def _header_url(row):return acceptance_header_url(row['master_cik'],row['accession'])
def _full_url(row):return 'https://www.sec.gov/Archives/'+row['filename']

def _strip_ns(root):
    for elem in root.iter():elem.tag=elem.tag.rsplit('}',1)[-1]
    return root

def _txt(elem,path,default=''):
    cur=elem
    for part in path.split('/'):
        cur=cur.find(part) if cur is not None else None
    return default if cur is None or cur.text is None else cur.text.strip()
def _bool(elem,path):return _txt(elem,path).lower() in ('1','true','yes')

def _ownership_xml(payload:bytes):
    text=payload.decode('utf-8',errors='replace');matches=re.findall(r'(?is)(<ownershipDocument\b.*?</ownershipDocument>)',text)
    if not matches:raise ValueError('ownershipDocument XML not found')
    if len(matches)!=1:raise ValueError(f'expected one ownershipDocument, got {len(matches)}')
    return _strip_ns(ET.fromstring(matches[0]))

def _synthetic_tail_rows(row,header_payload,full_payload):
    meta=parse_edgar_header(header_payload);root=_ownership_xml(full_payload)
    if meta.accession!=row['accession'] or meta.submission_type!='4':raise ValueError('Q3 SGML accession/form mismatch')
    document_type=_txt(root,'documentType').upper();period=_txt(root,'periodOfReport');issuer=root.find('issuer')
    issuer_cik=normalize_cik(_txt(issuer,'issuerCik'));symbol=_txt(issuer,'issuerTradingSymbol');name=_txt(issuer,'issuerName')
    if document_type!='4' or issuer_cik!=meta.issuer_cik:raise ValueError('Q3 XML document/issuer does not match SGML')
    owners=[]
    for ro in root.findall('reportingOwner'):
        cik=normalize_cik(_txt(ro,'reportingOwnerId/rptOwnerCik'));nm=_txt(ro,'reportingOwnerId/rptOwnerName');rel=ro.find('reportingOwnerRelationship');labels=[]
        if _bool(rel,'isDirector'):labels.append('DIRECTOR')
        if _bool(rel,'isOfficer'):labels.append('OFFICER')
        if _bool(rel,'isTenPercentOwner'):labels.append('TENPERCENTOWNER')
        if _bool(rel,'isOther'):labels.append('OTHER')
        owners.append({'ACCESSION_NUMBER':row['accession'],'RPTOWNERCIK':cik or '', 'RPTOWNERNAME':nm,'RPTOWNER_RELATIONSHIP':','.join(labels)})
    xml_owners=tuple(sorted({normalize_cik(o['RPTOWNERCIK']) for o in owners if normalize_cik(o['RPTOWNERCIK'])}))
    if xml_owners!=meta.reporting_owner_ciks:raise ValueError('Q3 XML owners do not match SGML')
    sub={'ACCESSION_NUMBER':row['accession'],'FILING_DATE':row['filed_date'],'PERIOD_OF_REPORT':period,'DOCUMENT_TYPE':'4','ISSUERCIK':issuer_cik or '', 'ISSUERNAME':name,'ISSUERTRADINGSYMBOL':symbol}
    tx=[];nd=root.find('nonDerivativeTable')
    if nd is not None:
        for i,item in enumerate(nd.findall('nonDerivativeTransaction'),1):
            tx.append({'ACCESSION_NUMBER':row['accession'],'NONDERIV_TRANS_SK':str(i),'SECURITY_TITLE':_txt(item,'securityTitle/value'),
                       'TRANS_DATE':_txt(item,'transactionDate/value'),'TRANS_FORM_TYPE':_txt(item,'transactionCoding/transactionFormType'),
                       'TRANS_CODE':_txt(item,'transactionCoding/transactionCode'),'TRANS_ACQUIRED_DISP_CD':_txt(item,'transactionAmounts/transactionAcquiredDisposedCode/value'),
                       'DIRECT_INDIRECT_OWNERSHIP':_txt(item,'ownershipNature/directOrIndirectOwnership/value')})
    return sub,owners,tx

def _zip_tail(subs,owners,txs):
    def encode(rows,fields):
        out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return out.getvalue().encode()
    sb=['ACCESSION_NUMBER','FILING_DATE','PERIOD_OF_REPORT','DOCUMENT_TYPE','ISSUERCIK','ISSUERNAME','ISSUERTRADINGSYMBOL'];ob=['ACCESSION_NUMBER','RPTOWNERCIK','RPTOWNERNAME','RPTOWNER_RELATIONSHIP'];tb=['ACCESSION_NUMBER','NONDERIV_TRANS_SK','SECURITY_TITLE','TRANS_DATE','TRANS_FORM_TYPE','TRANS_CODE','TRANS_ACQUIRED_DISP_CD','DIRECT_INDIRECT_OWNERSHIP']
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('SUBMISSION.tsv',encode(subs,sb));z.writestr('REPORTINGOWNER.tsv',encode(owners,ob));z.writestr('NONDERIV_TRANS.tsv',encode(txs,tb))
    return out.getvalue()

def acquire_q3_tail(raw_dir:Path,limiter:RateLimiter,workers:int=4):
    base=raw_dir/'q3_tail';headers=raw_dir/'acceptance_headers';filings=base/'filings';base.mkdir(parents=True,exist_ok=True);headers.mkdir(parents=True,exist_ok=True);filings.mkdir(parents=True,exist_ok=True)
    index_path=base/'master.idx'
    if not index_path.exists():write_atomic(index_path,sec_fetch(Q3_MASTER_URL,limiter))
    master=index_path.read_bytes();rows=_q3_master_rows(master);lock=__import__('threading').Lock();records={}
    def one(row):
        hp=headers/f"{row['accession']}.html";payload=None
        if hp.exists():
            try:
                candidate=hp.read_bytes();meta=parse_edgar_header(candidate)
                if meta.accession==row['accession'] and meta.submission_type=='4':payload=candidate
            except Exception:payload=None
        if payload is None:
            payload=sec_fetch(_header_url(row),limiter);meta=parse_edgar_header(payload)
            if meta.accession!=row['accession'] or meta.submission_type!='4':raise ValueError('Q3 master/header identity mismatch')
            write_atomic(hp,payload)
        period=_period_from_header(payload)
        with lock:records[row['accession']]={'row':row,'header':payload,'period':period,'meta':meta}
    with ThreadPoolExecutor(max_workers=max(1,workers)) as pool:
        for future in [pool.submit(one,r) for r in rows]:future.result()
    subs=[];owners=[];txs=[];manifest=[];candidate_count=0
    for acc in sorted(records):
        rec=records[acc];period=rec['period'];full_sha=None;full_bytes=None;need_full=period is None or period<=END_DATE.isoformat()
        if need_full:
            candidate_count+=1;fp=filings/f'{acc}.txt'
            if not fp.exists():write_atomic(fp,sec_fetch(_full_url(rec['row']),limiter))
            full=fp.read_bytes();sub,oo,tt=_synthetic_tail_rows(rec['row'],rec['header'],full);subs.append(sub);owners.extend(oo);txs.extend(tt);full_sha=_sha256_bytes(full);full_bytes=len(full)
        manifest.append({'accession':acc,'filed_date':rec['row']['filed_date'],'master_cik':rec['row']['master_cik'],'filename':rec['row']['filename'],
                         'period_of_report':period,'header_url':_header_url(rec['row']),'header_sha256':_sha256_bytes(rec['header']),'header_bytes':len(rec['header']),
                         'full_submission_sha256':full_sha,'full_submission_bytes':full_bytes})
    if any(x['period_of_report'] is None for x in manifest):raise RuntimeError('Q3 tail has unresolved periodOfReport; H1 completeness not certified')
    payload=_zip_tail(subs,owners,txs)
    audit={'source_url':Q3_MASTER_URL,'master_sha256':_sha256_bytes(master),'master_bytes':len(master),'master_form4_count':len(rows),
           'max_filing_date':max((r['filed_date'] for r in rows),default=None),'h1_earliest_transaction_candidates':candidate_count,
           'tail_submission_rows':len(subs),'tail_owner_rows':len(owners),'tail_nonderivative_rows':len(txs),
           'tail_p_acquired_rows_h1':sum(t.get('TRANS_CODE')=='P' and t.get('TRANS_ACQUIRED_DISP_CD')=='A' and t.get('TRANS_DATE') and t['TRANS_DATE']<=END_DATE.isoformat() for t in txs),
           'proof_semantics':'Q3 EDGAR master is scanned exhaustively for original Form 4; periodOfReport is SEC Form-4 Date of Earliest Transaction; only filings whose earliest transaction can be H1 require full XML expansion; transaction cutoff remains 2026-06-30.'}
    return payload,audit,manifest

def run(args):
    raw_dir=ROOT/args.raw_dir;out_dir=ROOT/args.output_dir;out_dir.mkdir(parents=True,exist_ok=True);calendar_path=ROOT/args.calendar
    if args.generate_calendar or not calendar_path.exists():generate_calendar(calendar_path)
    calendar=SessionCalendar.from_csv(calendar_path);limiter=RateLimiter(args.rate_per_second);manifest_path=out_dir/'provenance_manifest.json';expected=None
    if args.verify_source_hashes and manifest_path.exists():
        old=json.loads(manifest_path.read_text());expected={x['period']:x for x in old['sources']}
    payloads,sources=acquire(raw_dir,expected,limiter);tail_payload,q3_audit,q3_manifest=acquire_q3_tail(raw_dir,limiter,args.workers);payloads.append(('2026Q3_TAIL',tail_payload))
    build=build_census(payloads,calendar)
    events,losses,acceptance=resolve_event_times(build,cache_dir=raw_dir/'acceptance_headers',checkpoint_path=raw_dir/'acceptance_checkpoint.jsonl',workers=args.workers,limiter=limiter,rate_per_second=args.rate_per_second)
    build.events=events;build.losses=losses;build.waterfall['event_time_resolved_formations']=sum(e.event_time_status=='RESOLVED' for e in events);build.waterfall['event_time_unresolved_formations']=len(events)-build.waterfall['event_time_resolved_formations']
    price_status=None;price_path=out_dir/'price_coverage_snapshot.json'
    if args.verify_source_hashes and price_path.exists():price_status=json.loads(price_path.read_text())['symbols']
    elif args.probe_price_coverage:
        provisional=build_mapping_ledger(build,events,None);symbol_events={}
        for row in provisional:
            if row['selected_symbol'] and not row['reason_codes']:symbol_events.setdefault(row['selected_symbol'],[]).append(row['formation_transaction_date'])
        price_status=probe_yahoo_symbols(symbol_events);write_json(price_path,{'purpose':'mapping coverage only; no price arrays are read or persisted','symbols':price_status})
    mapping=build_mapping_ledger(build,events,price_status);build.waterfall['mappable_events']=sum(r['mapping_status']=='MAPPABLE' for r in mapping);build.waterfall['unmappable_events']=len(mapping)-build.waterfall['mappable_events']
    from quant.dataplane.sec_form4 import LossLedgerRecord
    for row in mapping:
        codes=tuple(sorted(set(row['reason_codes'])))
        if codes:losses.append(LossLedgerRecord(_stable_hash(['mapping',row['event_id'],codes],'LOSS-'),row['event_id'],None,row['issuer_cik'],None,'UNRESOLVED',codes,'security/price-path mapping unresolved'))
        if row['diagnostic_codes']:losses.append(LossLedgerRecord(_stable_hash(['mapping-diagnostic',row['event_id'],row['diagnostic_codes']],'LOSS-'),row['event_id'],None,row['issuer_cik'],None,'DIAGNOSTIC',tuple(row['diagnostic_codes']),'temporal ticker diagnostic'))
    deterministic={'normalized_candidates.jsonl.gz':deterministic_gzip(jsonl_bytes(candidate_to_dict(x) for x in sorted(build.normalized_candidates,key=lambda x:(x.accession,x.row_id)))),
      'normalized_purchase_observations.jsonl.gz':deterministic_gzip(jsonl_bytes(observation_to_dict(x) for x in build.observations)),
      'events.jsonl':jsonl_bytes(event_to_dict(x) for x in events),'loss_ledger.jsonl.gz':deterministic_gzip(jsonl_bytes(loss_to_dict(x) for x in sorted(losses,key=lambda x:x.record_id))),
      'mapping_ledger.jsonl':jsonl_bytes(sorted(mapping,key=lambda x:x['event_id'])),'q3_tail_manifest.jsonl.gz':deterministic_gzip(jsonl_bytes(q3_manifest))}
    for name,data in deterministic.items():(out_dir/name).write_bytes(data)
    summary=census_summary(build,events,mapping);summary['q3_tail_audit']=q3_audit;write_json(out_dir/'census_summary.json',summary);write_json(out_dir/'waterfall.json',build.waterfall);write_json(out_dir/'acceptance_manifest.json',acceptance);write_json(out_dir/'q3_tail_audit.json',q3_audit)
    report=['# SEC Form-4 deterministic census (V2-A1)','', 'No market-outcome or strategy-performance analysis is present.', '',f"- economic formations: **{summary['formations']}**",f"- event-time resolved: **{summary['event_time_resolved']}**; unresolved: **{summary['event_time_unresolved']}**",f"- original Form 4 filings: **{build.waterfall.get('original_form4_filings',0)}**",f"- Q3 tail Form 4 headers scanned: **{q3_audit['master_form4_count']}** through **{q3_audit['max_filing_date']}**",f"- Q3 filings whose earliest transaction can be H1: **{q3_audit['h1_earliest_transaction_candidates']}**",f"- Q3-tail H1 P+A rows: **{q3_audit['tail_p_acquired_rows_h1']}**",'', '## Annual formations','']
    report += [f'- {y}: {n}' for y,n in summary['annual_formations'].items()];report += ['', '## Raw row reconciliation','',json.dumps(build.diagnostics['raw_row_reconciliation'],sort_keys=True)]
    (out_dir/'CENSUS_REPORT.md').write_text('\n'.join(report)+'\n')
    hashes={n:_sha256_bytes(d) for n,d in deterministic.items()}
    for n in ('census_summary.json','waterfall.json','acceptance_manifest.json','q3_tail_audit.json','CENSUS_REPORT.md'):hashes[n]=_sha256_bytes((out_dir/n).read_bytes())
    price_hash=_sha256_bytes(json.dumps(price_status or {},sort_keys=True,separators=(',',':')).encode())
    provenance={'parser_version':PARSER_VERSION,'economic_transaction_cutoff':['2020-01-01','2026-06-30'],'sources':[asdict(x) for x in sources],
      'q3_tail':{**q3_audit,'manifest_sha256':hashes['q3_tail_manifest.jsonl.gz']},'calendar':{'path':str(calendar_path.relative_to(ROOT)),'sha256':_sha256_bytes(calendar_path.read_bytes()),'source':calendar.source,'version':calendar.version},
      'mapping_input':{'price_coverage_symbols_sha256':price_hash,'population_invariant':'price coverage is downstream-only and cannot alter events.jsonl'},'deterministic_outputs':hashes}
    write_json(manifest_path,provenance);write_json(out_dir/'run_metadata.json',{'generated_at':datetime.now(timezone.utc).isoformat(),'raw_cache':str(raw_dir)})
    print(json.dumps(summary,indent=2,sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',default='var/sec_form4_raw');p.add_argument('--output-dir',default='artifacts/sec_form4_census');p.add_argument('--calendar',default='data/calendars/xnys_sessions_2019_2026.csv');p.add_argument('--generate-calendar',action='store_true');p.add_argument('--probe-price-coverage',action='store_true');p.add_argument('--verify-source-hashes',action='store_true');p.add_argument('--workers',type=int,default=6);p.add_argument('--rate-per-second',type=float,default=DEFAULT_SEC_RATE_PER_SECOND);p.add_argument('--preflight',action='store_true');args=p.parse_args()
    if args.preflight:return preflight()
    run(args);return 0
if __name__=='__main__':raise SystemExit(main())
