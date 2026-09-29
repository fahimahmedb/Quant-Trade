import duckdb, subprocess, json, os, io, zipfile, datetime as dt, concurrent.futures as cf, time
os.makedirs('trades', exist_ok=True); os.makedirs('klines', exist_ok=True)
con=duckdb.connect()
ev=con.execute("SELECT event_id FROM 'hourly_markets.parquet' WHERE end_date>='2026-04-01' GROUP BY event_id").fetchall()
def get(e):
    p=f'trades/{e[0]}.json'
    if os.path.exists(p): return 0
    for a in range(4):
        out=subprocess.run(['curl','-sS','--max-time','60',f"https://data-api.polymarket.com/v2/trades?event_id={e[0]}&taker_only=true&side=BUY&limit=1000"],capture_output=True,text=True).stdout
        try:
            d=json.loads(out); assert 'data' in d
            if d.get('pagination',{}).get('has_more'): d['_truncated']=True
            json.dump(d,open(p,'w')); return 1
        except Exception: time.sleep(2*(a+1))
    return -1
with cf.ThreadPoolExecutor(8) as ex: r=list(ex.map(get, ev))
print('trades:', r.count(1), 'nouveaux,', r.count(-1), 'échecs')
def kl(args):
    sym, day = args; p=f'klines/{sym}-{day}.csv'
    if os.path.exists(p): return 0
    u=f'https://data.binance.vision/data/spot/daily/klines/{sym}/1m/{sym}-1m-{day}.zip'
    b=subprocess.run(['curl','-sS','--max-time','60',u],capture_output=True).stdout
    try: open(p,'wb').write(zipfile.ZipFile(io.BytesIO(b)).read(f'{sym}-1m-{day}.csv')); return 1
    except Exception: return -1
days=[(dt.date(2026,3,31)+dt.timedelta(i)).isoformat() for i in range(112)]
with cf.ThreadPoolExecutor(8) as ex: r=list(ex.map(kl, [(s,d) for s in ('BTCUSDT','ETHUSDT') for d in days]))
print('klines:', r.count(1), 'nouveaux,', r.count(-1), 'échecs')
for cur in ('BTC','ETH'):
    pts=[]; s=int(dt.datetime(2026,3,31,tzinfo=dt.timezone.utc).timestamp()*1000); e=int(dt.datetime(2026,7,22,tzinfo=dt.timezone.utc).timestamp()*1000)
    while True:
        d=json.loads(subprocess.run(['curl','-sS','--max-time','60',f'https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={cur}&start_timestamp={s}&end_timestamp={e}&resolution=3600'],capture_output=True,text=True).stdout)['result']
        pts+=d['data']
        if not d.get('continuation'): break
        e=d['continuation']
    json.dump(sorted(set(map(tuple,pts))),open(f'dvol_{cur}.json','w')); print(cur,'dvol points',len(set(map(tuple,pts))))
