from catalog import *
import gzip
con=sqlite3.connect(ROOT/'evidence/catalog.sqlite')
blobs={}
suffixes={'.md','.json','.jsonl','.txt','.yaml','.yml','.csv'}
for path,blob in con.execute('select distinct path,blob from trees'):
    if pathlib.Path(path).suffix.lower() in suffixes and not re.search(r'(?:^|/)(?:\.env|secrets?|credentials?)(?:$|/|\.)',path,re.I):
        blobs.setdefault(blob,set()).add(path)
for l in (ROOT/'evidence/all_reachable_objects.tsv').read_text().splitlines():
    a=l.split(' ',1)
    if len(a)==2 and re.search(r'(?:CP[_-]?\d+|CHECKPOINT|GIGA|CONVERGENCE|LONGITUDINAL|HORIZONTAL|VERTICAL)',a[1],re.I) and pathlib.Path(a[1]).suffix.lower() in suffixes:
        blobs.setdefault(a[0],set()).add(a[1])
out=ROOT/'evidence/blobs';out.mkdir(exist_ok=True)
p=subprocess.Popen(GIT+['cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
index=[]
for sha,paths in blobs.items():
    p.stdin.write((sha+'\n').encode());p.stdin.flush()
    header=p.stdout.readline().decode().strip().split()
    if len(header)!=3:continue
    typ=header[1];size=int(header[2]);data=p.stdout.read(size);p.stdout.read(1)
    if typ!='blob' or size>8_000_000: continue
    try: txt=data.decode('utf-8')
    except UnicodeDecodeError:continue
    if '\0' in txt:continue
    (out/(sha+'.txt')).write_text(txt)
    for path in sorted(paths):index.append({'path':path,'blob':sha,'size':size})
p.stdin.close();p.wait()
dump('artifact_blob_index.json',index)
(ROOT/'evidence/commit_changes.txt').write_bytes(git('log','--all','--format=COMMIT %H','--name-status','--no-renames'))
print(json.dumps({'text_blobs':len(list(out.iterdir())),'path_blob_pairs':len(index)}))
