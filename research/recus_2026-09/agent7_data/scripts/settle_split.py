import json, glob, statistics as st
R = {}
for f in glob.glob('settle_res2_*.json'):
    R.update(json.load(open(f)))
print('samples', sorted(R))
out = {}
for k in sorted(R):
    M = R[k]
    fills = [(fl, m) for m in M for fl in m['fills']]

    def agg(sel):
        n = 0; notl = 0; g = 0; l = 0; losers = 0; buyers = set(); holds = []
        for (ts, p, s, won, w, side), m in fills:
            if not sel(p):
                continue
            n += 1; notl += p * s
            if won:
                g += (1 - p) * s; holds.append((m['ct'] - ts) / 3600)
            else:
                l += p * s; losers += 1
            buyers.add(w)
        return n, notl, g, l, losers, len(buyers), (st.median(holds) if holds else None)

    a = agg(lambda p: p >= 0.999)
    b = agg(lambda p: 0.995 <= p < 0.999)
    mk = sum(1 for m in M if any(fl[1] >= 0.999 for fl in m['fills']))
    out[k] = {'n_markets': len(M), 'markets_with_0999': mk, 'p0999': a, 'p0995_0998': b}
    print(k, 'mkts', len(M), 'with>=.999', mk,
          '| >=0.999: fills %d notional %.0f gross %.0f loss %.0f net %.3f%% losers %d distinct takers %d med hold %.2fh' % (
              a[0], a[1], a[2], a[3], 100 * (a[2] - a[3]) / max(a[1], 1), a[4], a[5], a[6] or -1),
          '| 0.995-0.998: notional %.0f net %.3f%% losers %d' % (b[1], 100 * (b[2] - b[3]) / max(b[1], 1), b[4]))
for name, key in (('>=0.999', 'p0999'), ('0.995-0.998', 'p0995_0998')):
    tot = [sum(out[k][key][i] for k in out) for i in range(5)]
    print('ALL', name, 'notional %.0f gross %.0f loss %.0f net %.4f%% losing fills %d' % (
        tot[1], tot[2], tot[3], 100 * (tot[2] - tot[3]) / tot[1], tot[4]))
json.dump(out, open('settle_summary.json', 'w'))
