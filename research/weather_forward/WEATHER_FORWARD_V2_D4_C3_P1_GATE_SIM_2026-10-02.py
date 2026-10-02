"""Weather Forward V2 — D4-C3-P1 / M3 cycle-3 simulation (run J), 2026-10-02.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.
OUTCOME_INFORMATION_USED = FALSE.

Purpose (Astra @8874dc54):
  M3  the cycle-2 lambda constants (1.70 / 1.60) were calibrated over CORE price laws U(0.35,0.80), U(0.70,0.90) and
      their mix; the printed class text said "CORE prices to 0.90".  c ~ U(0.85,0.90) exceeds the stated level.
      Option (i): enlarge the class to near-cap favourite laws and recalibrate lambda (never below 1.70 / 1.60).
  P1  GO / theta_PCE (Z_80 = 2.4865) / SE_KAPPA_CEILING (0.020) were left at their nominal 5-date-block meaning.
      Option (a): outcome-free, stricter-only recalibration of the design gate to the tests actually run.

The full declaration (classes, plans, selection and derivation rules, order of work) is in ARCHITECT_PROGRESS_CYCLE3.md,
committed in a WIP checkpoint BEFORE any run of this file (git-verifiable order).  This file only implements it.
The cycle-2 engine (WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py) is imported unchanged; this file adds
  - new CORE price laws (fav80, fav85, pm89, pmmix10/50/90 and probe laws),
  - a per-replication design record (SE0_theta, SE0_kappa, theta_PCE under the old and the new multiplier),
  - gate modes, lean power cells, resumable JSONL output, and the P1 plans.

Usage
  OMP_NUM_THREADS=1 python3 THIS.py run PLAN [REPS] --out FILE     resumable: cells already in FILE are skipped
  OMP_NUM_THREADS=1 python3 THIS.py cell PLAN IDX REPS --out FILE  one cell, independent streams 1..5 of REPS/5 each
  python3 THIS.py check                                            engine-equivalence check against the cycle-2 engine
Constants for the P1 verification / GO-rate plans are read from WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json
(written by the derivation step after the M3 and P1-derive plans have run).
Seeds: SeedSequence([20261102, plan_code, cell_index, stream]).  Requires numpy, scipy.  Set OMP_NUM_THREADS=1.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from scipy import stats
from scipy.special import ndtri

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('m2cal', os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_M2_CAL_SIM_2026-10-01.py'))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

ERT, CUT, Z80, OPD = m.ERT, m.CUT, m.Z80, m.OPD
BL = m.BL
GRID3 = tuple(round(1.0 + 0.05 * i, 2) for i in range(51))          # 1.00 .. 3.50
SEED_BASE = 20261102
PLAN_CODE = dict(m3_class=11, m3_mix=12, m3_m35=13, m3_geo=14, m3_astra=15, m3_probe=16,
                 p1_t2=21, p1_neg=22, p1_hi=23, p1_verify=24, p1_go=25)
CONST_FILE = os.path.join(HERE, 'WEATHER_FORWARD_V2_D4_C3_P1_CONSTANTS_2026-10-02.json')

# mean CORE ask of each GO-feasible law (used only to turn a target kappa into a theta for the NEG cells)
LAW_MEAN = dict(mid=0.575, favmix=0.6875, fav=0.80, fav80=0.85, fav85=0.875, pm89=0.89)

_prices_orig = m.prices


def prices_ext(rng, kind, n):
    if kind == 'fav80':
        return rng.uniform(0.80, 0.90, n)
    if kind == 'fav85':
        return rng.uniform(0.85, 0.90, n)
    if kind == 'pm89':
        return np.full(n, 0.89)
    if kind.startswith('pmmix'):                       # share s of point mass 0.89, rest U(0.35, 0.80)
        s = int(kind[5:]) / 100.0
        u = rng.random(n) < s
        return np.where(u, 0.89, rng.uniform(0.35, 0.80, n))
    if kind == 'pm899':                                # probe laws (outside / in-between disclosure)
        return np.full(n, 0.899)
    if kind == 'pm85':
        return np.full(n, 0.85)
    if kind == 'pm80':
        return np.full(n, 0.80)
    if kind == 'fav88':
        return rng.uniform(0.88, 0.90, n)
    if kind == 'fav60':
        return rng.uniform(0.60, 0.90, n)
    return _prices_orig(rng, kind, n)


m.prices = prices_ext                                  # m.one_rep and helpers resolve `prices` in m's globals


# ------------------------------------------------------------------------------------------------ constants
def load_consts():
    if os.path.exists(CONST_FILE):
        return json.load(open(CONST_FILE))
    return None


# ------------------------------------------------------------------------------------------------ design record
def design_stats(c, C, st, S, zeff):
    """Spec 10.2 on the OP trades: SE0_theta, SE0_kappa, theta_PCE under Z80 and under zeff, station clause."""
    J = c.size
    if J == 0:
        return None
    mbar = J / OPD
    s2 = J * float((C * C * (1 - c) / c).sum()) / float(C.sum()) ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    if not core.any():
        return None
    se0k = math.sqrt(float((c[core] * (1 - c[core])).mean()) * deff / (120 * core.sum() / OPD))
    k = np.bincount(st, minlength=S); k = k[k > 0]
    stn = bool(k.size >= 25 and k.sum() ** 2 / float((k * k).sum()) >= 15)
    d = dict(se0=se0, se0k=se0k, stn=stn, pce_old=math.ceil(round(100 * Z80 * se0, 9)) / 100)
    d['pce_new'] = math.ceil(round(100 * zeff * se0, 9)) / 100 if zeff else None
    return d


def go_pass(mode, d, K):
    """Gate modes. old = cycle-2 GO (superset of the cycle-3 GO); th_old / th_new = theta-side only; new = full cycle-3 GO."""
    if d is None:
        return False
    if mode == 'none':
        return True
    if mode == 'old':
        return d['pce_old'] <= 0.10 and d['se0k'] <= 0.020 and d['stn']
    if mode == 'th_old':
        return d['pce_old'] <= 0.10 and d['stn']
    if mode == 'th_new':
        return d['pce_new'] <= 0.10 and d['stn']
    if mode == 'new':
        return d['pce_new'] <= 0.10 and d['se0k'] <= K['se_kappa_ceiling'] and d['stn']
    raise ValueError(mode)


def halfwidths_lean(day, st, r, Tc, S, Q):
    M, Cn = m.mats(day, st, r, Tc, S)
    out = {}
    for b in BL:
        out[b] = m.cr_b(M, Cn, Q, b)
    return out


def one_rep_p1(rng, g, K):
    """Identical RNG flow and statistics to the cycle-2 one_rep; adds the design record and gate modes.
    Returns (design_or_None, rec_or_None)."""
    S = g['S']
    n_op = int(np.minimum(rng.poisson(g['m'], OPD), 2 * S).sum())
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    st_op = rng.choice(S, n_op, p=act)
    c_op = m.prices(rng, g['pr'], n_op); C_op = m.fills(rng, g['cap'], n_op)
    d = design_stats(c_op, C_op, st_op, S, K.get('z_eff') if K else None)
    mode = g.get('go', 'old')
    if not go_pass(mode, d, K):
        return d, None
    thv = g['th']
    if isinstance(thv, str):
        thv = d['pce_old'] if thv == 'pce_old' else d['pce_new']
    Tc, day = m.gen_window(rng, g)
    n = day.size
    st = rng.choice(S, n, p=act)
    c = m.prices(rng, g['pr'], n); C = m.fills(rng, g['cap'], n)
    p = np.minimum(1.0, c * (1.0 + thv))
    z = (math.sqrt(m.RHO[0]) * rng.standard_normal(Tc)[day] + math.sqrt(m.RHO[1]) * rng.standard_normal(S)[st]
         + math.sqrt(m.RHO[2]) * rng.standard_normal(Tc * S)[day * S + st])
    used = sum(m.RHO)
    e = m.persistent(rng, g, Tc, S)
    if e is not None:
        rv = g['rv']
        if g['pk'] == 'hemi':
            z = z + math.sqrt(rv) * e[day, (st >= S // 2).astype(int)]
        elif g['pk'] == 'stn':
            z = z + math.sqrt(rv) * e[day, st]
        else:
            z = z + math.sqrt(rv) * e[day]
        used += rv
    z = z + math.sqrt(1 - used) * rng.standard_normal(n)
    y = (z < m.thresholds(p, g)).astype(float)
    nsh = C / c
    Q = float(C.sum())
    N = nsh * (y - c)
    th = float(N.sum()) / Q
    thW = float((nsh * (p - c)).sum()) / Q
    hw = halfwidths_lean(day, st, N - th * C, Tc, S, Q)
    core = c >= CUT
    tail = ~core
    x = (y - c)[core]
    nk = x.size
    kap = float(x.mean()); kap_true = float((p - c)[core].mean())
    hk = halfwidths_lean(day[core], st[core], x - kap, Tc, S, float(nk))
    sek5 = hk[5][0]
    viid = nk / (nk - 1.0) * float(((x - kap) ** 2).sum()) / float(nk) ** 2
    blocks5 = hw[5][2]
    sc = np.bincount(st, minlength=S); sc = sc[sc > 0]
    info = bool(g['D'] >= 60 and blocks5 >= 12 and sc.size >= 25 and sc.sum() ** 2 / float((sc * sc).sum()) >= 15
                and sek5 <= 0.025 and sek5 * sek5 / viid <= 6.0)
    if not info:
        return d, None
    if tail.any():
        Cc = C[core]; Qc = float(Cc.sum())
        thc = float(N[core].sum()) / Qc
        hc = halfwidths_lean(day[core], st[core], N[core] - thc * Cc, Tc, S, Qc)
        M_tail = float((nsh[tail] - C[tail]).sum()) / Q
        w = Qc / Q
    else:
        thc, hc, M_tail, w = th, hw, 0.0, 1.0
    cc = c + 0.01
    g1 = float(((C / cc) * (y - cc)).sum()) / Q > 0
    pos = np.maximum(N, 0.0); gross = float(pos.sum())
    top5 = float(np.partition(N, -5)[-5:].sum()) if n >= 5 else float(N.sum())
    g2 = bool(gross > 0 and (float(N.sum()) - top5) / Q > 0
              and np.bincount(day, weights=pos).max() <= 0.25 * gross
              and np.bincount(st, weights=pos, minlength=S).max() <= 0.20 * gross)
    rec = dict(th=th, thW=thW, kap=kap, kt=kap_true, thc=thc, w=w, Mt=M_tail, gates=bool(g1 and g2),
               H_A=m.H(hw, BL, m._T95), HkA=m.H(hk, BL, m._T975), HcA=m.H(hc, BL, m._T975),
               H_R0=m._T95[hw[5][1]] * hw[5][0], Hk5=m._T975[hk[5][1]] * hk[5][0], ntail=int(tail.sum()))
    return d, rec


# ------------------------------------------------------------------------------------------------ cell runner
wilson, rate = m.wilson, m.rate


def run_cell(plan, idx, g, reps, stream, K):
    seed = [SEED_BASE, PLAN_CODE[plan], idx, stream]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    recs = []
    dsum = dict(n=0, se0=0.0, se0k=0.0, pce_old=0.0, pce_new=0.0, n_go=0)
    for _ in range(reps):
        d, r = one_rep_p1(rng, g, K)
        if d is not None:
            dsum['n'] += 1; dsum['se0'] += d['se0']; dsum['se0k'] += d['se0k']; dsum['pce_old'] += d['pce_old']
            if d['pce_new'] is not None:
                dsum['pce_new'] += d['pce_new']
        if r is not None:
            recs.append(r)
    return counts(plan, idx, g, reps, seed, recs, dsum)


def counts(plan, idx, g, reps, seed, recs, dsum):
    out = dict(plan=plan, idx=idx, g=g, reps=reps, seed=seed, reach=rate(len(recs), reps), design=dsum)
    if not recs:
        out['empty'] = True
        return out
    A = {k: np.array([r[k] for r in recs], float) for k in recs[0]}
    th, thW, kap, kt = A['th'], A['thW'], A['kap'], A['kt']
    lam = np.array(GRID3)[:, None]
    Lr = th[None, :] - lam * A['H_A'][None, :]
    miss = (Lr > thW).sum(axis=1)
    pos = (Lr > 0) & (th >= ERT)
    fpos = (pos & (thW <= 0)).sum(axis=1)
    sup = (pos & (A['gates'] > 0)).sum(axis=1)
    t2 = (Lr > 0).sum(axis=1)
    U = A['w'] * (A['thc'] + lam * A['HcA']) + A['Mt']
    uw_miss = (U < thW).sum(axis=1)
    uw_loss = (U < 0).sum(axis=1)
    iv_miss = ((Lr > thW) | (U < thW)).sum(axis=1)
    T1a = (kap - lam * A['HkA'] > 0)
    NEG = (kap + lam * A['HkA'] < 0)
    out['grid'] = list(GRID3)
    out['by_lam'] = dict(miss=miss.tolist(), fpos=fpos.tolist(), sup=sup.tolist(), t2=t2.tolist(),
                         uw_miss=uw_miss.tolist(), uw_loss=uw_loss.tolist(), iv_miss=iv_miss.tolist(),
                         T1a=T1a.sum(axis=1).tolist(), NEG=NEG.sum(axis=1).tolist(),
                         T1a_null=(T1a & (kt <= 0)).sum(axis=1).tolist(), NEG_null=(NEG & (kt >= 0)).sum(axis=1).tolist())
    out['mean'] = dict(th=round(float(th.mean()), 5), thW=round(float(thW.mean()), 5), kap=round(float(kap.mean()), 5),
                       kt=round(float(kt.mean()), 5), HA=round(float(A['H_A'].mean()), 5), HkA=round(float(A['HkA'].mean()), 5),
                       Hk5=round(float(A['Hk5'].mean()), 5))
    out['tail_trades_mean'] = round(float(A['ntail'].mean()), 2)
    return out


def combine(parts, plan, idx, g):
    comb = dict(plan=plan, idx=idx, g=g, reps=sum(x['reps'] for x in parts), seed=[x['seed'] for x in parts],
                combined_streams=True)
    comb['reach'] = rate(sum(x['reach']['k'] for x in parts), comb['reps'])
    comb['design'] = {k: sum(x['design'][k] for x in parts) for k in parts[0]['design']}
    ok = [x for x in parts if 'by_lam' in x]
    comb['grid'] = list(GRID3)
    comb['by_lam'] = {k: [sum(x['by_lam'][k][i] for x in ok) for i in range(len(GRID3))] for k in ok[0]['by_lam']}
    comb['mean'] = {k: round(sum(x['mean'][k] * x['reach']['k'] for x in ok) / max(1, sum(x['reach']['k'] for x in ok)), 5)
                    for k in ok[0]['mean']}
    return comb


# ------------------------------------------------------------------------------------------------ plans
G = m.G
NEWLAWS = ('fav80', 'fav85', 'pm89')
CALS = (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run'))


def plan_m3_class():
    """The cycle-2 class grid (25 dependence x 3 calendars x 2 fills x theta {0, 0.10}, m = 17) on the three NEW CORE price laws."""
    cells = []
    for dep in m.DEPS(True):
        for pr in NEWLAWS:
            for cal in CALS:
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=17, cap=cap, th=th, pr=pr, **cal, **dep))
    return cells


def plan_m3_mix():
    """Two-point price mixtures: share 10 / 50 / 90 % of a point mass at 0.89, the rest U(0.35, 0.80)."""
    cells = []
    deps = [dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='mk', pp=0.9, rv=0.10),
            dict(pk='box', pp=30, rv=0.05), dict(pk='box', pp=30, rv=0.10)]
    for pr in ('pmmix10', 'pmmix50', 'pmmix90'):
        for dep in deps:
            for cal in (dict(P=0), dict(P=30, lay='run')):
                for th in (0.0, 0.10):
                    cells.append(G(m=17, cap='thin', th=th, pr=pr, **cal, **dep))
    return cells


def plan_m3_m35():
    cells = []
    deps = [dict()] + [dict(pk='ar', pp=0.9, rv=rv) for rv in (0.02, 0.05, 0.10)] + \
        [dict(pk='mk', pp=0.9, rv=rv) for rv in (0.05, 0.10)] + [dict(pk='box', pp=30, rv=rv) for rv in (0.05, 0.10)]
    for dep in deps:
        for pr in NEWLAWS:
            for cal in (dict(P=0), dict(P=30, lay='rand')):
                for cap in ('thin', 'full'):
                    cells.append(G(m=35, cap=cap, th=0.0, pr=pr, **cal, **dep))
                    cells.append(G(m=35, cap=cap, th=0.10, pr=pr, **cal, **dep))
                cells.append(G(m=17, cap='thin', th=0.05, pr=pr, **cal, **dep))
    return cells


def plan_m3_geo():
    cells = []
    deps = [dict(), dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='box', pp=30, rv=0.05)]
    for D in (60, 90):
        for dep in deps:
            for pr in NEWLAWS:
                for th in (0.0, 0.10):
                    cells.append(G(D=D, th=th, pr=pr, **dep))
    for pk in ('hemi', 'stn'):
        for rv in (0.05, 0.10):
            for pr in NEWLAWS:
                for th in (0.0, 0.10):
                    cells.append(G(th=th, pr=pr, pk=pk, pp=0.9, rv=rv))
    return cells


def plan_m3_astra():
    """Astra @8874dc54 M3 counterexamples verbatim (trailing mean 30, rv 0.10, m 17) and their price-law neighbours."""
    b = dict(pk='box', pp=30, rv=0.10)
    return [
        G(cap='full', th=0.10, pr='fav85', P=30, lay='run', **b),            # 0.0587 @100k, cycle-2 lambda
        G(cap='thin', th=0.10, pr='fav85', P=30, lay='run', **b),            # 0.0557
        G(cap='full', th=0.10, pr='fav85', P=0, **b),                        # 0.0523 (no pauses)
        G(cap='thin', th=0.0, pr='fav85', P=30, lay='run', **b),             # T1a 0.0262
        G(cap='thin', th=0.10, pr='fav80', P=30, lay='run', **b),            # 0.0506
        G(cap='full', th=0.10, pr='fav85', P=30, lay='rand', **b),           # 0.0522
        G(cap='thin', th=0.10, pr='pm89', P=30, lay='run', **b),
        G(cap='thin', th=0.0, pr='pm89', P=30, lay='run', **b),
        G(cap='thin', th=0.0, pr='fav80', P=30, lay='run', **b),
        G(cap='full', th=0.0, pr='fav85', P=30, lay='run', **b),
    ]


def plan_m3_probe():
    """Post-calibration price-law sensitivity at the adopted lambda: in-between laws (inside the stated class by monotone
    interpolation, tested) and laws OUTSIDE the stated class (disclosure only): pm899, pm85, pm80, fav88, fav60."""
    cells = []
    deps = [dict(pk='box', pp=30, rv=0.10), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='mk', pp=0.9, rv=0.10)]
    for pr in ('pm899', 'pm85', 'pm80', 'fav88', 'fav60'):
        for dep in deps:
            for th in (0.0, 0.10):
                cells.append(G(cap='thin', th=th, pr=pr, P=30, lay='run', **dep))
    return cells


P1_LAWS = ('mid', 'favmix', 'fav', 'fav80', 'fav85', 'pm89')
P1_DESIGNS = ((17, 'thin'), (17, 'full'), (35, 'thin'), (35, 'full'), (55, 'thin'), (55, 'full'))
P1_THETA = (0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.20, 0.25, 0.30)
P1_KAPPA = (-0.03, -0.05, -0.07, -0.09, -0.12, -0.16, -0.20, -0.25)


def plan_p1_t2():
    """P1 derive (T2): power curve of the calibrated T2 over the GO-feasible laws; no persistence, no pauses, no GO filter."""
    cells = []
    for pr in P1_LAWS:
        for mm, cap in P1_DESIGNS:
            for th in P1_THETA:
                cells.append(G(m=mm, cap=cap, th=th, pr=pr, go='none'))
    return cells


def plan_p1_neg():
    """P1 derive (NEG): power curve of NEG over kappa_core in P1_KAPPA (theta = kappa / mean CORE ask of the law)."""
    cells = []
    for pr in P1_LAWS:
        for mm, cap in P1_DESIGNS:
            for kp in P1_KAPPA:
                cells.append(G(m=mm, cap=cap, th=round(kp / LAW_MEAN[pr], 6), pr=pr, go='none'))
    return cells


def plan_p1_hi():
    """Best-case throughput (m 80 / 96 trades per date; the engine caps a date at 2 x 48 = 96): NEG power at kappa -0.07 / -0.12."""
    cells = []
    for pr in ('mid', 'fav', 'fav85'):
        for mm in (80, 96):
            for cap in ('thin', 'full'):
                for kp in (-0.07, -0.12, -0.20):
                    cells.append(G(m=mm, cap=cap, th=round(kp / LAW_MEAN[pr], 6), pr=pr, go='none'))
    return cells


def plan_p1_verify():
    """Power AT THE DESIGN'S OWN theta_PCE under the old (Z80) and the new multiplier, theta-side GO only; theta := the
    replication's own theta_PCE.  Laws x m in {17, 35, 55, 96} x fills."""
    cells = []
    for rule in ('old', 'new'):
        for pr in P1_LAWS:
            for mm in (17, 35, 55, 96):
                for cap in ('thin', 'full'):
                    cells.append(G(m=mm, cap=cap, th='pce_' + rule, pr=pr, go='th_' + rule))
    return cells


PLANS = dict(m3_class=plan_m3_class, m3_mix=plan_m3_mix, m3_m35=plan_m3_m35, m3_geo=plan_m3_geo, m3_astra=plan_m3_astra,
             m3_probe=plan_m3_probe, p1_t2=plan_p1_t2, p1_neg=plan_p1_neg, p1_hi=plan_p1_hi, p1_verify=plan_p1_verify)


# ------------------------------------------------------------------------------------------------ OP-only GO rates
GO_LAWS = ('mid', 'favmix', 'fav', 'fav80', 'fav85', 'pm89', 'tail1', 'tail3', 'wide', 'low')
GO_M = (8, 12, 17, 25, 35, 55, 80, 96)


def go_cells():
    return [dict(S=48, m=mm, cap=cap, pr=pr) for pr in GO_LAWS for mm in GO_M for cap in ('thin', 'full')]


def run_go_cell(idx, g, reps, K):
    rng = np.random.default_rng(np.random.SeedSequence([SEED_BASE, PLAN_CODE['p1_go'], idx, 0]))
    S = g['S']
    ct = dict(old=0, th_new=0, k_new=0, new=0, rsn_pce=0, rsn_kappa=0, rsn_stn=0)
    vals = dict(se0=[], se0k=[], pce_old=[], pce_new=[])
    for _ in range(reps):
        n_op = int(np.minimum(rng.poisson(g['m'], OPD), 2 * S).sum())
        act = rng.gamma(2.0, 1.0, S); act /= act.sum()
        st_op = rng.choice(S, n_op, p=act)
        c_op = m.prices(rng, g['pr'], n_op); C_op = m.fills(rng, g['cap'], n_op)
        d = design_stats(c_op, C_op, st_op, S, K['z_eff'])
        if d is None:
            ct['rsn_pce'] += 1
            continue
        vals['se0'].append(d['se0']); vals['se0k'].append(d['se0k']); vals['pce_old'].append(d['pce_old']); vals['pce_new'].append(d['pce_new'])
        ct['old'] += int(go_pass('old', d, K)); ct['th_new'] += int(go_pass('th_new', d, K))
        ct['k_new'] += int(d['se0k'] <= K['se_kappa_ceiling'])
        ct['new'] += int(go_pass('new', d, K))
        if d['pce_new'] > 0.10:
            ct['rsn_pce'] += 1
        elif d['se0k'] > K['se_kappa_ceiling']:
            ct['rsn_kappa'] += 1
        elif not d['stn']:
            ct['rsn_stn'] += 1
    q = lambda a: [round(float(np.quantile(a, x)), 5) for x in (0.05, 0.5, 0.95)] if a else None
    return dict(plan='p1_go', idx=idx, g=g, reps=reps, counts=ct, se0_q=q(vals['se0']), se0k_q=q(vals['se0k']),
                pce_old_q=q(vals['pce_old']), pce_new_q=q(vals['pce_new']))


# ------------------------------------------------------------------------------------------------ harness
def _job(a):
    plan, idx, g, reps, stream, K = a
    if plan == 'p1_go':
        return json.dumps(run_go_cell(idx, g, reps, K))
    return json.dumps(run_cell(plan, idx, g, reps, stream, K))


def done_keys(path):
    keys = set()
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                try:
                    x = json.loads(line)
                except ValueError:
                    continue                               # a torn last line from a killed run is recomputed
                keys.add((x['plan'], x['idx'], x['reps'], bool(x.get('combined_streams'))))
    return keys


def check():
    """Engine-equivalence: one_rep_p1 (mode 'old', theta numeric) reproduces the cycle-2 one_rep records exactly."""
    ok = True
    for i, g in enumerate([G(cap='thin', th=0.10, pr='fav', pk='box', pp=30, rv=0.10, P=30, lay='run'),
                           G(cap='full', th=0.0, pr='mid', pk='mk', pp=0.9, rv=0.05),
                           G(cap='thin', th=0.10, pr='favmix', pk='ar', pp=0.9, rv=0.10, P=30, lay='rand'),
                           G(m=35, cap='full', th=0.10, pr='tail3')]):
        r1 = np.random.default_rng(np.random.SeedSequence([1, i])); r2 = np.random.default_rng(np.random.SeedSequence([1, i]))
        for _ in range(60):
            a = m.one_rep(r1, g, False)
            _, b = one_rep_p1(r2, g, None)
            if (a is None) != (b is None):
                ok = False; break
            if a is not None:
                for k in ('th', 'thW', 'kap', 'kt', 'thc', 'w', 'Mt', 'gates', 'H_A', 'HkA', 'HcA', 'H_R0', 'Hk5', 'ntail'):
                    if a[k] != b[k]:
                        ok = False; print('MISMATCH', i, k, a[k], b[k])
    # gate equivalence against m.go_check on random OP draws
    rng = np.random.default_rng(5)
    for _ in range(300):
        pr = ('mid', 'fav', 'tail1', 'wide')[int(rng.integers(4))]
        mm = int(rng.integers(8, 60)); n = int(rng.poisson(mm * OPD)) + 1
        c = m.prices(rng, pr, n); C = m.fills(rng, 'thin', n); st = rng.choice(48, n)
        d = design_stats(c, C, st, 48, 3.0)
        a = m.go_check(c, C, st, 48)
        b = go_pass('old', d, None) if d else False
        if a != b:
            ok = False; print('GO MISMATCH', pr, mm)
    print('CHECK', 'PASS' if ok else 'FAIL')
    return ok


if __name__ == '__main__':
    from multiprocessing import Pool
    args = sys.argv[1:]
    if args[0] == 'check':
        sys.exit(0 if check() else 1)
    out = args[args.index('--out') + 1]
    args = [a for i, a in enumerate(args) if a != '--out' and (i == 0 or args[i - 1] != '--out')]
    procs = int(os.environ.get('WF_PROCS', '4'))
    K = load_consts()
    if args[0] == 'cell':
        plan, idx, reps = args[1], int(args[2]), int(args[3])
        g = PLANS[plan]()[idx]
        if (plan, idx, reps, True) in done_keys(out):
            sys.exit(0)
        jobs = [(plan, idx, g, reps // 5, s, K) for s in (1, 2, 3, 4, 5)]
        with Pool(procs) as pool:
            parts = [json.loads(x) for x in pool.map(_job, jobs)]
        with open(out, 'a') as f:
            f.write(json.dumps(combine(parts, plan, idx, g)) + '\n')
        sys.exit(0)
    plan = args[1]
    reps = int(args[2]) if len(args) > 2 else 20000
    if plan == 'p1_go':
        cells = go_cells()
    else:
        cells = PLANS[plan]()
    seen = done_keys(out)
    jobs = [(plan, i, g, reps, 0, K) for i, g in enumerate(cells) if (plan, i, reps, False) not in seen]
    print('plan', plan, 'cells', len(cells), 'to run', len(jobs), flush=True)
    with Pool(procs) as pool, open(out, 'a') as f:
        for line in pool.imap(_job, jobs):
            f.write(line + '\n'); f.flush()
