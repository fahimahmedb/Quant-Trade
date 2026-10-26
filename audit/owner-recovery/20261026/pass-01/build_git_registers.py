from catalog import *
refs=loadrefs();can=refs['builder/convergence-wave2-canonical-20261021']
commits=json.loads((ROOT/'evidence/all_commits.json').read_text());cm={x['sha']:x for x in commits}
con=sqlite3.connect(ROOT/'evidence/catalog.sqlite')
reach={}
for b,s in refs.items():reach[b]=set(git('rev-list',s).decode().splitlines())
dump('branch_reachability_counts.json',{b:len(s) for b,s in reach.items()})
rows=[]
for b,s in refs.items():
    mb=git('merge-base',can,s,check=False).decode().strip() or 'NOT_FOUND'
    counts=git('rev-list','--left-right','--count',can+'...'+s).decode().split()
    behind,ahead=map(int,counts)
    unique=git('log',can+'..'+s,'--format=%h %s','-8').decode().strip()
    ss=cm.get(s,{})
    ancestry='EXACT_ANCESTOR' if s in reach['builder/convergence-wave2-canonical-20261021'] else 'DIVERGED_OR_DESCENDANT'
    r={'BRANCH':b,'HEAD_SHA':s,'CREATED_FROM':'UNKNOWN_GIT_DOES_NOT_RECORD_BRANCH_BIRTH','MERGE_BASE_WITH_W2_CANDIDATE':mb,'COMMITS_AHEAD_OF_BASE':git('rev-list','--count',mb+'..'+s).decode().strip() if mb!='NOT_FOUND' else 'UNKNOWN','COMMITS_BEHIND_CURRENT_CANONICAL_CANDIDATE':behind,'COMMITS_UNIQUE_VS_W2_CANDIDATE':ahead,'MISSION':'UNKNOWN; head subject: '+ss.get('subject','UNKNOWN'),'CURRENT_STATUS':'HISTORICAL_ANCESTOR_OF_W2_CANDIDATE' if ancestry=='EXACT_ANCESTOR' else 'DIVERGED_REQUIRES_SCOPE_REVIEW','QUALIFIED':'UNKNOWN_NOT_INFERRED_FROM_NAME_OR_SUBJECT','INTEGRATED':ancestry+'; canonical here is W2 candidate, not Owner trunk proof','SUPERSEDED':'UNKNOWN','UNIQUE_UNINTEGRATED_WORK':'NO_UNIQUE_COMMITS' if ahead==0 else 'UNKNOWN_CONTENT_PORT_EQUIVALENCE_NOT_YET_PROVED','LAST_ACTIVITY':ss.get('commit_time','UNKNOWN'),'RELEVANCE_TODAY':'HISTORY_AND_SCOPE_RECONCILIATION','EVIDENCE_CLASS':'FACT_PROVEN_FOR_GIT_FIELDS; UNKNOWN_FOR_SEMANTIC_STATUS','EVIDENCE':'https://github.com/fahimahmedb/Quant-Trade/commit/'+s,'RECENT_UNIQUE_COMMITS':unique}
    rows.append(r)
csvout('05_BRANCH_AND_RAIL_LEDGER.csv',rows)
# All current/historical text artifacts with an explicit checkpoint number.
idx=json.loads((ROOT/'evidence/artifact_blob_index.json').read_text())
cp=[]
raw=git('log','--all','--raw','--no-abbrev','--format=COMMIT %H','--no-renames').decode(errors='replace')
(ROOT/'evidence/raw_commit_changes.txt').write_text(raw)
added={};head=''
for line in raw.splitlines():
    if line.startswith('COMMIT '):head=line[7:]
    elif line.startswith(':') and '\t' in line:
        meta,path=line.split('\t',1);parts=meta.split()
        if len(parts)>=5:added.setdefault((path,parts[3]),[]).append(head)
for x in idx:
    path=x['path'];name=pathlib.Path(path).name
    if pathlib.Path(path).suffix.lower() not in {'.md','.json'}:continue
    mat=re.search(r'(?<![A-Z])(?:CP[_-]?\d+[A-Z]?|CHECKPOINT[_-]?\d+)(?![0-9])',name,re.I)
    if not mat:continue
    # Exclude process logs and fixtures; retain qualification JSON as CP evidence.
    if '/tests/' in path or '/fixtures/' in path or '/worker_wakes/' in path:continue
    blob=x['blob'];txt=(ROOT/'evidence/blobs'/(blob+'.txt')).read_text()
    token=mat.group(0).upper();prefix=name[:mat.start()].rstrip('_-')
    rail=(str(pathlib.PurePosixPath(path).parent)+'/'+prefix).strip('/')
    intro=added.get((path,blob),[])
    chosen=min(intro,key=lambda s:cm.get(s,{}).get('commit_time','9999')) if intro else ''
    title=next((l.strip('# ').strip() for l in txt.splitlines() if l.strip().startswith('#')),name)
    bindings=re.findall(r'(?i)(?:HEAD_SHA|FINAL_SHA|SOURCE_SHA|TESTED_SOURCE_SHA|QUALIFIED_SOURCE_SHA|BASE_SHA|COMMIT_SHA)[`*\s:=]+[`*]?([a-f0-9]{40})',txt)
    rejected='MISSION_CHECKPOINT_ACCEPTED=FALSE' in txt or 'INSUFFICIENT_DEPTH' in txt[:2000]
    classification='REJECTED_AS_INSUFFICIENT' if rejected else 'UNKNOWN_REQUIRES_EVIDENCE_INTERPRETATION'
    if path.startswith('VERTICAL_CP'):
        num=int(re.search(r'\d+',token).group())
        classification=('REJECTED_AS_INSUFFICIENT' if num in list(range(47,61))+list(range(62,101)) else 'QUALIFICATION' if num==39 else 'REPAIR')
    if 'horizontal_convergence1' in path:classification='QUALIFICATION; REPAIR_SCOPE_IN_CHECKPOINT'
    cp.append({'RAIL':rail,'CP_ID':token,'DATE':cm.get(chosen,{}).get('commit_time','UNKNOWN'),'COMMIT_SHA':chosen or 'UNKNOWN','PARENT':cm.get(chosen,{}).get('parents','UNKNOWN'),'MISSION':title,'WHAT_WAS_TESTED':'SEE_EXACT_ARTIFACT; not inferred from PASS','WHAT_WAS_FOUND':txt[:650].replace('\n',' '),'WHAT_CHANGED_FUNCTIONALLY':'UNKNOWN_UNLESS_CHECKPOINT_SCOPE_PROVED','WAS_CODE_CHANGED':'UNKNOWN; commit delta available','ONLY_QUALIFICATION':'UNKNOWN','ONLY_DOCUMENTATION':'UNKNOWN','DEFECT_FOUND':'UNKNOWN','DEFECT_REPAIRED':'UNKNOWN','LATER_INVALIDATED':'YES_NUMERIC_DEPTH_CLAIM' if rejected else 'UNKNOWN','SUPERSEDED':'UNKNOWN; blob versions retained','EVIDENCE_REUSABLE':'AS_SCOPED_ARTIFACT_ONLY_REPLAY_ON_TARGET_REQUIRED','CLASSIFICATION':classification,'EVIDENCE_CLASS':'FACT_PROVEN_ARTIFACT_EXISTS; '+('FACT_PROVEN_RETRACTION' if rejected else 'UNKNOWN_FOR_UNREVIEWED_CLAIMS'),'PATH':path,'BLOB_SHA':blob,'BOUND_SHAS':';'.join(dict.fromkeys(bindings)),'EVIDENCE':('https://github.com/fahimahmedb/Quant-Trade/blob/'+chosen+'/'+path) if chosen else 'git blob '+blob})
csvout('04_CP_MASTER_INDEX.csv',cp)
dump('git_census_stats.json',{'branches':len(rows),'commits':len(commits),'cp_artifact_versions':len(cp),'distinct_cp_paths':len(set(x['PATH'] for x in cp)),'distinct_scoped_cp_labels':len(set((x['RAIL'],x['CP_ID']) for x in cp))})
print(json.dumps({'branches':len(rows),'cp_artifact_versions':len(cp),'cp_scoped_labels':len(set((x['RAIL'],x['CP_ID']) for x in cp))}))
