import datetime as dt,hashlib,json,signal,sys,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path('/workspace/scratch/discovery-v4-20261011/vix');ROOT.mkdir(exist_ok=True)
manifest=json.load(open('research/edge_lab/discovery/experiments/disc-cfe-vix-term-premium-l1-v0.manifest.json'))
start=int(sys.argv[1]); stop=min(start+4,len(manifest['files']))
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
opener=urllib.request.build_opener(NoRedirect())
def alarm(*a):raise TimeoutError('15-second wall ceiling')
signal.signal(signal.SIGALRM,alarm)
for item in manifest['files'][start:stop]:
 name=item['contract']; intent=ROOT/(name+'.intent.json'); result=ROOT/(name+'.receipt.json')
 assert not intent.exists(),'Already attempted: recover receipt; no replay'
 record=dict(item,at=dt.datetime.now(dt.timezone.utc).isoformat(),preregistration='6bcffa9395016764c854315a4001512b646d3293',max_bytes=262144,max_seconds=15,retries=0)
 intent.write_text(json.dumps(record))
 t=time.monotonic();cpu=time.process_time(); body=b'';record.update(status=None,error=None)
 try:
  signal.alarm(15)
  with opener.open(urllib.request.Request(item['url'],headers={'User-Agent':'QuantTrade personal research'}),timeout=15) as r:
   record.update(status=r.status,headers={k:v for k,v in r.headers.items() if k.lower() in ['date','last-modified','etag','content-type','content-length','location']})
   if r.status!=200:raise ValueError('Non-200')
   body=r.read(262144)
   if len(body)>=262144:raise ValueError('Payload ceiling; do not retry')
 except urllib.error.HTTPError as e:record.update(status=e.code,error=str(e))
 except Exception as e:record['error']=str(e)
 finally:signal.alarm(0)
 record.update(payload_bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),wall_seconds=time.monotonic()-t,cpu_seconds=time.process_time()-cpu,paid_usd=0)
 (ROOT/(name+'.csv')).write_bytes(body);result.write_text(json.dumps(record,indent=2))
 print(json.dumps(record),flush=True)
 if record['error']:sys.exit(2)
