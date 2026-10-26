from catalog import *
from collections import Counter
def rd(n):return list(csv.DictReader((ROOT/'reports'/n).open()))
refs=loadrefs();R=refs['builder/oracle-v2-core-20261020'];root=ROOT/'snapshots/runtime_v2'
b=rd('13_BLOCKER_REGISTER.csv');primary=len(b)
bc=json.load(open(ROOT/'evidence/blocked_tasks_reason_census.json'))
for x in bc:
    reasons=x['reasons'];txt=';'.join(reasons)
    cl='OPERATIONAL_GAP' if 'STAGE_NOT_EXPLICITLY_AUTHORIZED' in txt else ('EXTERNAL_DEPENDENCY' if 'MISSING_QUALIFIED' in txt else 'LEGITIMATE_BLOCK')
    why=('Existing task text fails mechanism_research authorization pattern; current frontier template is different. Do not silently rewrite old task authority.' if cl=='OPERATIONAL_GAP' else 'Exact duplicate of existing AAPL documentary hypothesis; no new distinct question.' if 'BLOCK_EXACT_CURRENT_DUPLICATE' in txt else 'Registered quant documentary source packet absent.' if 'MISSING_QUALIFIED' in txt else 'Legacy context requires explicit new epoch/trial enrollment; no scientific verdict.')
    b.append(dict(OBJECT_ID=x['task'],CLASS=cl,MISSING=txt+'; '+why,UNBLOCKED_BY='Owner-approved contract/template reconciliation and fresh admissible task' if cl=='OPERATIONAL_GAP' else 'A distinct qualified question/source or explicit epoch reenrollment; no retry loop',EVIDENCE=';'.join(R+':'+p for p in x['evidence']) or R+':research/research_os/tasks/'+x['task']+'.json',EVIDENCE_CLASS='FACT_PROVEN_REASON; STRONG_INFERENCE_OPERATIONAL_CLASS',AUTOMATIC_RETRY_ALLOWED='NO; tasks are terminal BLOCKED'))
csvout('13_BLOCKER_REGISTER.csv',b)
p=rd('11_POSITIVE_IDEA_LINEAGE.csv')
for hid in ['DOC-EVENT-d8d19dbf0b1291ce','DOC-FUND-9219d7f488ada3c2']:
    q={k:'UNKNOWN' for k in p[0]};q.update(IDEA_ID=hid,POSITIVE_DISPOSITION='PRODUCER_RESEARCH_DECISION_EXPLORE; NOT_SCIENTIFIC_PROMOTION',VALIDATION_TASK='VALIDATE-'+hid,POSITIVE_ARTIFACT=R+':research/research_os/hypotheses/'+hid+'.json',ACTUAL_HANDOFF_ARTIFACT=R+':research/research_os/tasks/VALIDATE-'+hid+'.json',ACTUAL_NEXT_TASK='VALIDATE-'+hid,ACTUAL_EXECUTION='PROVEN durable five-stage challenge artifacts, completion receipt and terminal task',LAST_DURABLE_RESULT=R+':research/research_os/artifacts/VALIDATE-'+hid+'/oracle-worker/integration_handoff.json',TERMINAL_CLASS='VALIDLY_PARKED',REASON='PARK_BLOCKED_NO_INTEGRATION_AUTHORITY; twelve named readiness blockers. Positive documentary premise was actually continued through independent challenge.',EVIDENCE_CLASS='FACT_PROVEN',SCOPE='Real Oracle documentary lineage; producer EXPLORE is not validated edge',TRACED_TO_TERMINUS='YES_SCOPED_DISPOSITION')
    p.append(q)
csvout('11_POSITIVE_IDEA_LINEAGE.csv',p)
stats=json.load(open(ROOT/'evidence/research_census_stats.json'));stats.update(positive_items_indexed=len(p),positive_items_scoped_terminal=sum(x['TRACED_TO_TERMINUS']=='YES_SCOPED_DISPOSITION' for x in p),positive_items_untraced=[x['IDEA_ID'] for x in p if x['TRACED_TO_TERMINUS']=='NO'],blocker_rows=len(b),blocked_task_reason_partition={'CURRENT_CORPUS_DUPLICATE':18,'MISSING_QUALIFIED_QUANT_SOURCE':10,'TASK_STAGE_AUTHORIZATION_MISMATCH':9,'LEGACY_REQUIRES_NEW_V2_TRIAL':1},native_v2_trial_files=11,native_v2_generated_proposals=11,native_v2_discarded_proposals=11)
dump('research_census_stats.json',stats)
# Keep source paths exact in the contradiction register; prose descriptions remain prose.
z=rd('23_CONTRADICTION_REGISTER.csv')
for row in z:
    for col in ['SOURCE_A','SOURCE_B']:
        s=row[col]
        if ':' not in s:continue
        sha,path=s.split(':',1)
        if not re.fullmatch('[a-f0-9]{40}',sha):continue
        if path.startswith(('runtime/','expansion/','tasks/','assessments/','architecture/work_receipts/')):path='research/research_os/'+path
        elif path.startswith('worker_wakes/'):path='research/research_os/runtime/'+path
        elif path=='scientific_adjudication.py':path='research/research_os/expansion/scientific_adjudication.py'
        elif path.startswith('FINAL_qualification.json'):path='research/vertical_depth/20261021/FINAL_qualification.json'
        row[col]=sha+':'+path
csvout('23_CONTRADICTION_REGISTER.csv',z)
print(json.dumps({k:stats[k] for k in ['positive_items_indexed','positive_items_scoped_terminal','positive_items_untraced','blocker_rows','blocked_task_reason_partition']},indent=2))
