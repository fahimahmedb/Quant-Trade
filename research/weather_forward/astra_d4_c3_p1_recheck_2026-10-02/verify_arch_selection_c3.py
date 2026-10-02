"""Re-derive lambda_theta / lambda_kappa from the Architect's committed run-J M3 raw output with the DECLARED criterion
(0364042 declaration: lambda_theta = smallest GRID3 value >= 1.70 with, in every new-law cell, P(reach & L_W miss), P(reach & false pos),
P(reach & U_W miss) <= 0.040; lambda_kappa = smallest >= 1.60 with T1a/NEG false rejection <= 0.020 in every theta = 0 cell).
This reads the Architect's committed numbers only to re-do the selection arithmetic (not for any verdict on levels)."""
import json, sys, collections
src = sys.argv[1]
rows_all = [json.loads(l) for l in open(src)]
rows = [r for r in rows_all if r['plan'] in ('m3_class','m3_mix','m3_m35','m3_geo','m3_astra')]   # declared selection class (probe laws / addendum excluded)
print('rows', len(rows), collections.Counter(r['plan'] for r in rows))
grid = rows[0]['grid']
def worst(key, cond=lambda r: True):
    out = []
    for i, lam in enumerate(grid):
        out.append(max(((r['by_lam'][key][i] / r['reps']), r['plan'], r['idx']) for r in rows if cond(r)))
    return out
th0 = lambda r: r['g']['th'] == 0.0
W = {k: worst(k) for k in ('miss', 'fpos', 'uw_miss')}
K = {k: worst(k, th0) for k in ('T1a_null', 'NEG_null')}
lt = next(l for i, l in enumerate(grid) if all(W[k][i][0] <= 0.040 for k in W))
lk = next(l for i, l in enumerate(grid) if all(K[k][i][0] <= 0.020 for k in K))
print('lambda_theta =', lt, ' lambda_kappa =', lk)
for lam in (1.70, 1.75, 2.0, 2.05, 2.10, 2.15, 2.20):
    i = grid.index(lam)
    print('lam %.2f' % lam, {k: (round(W[k][i][0], 4), W[k][i][1], W[k][i][2]) for k in W},
          {k: (round(K[k][i][0], 4), K[k][i][1], K[k][i][2]) for k in K})
for lam in (1.60, 1.65, 1.70, 1.75, 1.80):
    i = grid.index(lam)
    print('kappa lam %.2f' % lam, {k: (round(K[k][i][0], 4), K[k][i][1], K[k][i][2]) for k in K})
