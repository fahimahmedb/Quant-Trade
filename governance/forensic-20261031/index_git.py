import subprocess,json,sqlite3,pathlib,datetime,re,collections
P=pathlib.Path(__file__).parent
G=['git','--git-dir='+str(P/'repository.git')]
def git(*a): return subprocess.check_output(G+list(a))
db=sqlite3.connect(P/'index'/'coverage.sqlite')
db.executescript('''
create table if not exists commits(sha text primary key,parents text,author_date text,commit_date text,subject text,status text);
create table if not exists refs(ref text primary key,sha text,kind text,status text);
create table if not exists versions(blob text,path text,document integer,collected integer,indexed integer,read integer default 0,verified integer default 0,primary key(blob,path));
create table if not exists changes(commit_sha text,old_blob text,new_blob text,status text,path text);
create table if not exists head_files(ref text,path text,blob text,primary key(ref,path));
create table if not exists reads(blob text primary key,method text,note text);
''')
refs=[]
for l in git('for-each-ref','--format=%(refname)\t%(objectname)').decode().splitlines():
 r,s=l.split('\t');refs.append((r,s,r.split('/')[1],'INDEXED'))
db.executemany('insert or replace into refs values(?,?,?,?)',refs)
log=git('log','--all','--format=%H%x00%P%x00%aI%x00%cI%x00%s').decode(errors='replace')
for l in log.splitlines():
 parts=l.split('\0')
 if len(parts)==5: db.execute('insert or replace into commits values(?,?,?,?,?,?)',(*parts,'INDEXED'))
db.commit()
doc=lambda p: int(bool(re.search(r'\.(md|mdx|rst|txt|adoc|pdf|org|html?)$',p,re.I)))
raw=git('log','--all','--root','-m','--no-renames','--raw','--no-abbrev','--format=COMMIT %H').decode(errors='replace')
(P/'raw'/'git-changes.txt').write_text(raw)
db.execute('delete from changes')
sha=None
for l in raw.splitlines():
 if l.startswith('COMMIT '):sha=l[7:]
 elif l.startswith(':') and '\t' in l:
  meta,path=l.split('\t',1);parts=meta.split();old,new,status=parts[2:5]
  db.execute('insert into changes values(?,?,?,?,?)',(sha,old,new,status,path))
  for b in (old,new):
   if b!='0'*40: db.execute('insert or ignore into versions(blob,path,document,collected,indexed) values(?,?,?,?,?)',(b,path,doc(path),1,1))
db.commit()
for r,s,k,st in refs:
 if k not in ('heads','pull'):continue
 for l in git('ls-tree','-r',s).decode(errors='replace').splitlines():
  meta,path=l.split('\t',1);mode,typ,b=meta.split()
  if typ!='blob':continue
  db.execute('insert or replace into head_files values(?,?,?)',(r,path,b))
  db.execute('insert or ignore into versions(blob,path,document,collected,indexed) values(?,?,?,?,?)',(b,path,doc(path),1,1))
 db.commit()
heads=[(r,s) for r,s,k,st in refs if k=='heads']
targets=['refs/heads/blue/master-v2-2026-09-20','refs/heads/builder/convergence-wave2-canonical-20261021','refs/heads/builder/v2-forward-20261020']
rows=[]
for r,s in heads:
 row={'branch':r[11:],'sha':s,'content_review':'PENDING','disposition':'PRESERVE_PENDING_RECONCILIATION'}
 for t in targets:
  if not any(x[0]==t for x in heads):continue
  key=t[11:]
  row[key+'_ancestor']=subprocess.run(G+['merge-base','--is-ancestor',s,t]).returncode==0
  out=git('rev-list','--left-right','--count',s+'...'+t).decode().split();row[key+'_unique_commits']=int(out[0]);row[key+'_target_only_commits']=int(out[1])
 rows.append(row)
(P/'index'/'branch-ancestry.json').write_text(json.dumps(rows,indent=2))
summary={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'refs':len(refs),'branches':len(heads),'distinct_heads':len({s for r,s in heads}),'commits':db.execute('select count(*) from commits').fetchone()[0],'document_blob_path_versions':db.execute('select count(*) from versions where document=1').fetchone()[0],'unique_document_blobs':db.execute('select count(distinct blob) from versions where document=1').fetchone()[0],'document_blobs_read':db.execute('select count(*) from reads').fetchone()[0]}
(P/'index'/'git-counts.json').write_text(json.dumps(summary,indent=2)); print(json.dumps(summary))
db.close()
