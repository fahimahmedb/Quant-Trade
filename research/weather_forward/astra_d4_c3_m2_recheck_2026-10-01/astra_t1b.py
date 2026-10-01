"""ASTRA cycle-2: independent T1b (PINM, spec 8.2 / 8.3) and T1 = T1a u T1b check under persistence (resumable).
SYNTHETIC ONLY.  Sharp null: TAIL p = c; kappa_core = 0 (theta = 0).  PINM: declared copula (0.10, 0.10, 0.10), B draws,
p = (1 + #{W* >= W}) / (B + 1), T1b iff p <= 0.025.  T1a: NEW rule kappa - 1.60 Hk975 > 0 (and OLD 5-date for reference).
Usage: python3 astra_t1b.py REPS B   -> out_t1b_<REPS>_<B>.jsonl
Seeds: SeedSequence([77200201, 20, cell, chunk]).
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.special import ndtri

import astra_m2_engine as E
from astra_m2_run import G, AR, MK, BOX, key


def pinm_p(rng, day, st, c, W, S, B):
    n = c.size
    ud, di = np.unique(day, return_inverse=True)
    us, si = np.unique(st, return_inverse=True)
    uc, ci = np.unique(day * S + st, return_inverse=True)
    q = ndtri(c)
    cnt = 0
    for b0 in range(0, B, 500):
        k = min(500, B - b0)
        Z = (math.sqrt(0.1) * rng.standard_normal((k, ud.size))[:, di] + math.sqrt(0.1) * rng.standard_normal((k, us.size))[:, si]
             + math.sqrt(0.1) * rng.standard_normal((k, uc.size))[:, ci] + math.sqrt(0.7) * rng.standard_normal((k, n)))
        cnt += int(((Z < q).sum(axis=1) >= W).sum())
    return (1 + cnt) / (B + 1)


def one(rng, g, B):
    S, D, m = 48, g['D'], g['m']
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    n_op = int(np.minimum(rng.poisson(m, E.OPD), 2 * S).sum())
    st_op = rng.choice(S, n_op, p=act)
    go, _ = E.go_check(E.prices(rng, g['pr'], n_op), E.fills(rng, g['cap'], n_op), st_op, S)
    if not go:
        return None
    T, paused = E.calendar(rng, D, g['P'], g['lay'])
    cnt = np.minimum(rng.poisson(m, T), 2 * S); cnt[paused] = 0
    day = np.repeat(np.arange(T), cnt); n = day.size
    st = rng.choice(S, n, p=act)
    c = E.prices(rng, g['pr'], n); C = E.fills(rng, g['cap'], n)
    p = c.copy()
    z = (math.sqrt(0.05) * rng.standard_normal(T)[day] + math.sqrt(0.05) * rng.standard_normal(S)[st]
         + math.sqrt(0.10) * rng.standard_normal(T * S)[day * S + st])
    used = 0.20; mk_a = None
    for comp in g['comps']:
        e, kind = E.comp_path(rng, comp, T, S)
        z = z + math.sqrt(comp[2]) * e[day]
        used += comp[2]
        if comp[0] == 'mk':
            mk_a = math.sqrt(comp[2])
    z = z + math.sqrt(1 - used) * rng.standard_normal(n)
    y = (z < (ndtri(p) if mk_a is None else E.mk_quantile(p, mk_a))).astype(float)
    core = c >= E.CUT; tail = ~core
    x = (y - c)[core]; nk = x.size; kap = float(x.mean())
    crK = E.cr_all(day[core], st[core], x - kap, T, S, float(nk))
    sek5 = crK[5][0]
    viid = nk / (nk - 1.0) * float(np.sum((x - kap) ** 2)) / float(nk) ** 2
    nsh = C / c; Q = float(C.sum()); N = nsh * (y - c); tht = float(N.sum()) / Q
    crT = E.cr_all(day, st, N - tht * C, T, S, Q)
    sc = np.bincount(st, minlength=S); sc = sc[sc > 0]
    info = bool(crT[5][2] >= 12 and sc.size >= 25 and sc.sum() ** 2 / float(np.sum(sc * sc)) >= 15 and sek5 <= 0.025
                and sek5 * sek5 / viid <= 6.0)
    if not info:
        return None
    T1a_new = kap - E.LAM_K * E.H(crK, 0.975) > 0
    T1a_old = kap - E.tq(0.975, crK[5][1]) * sek5 > 0
    if tail.any():
        pv = pinm_p(rng, day[tail], st[tail], c[tail], float(y[tail].sum()), S, B)
    else:
        pv = 1.0
    t1b = pv <= 0.025
    return (int(t1b), int(T1a_new), int(T1a_old), int(t1b or T1a_new), int(t1b or T1a_old), int(tail.sum()))


def chunk(a):
    g, reps, seed, B = a
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    acc = np.zeros(6); reach = 0
    for _ in range(reps):
        r = one(rng, g, B)
        if r is not None:
            reach += 1; acc += r
    return reach, acc.tolist()


CELLS = [G(m=17, cap='thin', pr='tail1'), G(m=35, cap='full', pr='tail3'),
         G(m=17, cap='thin', pr='tail1', comps=AR(0.9, 0.05)), G(m=17, cap='thin', pr='tail1', comps=BOX(30, 0.10)),
         G(m=35, cap='full', pr='tail3', comps=AR(0.9, 0.10)), G(m=17, cap='thin', pr='tail1', comps=MK(0.9, 0.10)),
         G(m=17, cap='thin', pr='tail3', comps=BOX(30, 0.10), P=30, lay='run'),
         G(m=17, cap='full', pr='tail5', comps=BOX(30, 0.10))]

if __name__ == '__main__':
    reps, B = int(sys.argv[1]), int(sys.argv[2])
    out = 'out_t1b_%d_%d.jsonl' % (reps, B)
    done = {json.loads(l)['key'] for l in open(out)} if os.path.exists(out) else set()
    with Pool(4) as pool:
        for i, g in enumerate(CELLS):
            k = key(g)
            if k in done:
                continue
            parts = pool.map(chunk, [(g, reps // 4, [77200201, 20, i, ch], B) for ch in range(4)])
            reach = sum(p[0] for p in parts); acc = np.sum([p[1] for p in parts], axis=0)
            res = dict(key=k, g=g, reps=reps, B=B, reach=reach,
                       T1b=int(acc[0]), T1a_new=int(acc[1]), T1a_old=int(acc[2]), T1_new=int(acc[3]), T1_old=int(acc[4]),
                       tail_trades_mean=round(acc[5] / max(reach, 1), 2),
                       rates={k2: round(int(acc[j]) / reps, 5) for j, k2 in enumerate(('T1b', 'T1a_new', 'T1a_old', 'T1_new', 'T1_old'))},
                       T1b_wilson=E.wilson(int(acc[0]), reps), T1_new_wilson=E.wilson(int(acc[3]), reps))
            with open(out, 'a') as f:
                f.write(json.dumps(res) + '\n')
