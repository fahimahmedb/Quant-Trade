import datetime as dt,hashlib,json,signal,time,urllib.request,urllib.error
from pathlib import Path
from quant.edge_lab.remote import GitAuthority
r=Path.cwd();a=GitAuthority(r,r/'research/edge_lab');s=a.snapshot();assert not s['control']['paused'];assert s['sha']=='6b9daadaf6a5bf10b3b7356c2740080961add095'
p=Path('/workspace/scratch/discovery-v4-20261011/book');p.mkdir(exist_ok=True);intent=p/'capture.intent.json'
with intent.open('x') as f:json.dump({'at':dt.datetime.now(dt.timezone.utc).isoformat(),'preregistration':s['sha'],'slots':21,'interval_seconds':5,'max_seconds':120,'retries':0},f)
class NR(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a,**kw):return None
opener=urllib.request.build_opener(NR())
def alarm(*a):raise TimeoutError('120s ceiling')
signal.signal(signal.SIGALRM,alarm);signal.alarm(120);start=time.monotonic();cpu=time.process_time()
url='https://www.bitmex.com/api/v1/quote?symbol=XBTUSD&count=1&reverse=true'
try:
 for i in range(21):
  time.sleep(max(0,start+i*5-time.monotonic()))
  rec={'slot':i,'url':url,'send_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'send_monotonic':time.monotonic(),'status':None,'error':None};b=b''
  with (p/f'{i:02}.intent.json').open('x') as f:json.dump(rec,f)
  try:
   with opener.open(urllib.request.Request(url,headers={'User-Agent':'QuantTrade bounded public research','Cache-Control':'no-cache','Accept':'application/json'}),timeout=3) as response:
    rec['status']=response.status;rec['headers']={k:v for k,v in response.headers.items() if k.lower() in ['date','age','content-type','content-length','x-ratelimit-remaining']};b=response.read(16384)
    if len(b)>=16384:raise ValueError('body limit')
    body=json.loads(b);assert isinstance(body,list) and len(body)==1
    assert all(k in body[0] for k in ['timestamp','bidPrice','askPrice','bidSize','askSize'])
  except urllib.error.HTTPError as e:rec.update(status=e.code,error=str(e))
  except Exception as e:rec['error']=str(e)
  rec.update(receive_utc=dt.datetime.now(dt.timezone.utc).isoformat(),receive_monotonic=time.monotonic(),payload_bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  (p/f'{i:02}.body.json').write_bytes(b);(p/f'{i:02}.receipt.json').write_text(json.dumps(rec,indent=2))
  if rec['error']:print(json.dumps({'stopped_at_slot':i,'error':rec['error'],'status':rec['status']}),flush=True);break
  if i%5==0:print(json.dumps({'saved_slots':i+1,'elapsed_seconds':time.monotonic()-start}),flush=True)
finally:
 signal.alarm(0);(p/'capture.completion.json').write_text(json.dumps({'completed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'paid_usd':0,'tokens':None,'global_bill':None},indent=2))
