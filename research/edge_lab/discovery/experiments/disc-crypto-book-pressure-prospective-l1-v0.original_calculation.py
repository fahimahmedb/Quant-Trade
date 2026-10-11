import datetime as dt,json,math,statistics,hashlib,time
from pathlib import Path
from quant.edge_lab.remote import GitAuthority
r=Path.cwd();a=GitAuthority(r,r/'research/edge_lab');snap=a.snapshot();assert not snap['control']['paused'];p=Path('/workspace/scratch/discovery-v4-20261011/book');out=r/'research/edge_lab/discovery/experiments/disc-crypto-book-pressure-prospective-l1-v0.result.json'
assert not out.exists()
with (p/'calculation.intent.json').open('x') as f:json.dump({'at':dt.datetime.now(dt.timezone.utc).isoformat(),'head':snap['sha'],'no_result_exists':True},f)
t=time.monotonic();cpu=time.process_time()
def utc(x):return dt.datetime.fromisoformat(x.replace('Z','+00:00'))
quotes=[];receipts=[]
for f in sorted(p.glob('*.receipt.json')):
 rec=json.loads(f.read_text());receipts.append(rec);i=rec['slot'];bad=[];q={}
 try:
  raw=(p/f'{i:02}.body.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==rec['sha256'];row=json.loads(raw)[0]
  q={k:float(row[k]) for k in ['bidPrice','askPrice','bidSize','askSize']};q['time']=utc(row['timestamp']);q['receipt']=utc(rec['receive_utc']);q['slot']=i
  if not all(math.isfinite(q[k]) and q[k]>0 for k in ['bidPrice','askPrice','bidSize','askSize']):bad.append('nonpositive/invalid quote')
  if q['bidPrice']>q['askPrice']:bad.append('crossed quote')
  q['age_seconds']=(q['receipt']-q['time']).total_seconds()
  if not -1<=q['age_seconds']<=10:bad.append('stale/future quote')
 except Exception as e:bad.append('schema/integrity:'+str(e))
 q['invalid']=bad;quotes.append(q)
rows=[]
for i in range(1,len(quotes)-1):
 sig,en,ex=quotes[i-1:i+2];invalid=list(sig['invalid']+en['invalid']+ex['invalid'])
 if not invalid:
  for x,y in [(sig,en),(en,ex)]:
   if not 1<=(y['time']-x['time']).total_seconds()<=12:invalid.append('timestamp gap/duplicate')
  if any(en['time']<en['time'].replace(hour=h,minute=0,second=0,microsecond=0)<=ex['time'] for h in [0,8,16]):invalid.append('funding boundary')
 d={'entry_slot':i,'invalid':sorted(set(invalid))}
 if not invalid:
  imbalance=(sig['bidSize']-sig['askSize'])/(sig['bidSize']+sig['askSize']);direction=(imbalance>0)-(imbalance<0)
  if not direction:d['invalid']=['zero-signal abstention']
  else:
   mid=(en['bidPrice']+en['askPrice'])/2;endmid=(ex['bidPrice']+ex['askPrice'])/2
   gross=(ex['bidPrice']-en['askPrice'])/mid*10000 if direction>0 else (en['bidPrice']-ex['askPrice'])/mid*10000
   d.update(direction=direction,imbalance=imbalance,gross_crossing_bps=gross,central_net_bps=gross-11,stress_net_bps=gross-21,oracle_before_spread_bps=abs(endmid-mid)/mid*10000,oracle_central_net_bps=abs(endmid-mid)/mid*10000-11)
 rows.append(d)
valid=[x for x in rows if not x['invalid']];span=(quotes[-1]['time']-quotes[0]['time']).total_seconds() if all('time' in q for q in quotes) and quotes else None
adequate=len(valid)>=12 and span is not None and span>=60;decision='PARK';stats=None;reason='predeclared quote/sample adequacy failed'
if adequate:
 vals=[x['central_net_bps'] for x in valid];gross=[x['gross_crossing_bps'] for x in valid];mid=len(vals)//2
 stats={'mean_gross_crossing_bps':statistics.mean(gross),'mean_central_net_bps':statistics.mean(vals),'mean_stress_net_bps':statistics.mean(x['stress_net_bps'] for x in valid),'median_central_net_bps':statistics.median(vals),'worst_central_net_bps':min(vals),'best_central_net_bps':max(vals),'positive_central_trades':sum(x>0 for x in vals),'maximum_favorable_oracle_net_bps':max(x['oracle_central_net_bps'] for x in valid),'chronological_half_means_bps':[statistics.mean(vals[:mid]),statistics.mean(vals[mid:])]}
 if stats['maximum_favorable_oracle_net_bps']<=0 or stats['mean_central_net_bps']<=0:decision='KILL';reason='exact expression fails central costs in observed regime; see oracle and small-sample limits'
 elif stats['mean_central_net_bps']>=5 and stats['mean_stress_net_bps']>0 and min(stats['chronological_half_means_bps'])>0:decision='PROMOTE';reason='fixed coarse threshold passed; needs distinct prospective replication'
 else:reason='mixed/weak relative to fixed promotion threshold'
result={'experiment_id':'disc-crypto-book-pressure-prospective-l1-v0','label':'EXPLORATORY','decision':decision,'completed_at':dt.datetime.now(dt.timezone.utc).isoformat(),'predeclaration_commit':'6b9daadaf6a5bf10b3b7356c2740080961add095','receipts':receipts,'quote_count':len(quotes),'valid_trades':len(valid),'planned_trades':19,'quote_span_seconds':span,'quote_quality':[{'slot':q.get('slot'),'source_timestamp':q.get('time').isoformat() if q.get('time') else None,'age_seconds':q.get('age_seconds'),'invalid':q['invalid']} for q in quotes],'intervals':rows,'adequacy_passed':adequate,'economic_test_completed':adequate,'statistics':stats,'reason':reason,'raw_cache_private':str(p),'capture_cost':json.load(open(p/'capture.completion.json')),'compute_cost':{'wall_seconds':time.monotonic()-t,'cpu_seconds':time.process_time()-cpu,'paid_usd':0,'tokens':None,'global_bill':None},'verdict':{'RESULT':decision+': '+reason,'EFFECT_SIZE':stats if stats else 'NOT_ESTIMABLE under declared data gate','UNCERTAINTY':'19 overlapping lagged intervals in one short Sunday regime; highly dependent, no confidence/significance or long-run expectancy inference.','POWER_LIMITATION':'A coarse cost falsifier, not a broad microstructure or profitability study. REST reception cannot authenticate execution.','ECONOMIC_SIGNIFICANCE':'Only the fixed fast taker expression under assumed11/21bp fee+slippage and observed crossing; no capital return/alpha.','FAILED_CRITERIA':reason,'LESSON':'Use favorable cost bounds to assess whether short-horizon information can plausibly pay; stale/cached quotes cannot demonstrate price response.','FAMILY_STATUS':decision+' exact sampled expression only; parent book-pressure mechanism not generally closed.','NEXT_DECISION':'Stop this pass after3 data-test attempts. Preserve original results and private raws. No replay/retune; policy remains deferred until2026-10-13T12:45Z; seek a distinct cheap verified data route next.'}}
with out.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['decision','quote_count','valid_trades','quote_span_seconds','adequacy_passed','statistics','reason']},ensure_ascii=False))
