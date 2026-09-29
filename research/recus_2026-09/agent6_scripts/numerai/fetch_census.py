# Census of per-model stake/payout per resolved round via roundDetails (public, unauthenticated)
import json, time, os, datetime as dt
from q import q
Q='{ roundDetails(tournament: %d, roundNumber: %d) { roundNumber openTime payoutFactor roundResolved status totalAtStake totalBurned totalEarned totalPayout totalStakes totalSubmitted roundTarget payoutMultipliers { displayName multiplier } models { modelName id selectedStakeValue payoutSettled payoutPending } } }'
def window(t):
    rs=json.load(open('rounds_%d.json'%t))
    res=[r for r in rs if r['resolvedStaking']]
    last=max(res,key=lambda r:r['number'])
    end=dt.datetime.fromisoformat(last['openTime'].replace('Z','+00:00'))
    start=end-dt.timedelta(days=180)
    return sorted(r['number'] for r in res if dt.datetime.fromisoformat(r['openTime'].replace('Z','+00:00'))>=start)
log=open('fetch_log.txt','a')
for t in (8,11):
    w=window(t); print(t,len(w),w[0],w[-1],file=log,flush=True)
    for n in w:
        fn='rounds/t%d_r%d.json'%(t,n)
        if os.path.exists(fn): continue
        for attempt in range(3):
            try:
                d=q(Q%(t,n))
                if 'errors' in d: raise Exception(json.dumps(d['errors'])[:300])
                rd=d['data']['roundDetails']
                rd['models']=[m for m in rd['models'] if (m['selectedStakeValue'] and float(m['selectedStakeValue'])!=0) or (m['payoutSettled'] and float(m['payoutSettled'])!=0) or (m['payoutPending'] and float(m['payoutPending'])!=0)]
                json.dump(rd,open(fn,'w'))
                print('ok',t,n,len(rd['models']),file=log,flush=True)
                break
            except Exception as e:
                print('ERR',t,n,attempt,repr(e)[:300],file=log,flush=True); time.sleep(3)
        time.sleep(0.3)
print('DONE',file=log,flush=True)
