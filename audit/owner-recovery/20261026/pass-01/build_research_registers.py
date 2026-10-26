from catalog import *
from collections import Counter

REFS=loadrefs()
RHEAD=REFS['builder/oracle-v2-core-20261020']
R=ROOT/'snapshots/runtime_v2'
OS=R/'research/research_os'
EHEAD=REFS['research/edge-lab-continuous']
LEGACY_HEAD=REFS['research/legacy-economic-reconciliation-20261015']
def jread(p): return json.loads(p.read_text())
def flat(x):
    if isinstance(x,dict):
        for v in x.values(): yield from flat(v)
    elif isinstance(x,list):
        for v in x: yield from flat(v)
    elif isinstance(x,str): yield x
def ref(sha,path): return sha+':'+path
def first_commit(sha,path):
    z=git('log','--diff-filter=A','--format=%H|%cI','--reverse',sha,'--',path).decode().splitlines()
    return z[0] if z else 'NOT_FOUND'
tasks={p.stem:jread(p) for p in sorted((OS/'tasks').glob('*.json'))}
hyps={p.stem:jread(p) for p in sorted((OS/'hypotheses').glob('*.json'))}
runtime={}
for tid,t in tasks.items():
    runtime[tid]={'task':t,'receipt_files':[str(x.relative_to(R)) for x in sorted((OS/'receipts'/tid).glob('*.json'))],
                  'event_files':[str(x.relative_to(R)) for x in sorted((OS/'events'/tid).glob('*.json'))],
                  'artifact_files':[str(x.relative_to(R)) for x in sorted((OS/'artifacts'/tid).rglob('*.json'))]}
dump('runtime_task_census.json',runtime)
front=[]
for tid,t in tasks.items():
    if not tid.startswith('FRONTIER-'): continue
    hit=[h for h in hyps if h in json.dumps(t)]
    artifact_results=[]
    for f in runtime[tid]['artifact_files']:
        d=jread(R/f)
        for key in ['result','status','reason','blockers','terminal_disposition','decision']:
            if key in d: artifact_results.append(pathlib.Path(f).name+':'+key+'='+json.dumps(d[key],ensure_ascii=False))
    lease=t.get('lease') or {}
    origin='AUTOMATIC_REFILL_CREATION' if t.get('derivation',{}).get('type')=='EMPTY_QUEUE_FRONTIER_REFILL' else 'UNKNOWN'
    execution='MANUAL_WORKER_IDENTIFIED' if any(x in str(lease.get('owner','')).lower() for x in ['manual','interactive','chatgpt']) else ('ORACLE_WORKER_IDENTIFIED' if 'oracle-' in str(lease.get('owner','')) else 'WORKFLOW_LABEL_NOT_EXECUTION_PROOF')
    front.append(dict(TASK_ID=tid,FAMILY=t.get('derivation',{}).get('frontier_id',t.get('inputs',{}).get('frontier_id','UNKNOWN')),
        CREATED_AT=t.get('created_at','UNKNOWN'),ORIGIN=origin,AUTONOMOUS_OR_MANUAL=origin+';'+execution,
        HYPOTHESIS=';'.join(hit) or 'NONE_FOUND',RESULT=json.dumps(t.get('completion',t.get('result',{})),ensure_ascii=False),
        DESCENDANTS=';'.join('VALIDATE-'+h for h in hit if 'VALIDATE-'+h in tasks) or 'NONE_FOUND',FINAL_STATE=t.get('status','UNKNOWN'),
        WORKER=lease.get('owner','UNKNOWN'),ARTIFACT_RESULTS=' | '.join(artifact_results),RECEIPT_COUNT=len(runtime[tid]['receipt_files']),
        EVIDENCE=ref(RHEAD,'research/research_os/tasks/'+tid+'.json'),EVIDENCE_CLASS='FACT_PROVEN',
        LIMIT='Creation derivation and durable execution are separate; COMPLETE/BLOCKED is a task state, not an economic verdict.'))
csvout('09_AUTONOMOUS_RESEARCH_CENSUS.csv',front)

dispositions={
 'FLOW-UST-PRIMARY-DEALER-AUCTION-001':('PASS_TO_TEST_DESIGN_BOUNDED','ORPHANED_POSITIVE_HANDOFF','Frozen protocol at 7b843ddd; CP2 declares authorized acquisition; no execution/result task found in reachable head paths. Receipt missing for validation. Authority conflicts with later global false.', 'research/research_os/artifacts/FLOW-UST-PRIMARY-DEALER-AUCTION-001/frozen-economic-screen-v1.json','7b843ddd551c6770c0ff5941cf5cb1ffb74b8452'),
 'QUANT-FORM144-SUPPLY-001':('EXPLORE','VALIDLY_BLOCKED','Experiment admission and exact-head execution exist on isolated branch; SEC HTTP403 before event sample/outcomes. PARK_DATA, no economic rejection.','research/research_os/experiments/results/FORM144_SUPPLY_001_RESULT.json',REFS['research/economic-test-form144-supply-20261017']),
 'EVENT-DUEBILL-LARGE-DIST-001':('EXPLORE','VALIDLY_PARKED','Source-readiness artifact parks missing historical entitlement-bearing/when-issued paired prices.','research/research_os/assessments/DUEBILL_SOURCE_READINESS_20261017.json',REFS['research/duebill-source-readiness-20261017']),
 'FLOW-ADR-TERM-001':('EXPLORE','VALIDLY_BLOCKED','Ready for frozen design only; documentary-only authority. No actual design/task found. Authority block is real; automatic continuation not established.','research/research_os/assessments/VALIDATE-FLOW-ADR-TERM-001.json',RHEAD),
 'EVENT-SCHEDULE13D-DISCLOSURE-CLOCK-001':('PASS_TO_TEST_DESIGN_WITH_BLOCK_CLAIM_LEVEL','VALIDLY_BLOCKED','Item4 taxonomy/regime boundary unresolved; integration_handoff_authorized=false.','research/research_os/assessments/VALIDATE-EVENT-SCHEDULE13D-DISCLOSURE-CLOCK-001.json',RHEAD),
 'FUND-ASML-CAPACITY-PRICING-001':('PASS_BOUNDED_WITH_BLOCK_CLAIM_LEVEL','VALIDLY_BLOCKED','Business mechanism survives, stronger durable earnings/security claim blocked; handoff explicitly not authorized.','research/research_os/assessments/VALIDATE-FUND-ASML-CAPACITY-PRICING-001.json',RHEAD),
 'FUND-ASML-CAPACITY-SERVICE-001':('PASS_BOUNDED_WITH_BLOCK_CLAIM_LEVEL','VALIDLY_BLOCKED','Business mechanism only; claim restriction, no subsequent integration authority; source overlap with ASML pricing.','research/research_os/assessments/VALIDATE-FUND-ASML-CAPACITY-SERVICE-001.json',RHEAD),
 'FUND-TSMC-N2-MARGIN-LEARNING-001':('PASS_BOUNDED_WITH_BLOCK_CLAIM_LEVEL','VALIDLY_BLOCKED','N2 ramp learning mechanism only; stronger claim blocked; result handoff_created=false.','research/research_os/tasks/VALIDATE-FUND-TSMC-N2-MARGIN-LEARNING-001.json',RHEAD),
 'EVENT-FDA-ADCOM-BRIEFING-CLOCK-001':('PARK_DATA','VALIDLY_PARKED','Historical primary briefing publication timestamps and independent classification missing.','research/research_os/assessments/VALIDATE-EVENT-FDA-ADCOM-BRIEFING-CLOCK-001.json',RHEAD),
 'EVENT-STAPLED-CVR-PRV-001':('PARK_DATA_POPULATION_BLOCK','VALIDLY_PARKED','Documentary issuer example does not establish admissible general population.','research/research_os/assessments/VALIDATE-EVENT-STAPLED-CVR-PRV-001.json',RHEAD),
 'FLOW-RUSSELL-RECON-CLOSE-001':('PARK_DATA','VALIDLY_PARKED','PIT weights/float and forced-flow sizing not established.','research/research_os/assessments/VALIDATE-FLOW-RUSSELL-RECON-CLOSE-001.json',RHEAD),
 'QUANT-LETF-DAILY-RESET-001':('PARK_DATA','VALIDLY_PARKED','Pre-close AUM/shares/creation-redemption and net hedge mapping missing.','research/research_os/assessments/VALIDATE-QUANT-LETF-DAILY-RESET-001.json',RHEAD),
 'QUANT-CLOSE-AUCTION-IMBALANCE-001':('FROZEN_NO_VALIDATION_HANDOFF_AUTHORITY','VALIDLY_BLOCKED','Root task forbids unauthorized handoff; separate source-readiness branch must be reconciled.','research/research_os/tasks/FRONTIER-QUANT-MECHANISM-DISTINCT-SIGNAL-001.json',RHEAD),
}
for hid in ['DOC-EVENT-d8d19dbf0b1291ce','DOC-FUND-9219d7f488ada3c2']:
    dispositions[hid]=('PARK_BLOCKED_NO_INTEGRATION_AUTHORITY','VALIDLY_PARKED','Automatic documentary validation/challenge/red-team/claim restriction persisted; twelve named readiness blockers; handoff_created=false.',f'research/research_os/artifacts/VALIDATE-{hid}/oracle-worker/integration_handoff.json',RHEAD)

ideas=[]; positives=[]; orphans=[]; blockers=[]
for hid,h in hyps.items():
    related=[tid for tid,t in tasks.items() if hid in json.dumps(t)]
    roots=[tid for tid in related if not tid.startswith('VALIDATE-')]
    val=[tid for tid in related if tid.startswith('VALIDATE-')]
    dec,cl,why,ep,es=dispositions[hid]
    p='research/research_os/hypotheses/'+hid+'.json'
    first=first_commit(RHEAD,p)
    family=h.get('family_id',h.get('mechanism_family','UNKNOWN'))
    mechanism=h.get('mechanism',h.get('thesis',h.get('candidate_hypothesis','UNKNOWN')))
    prov=h.get('worker_provenance',{})
    src=h.get('decision_map',{}).get('primary_evidence',h.get('primary_document',h.get('source_artifact','UNKNOWN')))
    ideas.append(dict(IDEA_ID=hid,ROOT_TASK=';'.join(roots) or 'UNKNOWN',BIRTH_DATE=h.get('frozen_at','UNKNOWN'),FAMILY=family,
      FUNCTIONAL_DESCRIPTION=h.get('claim',str(mechanism)),SOURCE=json.dumps(src,ensure_ascii=False),
      ORIGIN_METHOD=('ORACLE_DOCUMENTARY_WORKER' if prov else 'BOUNDED_RESEARCH_WORKFLOW_OR_INTERACTIVE; see task lease'),
      MECHANISM=str(mechanism),HYPOTHESIS_ARTIFACT=ref(RHEAD,p),VALIDATION_TASK=';'.join(val) or 'NOT_FOUND',VALIDATION_RESULT=dec,
      NEXT_STAGE_DECLARED='See exact assessment / task authority',LAST_ACTUAL_DESCENDANT=ref(es,ep),CURRENT_STATE=cl,WHY_STOPPED=why,
      RECORD_KIND='FROZEN_HYPOTHESIS',COUNT_AS_DISTINCT_ROOT='YES_WITHIN_RESEARCH_OS_15_ONLY',FIRST_ADDITION=first,EVIDENCE_CLASS='FACT_PROVEN',
      AUDIT_LIMIT='Task/result existence proven; semantic terminal classification may be STRONG_INFERENCE. No global cross-program independence claimed.'))
    if dec.startswith('PASS') or dec=='EXPLORE':
      pd=dict(IDEA_ID=hid,POSITIVE_DISPOSITION=dec,VALIDATION_TASK=';'.join(val),POSITIVE_ARTIFACT=ref(RHEAD,('research/research_os/assessments/VALIDATE-'+hid+'.json') if (OS/'assessments'/('VALIDATE-'+hid+'.json')).exists() else 'research/research_os/tasks/VALIDATE-'+hid+'.json'),
        ACTUAL_HANDOFF_ARTIFACT=ref(es,ep) if hid in ['FLOW-UST-PRIMARY-DEALER-AUCTION-001','QUANT-FORM144-SUPPLY-001','EVENT-DUEBILL-LARGE-DIST-001'] else 'NOT_FOUND; no authorized handoff claimed',
        ACTUAL_NEXT_TASK='FORM144 single-historical-look Actions job 117396188885' if hid=='QUANT-FORM144-SUPPLY-001' else ('Protocol commit, no queue execution task found' if hid=='FLOW-UST-PRIMARY-DEALER-AUCTION-001' else 'NOT_FOUND'),
        ACTUAL_EXECUTION='PROVEN source acquisition reached; outcomes not reached' if hid=='QUANT-FORM144-SUPPLY-001' else 'NOT_FOUND downstream economic execution',
        LAST_DURABLE_RESULT=ref(es,ep),TERMINAL_CLASS=cl,REASON=why,EVIDENCE_CLASS='STRONG_INFERENCE' if 'ORPHANED' in cl else 'FACT_PROVEN',SCOPE='Research OS 15; positive subclaim is not scientific/economic pass',TRACED_TO_TERMINUS='NO' if 'ORPHANED' in cl else 'YES_SCOPED_DISPOSITION')
      positives.append(pd)
    if 'ORPHANED' in cl:
      orphans.append(dict(OBJECT_ID=hid,CLASS=cl,EXPECTED_DESCENDANT='Outcome-acquisition execution and durable result after frozen screen',LAST_ARTIFACT=ref(es,ep),MISSING_OBJECT='Execution task / run / result not found',REASON=why,OWNER='Research integration / Owner authority reconciliation',EVIDENCE_CLASS='STRONG_INFERENCE',SCOPE='All advertised head paths and extracted reachable documentary blobs; private host objects unavailable'))
    if cl in ['VALIDLY_BLOCKED','VALIDLY_PARKED']:
      blockers.append(dict(OBJECT_ID=hid,CLASS='EXTERNAL_DEPENDENCY' if dec=='PARK_DATA' or 'POPULATION' in dec or hid in ['QUANT-FORM144-SUPPLY-001','EVENT-DUEBILL-LARGE-DIST-001'] else 'LEGITIMATE_BLOCK',MISSING=why,UNBLOCKED_BY='Qualified data/evidence and authorized independent workflow; Owner for authority changes',EVIDENCE=ref(es,ep),EVIDENCE_CLASS='FACT_PROVEN',AUTOMATIC_RETRY_ALLOWED='NO; new evidence/authority required'))

edge=jread(ROOT/'snapshots/edge_lab/research/edge_lab/STATE.json')
disc=jread(ROOT/'snapshots/edge_lab/research/edge_lab/discovery/STATE.json')
legacy=jread(ROOT/'evidence/LEGACY_RESEARCH_LEDGER.json')
def generic(hid,family,desc,mechanism,decision,current,why,evidence,kind,birth='UNKNOWN',root='UNKNOWN',source='UNKNOWN',count='UNKNOWN'):
    return dict(IDEA_ID=hid,ROOT_TASK=root,BIRTH_DATE=birth,FAMILY=family,FUNCTIONAL_DESCRIPTION=desc,SOURCE=source,ORIGIN_METHOD='RECOVERED_DURABLE_RECORD',MECHANISM=mechanism,HYPOTHESIS_ARTIFACT=evidence,VALIDATION_TASK='UNKNOWN',VALIDATION_RESULT=decision,NEXT_STAGE_DECLARED='See source',LAST_ACTUAL_DESCENDANT=evidence,CURRENT_STATE=current,WHY_STOPPED=why,RECORD_KIND=kind,COUNT_AS_DISTINCT_ROOT=count,FIRST_ADDITION='UNKNOWN',EVIDENCE_CLASS='FACT_PROVEN_RECORD_EXISTS; UNDERLYING_CLAIM_NOT_YET_FULLY_REAUDITED',AUDIT_LIMIT='Do not add family, aggregate, generation and overlapping record counts.')
for hid,x in edge['families'].items():
    ideas.append(generic(hid,hid,x.get('label',''),x.get('label',''),x.get('status','UNKNOWN'),x.get('status','UNKNOWN'),x.get('wake','UNKNOWN'),ref(EHEAD,'research/edge_lab/STATE.json')+'#/families/'+hid,'PROGRAM_FAMILY',source=x.get('ref','UNKNOWN'),count='NO_AGGREGATE'))
for x in disc['queue']:
    hid=x['id'];ev=ref(EHEAD,'research/edge_lab/discovery/STATE.json')+'#/queue/'+hid
    ideas.append(generic(hid,x.get('family','UNKNOWN'),x.get('question',x.get('reason','UNKNOWN')),x.get('mechanism','UNKNOWN'),x.get('typed_verdict',x.get('decision','UNKNOWN')),x.get('status','UNKNOWN'),str(x.get('result',x.get('reason','UNKNOWN')))[:4000],ev,'EXPRESSION_OR_SOFTWARE_GENERATION',birth=x.get('created_at','UNKNOWN'),root=x.get('parent_experiment_id','UNKNOWN'),count='UNKNOWN_OVERLAPPING_GENERATIONS'))
    if x.get('decision')=='PROMOTE_EXPRESSION':
      positives.append(dict(IDEA_ID=hid,POSITIVE_DISPOSITION='PROMOTE_EXPRESSION',VALIDATION_TASK='Declared remove-largest-year adversary executed, passed',POSITIVE_ARTIFACT=ref(EHEAD,'research/edge_lab/discovery/experiments/'+hid+'.result.json'),ACTUAL_HANDOFF_ARTIFACT=ref(EHEAD,'research/edge_lab/discovery/qualifications/cfe-vix-l2-zero-cost-access-2026-10-12.md'),ACTUAL_NEXT_TASK=ref(EHEAD,'research/edge_lab/discovery/experiments/disc-cfe-vix-term-premium-prospective-oos-v1.register.json'),ACTUAL_EXECUTION='Historical 36-trade settlement expression executed; prospective observation count zero',LAST_DURABLE_RESULT='L2 PARK_DATA; prospective OOS register OOS_ACCUMULATING, zero observations; earliest eligible exit lower bound 2026-11-06 in STATE.next',TERMINAL_CLASS='VALIDLY_PARKED',REASON='Execution/risk/capital data unqualified; no retrospective replay; prospective exit not yet due at audit time',EVIDENCE_CLASS='FACT_PROVEN',SCOPE='Edge Lab expression; not alpha/economic identity; older V3 label is unrelated to intake V3',TRACED_TO_TERMINUS='YES_SCOPED_DISPOSITION'))
for x in legacy['records']:
    ideas.append(generic(x['HYPOTHESIS_ID'],x['RESEARCH_FAMILY_ID'],x['TITLE'],x.get('MECHANISM','UNKNOWN'),x.get('RESEARCH_DECISION','UNKNOWN'),x.get('RESULT','UNKNOWN'),';'.join(x.get('OPEN_BLOCKERS',[])),ref(LEGACY_HEAD,'LEGACY_RESEARCH_LEDGER.json')+'#/records/'+x['HYPOTHESIS_ID'],'LEGACY_RECONCILIATION_RECORD',birth=x.get('CREATED_AT','UNKNOWN'),source=str(x.get('PROVENANCE','UNKNOWN')),count='UNKNOWN_OVERLAPS_OR_UNRECOVERED'))
    if x.get('RESEARCH_DECISION') in ['EXPLORE','PROMOTE'] and x['HYPOTHESIS_ID']!='disc-cfe-vix-term-premium-l1-v2-reader':
      positives.append(dict(IDEA_ID=x['HYPOTHESIS_ID'],POSITIVE_DISPOSITION=x.get('RESULT','UNKNOWN'),VALIDATION_TASK='UNKNOWN',POSITIVE_ARTIFACT=ref(LEGACY_HEAD,'LEGACY_RESEARCH_LEDGER.json'),ACTUAL_HANDOFF_ARTIFACT='NOT_FOUND_IN_THIS_PASS',ACTUAL_NEXT_TASK='UNKNOWN',ACTUAL_EXECUTION='Historical retrospective result asserted in reconciliation; requires original-source audit',LAST_DURABLE_RESULT=x.get('RESULT_ARTIFACT','UNKNOWN'),TERMINAL_CLASS='UNKNOWN',REASON='Original run/descendant not yet semantically reconstructed',EVIDENCE_CLASS='UNKNOWN',SCOPE='Legacy reconciliation claim only',TRACED_TO_TERMINUS='NO'))
w=jread(ROOT/'evidence/weather_hypothesis_ledger.json')
for x in w['canonical_edges']:
    hid='WEATHER-V4:'+x['EDGE_ID']
    ideas.append(generic(hid,'weather-v4',x.get('EDGE_FAMILY',''),x.get('MECHANISM',''),x.get('CURRENT_AUTHORITY','UNKNOWN'),'REPAIR_SEED_NOT_PRE_REGISTRATION',x.get('MISSING_EVIDENCE_STATUS','UNKNOWN'),'07405b3c20168014993f1616c19e7d47f5e2a41f:research/weather_forward/v4/blue/BLUE_V4_HYPOTHESIS_LEDGER_2026-10-04.json#'+x['EDGE_ID'],'DESIGN_SEED_NOT_TRIAL',count='NO_NEW_FROZEN_HYPOTHESIS_PROVEN'))
csvout('10_IDEA_MASTER_LEDGER.csv',ideas)
csvout('11_POSITIVE_IDEA_LINEAGE.csv',positives)
orphans.append(dict(OBJECT_ID='VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001',CLASS='ORPHANED_ARTIFACT',EXPECTED_DESCENDANT='Durable completion receipt',LAST_ARTIFACT=ref(RHEAD,'research/research_os/tasks/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001.json'),MISSING_OBJECT='receipts/VALIDATE-FLOW-UST-PRIMARY-DEALER-AUCTION-001/*',REASON='Task COMPLETE and assessment exist; task-specific receipt directory not found in anchored runtime snapshot.',OWNER='Research Control Plane',EVIDENCE_CLASS='FACT_PROVEN',SCOPE='Runtime V2 anchored tree only'))
csvout('12_ORPHAN_REGISTER.csv',orphans)
csvout('13_BLOCKER_REGISTER.csv',blockers)
stats=dict(runtime_head=RHEAD,tasks=len(tasks),statuses=dict(Counter(x.get('status') for x in tasks.values())),task_types=dict(Counter(x.get('task_type') for x in tasks.values())),frontier_tasks=len(front),frontier_families=dict(Counter(x['FAMILY'] for x in front)),frontier_states=dict(Counter(x['FINAL_STATE'] for x in front)),frozen_hypotheses=len(hyps),validation_tasks=sum(x.get('task_type')=='VALIDATION' for x in tasks.values()),assessment_files=len(list((OS/'assessments').glob('*.json'))),hypothesis_births={hid:h.get('frozen_at','UNKNOWN') for hid,h in hyps.items()},last_task_update=max(x.get('updated_at','') for x in tasks.values()),idea_ledger_rows=len(ideas),row_kinds=dict(Counter(x['RECORD_KIND'] for x in ideas)),positive_items_indexed=len(positives),positive_items_scoped_terminal=sum(x['TRACED_TO_TERMINUS']=='YES_SCOPED_DISPOSITION' for x in positives),positive_items_untraced=[x['IDEA_ID'] for x in positives if x['TRACED_TO_TERMINUS']=='NO'],missing_complete_receipts=[tid for tid,t in tasks.items() if t.get('status')=='COMPLETE' and not runtime[tid]['receipt_files']],global_unique_ideas='UNKNOWN',complete=False)
dump('research_census_stats.json',stats)
print(json.dumps(stats,ensure_ascii=False,indent=2))
