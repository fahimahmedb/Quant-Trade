# M5 settlement-liquidity sampler. Usage: python3 settle_sample.py 2025-01 2025-04 ... (sample names from SAMPLES)
import json,urllib.request,time,datetime as dt,concurrent.futures as cf,random,re
def get(u,tries=5):
    for i in range(tries):
        try:
            r=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}); return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception: time.sleep(1.5+i)
    return None
SAMPLES=[('2025-01',dt.date(2025,1,13)),('2025-04',dt.date(2025,4,14)),('2025-07',dt.date(2025,7,14)),('2025-10',dt.date(2025,10,13)),
         ('2026-01',dt.date(2026,1,12)),('2026-04',dt.date(2026,4,13)),('2026-07',dt.date(2026,7,13)),('2026-09',dt.date(2026,9,21))]
random.seed(20260929)
def markets(d0):
    out=[];off=0
    while off<1500:
        d=get(f"https://gamma-api.polymarket.com/markets?closed=true&limit=100&offset={off}&end_date_min={d0}T00:00:00Z&end_date_max={d0+dt.timedelta(days=3)}T00:00:00Z&volume_num_min=1000")
        if not d: break
        out+=d; off+=100
        if len(d)<100: break
    return out
def ts(s):
    s=s.replace(' ','T').replace('+00','+00:00') if s and '+00:00' not in s else s
    return int(dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
def do(m):
    try:
        op=json.loads(m['outcomePrices']); outs=json.loads(m['outcomes'])
        if sorted(op)!=['0','1']: return None
        win=outs[op.index('1')]
        ct=ts(m['closedTime'])
    except Exception: return None
    trades=[];off=0
    while off<=3000:
        d=get(f"https://data-api.polymarket.com/trades?market={m['conditionId']}&limit=1000&offset={off}")
        if not d: break
        trades+=d
        if min(x['timestamp'] for x in d)<ct-86400 or len(d)<1000: break
        off+=1000
    rec={'fills':[],'slug':m.get('slug'),'q':m['question'][:80],'cat':(m.get('category') or ''),'ct':ct,'n':0,'notional':0,'profit':0,'loss':0,'n999':0,'not999':0,'holds':[],'buckets':{'0.995-0.997':0,'0.997-0.999':0,'0.999':0},'losers':0}
    for x in trades:
        if not (ct-86400<=x['timestamp']<=ct): continue
        p=float(x['price']); s=float(x['size'])
        if p<0.995: continue
        rec['n']+=1; rec['notional']+=p*s
        rec['fills'].append((x['timestamp'],p,s,x['outcome']==win,x.get('proxyWallet'),x.get('side')))
        if x['outcome']==win:
            rec['profit']+=(1-p)*s; rec['holds'].append((ct-x['timestamp'])/3600)
        else:
            rec['loss']+=p*s; rec['losers']+=1
        if p>=0.999: rec['n999']+=1; rec['not999']+=p*s; rec['buckets']['0.999']+=p*s
        elif p>=0.997: rec['buckets']['0.997-0.999']+=p*s
        else: rec['buckets']['0.995-0.997']+=p*s
    return rec
res={}
import sys
for name,d0 in [x for x in SAMPLES if x[0] in sys.argv[1:]]:
    ms=[m for m in markets(d0) if not re.search(r'up or down',m.get('question',''),re.I)]
    random.shuffle(ms); ms=ms[:200]
    with cf.ThreadPoolExecutor(10) as ex: R=[r for r in ex.map(do,ms) if r]
    res[name]=R
    notional=sum(r['notional'] for r in R); prof=sum(r['profit'] for r in R); loss=sum(r['loss'] for r in R)
    import statistics as st
    holds=[h for r in R for h in r['holds']]
    b={k:sum(r['buckets'][k] for r in R) for k in ['0.995-0.997','0.997-0.999','0.999']}
    print(name,'markets',len(ms),'used',len(R),'fills',sum(r['n'] for r in R),'notional %.0f'%notional,'gross %.0f'%prof,'loss %.0f'%loss,'net/notional %.3f%%'%(100*(prof-loss)/max(notional,1)),
          'share@0.999 %.0f%%'%(100*b['0.999']/max(notional,1)),'median hold h %.2f'%(st.median(holds) if holds else -1),'losing fills',sum(r['losers'] for r in R),flush=True)
    json.dump(res,open('settle_res2_%s.json' % '_'.join(sys.argv[1:]),'w'))
