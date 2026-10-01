"""Engine self-checks: (1) cr_all equals a direct trade-level two-way CR (spec 8.1) at every block length;
(2) exact thresholds: P(y=1)=p for Gaussian and two-state latent laws; (3) persistent shapes have unit variance and the
declared autocorrelation; (4) timing."""
import math, time
import numpy as np
from collections import defaultdict
import astra_m2_engine as E

rng = np.random.default_rng(1)
T, S = 157, 48
n = 3000
day = np.sort(rng.integers(0, T, n)); st = rng.integers(0, S, n); r = rng.standard_normal(n); Q = 1234.5
cr = E.cr_all(day, st, r, T, S, Q)
for b in E.BL:
    def V(keys):
        d = defaultdict(float)
        for k, x in zip(keys, r):
            d[k] += x
        G = len(d)
        return G / (G - 1) * sum(v * v for v in d.values()) / Q ** 2, G
    VB, GB = V(list(day // b)); VS, GS = V(list(st)); VBS, _ = V(list(zip(day // b, st)))
    se = math.sqrt(max(VB, VS, VB + VS - VBS))
    assert abs(se - cr[b][0]) < 1e-12 * max(1, se), (b, se, cr[b])
    assert cr[b][1] == min(GB, GS) - 1
print('CR direct check OK')
# thresholds
for a in (0.0, math.sqrt(0.05), math.sqrt(0.10)):
    p = np.array([0.03, 0.35, 0.7, 0.9, 0.99])
    q = E.mk_quantile(p, a) if a > 0 else E.ndtri(p)
    sg = math.sqrt(1 - a * a)
    F = 0.5 * E.ndtr((q - a) / sg) + 0.5 * E.ndtr((q + a) / sg)
    assert np.max(np.abs(F - p)) < 1e-10, (a, F - p)
print('threshold check OK')
# shapes
for comp in (('ar', 0.9, 0.1), ('mk', 0.9, 0.1), ('box', 30, 0.1)):
    xs = np.array([E.comp_path(rng, comp, 400, S)[0] for _ in range(400)])
    v = xs.var()
    ac5 = np.mean(xs[:, 5:] * xs[:, :-5]) / v
    exp = 0.9 ** 5 if comp[0] != 'box' else 1 - 5 / 30
    print(comp, 'var %.3f acf5 %.3f expected %.3f' % (v, ac5, exp))
t = time.time(); out = E.run_chunk(dict(pr='fav', comps=(('box', 30, 0.10),), P=30, lay='run', cap='full', th=0.10), 400, [1, 2, 3])
print('400 reps: %.1fs reach %d' % (time.time() - t, out['reach']))
