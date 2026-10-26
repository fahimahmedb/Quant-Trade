import datetime as dt,hashlib,json,signal,sys,time,urllib.request,urllib.error
from pathlib import Path
p=Path('/workspace/scratch/discovery-v4-20261011/france');p.mkdir(exist_ok=True)
m=json.load(open('research/edge_lab/discovery/experiments/disc-france-oat-bund-l1-v0.manifest.json'))
class NR(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None
opener=urllib.request.build_opener(NR())
def alarm(*a):raise TimeoutError('30s wall bound')
signal.signal(signal.SIGALRM,alarm)
for item in m['series']:
 name=item['country']; f=p/(name+'.intent.json');assert not f.exists(),'No replay'
 rec=dict(item,at=dt.datetime.now(dt.timezone.utc).isoformat(),preregistration='8e820f454f018a5c7bc7b61bf8002797b4a813d8',max_bytes=1048576,max_seconds=30,retries=0)
 f.write_text(json.dumps(rec));t=time.monotonic();cpu=time.process_time();body=b'';rec.update(status=None,error=None)
 try:
  signal.alarm(30)
  with opener.open(urllib.request.Request(item['url'],headers={'User-Agent':'QuantTrade personal exploratory research','Accept':'text/csv'}),timeout=30) as r:
   rec.update(status=r.status,headers={k:v for k,v in r.headers.items() if k.lower() in ['date','last-modified','etag','content-type','content-length','location']});body=r.read(1048576)
   if len(body)>=1048576:raise ValueError('size ceiling')
 except urllib.error.HTTPError as e:rec.update(status=e.code,error=str(e))
 except Exception as e:rec['error']=str(e)
 finally:signal.alarm(0)
 rec.update(payload_bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),wall_seconds=time.monotonic()-t,cpu_seconds=time.process_time()-cpu,paid_usd=0)
 (p/(name+'.csv')).write_bytes(body);(p/(name+'.receipt.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
 if rec['error']:sys.exit(2)
