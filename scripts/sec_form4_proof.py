#!/usr/bin/env python3
"""Exact artifact reconciliation for the SEC V2-A1 census gate."""
from __future__ import annotations
import argparse,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from quant.dataplane.sec_form4 import END_DATE,REASON_CODES  # noqa:E402
ART=ROOT/'artifacts'/'sec_form4_census'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load_jsonl(path):
    raw=gzip.decompress(path.read_bytes()).decode() if path.suffix=='.gz' else path.read_text()
    return [json.loads(x) for x in raw.splitlines() if x.strip()]
def fail(msg):print(msg);return 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true',required=True);p.parse_args()
    required=['provenance_manifest.json','census_summary.json','waterfall.json','normalized_candidates.jsonl.gz','normalized_purchase_observations.jsonl.gz','events.jsonl','loss_ledger.jsonl.gz','mapping_ledger.jsonl','acceptance_manifest.json','price_coverage_snapshot.json','q3_tail_audit.json','q3_tail_manifest.jsonl.gz','CENSUS_REPORT.md']
    missing=[x for x in required if not (ART/x).exists()]
    if missing:return fail('missing SEC census artifacts: '+', '.join(missing))
    manifest=json.loads((ART/'provenance_manifest.json').read_text());summary=json.loads((ART/'census_summary.json').read_text());waterfall=json.loads((ART/'waterfall.json').read_text());acceptance=json.loads((ART/'acceptance_manifest.json').read_text());q3=json.loads((ART/'q3_tail_audit.json').read_text())
    events=load_jsonl(ART/'events.jsonl');obs=load_jsonl(ART/'normalized_purchase_observations.jsonl.gz');candidates=load_jsonl(ART/'normalized_candidates.jsonl.gz');mapping=load_jsonl(ART/'mapping_ledger.jsonl');losses=load_jsonl(ART/'loss_ledger.jsonl.gz');tail=load_jsonl(ART/'q3_tail_manifest.jsonl.gz');price=json.loads((ART/'price_coverage_snapshot.json').read_text())
    for name,expected in manifest.get('deterministic_outputs',{}).items():
        if sha(ART/name)!=expected:return fail(f'stale artifact {name}')
    if canonical_sha(price.get('symbols',{}))!=manifest.get('mapping_input',{}).get('price_coverage_symbols_sha256'):return fail('price coverage hash drift')
    if manifest.get('economic_transaction_cutoff')!=['2020-01-01','2026-06-30']:return fail('economic transaction cutoff drift')
    if len(events)!=summary['formations'] or len(events)!=waterfall.get('economic_formations'):return fail('event count mismatch')
    if len({e['event_id'] for e in events})!=len(events):return fail('event IDs not unique')
    if sum(summary.get('annual_formations',{}).values())!=len(events) or sum(summary.get('issuer_event_distribution',{}).values())!=len(events):return fail('event distributions do not reconcile')
    if len(mapping)!=len(events) or {x['event_id'] for x in mapping}!={x['event_id'] for x in events}:return fail('mapping ledger does not biject events')
    mappable=sum(x['mapping_status']=='MAPPABLE' for x in mapping)
    if (mappable, len(events)-mappable)!=(summary['mappable_events'],summary['unmappable_events']):return fail('mapping counts mismatch')
    unresolved=sum(e['event_time_status']!='RESOLVED' for e in events)
    if unresolved!=summary['event_time_unresolved']:return fail('unresolved event-time mismatch')
    obs_by={x['observation_id']:x for x in obs}
    for event in events:
        if event['formation_transaction_date']>END_DATE.isoformat():return fail(f"event {event['event_id']} escaped cutoff")
        if len(set(event['owner_ciks']))<2 or int(event['session_distance'])>10:return fail(f"event {event['event_id']} violates frozen crossing/window")
        if any(x not in obs_by for x in event['constituent_observation_ids']):return fail(f"event {event['event_id']} broken observation lineage")
        relevant=[obs_by[x] for x in event['constituent_observation_ids']]
        owner_times=[];complete=True
        for owner in event['owner_ciks']:
            accs=sorted({a for o in relevant if o['owner_cik']==owner for a in o['accessions']})
            if not accs or any(a not in acceptance for a in accs):complete=False;continue
            owner_times.append(min(acceptance[a]['acceptance_time'] for a in accs))
        if event['event_time_status']=='RESOLVED':
            if not complete or len(owner_times)<2 or sorted(owner_times)[1]!=event['event_time']:return fail(f"event {event['event_id']} has non-causal resolved time")
        elif complete and len(owner_times)>=2:return fail(f"event {event['event_id']} is unresolved despite complete owner observability")
        exact=sorted((a,acceptance[a]['acceptance_time']) for a in event['accessions'] if a in acceptance)
        if exact!=[tuple(x) for x in event.get('acceptance_timestamps',[])]:return fail(f"event {event['event_id']} acceptance lineage drift")
    for row in candidates:
        if row['status']=='QUALIFYING':
            if row['document_type']!='4' or row['transaction_code']!='P' or row['acquired_disposed_code']!='A':return fail('qualifying candidate violates original Form4 P+A')
            if not row.get('issuer_cik') or not row.get('owner_cik') or row.get('unresolved_owner_cik_rows') or len(row.get('reporting_owner_ciks',[]))!=1:return fail('qualifying candidate identity ambiguity')
            if not (row.get('is_director') or row.get('is_officer')):return fail('qualifying candidate role violation')
            if row['transaction_date']>END_DATE.isoformat():return fail('qualifying row escaped cutoff')
    expected=waterfall.get('original_form4_p_acquired_rows',0)+waterfall.get('form4a_p_acquired_rows',0)
    if len(candidates)!=expected:return fail('normalized candidate table does not reconcile')
    if len({x['record_id'] for x in losses})!=len(losses):return fail('loss record IDs not unique')
    unknown=sorted({r for x in losses for r in x.get('reason_codes',[]) if r not in REASON_CODES})
    if unknown:return fail('unknown reason codes: '+','.join(unknown))
    raw=summary.get('diagnostics',{}).get('raw_row_reconciliation',{})
    if set(raw)!={'SUBMISSION','REPORTINGOWNER','NONDERIV_TRANS'}:return fail('raw row reconciliation missing SEC core tables')
    for table,audit in raw.items():
        if audit['raw_rows']!=audit['unkeyed_rows']+audit['unique_primary_keys']+audit['duplicate_rows']:return fail(f'raw row conservation failed: {table}')
        if audit['conflict_keys']<0:return fail(f'invalid conflict accounting: {table}')
    if q3!=summary.get('q3_tail_audit') or q3!=manifest.get('q3_tail',{}) | {'manifest_sha256':manifest.get('q3_tail',{}).get('manifest_sha256')}:
        # provenance adds only manifest_sha256; compare audit fields separately below.
        for k,v in q3.items():
            if manifest.get('q3_tail',{}).get(k)!=v:return fail(f'Q3 provenance drift: {k}')
    if q3.get('master_form4_count',0)!=len(tail):return fail('Q3 master Form4 count does not match tail manifest')
    if not q3.get('max_filing_date') or q3['max_filing_date']<'2026-07-01':return fail('Q3 tail snapshot does not cover any Q3 posting')
    if any(not row.get('period_of_report') for row in tail):return fail('Q3 tail has unresolved earliest transaction date')
    candidate_tail=[row for row in tail if row['period_of_report']<='2026-06-30']
    if len(candidate_tail)!=q3.get('h1_earliest_transaction_candidates'):return fail('Q3 H1 candidate count mismatch')
    if any(not row.get('full_submission_sha256') for row in candidate_tail):return fail('Q3 H1 candidate lacks full raw submission hash')
    forbidden=('forward_return','total_return','pnl','sharpe','alpha','hit_rate','return_t')
    def reject(value,where):
        if isinstance(value,dict):
            for k,v in value.items():
                if any(t in str(k).lower() for t in forbidden):raise ValueError(f'forbidden performance field {k!r} in {where}')
                reject(v,where)
        elif isinstance(value,list):
            for v in value:reject(v,where)
    try:
        for name,value in [('summary',summary),('waterfall',waterfall),('acceptance',acceptance),('price',price),('events',events),('mapping',mapping),('losses',losses),('candidates',candidates),('observations',obs),('q3',q3),('q3_tail',tail)]:reject(value,name)
    except ValueError as exc:return fail(str(exc))
    print(f"SEC V2-A1 artifacts reconcile: {len(events)} formations; {unresolved} unresolved event-times; {len(losses)} loss/diagnostic rows; raw/Q3/causal/no-outcome invariants pass")
    return 0
if __name__=='__main__':raise SystemExit(main())
