"""Weather Forward V2 — D4-C3-M1 source-bound calibration (run G), 2026-10-01.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.

Purpose: Astra finding M1 (@5bb57eb2): T2's lower bound L_W = theta_hat - t_{df,0.95} SE_CR(theta_hat) (two-way CR,
max-of-three, 5-date blocks x ICAO, df = min(G_B, G_S) - 1) undercovers theta_W when date dependence persists across the
5-date blocks (spec 9 names the mechanism). This script (fresh code, fresh seeds; independent of Astra's astra_lw.py and of
run F) reproduces M1, validates candidate repairs over a declared persistence class, and measures their power cost.

DECLARED BEFORE ANY RUN (not chosen from results):
  RULE R0 (frozen V2 / R3 engine; retired for L_W by this repair):
      L_W = theta_hat - t_{df5,0.95} SE_2w(5)
  RULE RM (first repair candidate):
      L_W = theta_hat - max_{b in {5, 10, 20}} t_{df_b,0.95} SE_2w(b)
      SE_2w(b) = sqrt(max(V_B(b), V_S, V_B(b) + V_S - V_BS(b))) exactly as spec 8.1, with date block
      block_b(D) = floor((D - D_0) / b) calendar days; df_b = min(G_B(b), G_S) - 1 (G = non-empty clusters).
  PERSISTENCE CLASS (declared): latent Gaussian copula (date, station, cell) = (0.05, 0.05, 0.10) [V2 simulation
      dependence] plus a stationary daily AR(1) date regime e_t = phi e_{t-1} + sqrt(1 - phi^2) z_t shared by every
      trade of date t, added on the latent scale with variance rv:
      phi in {0.5, 0.7, 0.8, 0.9} x rv in {0.02, 0.05, 0.10}, plus the no-persistence baseline (rv = 0);
      14 OP + 120 window dates, 48 stations gamma(2) activity, Poisson(m) trades/date (<= 96), m in {17, 35},
      fills thin C ~ U(5, 25) or full C = 50, CORE prices c ~ U(0.35, 0.80), p = min(1, c (1 + theta)),
      theta in {0, 0.05, 0.10}.
  PASS CRITERION (per cell, every rule reported): joint miss P(reach AND L_W > theta_W) <= 0.05 and, at theta = 0,
      P(reach AND positive REALIZED_WINDOW claim AND theta_W <= 0) <= 0.05, within Monte Carlo error: a point estimate
      above 0.05 passes only if 0.05 lies inside its 95% MC interval after a re-run at >= 100,000 replications.
      reach = GO (OP, spec 10.3) AND INFO_SUFFICIENT (IF2-IF5, spec 11.4); theta_W exact from the true p.
  OUTSIDE THE CLASS (disclosure only, never claimed): phi in {0.95, 0.97}, rv up to 0.20.

PRELIMINARY RUN (disclosed, not hidden): RM was run first on the first 45 class cells (same seeds as below). It passed for
  phi <= 0.8 and FAILED at phi = 0.9 (joint miss 0.054-0.070, MC intervals above 0.05). Two comparators were then declared,
  before their own first run; no constant of RM was changed:
  RW (wider blocks):  L_W = theta_hat - max_{b in {5, 10, 20, 30}} t_{df_b,0.95} SE_2w(b)   (30 = W, the 30-date
                      trailing-bias window whose seasonal lag is the persistence mechanism spec 9 names)
  RE (two-way EWC):   date sums E_t over the T calendar days of the window, K = max(2, floor(T omega_h / pi)) cosine terms
                      sqrt(2/T) cos(pi k (t + 1/2) / T), omega_h = the AR(1) half-power frequency at phi = 0.9 (K = 4 at
                      T = 120, 2 at T = 60); V_D = T mean_k(Lambda_k^2) / Q^2, V_SD the same on station-by-date sums, V_S as
                      spec 8.1; SE = sqrt(max(V_D, V_S, V_D + V_S - V_SD)); reference t_{min(K, G_S - 1)} (fixed-K).
  Selection criterion (declared with the comparators): validity over the whole declared class first; among valid rules,
  power and behaviour at the information floor. Every cell reports all four rules on the same replications.
  OUTCOME (spec 8.1b): RW is the only rule valid over the whole class and is ADOPTED as the D4-C3-M1 rule; RM (valid only
  for phi <= 0.8) and RE (valid only for phi <= 0.8) are published comparators; R0 is the retired R3 engine.
  Frozen surfaces measured on the same replications (disclosure only; not changed by this repair): T1a (kappa_core > 0 at
  0.025), NEG (0.025), U_W (spec 8.5, one-sided 0.975 core bound; TAIL empty here) — all with 5-date blocks.

Usage:
  python3 <this file> repro [REPS]     # Astra M1 counterexample cells (same ids and seeds as in the class plan; default 20000)
  python3 <this file> class [REPS]     # the declared persistence class grid (default 20000)
  python3 <this file> boundary [REPS]  # boundary geometries (default 20000)
  python3 <this file> stress [REPS]    # outside-class disclosure cells (default 20000)
  python3 <this file> c3 [REPS]        # Astra C3 regression on run F's loss-date process, every rule (default 20000)
  python3 <this file> power [REPS]     # T2 power at the design's theta_PCE, all rules (default 20000)
  python3 <this file> cell ID REPS     # one cell by id, independent streams 1-4 of REPS/4 each (>= 100,000 re-runs)
Requires numpy and scipy.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
from scipy import stats
from scipy.signal import lfilter
from scipy.special import ndtr

ERT, CUT, Z80 = 0.02, 0.04, 2.4865
OPD = 14
RHO = (0.05, 0.05, 0.10)
BLOCKS = (5, 10, 20)             # rule RM
BLOCKS_WIDE = (5, 10, 20, 30)    # comparator RW
BLOCKS_ALL = (5, 10, 20, 30)
RULES = ('R0', 'RM', 'RW', 'RE')
SEED_BASE = 20261017            # SeedSequence([SEED_BASE, cell_id]); distinct from run D/E/F and Astra seeds
_TQ = {}


def tq(p, df):
    k = (p, df)
    if k not in _TQ:
        _TQ[k] = float(stats.t.ppf(p, df))
    return _TQ[k]


# ------------------------------------------------------------------------------------------------ process
def gen(rng, g):
    D, S, m = g['D'], g['S'], g['m']
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    if g.get('dom_st'):                       # one station carries a fixed share of activity
        act = act * (1.0 - g['dom_st']) / (1.0 - act[0]); act[0] = g['dom_st']
        act /= act.sum()
    T = OPD + D
    cnt = np.minimum(2 * S, rng.poisson(m, T))
    if g.get('dom_date'):                     # one window date at the 2S-event cap
        cnt[OPD + int(rng.integers(D))] = 2 * S
    date = np.repeat(np.arange(T), cnt)
    N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(0.35, 0.80, N)
    C = rng.uniform(5.0, 25.0, N) if g['cap'] == 'thin' else np.full(N, 50.0)
    p = np.minimum(1.0, c * (1.0 + g['th']))
    op = date < OPD
    w = ~op
    return (dict(date=date[w] - OPD, st=st[w], c=c[w], C=C[w], p=p[w]),
            dict(st=st[op], c=c[op], C=C[op]))


def draw_y(rng, w, g):
    D, S = g['D'], g['S']
    date, st = w['date'], w['st']
    cell = date * S + st
    _, ci = np.unique(cell, return_inverse=True)
    z = (math.sqrt(RHO[0]) * rng.standard_normal(D)[date] + math.sqrt(RHO[1]) * rng.standard_normal(S)[st]
         + math.sqrt(RHO[2]) * rng.standard_normal(ci.max() + 1)[ci])
    rest = 1.0 - sum(RHO)
    rv = g.get('rv', 0.0)
    if rv > 0:
        phi = g['phi']
        u = rng.standard_normal(D)
        e = np.empty(D); e[0] = u[0]
        if D > 1:
            e[1:] = lfilter([math.sqrt(1.0 - phi * phi)], [1.0, -phi], u[1:], zi=[phi * u[0]])[0]
        z = z + math.sqrt(rv) * e[date]
        rest -= rv
    z = z + math.sqrt(rest) * rng.standard_normal(date.size)
    return (ndtr(z) < w['p']).astype(float)


# ------------------------------------------------------------------------------------------------ engine (spec 8.1)
def cr2w(r, blk, st, Q, S):
    """Two-way CR, max-of-three, CR1 factors per dimension; returns (SE, df)."""
    nb = blk.max() + 1
    out = []
    for key, size in ((blk, nb), (st, S), (blk * S + st, nb * S)):
        cnt = np.bincount(key, minlength=size)
        G = int(np.count_nonzero(cnt))
        s = np.bincount(key, weights=r, minlength=size)
        out.append((G / (G - 1.0) * float(s @ s) / (Q * Q), G))
    (VB, GB), (VS, GS), (VBS, _) = out
    return math.sqrt(max(VB, VS, VB + VS - VBS)), min(GB, GS) - 1, (VB, VS, VBS)


def ready(op, S):
    c, C, st = op['c'], op['C'], op['st']
    mbar = c.size / OPD
    s2 = c.size * float((C * C * (1 - c) / c).sum()) / float(C.sum()) ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt(float((c[core] * (1 - c[core])).mean()) * deff / (120 * core.sum() / OPD))
    k = np.bincount(st, minlength=S); k = k[k > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    go = bool(pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and k.sum() ** 2 / float((k * k).sum()) >= 15)
    return pce, go


PHI_MAX = 0.9                    # upper edge of the declared persistence class (used only by comparator RE)
OMEGA_H = math.acos((1 + PHI_MAX ** 2 - 2 * (1 - PHI_MAX) ** 2) / (2 * PHI_MAX))   # AR(1) half-power frequency
_BASIS = {}


def ewc_K(T):
    """Comparator RE: number of cosine terms whose frequencies pi k / T stay inside the AR(1) half-power band at PHI_MAX."""
    return max(2, int(math.floor(T * OMEGA_H / math.pi)))


def ewc2w(r, date, st, Q, S, T):
    """Comparator RE: two-way equally-weighted-cosine (orthonormal series) HAR estimator on date sums x station CR,
    max-of-three as spec 8.1; reference t_{min(K, G_S - 1)}."""
    K = ewc_K(T)
    if (T, K) not in _BASIS:
        t = np.arange(T) + 0.5
        _BASIS[(T, K)] = np.sqrt(2.0 / T) * np.cos(np.pi * np.outer(np.arange(1, K + 1), t) / T)
    Bm = _BASIS[(T, K)]
    Et = np.bincount(date, weights=r, minlength=T)
    lam = Bm @ Et
    Vd = T * float(lam @ lam) / K / (Q * Q)
    Est = np.bincount(st * T + date, weights=r, minlength=S * T).reshape(S, T)
    lam_s = Est @ Bm.T
    Vsd = T * float((lam_s * lam_s).sum()) / K / (Q * Q)
    cnt = np.bincount(st, minlength=S); GS = int(np.count_nonzero(cnt))
    ss = np.bincount(st, weights=r, minlength=S)
    VS = GS / (GS - 1.0) * float(ss @ ss) / (Q * Q)
    return math.sqrt(max(Vd, VS, Vd + VS - Vsd)), min(K, GS - 1)


def analyse(w, y, S, T):
    c, C, date, st = w['c'], w['C'], w['date'], w['st']
    n = C / c
    Q = float(C.sum())
    N = n * (y - c)
    th = float(N.sum()) / Q
    r = N - th * C
    half = {}                                       # one-sided 95% half-widths t_{df_b,0.95} SE_2w(b)
    se5 = df5 = None
    for b in BLOCKS_ALL:
        se, df, _ = cr2w(r, date // b, st, Q, S)
        half[b] = tq(0.95, df) * se
        if b == 5:
            se5, df5 = se, df
    se_e, df_e = ewc2w(r, date, st, Q, S, T)
    L = dict(R0=th - half[5],                                   # frozen V2 / R3 bound (retired for L_W)
             RM=th - max(half[b] for b in BLOCKS),              # adopted repair candidate (declared first)
             RW=th - max(half[b] for b in BLOCKS_WIDE),         # comparator: adds 30-date blocks
             RE=th - tq(0.95, df_e) * se_e,                     # comparator: two-way EWC
             B10=th - half[10], B20=th - half[20])              # diagnostics: single block lengths
    # information axis (frozen; 5-date blocks) — core = all trades here (c >= 0.35)
    blk5 = date // 5
    x = y - c
    k = float(x.mean())
    sek, dfk, _ = cr2w(x - k, blk5, st, float(x.size), S)
    viid = x.size / (x.size - 1.0) * float(((x - k) ** 2).sum()) / x.size ** 2
    cnt = np.bincount(st, minlength=S); cnt = cnt[cnt > 0]
    info = bool(np.unique(blk5).size >= 12 and cnt.size >= 25 and cnt.sum() ** 2 / float((cnt * cnt).sum()) >= 15
                and sek <= 0.025 and sek * sek / viid <= 6)
    T1a = k - tq(0.975, dfk) * sek > 0
    NEG = k + tq(0.975, dfk) * sek < 0
    U_W = th + tq(0.975, df5) * se5                 # spec 8.5 with an empty TAIL (theta_core = theta), frozen R1
    # gates (spec 17.2; G3 is implied: every synthetic settlement is NOAA-mode and T2 AND theta_hat >= ERT gives theta_hat > 0)
    cc = c + 0.01
    g1 = float(((C / cc) * (y - cc)).sum()) / Q > 0
    pos = np.maximum(N, 0.0); gross = float(pos.sum())
    g2 = bool(gross > 0 and (float(N.sum()) - float(np.sort(N)[-5:].sum())) / Q > 0
              and np.bincount(date, weights=pos).max() <= 0.25 * gross
              and np.bincount(st, weights=pos, minlength=S).max() <= 0.20 * gross)
    thW = float((n * (w['p'] - c)).sum()) / Q
    return dict(th=th, thW=thW, L=L, info=info, T1a=T1a, NEG=NEG, U_W=U_W, gates=bool(g1 and g2))


# ------------------------------------------------------------------------------------------------ Monte Carlo
def mc(k, n):
    if n == 0:
        return dict(p=None, se=None, ci=None, k=0, n=0)
    p = k / n
    se = math.sqrt(max(p * (1 - p), 0.0) / n)
    return dict(p=round(p, 5), se=round(se, 5), ci=[round(max(0.0, p - 1.96 * se), 5), round(min(1.0, p + 1.96 * se), 5)],
                k=int(k), n=int(n))


def run_cell(cell, reps, stream=0):
    g = cell['g']
    seed = [SEED_BASE, cell['id']] + ([stream] if stream else [])
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    K = {key: 0 for key in ('go', 'info', 'reach', 'T1a', 'NEG', 'UWmiss')}
    for rule in RULES + ('B10', 'B20'):
        K['miss_' + rule] = 0
    for rule in RULES:
        for key in ('pos_', 'fpos_', 'sup_'):
            K[key + rule] = 0
    pces = []
    for _ in range(reps):
        w, op = gen(rng, g)
        pce, go = ready(op, g['S'])
        y = draw_y(rng, w, g)
        o = analyse(w, y, g['S'], g['D'])
        reach = go and o['info']
        pces.append(pce)
        K['go'] += go; K['info'] += o['info']; K['reach'] += reach
        if not reach:
            continue
        for rule, Lr in o['L'].items():
            K['miss_' + rule] += Lr > o['thW']                  # sampling miss of the source bound
            if rule in RULES:
                pr = Lr > 0 and o['th'] >= ERT                  # REALIZED_WINDOW_VALUE_SUPPORTED or NOT_ROBUST
                K['pos_' + rule] += pr
                K['fpos_' + rule] += pr and o['thW'] <= 0       # false positive realised-window claim
                K['sup_' + rule] += pr and o['gates']           # REALIZED_WINDOW_VALUE_SUPPORTED
        K['T1a'] += o['T1a']; K['NEG'] += o['NEG']; K['UWmiss'] += o['U_W'] < o['thW']
    res = {k: mc(v, reps) for k, v in K.items()}
    for rule in RULES:
        res['miss_given_reach_' + rule] = mc(K['miss_' + rule], K['reach'])
    return dict(id=cell['id'], name=cell['name'], g=g, reps=reps, seed=seed,
                pce_median=float(np.median(pces)), **res)


# ------------------------------------------------------------------------------------------------ plans
BASE = dict(D=120, S=48, m=17, cap='thin', th=0.0, rv=0.0, phi=0.0)


def G(**kw):
    g = dict(BASE); g.update(kw); return g


def class_plan():
    cells = []
    i = 0
    for m in (17, 35):
        for cap in ('thin', 'full'):
            for th in (0.0, 0.05, 0.10):
                cells.append(dict(id=1000 + i, name=f'baseline m={m} {cap} th={th} (no persistence)',
                                  g=G(m=m, cap=cap, th=th))); i += 1
                for phi in (0.5, 0.7, 0.8, 0.9):
                    for rv in (0.02, 0.05, 0.10):
                        cells.append(dict(id=1000 + i, name=f'AR phi={phi} rv={rv} m={m} {cap} th={th}',
                                          g=G(m=m, cap=cap, th=th, phi=phi, rv=rv))); i += 1
    return cells


def repro_ids():
    """Astra M1 cells (by name in the class plan): L21 (size, thin), L23 (full, th 0.10), L17 (thin, th 0.05),
    phi 0.9 / rv 0.10 thin th 0.05 and th 0"""
    want = ['AR phi=0.8 rv=0.05 m=17 thin th=0.0', 'AR phi=0.8 rv=0.05 m=17 full th=0.1',
            'AR phi=0.8 rv=0.05 m=17 thin th=0.05', 'AR phi=0.9 rv=0.1 m=17 thin th=0.05',
            'AR phi=0.9 rv=0.1 m=17 thin th=0.0']
    by = {c['name']: c for c in class_plan()}
    return [by[n] for n in want]


def boundary_plan():
    out = []
    specs = [
        ('min geometry 60/25 m=17 thin', dict(D=60, S=25)),
        ('min geometry 60/25 m=35 full', dict(D=60, S=25, m=35, cap='full')),
        ('dominant station 20% m=17 thin', dict(dom_st=0.20)),
        ('one dominant date (96 trades) m=17 thin', dict(dom_date=True)),
        ('thick m=35 full', dict(m=35, cap='full')),
        ('thick m=35 thin', dict(m=35, cap='thin')),
    ]
    i = 0
    for name, kw in specs:
        for th in (0.0, 0.10):
            for per in ((0.0, 0.0), (0.8, 0.05), (0.9, 0.10)):
                gg = G(th=th, **kw)
                if per[1] > 0:
                    gg.update(phi=per[0], rv=per[1])
                tag = 'no persistence' if per[1] == 0 else f'AR phi={per[0]} rv={per[1]}'
                out.append(dict(id=2000 + i, name=f'{name} th={th} {tag}', g=gg)); i += 1
    return out


def stress_plan():
    out = []
    i = 0
    for phi, rv in ((0.95, 0.05), (0.95, 0.10), (0.97, 0.05), (0.97, 0.10), (0.9, 0.20)):
        for m, cap in ((17, 'thin'), (17, 'full'), (35, 'full')):
            out.append(dict(id=3000 + i, name=f'OUTSIDE CLASS AR phi={phi} rv={rv} m={m} {cap} th=0.0',
                            g=G(m=m, cap=cap, th=0.0, phi=phi, rv=rv))); i += 1
    return out


def all_cells():
    return {c['id']: c for c in class_plan() + boundary_plan() + stress_plan()}


# ------------------------------------------------------------------------------------------------ power at theta_PCE
def power_plan():
    """D1 disclosure: T2 power at the design's own theta_PCE (spec 10.2; 0.09 / 0.08 / 0.07 / 0.07 for m = 17 thin /
    17 full / 35 thin / 35 full in this synthetic process) and at 0.12 / 0.15 (to locate the 80%-power effect of each
    rule), without persistence; theta_PCE also under mild persistence (phi 0.8, rv 0.05)."""
    out = []
    i = 0
    for (m, cap, pce) in ((17, 'thin', 0.09), (17, 'full', 0.08), (35, 'thin', 0.07), (35, 'full', 0.07)):
        for th, per in ((pce, (0.0, 0.0)), (0.12, (0.0, 0.0)), (0.15, (0.0, 0.0)), (pce, (0.8, 0.05))):
            gg = G(m=m, cap=cap, th=th)
            if per[1] > 0:
                gg.update(phi=per[0], rv=per[1])
            tag = 'no persistence' if per[1] == 0 else f'AR phi={per[0]} rv={per[1]}'
            lab = f'theta_PCE={pce}' if th == pce else f'theta={th}'
            out.append(dict(id=5000 + i, name=f'power at {lab} m={m} {cap} {tag}', g=gg)); i += 1
    return out


def run_power(cell, reps):
    g = cell['g']
    seed = [SEED_BASE, cell['id']]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    K = dict(reach=0, go=0)
    for rule in RULES:
        K['T2_' + rule] = 0; K['T2_reach_' + rule] = 0; K['sup_' + rule] = 0
    pces = []
    for _ in range(reps):
        w, op = gen(rng, g)
        pce, go = ready(op, g['S'])
        y = draw_y(rng, w, g)
        o = analyse(w, y, g['S'], g['D'])
        reach = go and o['info']
        pces.append(pce); K['go'] += go; K['reach'] += reach
        for rule in RULES:
            t2 = o['L'][rule] > 0
            K['T2_' + rule] += t2                                        # T2 alone (the D1 / theta_PCE power notion)
            K['T2_reach_' + rule] += t2 and reach
            K['sup_' + rule] += t2 and reach and o['th'] >= ERT and o['gates']
    return dict(id=cell['id'], name=cell['name'], g=g, reps=reps, seed=seed, pce_median=float(np.median(pces)),
                **{k: mc(v, reps) for k, v in K.items()})


def _pjob(a):
    return json.dumps(run_power(*a))


# ------------------------------------------------------------------------------------------------ C3 regression
def c3_regression(reps):
    """Astra C3 cells on run F's own loss-date process (imported unchanged from the committed run F script), analysed
    with every rule. Structural (not measured): the spec 17.2 / 17.3 vocabulary has no unconditional prospective label and
    no exclusion label, so none can be issued; measured: the window claims and the conditional claim at the true eps."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, 'WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py')
    spec = importlib.util.spec_from_file_location('runF', path)
    F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
    rows = []
    for j, sc in enumerate(F.c3_plan()):
        rng = np.random.default_rng(np.random.SeedSequence([SEED_BASE, 4000 + j]))
        tP = F.theta_P(sc); eps = F.cost_share_bad(sc)
        K = dict(reach=0)
        for rule in RULES:
            for key in ('pos_', 'fpos_', 'miss_', 'cond_false_'):
                K[key + rule] = 0
        for _ in range(reps):
            w, op = F.draw(rng, sc); _, go = F.readiness(op)
            y = F.outcomes(rng, w)
            o = analyse(dict(date=w['date'], st=w['st'], c=w['c'], C=w['C'], p=w['p']), y, F.S, F.WD)
            reach = go and o['info']
            K['reach'] += reach
            if not reach:
                continue
            for rule in RULES:
                Lr = o['L'][rule]
                pr = Lr > 0 and o['th'] >= ERT                     # REALIZED_WINDOW_VALUE_SUPPORTED or NOT_ROBUST
                K['pos_' + rule] += pr
                K['fpos_' + rule] += pr and o['thW'] <= 0
                K['miss_' + rule] += Lr > o['thW']
                K['cond_false_' + rule] += (1 - eps) * Lr - eps > tP + 1e-12   # conditional claim false at true eps, delta 0
        rows.append(dict(name=sc['name'], theta_P=round(tP, 4), eps_true=round(eps, 4), reps=reps,
                         seed=[SEED_BASE, 4000 + j], **{k: mc(v, reps) for k, v in K.items()}))
    return rows


def _job(a):
    cell, reps, stream = a
    return json.dumps(run_cell(cell, reps, stream))


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'c3':
        for row in c3_regression(int(sys.argv[2]) if len(sys.argv) > 2 else 20000):
            print(json.dumps(row), flush=True)
        sys.exit()
    if mode == 'power':
        from multiprocessing import Pool
        with Pool(int(os.environ.get('WF_PROCS', '4'))) as pool:
            for line in pool.imap(_pjob, [(c, int(sys.argv[2]) if len(sys.argv) > 2 else 20000) for c in power_plan()]):
                print(line, flush=True)
        sys.exit()
    if mode == 'cell':                     # independent stream 1, split into 4 chunks (streams 1..4) for the pool
        cell, reps = all_cells()[int(sys.argv[2])], int(sys.argv[3])
        jobs = [(cell, reps // 4, s) for s in (1, 2, 3, 4)]
    else:
        reps = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
        plan = dict(repro=repro_ids, boundary=boundary_plan, stress=stress_plan)
        cells = class_plan() if mode == 'class' else plan[mode]()
        jobs = [(c, reps, 0) for c in cells]
    from multiprocessing import Pool
    with Pool(int(os.environ.get('WF_PROCS', '4'))) as pool:
        lines = []
        for line in pool.imap(_job, jobs):
            lines.append(line)
            if mode != 'cell':
                print(line, flush=True)
    if mode == 'cell':                     # one combined line: counts summed over the four independent streams
        parts = [json.loads(x) for x in lines]
        comb = dict(id=parts[0]['id'], name=parts[0]['name'], g=parts[0]['g'], reps=sum(x['reps'] for x in parts),
                    seed=[x['seed'] for x in parts], combined_streams=True)
        for key, v in parts[0].items():
            if isinstance(v, dict) and 'k' in v and 'n' in v:
                if key.startswith('miss_given_reach_'):
                    rule = key[len('miss_given_reach_'):]
                    comb[key] = mc(sum(x['miss_' + rule]['k'] for x in parts), sum(x['reach']['k'] for x in parts))
                else:
                    comb[key] = mc(sum(x[key]['k'] for x in parts), sum(x[key]['n'] for x in parts))
        print(json.dumps(comb), flush=True)
