from catalog import *
import zipfile,datetime
REPORTS=ROOT/'reports'
# Correct one conceptual graph edge: the forward rail shares CP079, not2b99 ancestry.
p=REPORTS/'21_SUPERSESSION_GRAPH.md';s=p.read_text().replace('  IMM --> VF[V2 forward CP080-099 /ded4228]','  CPS[Builder CP079 source cf593275] --> C79\n  CPS --> VF[V2 forward CP080-099 /ded4228]');p.write_text(s)
p=ROOT/'evidence/late_v2_control_recovery.json';d=json.loads(p.read_text());d.update(merge_base_with_w2='cf593275e41d21435ac308a144570e1451148815',immutable_2b99_is_ancestor_of_forward=False,ancestry_note='Forward continues the Builder CP079 source; cumulative2b99 has25 commits beyond shared source while forward has20. Do not draw2b99 as its Git parent.');p.write_text(json.dumps(d,indent=2))

movement=json.loads((ROOT/'evidence/moving_head_check.json').read_text())
for name in ['02_CANONICAL_STATE_SNAPSHOT.md','16_RUNTIME_REALITY.md','00_AUDIT_PROTOCOL_AND_GAP_PASS.md']:
 p=REPORTS/name;s=p.read_text();s+='\n\n## Moving-head check after the anchor\n\n'
 s+='At '+movement['checked_at']+', a separate remote-ref check found the following changes. The frozen mirror, census and as-of claims above were not updated. These later commits are not silently included or qualified by this audit.\n\n'
 s+='| Branch | Frozen audit HEAD | Later advertised HEAD |\n|---|---|---|\n'
 for x in movement['changes']:s+='|'+x['branch']+'|`'+x['anchor']+'`|`'+x['end']+'`|\n'
 s+='\nEvidence: `../evidence/moving_head_check.json` and `remote_refs_end.tsv`.\n';p.write_text(s)

# Preserve the fact that original historical positives were found, without inventing descendants.
p=REPORTS/'11_POSITIVE_IDEA_LINEAGE.csv';rows=list(csv.DictReader(p.open()))
for r in rows:
 if r['IDEA_ID'].startswith(('LAB24-','LAB25-')):
  r['REASON']='Original primary lab report/output exists at337c4b7c and was read; final descendant attribution, independent validation and exposure accounting still pending.'
  r['EVIDENCE_CLASS']='FACT_PROVEN_PRIMARY_RESULT_ARTIFACT_EXISTS; FINAL_LINEAGE_UNKNOWN'
  r['SCOPE']='Original retrospective lab result, not an independently confirmed edge or completed current research chain'
csvout(p.name,rows)
csvout('GAP_POSITIVE_LINEAGES.csv',[r for r in rows if r['TRACED_TO_TERMINUS']=='NO'])

# Remove concatenated count words in the short French and method documents without touching hashes/paths.
replacements={'Les25livrables':'Les 25 livrables','des261refs':'des 261 refs','5509commits':'5 509 commits','261branches':'261 branches','252HEAD':'252 HEAD','des162087entrées':'des 162 087 entrées','9267paths':'9 267 paths','de4483blobs':'de 4 483 blobs','4669couples':'4 669 couples','de12snapshots':'de 12 snapshots','de704records':'de 704 records','83/83hashes':'83/83 hashes','334/334hashes':'334/334 hashes','et21logs':'et 21 logs','des72tasks':'des 72 tasks','et15hypothèses':'et 15 hypothèses','49frontier tasks':'49 frontier tasks','des38blocages':'des 38 blocages','15result paths':'15 result paths','20legacy records':'20 legacy records','33seeds Weather':'33 seeds Weather','6versions':'6 versions','146lignes':'146 lignes','Les120records':'Les 120 records','sont100dispositions':'sont 100 dispositions','et20du':'et 20 du','ni120réparations':'ni 120 réparations','ni704CP':'ni 704 CP','Les53labels':'Les 53 labels','223rails':'223 rails','222census':'222 census','et1partiel':'et 1 partiel','584records':'584 records','dont187mentions':'dont 187 mentions','des72tasks':'des 72 tasks','Les764cas':'Les 764 cas','5positifs':'5 positifs','38 tâches':'38 tâches','quotas4×12':'quotas 4 × 12','15 hypothèses':'15 hypothèses','pas15 découvertes':'pas 15 découvertes','pas100 avances':'pas 100 avances','46groupes':'46 groupes','1preuve':'1 preuve','33canonical_edges':'33 canonical_edges'}
for name in ['00_AUDIT_PROTOCOL_AND_GAP_PASS.md','01_OWNER_BRIEF.md','02_CANONICAL_STATE_SNAPSHOT.md','EVIDENCE_INDEX.md']:
 p=REPORTS/name;s=p.read_text()
 for a,b in replacements.items():s=s.replace(a,b)
 p.write_text(s)

required=['01_OWNER_BRIEF.md','02_CANONICAL_STATE_SNAPSHOT.md','03_MASTER_TIMELINE.md','04_CP_MASTER_INDEX.csv','05_BRANCH_AND_RAIL_LEDGER.csv','06_CAPABILITY_MATRIX.csv','07_QUALIFIED_UNINTEGRATED_REGISTER.csv','08_PLANNED_VS_REAL_REGISTER.csv','09_AUTONOMOUS_RESEARCH_CENSUS.csv','10_IDEA_MASTER_LEDGER.csv','11_POSITIVE_IDEA_LINEAGE.csv','12_ORPHAN_REGISTER.csv','13_BLOCKER_REGISTER.csv','14_END_TO_END_LINEAGE.md','15_HVL_HISTORY_AND_CURRENT_VALUE.md','16_RUNTIME_REALITY.md','17_AUTHORITY_MAP.md','18_SECOND_TRUTH_REGISTER.md','19_RESEARCH_DENOMINATOR.md','20_NORTH_STAR_DELTA.md','21_SUPERSESSION_GRAPH.md','22_RECOVERABLE_VALUE_REGISTER.csv','23_CONTRADICTION_REGISTER.csv','24_FUNCTIONAL_PROGRESS_MATRIX.md','25_RECOMMENDED_NEXT_SEQUENCE.md']
errors=[]
for name in required:
 p=REPORTS/name
 if not p.exists() or not p.stat().st_size:errors.append('Missing/empty '+name)
for p in REPORTS.glob('*.csv'):
 with p.open(newline='') as f:
  reader=csv.DictReader(f)
  for i,r in enumerate(reader,2):
   if None in r:errors.append(str(p.name)+': malformed row '+str(i))
def rd(n):return list(csv.DictReader((REPORTS/n).open()))
m=json.loads((ROOT/'evidence/audit_completeness_metrics.json').read_text())
checks={'branch_rows':len(rd('05_BRANCH_AND_RAIL_LEDGER.csv'))==261,'cp_rows':len(rd('04_CP_MASTER_INDEX.csv'))==704,'frontier_rows':len(rd('09_AUTONOMOUS_RESEARCH_CENSUS.csv'))==49,'idea_rows':len(rd('10_IDEA_MASTER_LEDGER.csv'))==146,'capability_rows':len(rd('06_CAPABILITY_MATRIX.csv'))==63,'positive_rows':len(rd('11_POSITIVE_IDEA_LINEAGE.csv'))==15,'positive_termini':sum(x['TRACED_TO_TERMINUS']=='YES_SCOPED_DISPOSITION' for x in rd('11_POSITIVE_IDEA_LINEAGE.csv'))==10,'frozen_dispositions':dict(__import__('collections').Counter(x['CURRENT_STATE'] for x in rd('10_IDEA_MASTER_LEDGER.csv') if x['RECORD_KIND']=='FROZEN_HYPOTHESIS'))=={'VALIDLY_PARKED':7,'VALIDLY_BLOCKED':7,'ORPHANED_POSITIVE_HANDOFF':1},'gap_branches':len(rd('GAP_BRANCHES.csv'))==223,'gap_cps':len(rd('GAP_CP_RECORDS.csv'))==584,'gap_positive':len(rd('GAP_POSITIVE_LINEAGES.csv'))==5,'contradictions_open':sum(x['STATE']=='OPEN' for x in rd('23_CONTRADICTION_REGISTER.csv'))==8,'explicit_incomplete':m['AUDIT_COMPLETENESS']=='INCOMPLETE'}
for k,v in checks.items():
 if not v:errors.append('Failed consistency '+k)
# Local relative markdown links must resolve. Remote URLs and illustrative schema fragments excluded.
for p in REPORTS.glob('*.md'):
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if target.startswith(('https://','http://','#')):continue
  f=(p.parent/target.split('#')[0]).resolve()
  if not f.exists():errors.append('Broken local link '+p.name+' -> '+target)
proof=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),required_deliverables=len(required),consistency_checks=checks,errors=errors,product_tests_run=False,product_edits=False,completeness='INCOMPLETE')
dump('report_integrity_checks.json',proof)
if errors:print(json.dumps(proof,indent=2));raise SystemExit(1)

readme='''# Quant-Trade Owner Recovery — frozen forensic pass

Start with reports/01_OWNER_BRIEF.md, then reports/02_CANONICAL_STATE_SNAPSHOT.md.
Audit completeness is INCOMPLETE. reports/00_AUDIT_PROTOCOL_AND_GAP_PASS.md and the three GAP CSVs enumerate what remains.

The25 numbered files are the requested deliverables. EVIDENCE_INDEX.md maps facts to exact Git objects and CI observations. All report files are frozen projections, not operational state.

The archive includes reports, analysis scripts and selected complete evidence/CI logs. The original full Git mirror and extracted source snapshots remain in /workspace/quant-trade-owner-recovery; they are excluded from this compact archive. Exact public GitHub links and content IDs preserve source retrieval. No product tests or modifications were performed.

Original snapshot anchor:2026-10-26 00:52:12 UTC. Later remote head movement is listed separately, not merged into counts.
'''
(ROOT/'README.md').write_text(readme)
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(REPORTS.iterdir()) if p.is_file()}
dump('report_sha256_manifest.json',manifest)
selected=[]
for p in (ROOT/'evidence').iterdir():
 if not p.is_file():continue
 if p.suffix in ['.json','.txt','.tsv'] and p.stat().st_size<5_000_000:selected.append(p)
archive=ROOT/'QUANT_TRADE_OWNER_RECOVERY_PASS_1.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(REPORTS.iterdir()):
  if p.is_file():z.write(p,str(p.relative_to(ROOT)))
 for p in sorted(selected):z.write(p,str(p.relative_to(ROOT)))
 for p in sorted(ROOT.glob('*.py')):z.write(p,p.name)
 z.write(ROOT/'README.md','README.md')
print(json.dumps({'archive':str(archive),'archive_bytes':archive.stat().st_size,'required_deliverables':25,'report_integrity':'PASS','audit_completeness':'INCOMPLETE','metrics':m},indent=2))
