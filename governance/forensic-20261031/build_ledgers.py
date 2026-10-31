import pathlib,json,sqlite3,csv,hashlib,collections,datetime,zoneinfo,subprocess
P=pathlib.Path(__file__).parent; D=sqlite3.connect(P/'index/coverage.sqlite');D.row_factory=sqlite3.Row
def writecsv(name,rows,fields=None):
 rows=list(rows)
 with (P/'index'/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]) if rows else ['id']);w.writeheader();w.writerows(rows)
writecsv('commits.csv',[dict(x) for x in D.execute('select * from commits order by commit_date,sha')])
writecsv('document-versions.csv',[dict(x) for x in D.execute('select * from versions where document=1 order by blob,path')])
writecsv('all-file-versions.csv',[dict(x) for x in D.execute('select * from versions order by blob,path')])
writecsv('refs.csv',[dict(x) for x in D.execute('select * from refs order by ref')])
events=[]
paris=zoneinfo.ZoneInfo('Europe/Paris')
def ev(kind,id,at,subject,source,**kw):
 if not at:return
 dt=datetime.datetime.fromisoformat(at.replace('Z','+00:00'))
 events.append(dict(kind=kind,id=str(id),at_utc=dt.astimezone(datetime.timezone.utc).isoformat(),at_paris=dt.astimezone(paris).isoformat(),subject=subject,source=source,**kw))
for x in D.execute('select * from commits'):
 ev('commit',x['sha'],x['commit_date'],x['subject'],'git:'+x['sha'],author_date=x['author_date'],parents=x['parents'])
issues=json.loads((P/'raw/issues-1.json').read_text())
for x in issues:
 ev('issue_or_pr_created',x['id'],x['created_at'],x['title'],x['html_url'],number=x['number'])
 if x['closed_at']:ev('issue_or_pr_closed',x['id'],x['closed_at'],x['title'],x['html_url'],number=x['number'])
objects=[];runs=[];reviews=[];threads=[];timelines=[]
prior_discussion={}
if (P/'index/discussion-coverage.csv').exists():
 for x in csv.DictReader((P/'index/discussion-coverage.csv').open()):
  prior_discussion[(x['kind'],str(x['id']))]=x['read'].lower()=='true'
for f in sorted((P/'raw').glob('*.json')):
 d=json.loads(f.read_text());name=f.stem
 if name.startswith('runs-'):runs+=d.get('workflow_runs',[])
 if name.startswith('timeline-') and isinstance(d,list):timelines+= [(name,x) for x in d]
 if name.startswith('reviews-') and isinstance(d,list):reviews+=d
 if name.startswith('threads-'):threads+=d.get('structuredContent',{}).get('review_threads',[])
 if name.startswith(('issue-comments-','review-comments-','reviews-')) and isinstance(d,list):
  for x in d:
   body=x.get('body') or '';objects.append({'kind':name.rsplit('-',1)[0],'id':x['id'],'sha256':hashlib.sha256(body.encode()).hexdigest(),'bytes':len(body.encode()),'collected':True,'indexed':True,'read':prior_discussion.get((name.rsplit('-',1)[0],str(x['id'])),False),'verified':False,'source':str(f.relative_to(P))})
   ev(name.rsplit('-',1)[0],x['id'],x.get('created_at') or x.get('submitted_at'),body.split('\n')[0][:200],str(f.relative_to(P)))
for name,x in timelines:
 ev('timeline',x.get('id') or x.get('sha') or name,x.get('created_at') or x.get('submitted_at'),x.get('event',''),str(P/'raw'/(name+'.json')))
for x in runs:ev('actions_run',x['id'],x['created_at'],x['name'],x['html_url'],head_sha=x['head_sha'],conclusion=x['conclusion'])
events.sort(key=lambda x:(x['at_utc'],x['kind'],x['id']))
with (P/'index/chronology.jsonl').open('w') as f:
 for x in events:f.write(json.dumps(x)+'\n')
counts=collections.defaultdict(collections.Counter)
for x in events:counts[x['at_utc'][:10]][x['kind']]+=1
with (P/'reports/DAILY_LEDGER.md').open('w') as f:
 f.write('# Registre quotidien — UTC\n\nComptage mécanique des traces ; ni lecture sémantique ni récit causal. Horodatages originaux dans chronology.jsonl, affichage Europe/Paris avec DST. Les dates des commits ne prouvent pas une publication GitHub à cette heure.\n\n')
 for day,c in sorted(counts.items()):f.write(f'- {day} : '+', '.join(f'{k}={v}' for k,v in sorted(c.items()))+'\n')
writecsv('discussion-coverage.csv',objects)
writecsv('runs.csv',({k:x.get(k) for k in ['id','name','head_sha','head_branch','created_at','updated_at','status','conclusion','run_attempt','html_url']} for x in runs))
branch=json.loads((P/'index/branch-ancestry.json').read_text())
target='refs/heads/builder/convergence-wave2-canonical-20261021'
tf={x['path']:x['blob'] for x in D.execute('select path,blob from head_files where ref=?',(target,))}; blobs=set(tf.values())
for b in branch:
 files={x['path']:x['blob'] for x in D.execute('select path,blob from head_files where ref=?',('refs/heads/'+b['branch'],))}
 b['file_count']=len(files);b['wave2_same_path_and_blob']=sum(tf.get(p)==h for p,h in files.items());b['wave2_blob_present_any_path']=sum(h in blobs for h in files.values());b['wave2_blob_not_present']=sum(h not in blobs for h in files.values())
writecsv('branches.csv',branch)
carry=[]
sources=['builder/research-factory-core-v2','builder/evidence-store-identity-v2','builder/sec-form4-census-v2a','builder/research-os-aggressive-architecture-20261015','research/design-v1','codex/test','codex/horizontal-completeness-convergence1-20261021','codex/vertical-depth-prewave2-20261021','builder/mega-b-discovery-engine-20261021','builder/mega-c0-scientific-adjudication-20261021','builder/mega-d0-economic-lifecycle-20261021','builder/mega-e-autonomous-runtime-20261021']
for source in sources:
 for x in D.execute('select path,blob from head_files where ref=?',('refs/heads/'+source,)):
  if not x['path'].startswith(('src/','tests/','research/research_os/expansion/')):continue
  h=x['blob'];matches=[p for p,b in tf.items() if b==h]
  carry.append(dict(source=source,path=x['path'],blob=h,target=target,destination='|'.join(matches),status='EXACT_BYTES_PRESENT' if matches else 'SEMANTIC_RECONCILIATION_PENDING',behavioral_verification='NOT_PERFORMED'))
writecsv('carryover-bytes.csv',carry)
manifest=[]
for f in sorted((P/'raw').iterdir()):
 if f.is_file():
  b=f.read_bytes();manifest.append(dict(path=str(f.relative_to(P)),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),status='COLLECTED',read=False))
(P/'index/raw-manifest.json').write_text(json.dumps(manifest,indent=2))
summary=dict(branches=len(branch),commits=D.execute('select count(*) from commits').fetchone()[0],file_blob_versions=D.execute('select count(distinct blob) from versions').fetchone()[0],document_blobs=D.execute('select count(distinct blob) from versions where document=1').fetchone()[0],issues=len(issues),prs=sum('pull_request' in x for x in issues),discussion_objects=len(objects),conversation_comments=sum(x['kind']=='issue-comments' for x in objects),inline_comments=sum(x['kind']=='review-comments' for x in objects),review_submissions=len(reviews),review_threads=len(threads),timeline_events=len(timelines),runs=len(runs),unique_runs=len({x['id'] for x in runs}),raw_files=len(manifest),raw_bytes=sum(x['bytes'] for x in manifest),semantic_review_complete=False,document_blobs_read=D.execute('select count(*) from reads').fetchone()[0],discussion_objects_read=sum(x['read'] for x in objects))
(P/'index/coverage-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
