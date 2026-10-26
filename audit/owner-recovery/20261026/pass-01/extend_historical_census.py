from catalog import *
from collections import defaultdict
def readcsv(name):return list(csv.DictReader((ROOT/'reports'/name).open()))
ideas=readcsv('10_IDEA_MASTER_LEDGER.csv');pos=readcsv('11_POSITIVE_IDEA_LINEAGE.csv');refs=loadrefs()
con=sqlite3.connect(ROOT/'evidence/catalog.sqlite')
ids={x['IDEA_ID'] for x in ideas}
results=json.load(open(ROOT/'evidence/all_experiment_result_versions.json'))
for x in results:
    hid=x['id']
    if hid in ids:continue
    d=json.loads((ROOT/'evidence/blobs'/(x['blob']+'.txt')).read_text())
    q=con.execute('select head from trees where path=? and blob=? limit 1',(x['path'],x['blob'])).fetchone()
    ev=(q[0]+':'+x['path']) if q else 'git blob '+x['blob']
    row={k:'UNKNOWN' for k in ideas[0]};row.update(IDEA_ID=hid,FAMILY=hid,FUNCTIONAL_DESCRIPTION=d.get('reason','Frozen expression; see protocol'),SOURCE='Existing repository result',ORIGIN_METHOD='PINNED_EXPERIMENT_RESULT',HYPOTHESIS_ARTIFACT=ev,VALIDATION_RESULT=x['decision'],LAST_ACTUAL_DESCENDANT=ev,CURRENT_STATE=x['decision'],WHY_STOPPED=str(d.get('reason',d.get('next_action',d.get('limits','UNKNOWN')))),RECORD_KIND='EXPRESSION_RESULT_NOT_IN_CURRENT_QUEUE',COUNT_AS_DISTINCT_ROOT='UNKNOWN_MECHANISM_OVERLAP',EVIDENCE_CLASS='FACT_PROVEN_RESULT_RECORD',AUDIT_LIMIT='Result existence and declared verdict verified; all input/source hashes and ancestor Actions runs not yet re-audited.')
    ideas.append(row);ids.add(hid)
# A named historical positive is a lead even if its reconciler has decision UNKNOWN.
legacy=json.load(open(ROOT/'evidence/LEGACY_RESEARCH_LEDGER.json'))
for d in legacy['records']:
    if d['HYPOTHESIS_ID']=='LAB24-FUTURES-TREND-CARRY':
        row={k:'UNKNOWN' for k in pos[0]};row.update(IDEA_ID=d['HYPOTHESIS_ID'],POSITIVE_DISPOSITION=d['RESULT'],POSITIVE_ARTIFACT=refs['research/legacy-economic-reconciliation-20261015']+':LEGACY_RESEARCH_LEDGER.json',LAST_DURABLE_RESULT=d['RESULT_ARTIFACT'],TERMINAL_CLASS='UNKNOWN',REASON='Original result exists in historical lab branch; descendant attribution and contamination accounting still pending',EVIDENCE_CLASS='FACT_PROVEN_RECONCILIATION_RECORD; UNDERLYING_LINEAGE_UNKNOWN',SCOPE='Retrospective lab claim, not independent confirmed edge',TRACED_TO_TERMINUS='NO')
        pos.append(row)
groups=defaultdict(list)
for d in json.load(open(ROOT/'evidence/fast_rail_all_versions.json')):
    groups[d['blob']].append(d)
for blob,rows in groups.items():
    byid=defaultdict(list)
    for x in rows:
        rid=x['record'].get('id','')
        if re.fullmatch(r'H-\d+',rid):byid[rid].append(x['record'])
    for hid,records in sorted(byid.items()):
        declared=[x for x in records if x.get('event')=='declared']
        first=declared[0] if declared else records[0]
        verdicts=[x for x in records if x.get('event') in ['verdict','shadow_direct_decision','diagnostic','shadow_direct_amended']]
        last=verdicts[-1] if verdicts else records[-1]
        # Version namespace intentionally preserves competing H-006 meanings.
        ev=rows[0]['heads'][0]+':research/fast_rail/registry.jsonl#blob='+blob+';id='+hid
        row={k:'UNKNOWN' for k in ideas[0]};row.update(IDEA_ID='FAST:'+blob[:12]+':'+hid,ROOT_TASK=hid,BIRTH_DATE=first.get('at','UNKNOWN'),FAMILY='FAST_RAIL_SCOPED_ID; NOT_HORIZONTAL_H',FUNCTIONAL_DESCRIPTION=first.get('title',first.get('reason','UNKNOWN')),SOURCE=json.dumps(first.get('data','UNKNOWN')),ORIGIN_METHOD='HISTORICAL_REGISTRY',MECHANISM=first.get('mechanism','UNKNOWN'),HYPOTHESIS_ARTIFACT=ev,VALIDATION_RESULT=last.get('level',last.get('event','UNKNOWN')),LAST_ACTUAL_DESCENDANT=ev,CURRENT_STATE=last.get('level',last.get('event','UNKNOWN')),WHY_STOPPED=last.get('reason','UNKNOWN'),RECORD_KIND='FAST_RAIL_VERSIONED_RECORD',COUNT_AS_DISTINCT_ROOT='NO_ADDITION_WITHOUT_VERSION_AND_ID_COLLISION_RECONCILIATION',EVIDENCE_CLASS='FACT_PROVEN_RECORD_EXISTS; LINEAGE_NOT_RECONSTRUCTED',AUDIT_LIMIT='Six registry versions overlap. H-006 means listing fade in one rail and sports-value test in unified rail. at timestamps include an explicit historical correction; do not trust as preregistration proof.')
        ideas.append(row)
csvout('10_IDEA_MASTER_LEDGER.csv',ideas);csvout('11_POSITIVE_IDEA_LINEAGE.csv',pos)
stats=json.load(open(ROOT/'evidence/research_census_stats.json'))
stats.update(idea_ledger_rows=len(ideas),row_kinds=dict(__import__('collections').Counter(x['RECORD_KIND'] for x in ideas)),positive_items_indexed=len(pos),positive_items_scoped_terminal=sum(x['TRACED_TO_TERMINUS']=='YES_SCOPED_DISPOSITION' for x in pos),positive_items_untraced=[x['IDEA_ID'] for x in pos if x['TRACED_TO_TERMINUS']=='NO'],experiment_result_paths_indexed=len(results),fast_registry_versions=len(groups))
dump('research_census_stats.json',stats)
print(json.dumps({k:v for k,v in stats.items() if k in ['idea_ledger_rows','row_kinds','positive_items_indexed','positive_items_scoped_terminal','positive_items_untraced','experiment_result_paths_indexed','fast_registry_versions']},indent=2))
