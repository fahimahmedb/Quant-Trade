"""ASTRA cycle-2 recheck runner (resumable).  SYNTHETIC ONLY; OUTCOME_INFORMATION_USED = FALSE.

Usage:  python3 astra_m2_run.py PLAN REPS [PROCS]
Writes out_<PLAN>_<REPS>.jsonl, one line per completed cell; cells already present (by key) are skipped on rerun.
Seeds: SeedSequence([77200201, plan_code, cell_index, chunk]), chunk = 0..k-1 of REPS/k replications.
"""
import json
import os
import sys
from multiprocessing import Pool

import astra_m2_engine as E

SEED = 77200201
CODES = dict(repro=1, repro100=2, class_=3, slice=4, probe=5, worst100=6, power=7, probe100=8, sample=9)


def G(**kw):
    g = dict(D=120, S=48, m=17, cap='thin', th=0.0, pr='mid', P=0, lay='rand', comps=())
    g.update(kw)
    g['comps'] = tuple(tuple(c) for c in g['comps'])
    return g


def AR(phi, rv):
    return (('ar', phi, rv),)


def MK(phi, rv):
    return (('mk', phi, rv),)


def BOX(L, rv):
    return (('box', L, rv),)


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


def plan_repro():
    """Astra @ac777a87 M1-R / M2 counterexample geometry (m 17), evaluated under OLD and NEW on the same replications."""
    return [
        ('M1R_fav_ar09_rv05_thin_th10', G(pr='fav', comps=AR(0.9, 0.05), th=0.10)),
        ('M1R_fav_ar09_rv05_thin_th0', G(pr='fav', comps=AR(0.9, 0.05), th=0.0)),
        ('M1R_fav_ar09_rv10_thin_th10', G(pr='fav', comps=AR(0.9, 0.10), th=0.10)),
        ('M1R_fav_ar09_rv10_thin_th0', G(pr='fav', comps=AR(0.9, 0.10), th=0.0)),
        ('M1R_mid_ar09_rv05_P30rand_th10', G(comps=AR(0.9, 0.05), P=30, lay='rand', th=0.10)),
        ('M1R_mid_mk09_rv05_th10', G(comps=MK(0.9, 0.05), th=0.10)),
        ('M1R_mid_box30_rv05_th10', G(comps=BOX(30, 0.05), th=0.10)),
        ('M1R_mid_box30_rv05_th0', G(comps=BOX(30, 0.05), th=0.0)),
        ('M2_mid_ar09_rv05_thin_th0', G(comps=AR(0.9, 0.05), th=0.0)),
        ('M2_mid_ar09_rv10_thin_th0', G(comps=AR(0.9, 0.10), th=0.0)),
        ('M2_mid_ar09_rv05_full_th0', G(comps=AR(0.9, 0.05), cap='full', th=0.0)),
        ('M2_mid_ar09_rv10_full_th0', G(comps=AR(0.9, 0.10), cap='full', th=0.0)),
        ('M2_fav_ar09_rv05_thin_th0', G(pr='fav', comps=AR(0.9, 0.05), th=0.0)),
        ('M2_mid_box30_rv05_thin_th0', G(comps=BOX(30, 0.05), th=0.0)),
        ('grid_mid_ar09_rv05_thin_th10', G(comps=AR(0.9, 0.05), th=0.10)),
        ('OUT_fav_ar095_rv05_thin_th10', G(pr='fav', comps=AR(0.95, 0.05), th=0.10)),
    ]


def plan_repro100():
    keep = ('M1R_fav_ar09_rv05_thin_th10', 'M1R_fav_ar09_rv05_thin_th0', 'M1R_mid_ar09_rv05_P30rand_th10',
            'M2_mid_ar09_rv05_thin_th0')
    return [c for c in plan_repro() if c[0] in keep]


def plan_class():
    cells = []
    for dep in deps_full():
        for pr in ('mid', 'fav', 'favmix'):
            for cal in (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run')):
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        g = G(m=17, cap=cap, th=th, pr=pr, comps=dep, **cal)
                        cells.append((key(g), g))
    return cells


def plan_slice():
    cells = []
    deps = [(), AR(0.9, 0.02), AR(0.9, 0.05), AR(0.9, 0.10), MK(0.9, 0.05), MK(0.9, 0.10), BOX(30, 0.05), BOX(30, 0.10)]
    for dep in deps:
        for pr in ('mid', 'fav'):
            for cal in (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run')):
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=35, cap=cap, th=th, pr=pr, comps=dep, **cal))
                cells.append(G(m=17, cap='thin', th=0.05, pr=pr, comps=dep, **cal))
    for D in (60, 90):
        for dep in [(), AR(0.9, 0.10), MK(0.9, 0.10), BOX(30, 0.10)]:
            for pr in ('mid', 'fav'):
                for cal in (dict(P=0), dict(P=30, lay='run')):
                    for th in (0.0, 0.10):
                        cells.append(G(D=D, th=th, pr=pr, comps=dep, **cal))
    for kind in ('hemi', 'stn'):
        for rv in (0.05, 0.10):
            for pr in ('mid', 'fav'):
                for th in (0.0, 0.10):
                    cells.append(G(th=th, pr=pr, comps=((kind, 0.9, rv),)))
    for pr, m, cap in (('tail1', 17, 'thin'), ('tail3', 35, 'full')):
        for dep in [(), AR(0.9, 0.10), MK(0.9, 0.10), BOX(30, 0.10)]:
            for cal in (dict(P=0), dict(P=30, lay='run')):
                for th in (0.0, 0.10):
                    cells.append(G(m=m, cap=cap, th=th, pr=pr, comps=dep, **cal))
    for pr in ('wide', 'low'):
        for dep in [(), BOX(30, 0.10)]:
            cells.append(G(pr=pr, comps=dep))
    return [(key(g), g) for g in cells]


def plan_probe():
    """Second-order search: inside-the-text but off-grid laws, gaps between grid points, boundaries, mixtures."""
    W = dict(comps=BOX(30, 0.10), P=30, lay='run')          # worst declared slice (run H): trailing mean 30, rv 0.10
    cells = []
    for pr in ('fav80', 'fav85', 'pt90', 'fav60', 'favtail3', 'tail5', 'tail10'):
        for cap in ('thin', 'full'):
            for th in (0.0, 0.10):
                cells.append(G(pr=pr, cap=cap, th=th, **W))
    for m in (8, 12, 25, 50):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', m=m, th=th, **W))
    for L in (20, 25, 40, 45):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', th=th, comps=BOX(L, 0.10), P=30, lay='run'))
    for comps in (AR(0.85, 0.10), MK(0.85, 0.10), AR(0.9, 0.07), BOX(30, 0.07), MK(0.95, 0.10), AR(0.95, 0.10)):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', th=th, comps=comps, P=30, lay='run'))
    for lay in ('two', 'early', 'late'):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', th=th, comps=BOX(30, 0.10), P=30, lay=lay))
    for P in (10, 20):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', th=th, comps=BOX(30, 0.10), P=P, lay='run'))
    for D in (60, 90):
        for th in (0.0, 0.10):
            cells.append(G(D=D, pr='fav', cap='full', th=th, **W))
    for th in (-0.05, -0.10, 0.05, 0.15):
        cells.append(G(pr='fav', cap='full', th=th, **W))
    # mixed / two components (outside by declaration) and price drift between OP and window
    for comps in (BOX(30, 0.05) + AR(0.9, 0.05), BOX(30, 0.10) + AR(0.9, 0.05)):
        for th in (0.0, 0.10):
            cells.append(G(pr='fav', cap='full', th=th, comps=comps, P=30, lay='run'))
    for th in (0.0, 0.10):
        cells.append(G(pr='fav', pr_op='mid', cap='full', th=th, **W))
    return [(key(g), g) for g in cells]


def plan_power():
    cells = []
    for m, cap in ((17, 'thin'), (17, 'full'), (35, 'thin'), (35, 'full')):
        for th in (-0.12, -0.06, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25):
            cells.append(G(m=m, cap=cap, th=th))
    for th in (0.0, 0.09, 0.20):
        cells.append(G(m=17, cap='thin', th=th, comps=BOX(30, 0.10)))
        cells.append(G(m=17, cap='thin', th=th, pr='fav', comps=BOX(30, 0.10), P=30, lay='run'))
        cells.append(G(m=17, cap='thin', th=th, pr='fav'))
    return [(key(g), g) for g in cells]


def key(g):
    parts = ['D%d' % g['D'], 'm%d' % g['m'], g['cap'], 'th%+.2f' % g['th'], g['pr']]
    if g.get('pr_op'):
        parts.append('op_' + g['pr_op'])
    parts.append('P%d%s' % (g['P'], g['lay'] if g['P'] else ''))
    parts.append('+'.join('%s%g_%g' % c for c in g['comps']) or 'none')
    return '|'.join(parts)


def plan_from_file(name):
    """worst100 / probe100: cells listed (by key) in a JSON file written after inspecting Astra's own 20k runs."""
    lst = json.load(open(name))
    return [(k, g) for k, g in lst]


PLANS = dict(repro=plan_repro, repro100=plan_repro100, class_=plan_class, slice=plan_slice, probe=plan_probe,
             power=plan_power)


def _job(a):
    g, reps, seed = a
    return E.run_chunk(g, reps, seed)


def main():
    plan = sys.argv[1]
    reps = int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if plan in ('worst100', 'probe100', 'sample'):
        cells = plan_from_file('cells_%s.json' % plan)
    else:
        cells = PLANS[plan]()
    out = 'out_%s_%d.jsonl' % (plan, reps)
    done = set()
    if os.path.exists(out):
        for line in open(out):
            if line.strip():
                done.add(json.loads(line)['key'])
    nch = max(4, reps // 5000)
    with Pool(procs) as pool:
        for idx, (k, g) in enumerate(cells):
            if k in done:
                continue
            seeds = [[SEED, CODES[plan], idx, ch] for ch in range(nch)]
            parts = pool.map(_job, [(g, reps // nch, s) for s in seeds])
            res = E.merge(parts)
            res.update(key=k, g=g, plan=plan, idx=idx, seeds='[%d,%d,%d,0..%d]' % (SEED, CODES[plan], idx, nch - 1))
            with open(out, 'a') as f:
                f.write(json.dumps(res) + '\n')


if __name__ == '__main__':
    main()
