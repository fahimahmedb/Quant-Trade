"""B6 historical diagnostic — protocol frozen in commit 0389c1c (P7-B6 amended_before_data)."""
import duckdb, json, glob, re, math, os, statistics as st, collections, datetime as dt, sys
sys.path.insert(0, '/home/user/Quant-Trade/src')
from quant.factory.evaluate import required_t_statistic
N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
con = duckdb.connect()
RES = json.load(open('resolutions_gamma.json'))
mk = con.execute("SELECT question, condition_id, token1, token2, answer1, outcome_prices, end_date, event_id FROM 'hourly_markets.parquet' WHERE end_date>='2026-04-01'").fetchall()
# spot: minute close keyed by close-time (s)
spot = {}
for f in glob.glob('klines/*.csv'):
    sym = 'BTC' if 'BTC' in f else 'ETH'
    for line in open(f):
        c = line.split(',')
        ot = int(c[0]); ot = ot // 1000 if ot > 1e14 else ot   # micro -> ms
        spot[(sym, ot // 1000 + 60)] = float(c[4])
dvol = {c: {int(p[0]) // 1000: p[4] for p in json.load(open(f'dvol_{c}.json'))} for c in ('BTC', 'ETH')}
trades = collections.defaultdict(list); trunc = 0
for f in glob.glob('trades/*.json'):
    d = json.load(open(f)); trunc += bool(d.get('_truncated'))
    for t in d['data']:
        trades[t['token_id']].append((t['timestamp'], t.get('transaction_hash') or '', float(t['price'])))
tau = 3600 / (365 * 24 * 3600)
rows = []; skipped = collections.Counter()
for q, cid, tok1, tok2, ans1, op, end, ev in mk:
    asset = 'BTC' if q.startswith('Bitcoin') else 'ETH'
    K = float(re.search(r'above ([\d,]+) on', q).group(1).replace(',', ''))
    g = RES.get(cid)
    if not g or not g['op'] or not g['closed']:
        skipped['unresolved'] += 1; continue
    o = [float(x) for x in json.loads(g['op'])]; names = json.loads(g['outcomes'])
    if sorted(o) != [0.0, 1.0]:
        skipped['unresolved'] += 1; continue
    yes_tok, no_tok = (tok1, tok2) if ans1 == 'Yes' else (tok2, tok1)
    yes_won = o[names.index('Yes')] == 1.0
    t0 = int(end.timestamp()) - 3600
    S0 = spot.get((asset, t0)); vol = dvol[asset].get(t0 - 3600)
    if S0 is None or vol is None:
        skipped['no_spot_or_dvol'] += 1; continue
    s = vol / 100
    d2 = (math.log(S0 / K) - s * s * tau / 2) / (s * math.sqrt(tau)); pstar = N(d2)
    for side, tok, fair, won in (('YES', yes_tok, pstar, yes_won), ('NO', no_tok, 1 - pstar, not yes_won)):
        w = sorted(x for x in trades.get(tok, []) if t0 <= x[0] <= t0 + 300)
        if not w:
            continue
        price = w[0][2]; fee = 0.07 * price * (1 - price)
        rows.append(dict(asset=asset, cluster=(asset, t0), side=side, price=price, fair=fair,
                         take=price + fee < fair, pnl=((1.0 if won else 0.0) - price - fee) / (price + fee),
                         brier_mkt=(price - (1.0 if won else 0.0)) ** 2, brier_fair=(fair - (1.0 if won else 0.0)) ** 2))
def tstat(sel):
    by = collections.defaultdict(list)
    for r in sel: by[r['cluster']].append(r['pnl'])
    m = [st.mean(v) for v in by.values()]
    if len(m) < 3: return len(sel), len(m), float('nan'), float('nan')
    return len(sel), len(m), st.mean(m), st.mean(m) / (st.stdev(m) / math.sqrt(len(m)))
req = required_t_statistic(2)
out = {'required_t_2_trials': round(req, 3), 'truncated_events': trunc, 'skipped': dict(skipped),
       'fill_sides_in_window': len(rows)}
for name, filt in (('A', lambda r: True), ('B', lambda r: 0.15 <= r['price'] <= 0.85)):
    sel = [r for r in rows if r['take'] and filt(r)]
    res = {'all': tstat(sel)}
    for a in ('BTC', 'ETH'):
        res[a] = tstat([r for r in sel if r['asset'] == a])
    out[name] = {k: {'trades': v[0], 'clusters': v[1], 'mean_pnl_per_$': round(v[2], 4), 't': round(v[3], 2)} for k, v in res.items()}
cal = [r for r in rows]
out['secondary_brier'] = {'n': len(cal), 'market_fill_price': round(st.mean(r['brier_mkt'] for r in cal), 4),
                          'p_star': round(st.mean(r['brier_fair'] for r in cal), 4)}
m, t = out['A']['all']['mean_pnl_per_$'], out['A']['all']['t']
same = all(out['A'][a]['mean_pnl_per_$'] * m > 0 for a in ('BTC', 'ETH'))
out['verdict'] = ('REJECT' if (m < 0 and t <= -1.96) else
                  'CANDIDATE' if (t >= req and same) else 'INCONCLUSIVE -> forward SHADOW_DIRECT')
json.dump(out, open('result_b6_historique.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
