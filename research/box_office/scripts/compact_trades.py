"""Compact trades_u.json.gz to the replay window (Thu 00:00 ET-1d .. Tue) as arrays [ts, side(1=BUY,-1=SELL), outcomeIndex, price, size]."""
import json,gzip,datetime as dt
T=json.load(gzip.open('trades_u.json.gz','rt'))
U=json.load(gzip.open('universe_raw.json.gz','rt'))
c2w={b['cond']:r['wk_start'] for r in U for b in r['brackets'] if r['wk_start']}
out={}
for c,v in T.items():
    F=dt.datetime.fromisoformat(c2w[c]+'T00:00:00+00:00')
    lo=(F-dt.timedelta(days=2)).timestamp(); hi=(F+dt.timedelta(days=5)).timestamp()
    out[c]={'truncated':bool(v and 'TRUNCATED' in v[-1]),'n_all':len([t for t in v if 'TRUNCATED' not in t]),
            't':sorted([[t['timestamp'],1 if t['side']=='BUY' else -1,t['outcomeIndex'],t['price'],round(t['size'],4)] for t in v if 'TRUNCATED' not in t and lo<=t['timestamp']<=hi])}
json.dump(out,gzip.open('trades_window.json.gz','wt'),separators=(',',':'))
print(sum(len(x['t']) for x in out.values()))
