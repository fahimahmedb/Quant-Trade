from pathlib import Path
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from research.research_os.queue_replenisher import load_source_catalog, load_frontier, load_tasks
from research.research_os.frontier_source_planner_v2 import plan_frontier_source
from research.research_os.expansion.engine_dossiers_v1 import qualify_document_packet
root=Path(__file__).resolve().parents[2]; base=root/'research/research_os'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
start=datetime.now(timezone.utc).isoformat()
catalog=load_source_catalog(base)
for path,entry in catalog.items():
 entry['blob_sha']=subprocess.check_output(['git','rev-parse',f'{head}:{path}'],cwd=root,text=True).strip()
frontier=load_frontier(base); tasks=load_tasks(base)
plans=[plan_frontier_source(frontier_entry=f,tasks=tasks,source_catalog=catalog) for f in frontier['frontiers']]
source_path='research/research_os/sources/sec_t1_operative_rule.json'
record=catalog[source_path]['record']; packet=record['documentary_packet']; capture=packet['capture']
raw=root/'research/research_os/sources/captures/sec_15c6_1_2025.xml'
raw_digest=hashlib.sha256(raw.read_bytes()).hexdigest()
qualification=qualify_document_packet(packet,'INSTITUTIONAL_FLOW',record['freeze_time'])
flow=next(p for p in plans if p['family']=='INSTITUTIONAL_FLOW')
admissible=(flow['status']=='SOURCE_SELECTED' and flow.get('source',{}).get('path')==source_path and qualification['status']=='PASS' and raw_digest==capture['raw_sha256'] and bool(capture['retrieved_at']) and bool(record['freeze_time']) and bool(packet['content_hash']))
source_status='REAL_SOURCE_SHADOW_PASS' if admissible else 'NO_ADMISSIBLE_ADDRESSABLE_REAL_SOURCE'
result={'HEAD_SHA':head,'START_TIME':start,'END_TIME':datetime.now(timezone.utc).isoformat(),'STATUS':source_status,
 'COMMAND':'PYTHONPATH=src:. python3 '+str(Path(__file__)),'PRODUCTION_RESEARCH_STATE_MUTATED':False,'OUTCOME_ACCESSED':False,
 'OPERATION':'read-only registered source qualification and planner projection; no Candidate/root/trial/task creation',
 'catalog_size':len(catalog),'durable_task_count':len(tasks),'planner_results':plans,
 'source_witness':{'path':source_path,'NON_FIXTURE':True,'NON_DEMO':True,'NON_SYNTHETIC':True,
 'DURABLE_PROVENANCE':{'source_ref':packet['source_ref'],'raw_capture_path':str(raw.relative_to(root)),'raw_sha256_declared':capture['raw_sha256'],'raw_sha256_observed':raw_digest,'raw_sha256_matches':raw_digest==capture['raw_sha256'],'git_blob_sha':catalog[source_path]['blob_sha']},
 'HASH_OR_VERSION_PRESENT':{'content_hash':packet['content_hash'],'revision_status':packet['revision_status']},
 'CAPTURE_CLOCK_PRESENT':capture['retrieved_at'],'QUALIFICATION_STATUS_PRESENT':qualification,
 'ACCESS_SCOPE':'UNKNOWN_EXPLICIT_MISSION_READ_ONLY_ONLY','INFORMATION_CUTOFF':record['freeze_time'],'SOURCE_FAMILY':'INSTITUTIONAL_FLOW',
 'ADDRESSABLE_BY_EXISTING_PLANNER':flow['status']=='SOURCE_SELECTED','planner_status':flow['status'],
 'NON_SYNTHETIC_EVIDENCE_REF':'research/research_os/architecture/work_receipts/BUILDER_CP_004_FRONTIER_SOURCE_ADMISSIBILITY_20261020.md#Source-admissibility-proof',
 'limits':['current captured CFR edition does not prove historical PIT availability or current legal applicability','consumed source is still admissible documentary evidence but cannot be issued as unused source']}}
Path('/tmp/oneshot_real_source.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
sys.exit(0 if admissible else 1)
