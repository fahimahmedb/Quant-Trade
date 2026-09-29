import json, math, statistics as st, collections, random
random.seed(11)
d = json.load(open('wx_nyc_lon.json'))
A = ['Dm1_12', 'D_00', 'D_09', 'D_15']
ev = []
for e in d:
    rows = e['rows']
    if sum(r['won'] for r in rows) != 1:
        continue
    ev.append(e)
print('usable events', len(ev), 'of', len(d))

def metrics(e, a):
    rs = [r for r in e['rows'] if r['p'][a] is not None]
    if len(rs) < len(e['rows']) - 1 or not rs:
        return None
    s = sum(r['p'][a] for r in rs)
    if s <= 0:
        return None
    w = [r for r in rs if r['won']]
    if not w:
        return None
    pw = w[0]['p'][a]
    brier = sum(((r['p'][a] / s) - (1 if r['won'] else 0)) ** 2 for r in rs)
    fav = max(rs, key=lambda r: r['p'][a])
    pf = fav['p'][a]
    ret = None
    if 0.02 < pf < 0.995:
        ret = (1 if fav['won'] else 0) / (pf + 0.05 * pf * (1 - pf)) - 1
    return pw, brier, fav['won'], ret, len(e['rows'])

g = collections.defaultdict(list)
for e in ev:
    ym = e['date'][:7]
    g[(e['city'], ym)].append(e)
print('\ncity month | n | nbuckets med | vol med | winner median Dm1_12/D_00/D_09/D_15 | brier D_00 | fav=win D_00')
for k in sorted(g):
    L = g[k]
    row = []
    for a in A:
        v = [m[0] for m in (metrics(e, a) for e in L) if m]
        row.append('%.2f' % st.median(v) if v else ' na ')
    br = [m[1] for m in (metrics(e, 'D_00') for e in L) if m]
    fw = [m[2] for m in (metrics(e, 'D_00') for e in L) if m]
    print(k[0], k[1], len(L), st.median(len(e['rows']) for e in L), '%.0fk' % (st.median(e['vol'] for e in L) / 1e3), '/'.join(row),
          '%.3f' % st.median(br) if br else 'na', '%.0f%%' % (100 * sum(fw) / len(fw)) if fw else 'na')

# year-over-year same months Feb..Sep
print('\nYoY same months (Feb-Sep), per city and anchor: median winner price 2025 vs 2026, mean brier, fav hit, fav return')
for city in ('NYC', 'London'):
    for a in A:
        res = {}
        for yr in ('2025', '2026'):
            L = [e for e in ev if e['city'] == city and e['date'][:4] == yr and '02' <= e['date'][5:7] <= '09']
            M = [m for m in (metrics(e, a) for e in L) if m]
            if not M:
                res[yr] = None; continue
            R = [m[3] for m in M if m[3] is not None]
            bs = sorted(st.mean(random.choices(R, k=len(R))) for _ in range(1000)) if R else [0] * 1000
            res[yr] = (len(M), st.median(m[0] for m in M), st.mean(m[1] for m in M), sum(m[2] for m in M) / len(M), st.mean(R) if R else float('nan'), bs[25], bs[974])
        s = city + ' ' + a
        for yr in ('2025', '2026'):
            r = res[yr]
            if r:
                s += ' | %s n=%d win_med=%.2f brier=%.3f favhit=%.0f%% favret=%.3f [%.3f,%.3f]' % (yr, r[0], r[1], r[2], 100 * r[3], r[4], r[5], r[6])
        print(s)

# quarterly fav return at D_00 all events
print('\nQuarterly favourite return at D_00 and Dm1_12 (both cities)')
q = collections.defaultdict(list)
for e in ev:
    y, m = e['date'][:4], int(e['date'][5:7])
    q[f'{y}Q{(m - 1) // 3 + 1}'].append(e)
for k in sorted(q):
    for a in ('Dm1_12', 'D_00'):
        R = [m[3] for m in (metrics(e, a) for e in q[k]) if m and m[3] is not None]
        if len(R) < 10:
            continue
        bs = sorted(st.mean(random.choices(R, k=len(R))) for _ in range(1000))
        print(k, a, 'n', len(R), 'fav ret %.3f [%.3f,%.3f]' % (st.mean(R), bs[25], bs[974]))

# bucket-level calibration error (ECE) at D 00:00 local, 7 price bins
bins = [0, 0.05, 0.15, 0.3, 0.5, 0.7, 0.9, 1.0001]
print('\nquarter | n buckets | ECE at D_00 | per-bin mean price:hit rate(n)')
qq = collections.defaultdict(list)
for e in d:
    y, m = e['date'][:4], int(e['date'][5:7])
    for r in e['rows']:
        if r['p']['D_00'] is not None:
            qq[f'{y}Q{(m - 1) // 3 + 1}'].append((r['p']['D_00'], 1 if r['won'] else 0))
for k in sorted(qq):
    Lq = qq[k]; ece = 0; parts = []
    for i in range(len(bins) - 1):
        B = [x for x in Lq if bins[i] <= x[0] < bins[i + 1]]
        if not B:
            continue
        mp = st.mean(x[0] for x in B); hr = st.mean(x[1] for x in B)
        ece += len(B) / len(Lq) * abs(mp - hr); parts.append('%.2f:%.2f(%d)' % (mp, hr, len(B)))
    print(k, len(Lq), '%.3f' % ece, ' '.join(parts))
