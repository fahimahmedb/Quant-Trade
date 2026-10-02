"""Engine self-checks: (1) cr_all equals a direct trade-level two-way CR (spec 8.1) at every block length;
(2) exact thresholds: P(y=1)=p for Gaussian and two-state latent laws; (3) persistent shapes have unit variance and the
declared autocorrelation; (4) timing."""
import math, time
import numpy as np
from collections import defaultdict
import astra_c3_engine as E

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

# (5) equivalence with Astra's cycle-2 engine (same seeds): c3 'old' (1.70/1.60) counts == m2 'new' counts, gate go2 == m2 go_check
import sys, importlib.util, os
sp = importlib.util.spec_from_file_location('m2', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'astra_d4_c3_m2_recheck_2026-10-01', 'astra_m2_engine.py'))
M2 = importlib.util.module_from_spec(sp); sp.loader.exec_module(M2)
for g in (dict(pr='fav', comps=(('box', 30, 0.10),), P=30, lay='run', cap='full', th=0.10),
          dict(pr='mid', comps=(('ar', 0.9, 0.05),), cap='thin', th=0.0),
          dict(pr='favmix', comps=(('mk', 0.9, 0.10),), P=30, lay='rand', cap='thin', th=0.10, m=35)):
    gg = dict(g); gg['gate'] = 'go2'
    a = E.run_chunk(gg, 300, [5, 6, 7]); b = M2.run_chunk(g, 300, [5, 6, 7])
    assert a['reach'] == b['reach'], (a['reach'], b['reach'])
    for k in ('miss', 'fpos', 't2', 'uwmiss', 'T1a', 'NEG', 'T1a_null', 'NEG_null'):
        assert a['old'][k] == b['new'][k], (k, a['old'][k], b['new'][k])
print('equivalence with cycle-2 engine (same seeds): OK')
# gate arithmetic: theta_PCE new = ceil(100*7.2*SE0)/100 >= old; go3 implies go2
rng = np.random.default_rng(3)
nvio = 0
for _ in range(2000):
    n = int(rng.integers(50, 600)); st = rng.integers(0, 48, n)
    c = E.prices(rng, ['mid', 'fav', 'favmix', 'pm89', 'fav85', 'tail1', 'wide', 'low'][int(rng.integers(0, 8))], n)
    d = E.design_stats(c, np.where(rng.random(n) < .5, 50.0, rng.uniform(5, 25, n)), st, 48)
    if d is None: continue
    assert d['pce_new'] >= d['pce_old']
    nvio += int(E.gate('go3', d) and not E.gate('go2', d))
print('go3 admits a design that go2 rejects (count over 2000 random designs):', nvio)
