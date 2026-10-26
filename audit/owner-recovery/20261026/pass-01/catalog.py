import subprocess, json, csv, re, sqlite3, hashlib, pathlib, datetime
ROOT=pathlib.Path('/workspace/quant-trade-owner-recovery')
GIT=['git','--git-dir='+str(ROOT/'source-mirror.git')]
def git(*args, check=True):
    return subprocess.run(GIT+list(args),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check).stdout
def dump(name,obj):
    (ROOT/'evidence'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def csvout(name,rows,fields=None):
    rows=list(rows)
    with (ROOT/'reports'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def loadrefs():
    refs={}
    for l in (ROOT/'evidence/remote_refs_start.tsv').read_text().splitlines():
        a=l.split('\t')
        if len(a)==2 and a[1].startswith('refs/heads/'): refs[a[1][11:]]=a[0]
    return refs
if __name__=='__main__':
    refs=loadrefs();dump('anchored_heads.json',refs)
    commits=[]
    raw=git('log','--all','--format=%H%x00%P%x00%aI%x00%cI%x00%s%x00%B%x1e').decode(errors='replace')
    for rec in raw.split('\x1e'):
        v=rec.strip('\n').split('\x00',5)
        if len(v)==6:commits.append(dict(zip(['sha','parents','author_time','commit_time','subject','body'],v)))
    dump('all_commits.json',commits)
    con=sqlite3.connect(ROOT/'evidence/catalog.sqlite')
    con.execute('create table if not exists trees (head text,path text,blob text,mode text)')
    con.execute('delete from trees')
    for head in sorted(set(refs.values())):
        rows=[]
        for rec in git('ls-tree','-r','-z',head).split(b'\0'):
            if b'\t' not in rec:continue
            meta,path=rec.split(b'\t',1);mode,typ,blob=meta.decode().split()
            if typ=='blob':rows.append((head,path.decode(errors='replace'),blob,mode))
        con.executemany('insert into trees values (?,?,?,?)',rows)
    con.execute('create index if not exists tree_path on trees(path)')
    con.execute('create index if not exists tree_blob on trees(blob)');con.commit()
    paths=con.execute('select distinct path from trees').fetchall()
    dump('all_head_paths.json',[x[0] for x in paths])
    # Complete reachable object inventory also preserves deleted historical paths.
    (ROOT/'evidence/all_reachable_objects.tsv').write_bytes(git('rev-list','--objects','--all'))
    print(json.dumps({'branches':len(refs),'unique_heads':len(set(refs.values())),'commits':len(commits),'head_tree_rows':con.execute('select count(*) from trees').fetchone()[0],'distinct_paths':len(paths)}))
