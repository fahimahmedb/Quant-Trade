import pathlib,sqlite3,json,datetime,collections,hashlib,csv
P=pathlib.Path(__file__).parent;D=sqlite3.connect(P/'index/coverage.sqlite');D.row_factory=sqlite3.Row
out=P/'surface';out.mkdir(exist_ok=True);events=[]
def add(kind,id,at,title,source,**kw):
 dt=datetime.datetime.fromisoformat(at.replace('Z','+00:00')) if at else None
 events.append(dict(id=kind+':'+str(id),kind=kind,time_original=at,time_utc=dt.astimezone(datetime.timezone.utc).isoformat() if dt else None,day=dt.astimezone(datetime.timezone.utc).date().isoformat() if dt else 'UNKNOWN',title=title,source=source,status='INDEXED_PENDING_SURFACE_REVIEW',**kw))
for r in D.execute('select * from commits'):
 paths=[x[0] for x in D.execute('select distinct path from changes where commit_sha=?',(r['sha'],))]
 add('commit',r['sha'],r['commit_date'],r['subject'],'git:'+r['sha'],author_date=r['author_date'],parents=r['parents'],paths=paths)
for f in sorted((P/'raw').glob('*.json')):
 n=f.stem
 if not (n=='issues-1' or n.startswith(('timeline-','issue-comments-','review-comments-','reviews-','runs-'))):continue
 d=json.loads(f.read_text());src=str(f.relative_to(P))
 if n=='issues-1':
  for x in d:
   add('issue_created',x['id'],x['created_at'],x['title'],src,number=x['number'],url=x['html_url'])
   if x['closed_at']:add('issue_closed',x['id'],x['closed_at'],x['title'],src,number=x['number'])
 elif n.startswith('runs-'):
  for x in d.get('workflow_runs',[]):add('run',x['id'],x['created_at'],x['name'],src,sha=x['head_sha'],conclusion=x['conclusion'])
 elif isinstance(d,list):
  for i,x in enumerate(d):
   if n.startswith('timeline-') and x.get('event')=='committed':
    add('timeline_commit_appearance',n+':'+str(i),None,x.get('message','').split('\n')[0],src,commit_sha=x.get('sha'),note='Occurrence in PR; no GitHub event time supplied; Git commit dates remain in commit record.');continue
   at=x.get('created_at') or x.get('submitted_at');body=x.get('body') or '';kind='timeline' if n.startswith('timeline-') else n.rsplit('-',1)[0]
   id=x.get('id') or n+':'+str(i)
   add(kind,id,at,x.get('event') or body.split('\n')[0][:200],src,source_ordinal=i,issue=x.get('issue_url'),body_sha256=hashlib.sha256(body.encode()).hexdigest(),actor=(x.get('user') or x.get('actor') or {}).get('login'))
# Separate source occurrences are retained; repeated representations are not independent events.
assert sum(x['kind']=='commit' for x in events)==6393
counts=collections.Counter(x['id'] for x in events)
for x in events:x['representations_for_same_id']=counts[x['id']]
events.sort(key=lambda x:(x['day'],x['time_utc'] or '',x['id']))
with (out/'traces.jsonl').open('w') as f:
 for x in events:f.write(json.dumps(x,ensure_ascii=False)+'\n')
by=collections.defaultdict(list)
for x in events:by[x['day']].append(x)
start=datetime.date(2026,7,13);end=datetime.date(2026,10,31);days=[]
while start<=end:
 day=start.isoformat();a=by.get(day,[]);c=collections.Counter(x['kind'] for x in a)
 days.append(dict(day=day,source_occurrences=len(a),commits=c['commit'],github_occurrences=len(a)-c['commit'],status='PENDING_SURFACE_REVIEW' if a else 'NO_DATED_TRACE_IN_SNAPSHOT',reviewed_trace_ids=[]));start+=datetime.timedelta(days=1)
(out/'days.json').write_text(json.dumps(days,indent=2))
with (out/'DAILY_INDEX.md').open('w') as f:
 f.write('# Historique quotidien — index de couverture UTC\n\nInventaire automatique, pas un récit relu. Les occurrences de timeline peuvent répéter des commits/commentaires. UNKNOWN conserve les dates absentes. Aucune activité n’est inventée pour les journées sans trace.\n\n| Jour | Commits | Occurrences GitHub | État |\n|---|---:|---:|---|\n')
 for x in days:f.write(f"| {x['day']} | {x['commits']} | {x['github_occurrences']} | {x['status']} |\n")
(out/'coverage.json').write_text(json.dumps(dict(method='CHRONOLOGICAL_SURFACE',target_active_branches=['code','projet'],target_names_provisional=True,calendar_days=len(days),commit_traces=6393,total_source_occurrences=len(events),undated_occurrences=len(by['UNKNOWN']),surface_reviewed_days=0,deep_document_reads_not_completion_criterion=True),indent=2))
print((out/'coverage.json').read_text())
