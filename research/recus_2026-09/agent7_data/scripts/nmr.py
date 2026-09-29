import requests,json,time,concurrent.futures as cf
URL='https://api-tournament.numer.ai/'
Q='{ roundDetails(tournament: 8, roundNumber: %d) { roundNumber openTime payoutFactor roundResolved totalAtStake totalPayout payoutMultipliers { displayName multiplier } } }'
def f(n):
    for i in range(3):
        try:
            d=requests.post(URL,json={'query':Q%n},timeout=60).json()
            return d['data']['roundDetails']
        except Exception: time.sleep(2)
with cf.ThreadPoolExecutor(6) as ex:
    R=[r for r in ex.map(f,range(250,1375,5)) if r]
json.dump(R,open('nmr_rounds.json','w'))
import collections
g=collections.defaultdict(list)
for r in R:
    if not r.get('totalAtStake'): continue
    q=r['openTime'][:4]+'H'+('1' if int(r['openTime'][5:7])<=6 else '2')
    y=(float(r['totalPayout'] or 0)/float(r['totalAtStake'])) if r.get('roundResolved') else None
    g[q].append((r['roundNumber'],float(r['payoutFactor'] or 0),float(r['totalAtStake']),y,json.dumps([(m['displayName'],m['multiplier']) for m in (r.get('payoutMultipliers') or [])])))
for k in sorted(g):
    L=g[k]; ys=[x[3] for x in L if x[3] is not None]
    import statistics as st
    print(k,'rounds',L[0][0],'-',L[-1][0],'n',len(L),'pf med %.3f'%st.median(x[1] for x in L),'stake med %.0fk'%(st.median(x[2] for x in L)/1e3),
          'payout/stake per round mean %.3f%%'%(100*st.mean(ys)) if ys else 'unresolved','mult',L[-1][4])
