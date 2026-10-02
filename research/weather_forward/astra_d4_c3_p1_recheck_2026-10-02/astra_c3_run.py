"""ASTRA cycle-3 (D4-C3-P1) recheck runner (resumable).  SYNTHETIC ONLY; OUTCOME_INFORMATION_USED = FALSE.

Usage:  python3 astra_c3_run.py PLAN REPS [PROCS]
Writes out_<PLAN>_<REPS>.jsonl, one line per completed cell; completed keys are skipped on rerun.
Seeds: SeedSequence([77300301, plan_code, cell_index, chunk]); chunks = 12 (or 12 per 100k block) with REPS split evenly.
Plans derive_t2 / derive_neg stop a design's curve once the power reaches 0.95 / 0.97 (deterministic given the file order).
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
import astra_c3_engine as E

SEED = 77300301
CODES = dict(repro_m3=1, repro_p1=2, derive_t2=3, derive_neg=4, verify_old=5, verify_new=6, gorate=7, level=8, probe=9,
             worst100=10, persist=11, probe100=12, level2=13)
LAWMEAN = dict(mid=0.575, favmix=0.6875, fav=0.80, fav80=0.85, fav85=0.875, pm89=0.89)


def G(**kw):
    g = dict(D=120, S=48, m=17, cap='thin', th=0.0, pr='mid', P=0, lay='rand', comps=(), gate='go2')
    g.update(kw)
    g['comps'] = tuple(tuple(c) for c in g['comps'])
    return g


def AR(phi, rv): return (('ar', phi, rv),)
def MK(phi, rv): return (('mk', phi, rv),)
def BOX(L, rv): return (('box', L, rv),)


def deps_full():
    d = [()]
    for phi in (0.5, 0.7, 0.8, 0.9):
        for rv in (0.02, 0.05, 0.10):
            d.append(AR(phi, rv))
    for phi in (0.8, 0.9):
        for rv in (0.02, 0.05, 0.10):
            d.append(MK(phi, rv))
    for L in (15, 30):
        for rv in (0.02, 0.05, 0.10):
            d.append(BOX(L, rv))
    return d


def key(g):
    pr = g['pr'] if isinstance(g['pr'], str) else json.dumps(g['pr'])
    parts = ['D%d' % g['D'], 'm%d' % g['m'], g['cap'], 'th%s' % (('%+.4f' % g['th']) if not isinstance(g['th'], str) else g['th']), pr,
             'gate_' + g['gate']]
    if g.get('pr_op'):
        parts.append('op_' + str(g['pr_op']))
    parts.append('P%d%s' % (g['P'], g['lay'] if g['P'] else ''))
    parts.append('+'.join('%s%g_%g' % c for c in g['comps']) or 'none')
    if g.get('S', 48) != 48:
        parts.append('S%d' % g['S'])
    return '|'.join(parts)


# ----------------------------------------------------------------------------- plans
def plan_repro_m3():
    """Astra @8874dc54 M3 cells (cycle-2 report 5.1): trailing mean 30, rv 0.10, m 17; OLD = 1.70/1.60, NEW = 2.15/1.80 on the same replications."""
    W = dict(comps=BOX(30, 0.10))
    cells = [
        ('M3_fav85_full_th10_P30run', G(pr='fav85', cap='full', th=0.10, P=30, lay='run', **W)),
        ('M3_fav85_thin_th10_P30run', G(pr='fav85', cap='thin', th=0.10, P=30, lay='run', **W)),
        ('M3_fav85_full_th10_P0', G(pr='fav85', cap='full', th=0.10, **W)),
        ('M3_fav85_thin_th0_P30run', G(pr='fav85', cap='thin', th=0.0, P=30, lay='run', **W)),
        ('M3_fav80_thin_th10_P30run', G(pr='fav80', cap='thin', th=0.10, P=30, lay='run', **W)),
        ('M3_fav85_full_th10_P30rand', G(pr='fav85', cap='full', th=0.10, P=30, lay='rand', **W)),
        ('M3_pm89_thin_th10_P30run', G(pr='pm89', cap='thin', th=0.10, P=30, lay='run', **W)),
        ('M3_pm89_thin_th0_P30run', G(pr='pm89', cap='thin', th=0.0, P=30, lay='run', **W)),
        ('M3_pm89_full_th10_P0_m35', G(pr='pm89', cap='full', th=0.10, m=35, **W)),
    ]
    return cells


def plan_repro_p1():
    """P1 counterexample (cycle-2 report 7 / 15): no persistence, m 17; the cycle-2 gate (go2) vs the cycle-3 gate (go3).
    Effect = the design's own theta_PCE under the cycle-2 formula (Z_80); NEG at kappa = -0.12 (mid) / -0.07 (per share)."""
    cells = []
    for pr in ('mid', 'fav'):
        for cap in ('thin', 'full'):
            for gate in ('go2', 'go3'):
                cells.append(G(pr=pr, cap=cap, th='own_old', gate=gate))
                th = -0.07 / LAWMEAN[pr]
                cells.append(G(pr=pr, cap=cap, th=th, gate=gate))
    return [(key(g), g) for g in cells]


T2_TH = (0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30)
NEG_K = (-0.03, -0.05, -0.07, -0.09, -0.12, -0.16, -0.20, -0.25)
LAWS6 = ('mid', 'favmix', 'fav', 'fav80', 'fav85', 'pm89')
T2_START = dict(mid=0.10, favmix=0.08, fav=0.04, fav80=0.04, fav85=0.04, pm89=0.04)
NEG_START = dict(mid=-0.07, favmix=-0.07, fav=-0.05, fav80=-0.05, fav85=-0.05, pm89=-0.05)


def designs36():
    return [(pr, m, cap) for pr in LAWS6 for m in (17, 35, 55) for cap in ('thin', 'full')]


def plan_derive_t2():
    cells = []
    for (pr, m, cap) in designs36():
        for th in T2_TH:
            if th < T2_START[pr] - 1e-9:
                continue
            g = G(pr=pr, m=m, cap=cap, th=th, gate='none')
            cells.append((key(g), g))
    return cells


def plan_derive_neg():
    cells = []
    for (pr, m, cap) in designs36():
        for k in NEG_K:
            if k > NEG_START[pr] + 1e-9:
                continue
            g = G(pr=pr, m=m, cap=cap, th=k / LAWMEAN[pr], gate='none')
            g['kappa_target'] = k
            cells.append((key(g), g))
    return cells


def plan_verify(which):
    cells = []
    for (pr, m, cap) in designs36():
        g = G(pr=pr, m=m, cap=cap, th='own_' + which, gate='th_' + which)
        cells.append((key(g), g))
    return cells


LAWS10 = ('mid', 'favmix', 'fav', 'fav80', 'fav85', 'pm89', 'tail1', 'tail3', 'wide', 'low')
MS = (8, 12, 17, 25, 35, 55, 80, 96)


def plan_gorate():
    cells = []
    for pr in LAWS10:
        for m in MS:
            for cap in ('thin', 'full'):
                g = G(pr=pr, m=m, cap=cap, gate='none')
                g['op_only'] = True
                cells.append((key(g) + '|OPONLY', g))
    return cells


def plan_level():
    """Class verification (enlarged D_P**): 100 targeted worst-geometry cells + 90 random cells of the factorial (Astra's own RNG)."""
    rng = np.random.default_rng(77300302)
    deps = deps_full()
    cells = []
    laws = ('pm89', 'fav85', 'fav80')
    cals = (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run'))
    # random factorial sample: 25 deps x laws(3 new + 3 mixes) x cals x fills x theta
    allc = []
    for dep in deps:
        for pr in laws + ('pmmix10', 'pmmix50', 'pmmix90'):
            for cal in cals:
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        allc.append(G(m=17, cap=cap, th=th, pr=pr, comps=dep, **cal))
    for i in rng.choice(len(allc), 90, replace=False):
        cells.append(allc[int(i)])
    # targeted worst-geometry: trailing mean 30 / AR 0.9 / two-state 0.9 at rv 0.10 and 0.05, m 12/17/35/55
    W = [BOX(30, 0.10), BOX(30, 0.05), AR(0.9, 0.10), MK(0.9, 0.10), BOX(15, 0.10)]
    for pr in laws:
        for dep in W[:2]:
            for m in (12, 35, 55):
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=m, cap=cap, th=th, pr=pr, comps=dep, P=0))
    for pr in ('pm89', 'fav85'):
        for dep in W[2:]:
            for cap in ('thin', 'full'):
                for th in (0.0, 0.10):
                    cells.append(G(m=35, cap=cap, th=th, pr=pr, comps=dep, P=30, lay='run'))
    # geometry slices: D 60 / 90 with 30 contiguous paused; hemisphere / station; early pause run
    for pr in laws:
        for D in (60, 90):
            for dep in (BOX(30, 0.10), MK(0.9, 0.10)):
                for th in (0.0, 0.10):
                    cells.append(G(D=D, th=th, pr=pr, comps=dep, P=30, lay='run'))
        for kind in ('hemi', 'stn'):
            for th in (0.0, 0.10):
                cells.append(G(th=th, pr=pr, comps=((kind, 0.9, 0.10),)))
        for th in (0.0, 0.10):
            cells.append(G(th=th, pr=pr, comps=BOX(30, 0.10), P=30, lay='early'))
    seen, out = set(), []
    for g in cells:
        k = key(g)
        if k not in seen:
            seen.add(k)
            out.append((k, g))
    return out


def plan_probe():
    """Second-order search beyond the enumerated laws (all at the worst declared shape: trailing mean 30, rv 0.10, 30 contiguous paused unless noted)."""
    W = dict(comps=BOX(30, 0.10))
    laws = [('PM', 0.895), ('PM', 0.899), ('PM', 0.88), ('PM', 0.87), ('U', 0.88, 0.90), ('U', 0.89, 0.899),
            ('MIX', 0.25, ('PM', 0.89), ('U', 0.35, 0.80)), ('MIX', 0.75, ('PM', 0.89), ('U', 0.35, 0.80)),
            ('MIX', 0.50, ('PM', 0.89), ('PM', 0.60)), ('MIX', 0.50, ('PM', 0.89), ('PM', 0.70)),
            ('MIX', 0.90, ('PM', 0.89), ('PM', 0.60)), ('MIX', 0.50, ('PM', 0.895), ('U', 0.35, 0.80)),
            ('MIX', 0.50, ('PM', 0.89), ('U', 0.04, 0.35)), ('MIX', 0.90, ('PM', 0.89), ('U', 0.04, 0.35)),
            ('MIX', 0.50, ('U', 0.85, 0.90), ('U', 0.35, 0.80)),
            'pmtail1', 'pmtail3', 'pmmix25', 'pmmix75']
    cells = []
    for pr in laws:
        for cap in ('thin', 'full'):
            for th in (0.0, 0.10):
                for cal in (dict(P=0, m=35), dict(P=30, lay='run', m=17)):
                    cells.append(G(pr=pr, cap=cap, th=th, **W, **cal))
    return [(key(g), g) for g in cells]


def plan_persist():
    """Does persistence make the gate non-conservative?  Power at the design's own new theta_PCE (theta-side new GO) under persistence."""
    cells = []
    for pr, m, cap in (('fav', 35, 'full'), ('fav', 55, 'full'), ('fav80', 17, 'full'), ('fav85', 17, 'full'), ('pm89', 17, 'full'),
                       ('pm89', 35, 'thin'), ('fav', 55, 'thin'), ('mid', 55, 'full')):
        for dep in ((), AR(0.9, 0.05), BOX(30, 0.05), BOX(30, 0.10), MK(0.9, 0.10), AR(0.9, 0.10)):
            g = G(pr=pr, m=m, cap=cap, th='own_new', gate='th_new', comps=dep)
            cells.append((key(g), g))
    return cells


PLANS = dict(repro_m3=plan_repro_m3, repro_p1=plan_repro_p1, derive_t2=plan_derive_t2, derive_neg=plan_derive_neg,
             verify_old=lambda: plan_verify('old'), verify_new=lambda: plan_verify('new'), gorate=plan_gorate, level=plan_level,
             probe=plan_probe, persist=plan_persist)


def _job(a):
    g, reps, seed = a
    if g.get('op_only'):
        return op_only(g, reps, seed)
    return E.run_chunk(g, reps, seed)


def op_only(g, reps, seed):
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    S, m, pr, cap = 48, g['m'], g['pr'], g['cap']
    out = dict(reps=reps, n_ok=0, go2=0, go3=0, th_old=0, th_new=0, k2=0, k3=0, stn=0, sum_se0=0.0, sum_se0k=0.0, sum_pce_old=0.0, sum_pce_new=0.0,
               min_se0k=1e9, reasons={})
    for _ in range(reps):
        act = rng.gamma(2.0, 1.0, S); act = act / act.sum()
        n_op = int(np.minimum(rng.poisson(m, E.OPD), 2 * S).sum())
        st_op = rng.choice(S, n_op, p=act)
        d = E.design_stats(E.prices(rng, pr, n_op), E.fills(rng, cap, n_op), st_op, S)
        if d is None:
            r = 'NO_CORE'
            out['reasons'][r] = out['reasons'].get(r, 0) + 1
            continue
        out['n_ok'] += 1
        out['go2'] += int(E.gate('go2', d)); out['go3'] += int(E.gate('go3', d))
        out['th_old'] += int(E.gate('th_old', d)); out['th_new'] += int(E.gate('th_new', d))
        out['k2'] += int(d['se0k'] <= 0.020); out['k3'] += int(d['se0k'] <= E.SEK_CEIL); out['stn'] += int(d['stn'])
        out['sum_se0'] += d['se0']; out['sum_se0k'] += d['se0k']
        out['sum_pce_old'] += d['pce_old']; out['sum_pce_new'] += d['pce_new']
        out['min_se0k'] = min(out['min_se0k'], d['se0k'])
        if d['pce_new'] > 0.10:
            r = 'PCE_ABOVE_CEILING'
        elif d['se0k'] > E.SEK_CEIL:
            r = 'KAPPA_UNDERPOWERED'
        elif not d['stn']:
            r = 'STATION_DIVERSITY'
        else:
            r = 'GO'
        out['reasons'][r] = out['reasons'].get(r, 0) + 1
    return out


def merge_op(parts):
    out = {}
    for p in parts:
        for k, v in p.items():
            if k == 'reasons':
                d = out.setdefault('reasons', {})
                for kk, vv in v.items():
                    d[kk] = d.get(kk, 0) + vv
            elif k == 'min_se0k':
                out[k] = min(out.get(k, 1e9), v)
            else:
                out[k] = out.get(k, 0) + v
    return out


def stop_reached(done_recs, k, g, plan):
    """Deterministic early stop of an adaptive curve: a design is finished once a previous (ascending) point reached the stop power."""
    dk = design_key(g)
    thr = 0.95 if plan == 'derive_t2' else 0.97
    for r in done_recs:
        if r['design'] == dk and r.get('reach', 0) > 200:
            pw = (r['new']['t2'] if plan == 'derive_t2' else r['new']['NEG']) / r['reach']
            if pw >= thr:
                return True
    return False


def design_key(g):
    h = dict(g); h.pop('th', None); h.pop('kappa_target', None)
    return key(dict(h, th=0.0))


def main():
    plan = sys.argv[1]
    reps = int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    if plan in ('worst100', 'probe100', 'level2'):
        cells = [(k, G(**{**g, 'comps': tuple(tuple(c) for c in g['comps'])})) if False else (k, _fixg(g)) for k, g in json.load(open('cells_%s.json' % plan))]
    else:
        cells = PLANS[plan]()
    out = 'out_%s_%d.jsonl' % (plan, reps)
    done, recs = set(), []
    if os.path.exists(out):
        for line in open(out):
            if line.strip():
                r = json.loads(line)
                done.add(r['key']); recs.append(r)
    nch = 12 if reps <= 20000 else 12 * (reps // 20000)
    with Pool(procs) as pool:
        for idx, (k, g) in enumerate(cells):
            if k in done:
                continue
            if plan in ('derive_t2', 'derive_neg') and stop_reached(recs, k, g, plan):
                continue
            sizes = [reps // nch + (1 if i < reps % nch else 0) for i in range(nch)]
            seeds = [[SEED, CODES[plan], idx, ch] for ch in range(nch)]
            parts = pool.map(_job, [(g, s, sd) for s, sd in zip(sizes, seeds)], chunksize=1)
            res = merge_op(parts) if g.get('op_only') else E.merge(parts)
            if not g.get('op_only'):
                res['ngate'] = sum(p['ngate'] for p in parts); res['nd'] = sum(p['nd'] for p in parts)
                res['sum_se0_op'] = sum(p['sum_se0_op'] for p in parts); res['sum_se0k_op'] = sum(p['sum_se0k_op'] for p in parts)
            res.update(key=k, g=g, plan=plan, idx=idx, design=design_key(g), seeds='[%d,%d,%d,0..%d]' % (SEED, CODES[plan], idx, nch - 1))
            with open(out, 'a') as f:
                f.write(json.dumps(res) + '\n')
            recs.append(res)


def _fixg(g):
    g = dict(g)
    g['comps'] = tuple(tuple(c) for c in g['comps'])
    for kk in ('pr', 'pr_op'):
        if isinstance(g.get(kk), list):
            g[kk] = _tup(g[kk])
    return g


def _tup(x):
    return tuple(_tup(y) if isinstance(y, list) else y for y in x)


if __name__ == '__main__':
    main()
