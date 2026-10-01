"""Re-derive lambda_theta / lambda_kappa from the Architect's committed run-H raw output with the declared criterion
(<= 0.040 joint L_W miss, false positive, U_W miss in every in-class cell; <= 0.020 T1a / NEG in every theta = 0 cell),
and list worst cells. In-class = every plan except 'outside', excluding the astra phi 0.95 cell; NO_GO cells have no counts."""
import json, sys
src = sys.argv[1]
rows = [json.loads(l) for l in open(src)]
inc = []
for r in rows:
    g = r['g']
    if r['plan'] == 'outside':
        continue
    if g.get('pk') in ('ar', 'hemi', 'stn', 'mk') and g.get('pp', 0) > 0.9:
        continue
    if r.get('empty'):
        continue
    inc.append(r)
print('rows', len(rows), 'in-class reached cells', len(inc))
grid = inc[0]['grid']
def worst(key, cond=lambda r: True):
    out = []
    for i, lam in enumerate(grid):
        w = max(((r['by_lam'][key][i] / r['reps']), r['plan'], r['idx']) for r in inc if cond(r))
        out.append((lam, w))
    return out
th0 = lambda r: r['g']['th'] == 0.0
W = {k: worst(k) for k in ('miss', 'fpos', 'uw_miss')}
K = {k: worst(k, th0) for k in ('T1a_null', 'NEG_null')}
lt = next(lam for i, lam in enumerate(grid) if all(W[k][i][1][0] <= 0.040 for k in W))
lk = next(lam for i, lam in enumerate(grid) if all(K[k][i][1][0] <= 0.020 for k in K))
print('lambda_theta =', lt, ' lambda_kappa =', lk)
for lam in (1.0, 1.6, 1.65, 1.7, 1.75):
    i = grid.index(lam)
    print('lam %.2f' % lam, {k: (round(W[k][i][1][0], 4), W[k][i][1][1], W[k][i][1][2]) for k in W},
          {k: (round(K[k][i][1][0], 4), K[k][i][1][1], K[k][i][1][2]) for k in K})
# max given reach (reach >= 0.10) at the frozen lambdas
it, ik = grid.index(1.7), grid.index(1.6)
cond = [(r['by_lam']['miss'][it] / r['reach']['k'], r['reach']['p'], r['plan'], r['idx']) for r in inc if r['reach']['p'] >= 0.10]
print('max L_W miss given reach (reach>=0.10):', max(cond))
