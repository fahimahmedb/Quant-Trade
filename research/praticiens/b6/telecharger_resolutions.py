import duckdb, subprocess, json, concurrent.futures as cf, time
con=duckdb.connect()
ids=[r[0] for r in con.execute("SELECT condition_id FROM 'hourly_markets.parquet' WHERE end_date>='2026-04-01'").fetchall()]
batches=[ids[i:i+40] for i in range(0,len(ids),40)]
def get(b):
    q='&'.join('condition_ids='+c for c in b)
    for a in range(4):
        out=subprocess.run(['curl','-sS','--max-time','60',f"https://gamma-api.polymarket.com/markets?{q}&limit=100&closed=true"],capture_output=True,text=True).stdout
        try:
            d=json.loads(out); return {x['conditionId']:{'op':x.get('outcomePrices'),'closed':x.get('closed'),'uma':x.get('umaResolutionStatus'),'outcomes':x.get('outcomes')} for x in d}
        except Exception: time.sleep(2*(a+1))
    return {}
res={}
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(get,batches): res.update(r)
json.dump(res,open('resolutions_gamma.json','w'))
print('demandés',len(ids),'reçus',len(res))
