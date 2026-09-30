"""Weather Forward V2 — D4-C2 repair validation (prospective estimand vs unsampled rare tail arrivals), 2026-09-30.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.

Bounded reproducibility file for D4 repair R2 (spec 8.5, 8.5b, 17). It
  1. reproduces Astra's C2 counterexample (V2@24d2342 rule E1: U_W < theta_ERT -> NET_VALUE_EXCLUDED) with a fresh,
     independent implementation and fresh seeds;
  2. evaluates the R2-A candidate (arrival-rate upper bound x maximum payoff) and the frozen R2 rule
     (prospective exclusion not identified; realised-window bound kept as a separately labelled report field);
  3. measures prospective confirmation (T2 + theta_hat >= theta_ERT + gates) under rare-arrival alternatives;
  4. prints the deterministic identification ceiling of spec 8.5b.

Prospective process (theta_P = E[N]/E[C], spec 5.1): 14 observation-phase dates followed by 120 window dates; each date
has Poisson(m) executed R* trades at 48 gamma(2) stations, C = 50 USD; CORE c ~ U(0.35, 0.80), p = c (1 + theta_core);
rare TAIL type at all-in cost c_t with win probability p_t arrives either per trade (independent, rate r) or per date
(date-clustered: with probability eta a date is a 'tail date' on which a fraction phi of its trades are the tail type).
Outcomes: latent Gaussian copula (date, station, cell) = (0.05, 0.05, 0.10) (V2 'TRUE').

Usage:
  python3 WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py ceiling            # spec 8.5b identification table (no randomness)
  python3 WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py scenarios [REPS]   # power table 4.6, scenario table (default 4000)
  python3 WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py counts [REPS]      # old false exclusion by observed tail count
  python3 WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py grid [REPS]        # dangerous-region search (default 200 / cell)
  python3 WEATHER_FORWARD_V2_D4_C2_SIM_2026-09-30.py confirm [REPS]     # prospective confirmation under rare losses
Requires numpy and scipy.
"""
import json
import math
import sys

import numpy as np
from scipy import sparse, stats
from scipy.special import ndtr

ERT = 0.02
CUT = 0.04
Z80 = 2.4865
ALPHA = 0.05
C_MIN = 0.001 + 0.05 * 0.001 * 0.999          # all-in cost per share at the 0.001 tick incl. fee (spec 3)
RHO = (0.05, 0.05, 0.10)
OP_DATES, WIN_DATES, S = 14, 120, 48
TQ = stats.t.ppf
TAIL_BINS = [(C_MIN, 0.002), (0.002, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.04)]


# ------------------------------------------------------------------------------------------------ design + truth
def draw(rng, sc):
    """One prospective realisation: OP + window trades, prices, truth p. Returns (window dict, op dict)."""
    D = OP_DATES + WIN_DATES
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), rng.poisson(sc.get('m', 35), D)); N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(0.35, 0.80, N)
    p = c * (1 + sc['th_core'])
    ct, pt = sc.get('c_t', 0.001), sc.get('p_t', 0.0)
    if sc.get('arrival') == 'date':
        tdate = rng.random(D) < sc['eta']
        is_t = tdate[date] & (rng.random(N) < sc.get('phi', 1.0))
    else:
        is_t = rng.random(N) < sc.get('r', 0.0)
    c[is_t] = ct; p[is_t] = pt
    if sc.get('fixed_tail_039'):            # ordinary 0.039 legs at fixed count (Astra C1 design element)
        idx = rng.choice(np.flatnonzero(~is_t), sc['fixed_tail_039'], replace=False)
        c[idx] = 0.039; p[idx] = 0.039
    C = np.full(N, 50.0)
    d = dict(date=date, st=st, c=c, p=np.clip(p, 0, 1), C=C, n=C / c, is_rare=is_t)
    op = {k: v[date < OP_DATES] for k, v in d.items()}
    win = {k: v[date >= OP_DATES] for k, v in d.items()}
    win['date'] = win['date'] - OP_DATES
    return win, op


def theta_P(sc):
    """Exact prospective theta = E[N]/E[C] of the generating process (C constant)."""
    ct, pt = sc.get('c_t', 0.001), sc.get('p_t', 0.0)
    share = sc['eta'] * sc.get('phi', 1.0) if sc.get('arrival') == 'date' else sc.get('r', 0.0)
    return (1 - share) * sc['th_core'] + share * (pt / ct - 1)


# ------------------------------------------------------------------------------------------------ engines
def _ind(g):
    _, gi = np.unique(g, return_inverse=True)
    G = gi.max() + 1
    return sparse.csr_matrix((np.ones(gi.size), (np.arange(gi.size), gi)), shape=(gi.size, G)), G


def cr(e, blk, st, Q):
    """Spec 8.1: CR1 max(V_B, V_S, V_2w), df = min(G_B, G_S) - 1."""
    V, G = [], []
    for g in (blk, st, blk * 1000 + st):
        M, n = _ind(g)
        s = M.T @ e
        V.append(n / (n - 1) * (s ** 2).sum() / Q ** 2); G.append(n)
    return math.sqrt(max(V[0], V[1], V[0] + V[1] - V[2])), min(G[0], G[1]) - 1


def readiness(op):
    """Spec 10.2 / 10.3 on the 14 OP dates (prices, capital, stations only)."""
    c, C, st = op['c'], op['C'], op['st']
    if c.size < 2:
        return dict(pce=1.0, GO=False)
    mbar = c.size / OP_DATES
    s2 = c.size * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean() * deff / (120 * core.sum() / OP_DATES))
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    go = pce <= 0.10 and se0k <= 0.020 and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
    return dict(pce=pce, GO=bool(go))


def analyse(w, y):
    c, C, n, date, st = w['c'], w['C'], w['n'], w['date'], w['st']
    blk = date // 5
    tail = c < CUT; core = ~tail
    N = n * (y - c)
    out = {}
    th = N.sum() / C.sum(); se, df = cr(N - th * C, blk, st, C.sum())
    out['theta_hat'] = th
    out['T2'] = th - TQ(0.95, df) * se > 0
    thc = N[core].sum() / C[core].sum()
    sec, dfc = cr(N[core] - thc * C[core], blk[core], st[core], C[core].sum())
    x = (y - c)[core]; k = x.mean()
    sek, dfk = cr(x - k, blk[core], st[core], core.sum())
    viid = core.sum() / (core.sum() - 1) * ((x - k) ** 2).sum() / core.sum() ** 2
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    out['INFO'] = (np.unique(blk).size >= 12 and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
                   and sek <= 0.025 and sek ** 2 / viid <= 6)
    out['T1a'] = k - TQ(0.975, dfk) * sek > 0
    out['NEG'] = k + TQ(0.975, dfk) * sek < 0
    wc = C[core].sum() / C.sum()
    M_tail = (n[tail] - C[tail]).sum() / C.sum() if tail.any() else 0.0
    out['U_W'] = wc * (thc + TQ(0.975, dfc) * sec) + M_tail          # R1 bound (spec 8.5): valid for theta_W
    # R2-A candidate (evaluated, NOT adopted): replace M_tail by sum over tail price bins of an exact Poisson 0.995
    # upper bound on executed arrivals (Bonferroni over 5 bins, total 0.025) x the bin's maximum payoff per dollar.
    A = 0.0
    for lo, hi in TAIL_BINS:
        kb = int(((c >= lo) & (c < hi)).sum())
        ucb = stats.chi2.ppf(1 - 0.005, 2 * kb + 2) / 2
        A += ucb * 50.0 * (1 / lo - 1) / C.sum()
    out['U_R2A'] = wc * (thc + TQ(0.975, dfc) * sec) + A
    # gates G1-G3 (spec 17.2): G1 CONSERVATIVE = one tick worse; G3 true (NOAA-only synthetic)
    cc = c + np.where(c < CUT, 0.001, 0.01); nn = C / cc
    g1 = (nn * (y - cc)).sum() / C.sum() > 0
    pos = np.maximum(N, 0); gross = pos.sum()
    g2 = ((N.sum() - np.sort(N)[-5:].sum()) / C.sum() > 0 and gross > 0
          and np.bincount(date, weights=pos).max() <= 0.25 * gross and np.bincount(st, weights=pos).max() <= 0.20 * gross)
    out['GATES'] = bool(g1 and g2)
    out['theta_W'] = float((n * (w['p'] - c)).sum() / C.sum())
    out['n_rare'] = int(w['is_rare'].sum())
    return out


def labels_old(o, pce):
    """V2@24d2342 (R1) economic axis: E1 U_W < ERT -> NET_VALUE_EXCLUDED; rule 17.6 rejects R* on E1."""
    if o['U_W'] < ERT: e = 'NET_VALUE_EXCLUDED'
    elif o['T2'] and o['theta_hat'] >= ERT: e = 'NET_VALUE_CONFIRMED' if o['GATES'] else 'NET_VALUE_NOT_ROBUST'
    else: e = 'NET_VALUE_INDETERMINATE'
    large = o['U_W'] < max(pce, ERT)
    return e, large


def labels_new(o, pce):
    """Frozen R2 (spec 17.2 / 17.3 / 17.6): prospective axis has no exclusion value; R1 bound -> REALIZED_WINDOW_BOUND."""
    if o['T2'] and o['theta_hat'] >= ERT:
        e = 'PROSPECTIVE_VALUE_CONFIRMED' if o['GATES'] else 'PROSPECTIVE_VALUE_NOT_ROBUST'
    else:
        e = 'PROSPECTIVE_VALUE_INDETERMINATE'
    U = o['U_W']
    rw = ('REALIZED_WINDOW_LOSS_CONFIRMED' if U < 0 else 'REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED' if U < ERT
          else 'REALIZED_WINDOW_LARGE_VALUE_EXCLUDED' if U < max(pce, ERT) else 'REALIZED_WINDOW_NOT_EXCLUDED')
    rstar_rejected = False                      # spec 17.6: prospective economic rejection is not identified in V2
    prospective_excluded = e not in ('PROSPECTIVE_VALUE_CONFIRMED', 'PROSPECTIVE_VALUE_NOT_ROBUST',
                                     'PROSPECTIVE_VALUE_INDETERMINATE')
    return e, rw, rstar_rejected, prospective_excluded


def mc(k, n):
    p = k / n if n else float('nan')
    se = math.sqrt(max(p * (1 - p), 0) / n) if n else float('nan')
    return [round(p, 4), [round(max(0, p - 1.96 * se), 4), round(min(1, p + 1.96 * se), 4)]]


def run(sc, reps, seed):
    rng = np.random.default_rng(seed)
    tp = theta_P(sc)
    K = dict(GO=0, INFO=0, reach=0, old_excl=0, old_large=0, old_rej=0, new_pros_excl=0, new_rstar=0,
             new_conf=0, rw_excl=0, rw_excl_false=0, cov_W=0, r2a_excl=0, r2a_large=0, zero_rare=0)
    for _ in range(reps):
        w, op = draw(rng, sc)
        rd = readiness(op)
        lat = (math.sqrt(RHO[0]) * rng.standard_normal(WIN_DATES)[w['date']]
               + math.sqrt(RHO[1]) * rng.standard_normal(S)[w['st']])
        _, ci = np.unique(w['date'] * 1000 + w['st'], return_inverse=True)
        lat = lat + math.sqrt(RHO[2]) * rng.standard_normal(ci.max() + 1)[ci] + math.sqrt(1 - sum(RHO)) * rng.standard_normal(w['c'].size)
        y = (ndtr(lat) < w['p']).astype(float)
        o = analyse(w, y)
        reach = rd['GO'] and o['INFO']
        eo, large_old = labels_old(o, rd['pce'])
        en, rw, rstar, pex = labels_new(o, rd['pce'])
        thr_pce = max(rd['pce'], ERT)
        K['GO'] += rd['GO']; K['INFO'] += o['INFO']; K['reach'] += reach
        K['zero_rare'] += o['n_rare'] == 0
        K['old_excl'] += reach and eo == 'NET_VALUE_EXCLUDED' and tp >= ERT
        K['old_large'] += reach and large_old and tp >= thr_pce
        K['old_rej'] += reach and eo == 'NET_VALUE_EXCLUDED' and tp >= ERT
        K['new_pros_excl'] += reach and pex
        K['new_rstar'] += rstar
        K['new_conf'] += reach and en == 'PROSPECTIVE_VALUE_CONFIRMED'
        K['rw_excl'] += reach and rw in ('REALIZED_WINDOW_LOSS_CONFIRMED', 'REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED')
        K['rw_excl_false'] += reach and o['U_W'] < ERT and o['theta_W'] >= ERT
        K['cov_W'] += o['theta_W'] <= o['U_W']
        K['r2a_excl'] += reach and o['U_R2A'] < ERT
        K['r2a_large'] += reach and o['U_R2A'] < thr_pce
    out = dict(sc={k: v for k, v in sc.items()}, reps=reps, theta_P=round(tp, 4),
               E_rare_window=round((sc['eta'] * sc.get('phi', 1.0) if sc.get('arrival') == 'date' else sc.get('r', 0.0)) * 35 * WIN_DATES, 2))
    for k, v in K.items():
        out[k] = mc(v, reps)
    out['old_excl_given_reach'] = mc(K['old_excl'], K['reach'])
    return out


def rate_for(target, th_core, c_t, p_t):
    return (target - th_core) / (p_t / c_t - 1 - th_core)


# ------------------------------------------------------------------------------------------------ plans
def scenario_plan():
    P = []
    def add(name, **kw): P.append(dict(name=name, **kw))
    add('C2-S1 p_t=0.17 core=-0.05 thP=0.025', th_core=-0.05, c_t=0.001, p_t=0.17, r=rate_for(0.025, -0.05, 0.001, 0.17))
    add('C2 p_t=0.50 core=-0.10 thP=0.025', th_core=-0.10, c_t=0.001, p_t=0.50, r=rate_for(0.025, -0.10, 0.001, 0.50))
    add('C2 p_t=0.50 core=-0.05 thP=0.025', th_core=-0.05, c_t=0.001, p_t=0.50, r=rate_for(0.025, -0.05, 0.001, 0.50))
    add('C2 p_t=1.00 core=-0.10 thP=0.025', th_core=-0.10, c_t=0.001, p_t=1.00, r=rate_for(0.025, -0.10, 0.001, 1.00))
    add('C2 PCE p_t=0.50 core=0 thP=0.10', th_core=0.0, c_t=0.001, p_t=0.50, r=rate_for(0.10, 0.0, 0.001, 0.50))
    add('date-clustered jackpot p_t=1 core=-0.10 thP=0.025', th_core=-0.10, c_t=0.001, p_t=1.0, arrival='date', phi=1.0,
        eta=rate_for(0.025, -0.10, 0.001, 1.0))
    add('C2 p_t=1.00 core=-0.10 thP=0.025 (independent replicate seed)', th_core=-0.10, c_t=0.001, p_t=1.0,
        r=rate_for(0.025, -0.10, 0.001, 1.0))
    add('frequent tail: c_t=0.01 p_t=0.05 core=-0.05 thP=0.025', th_core=-0.05, c_t=0.01, p_t=0.05,
        r=rate_for(0.025, -0.05, 0.01, 0.05))
    add('Astra C1-like: 84 fair 0.039 legs + rare 0.001 p=0.17, core=-0.05', th_core=-0.05, c_t=0.001, p_t=0.17,
        r=rate_for(0.025, -0.05, 0.001, 0.17), fixed_tail_039=84)
    add('tail-free regression core=-0.05', th_core=-0.05)
    add('tail-free regression core=-0.10', th_core=-0.10)
    add('tail-free regression core=+0.02 (ERT boundary)', th_core=0.02)
    add('tail-free core=+0.10 (confirmation power)', th_core=0.10)
    return P


def ceiling_table():
    """Spec 8.5b: power ceiling of ANY level-alpha prospective exclusion test (date-clustered alternative)."""
    rows = []
    for thr_name, thr in [('ERT', 0.02), ('PCE=0.05', 0.05), ('PCE=0.10', 0.10)]:
        for th0 in [-1.0, -0.5, -0.15, -0.10, -0.05, 0.0]:
            if th0 >= thr: continue
            eta = (thr - th0) / (1 / C_MIN - 1 - th0)
            for label, units in [('dates D=134 (V2 dependence class)', OP_DATES + WIN_DATES),
                                 ('trades N=4,200 (independence, not justified)', 4200),
                                 ('trades N=11,520 (independence, 96 events x 120)', 11520)]:
                ceil = min(1.0, ALPHA / (1 - eta) ** units)
                rows.append(dict(threshold=thr_name, theta_0=th0, eta=round(eta, 7), units=label, power_ceiling=round(ceil, 4)))
    return rows


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'ceiling'
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if mode == 'ceiling':
        print(json.dumps(dict(C_MIN=C_MIN, max_payoff_per_dollar=round(1 / C_MIN - 1, 2))))
        for r in ceiling_table(): print(json.dumps(r))
        sys.exit()
    from multiprocessing import Pool
    if mode == 'scenarios':
        jobs = [(sc, reps or 4000, 20260930 + i) for i, sc in enumerate(scenario_plan())]
    elif mode == 'counts':   # E[rare] ~ 2.5 so observed counts 0..10 all occur; report old/new by observed count
        base = dict(th_core=-0.10, c_t=0.001, p_t=1.0, r=None)
        jobs = []
        for i, lam in enumerate([0.5, 2.0, 5.0, 10.0]):
            r = lam / (35 * WIN_DATES)
            jobs.append((dict(name=f'counts lambda={lam}', th_core=-0.10, c_t=0.001, p_t=None, r=r, count_mode=True),
                         reps or 4000, 20261930 + i))
    elif mode == 'grid':
        jobs = []; i = 0
        for c_t in [0.001, 0.002, 0.005, 0.01, 0.02, 0.039]:
            for p_kind in ['0', 'implied', '0.05', '0.17', '0.50', '1.00']:
                p_t = c_t if p_kind == 'implied' else float(p_kind)
                for thc in [-0.15, -0.10, -0.05, 0.0, 0.02]:
                    for tgt in [0.02, 0.021, 0.025, 0.05, 0.08, 0.10]:
                        if p_t / c_t - 1 <= tgt:
                            continue                       # tail type cannot lift theta_P to the target
                        r = rate_for(tgt, thc, c_t, p_t)
                        if not (0 < r <= 0.5):
                            continue
                        for arr in ['trade', 'date']:
                            sc = dict(name=f'grid c_t={c_t} p_t={p_kind} core={thc} thP={tgt} {arr}', th_core=thc,
                                      c_t=c_t, p_t=p_t)
                            if arr == 'trade': sc['r'] = r
                            else: sc.update(arrival='date', eta=min(1.0, r), phi=1.0)
                            if r * 35 * WIN_DATES > 30:      # frequent tails are sampled; keep the rare region only
                                continue
                            jobs.append((sc, reps or 200, 20262000 + i)); i += 1
    elif mode == 'confirm':
        jobs = []
        for i, th0 in enumerate([0.02, 0.03, 0.05, 0.10]):
            eta = th0 / (1 + th0)                          # catastrophic dates (all trades lose) make theta_P = 0
            sc = dict(name=f'confirm: core={th0} + catastrophic dates eta={eta:.4f} -> thP=0', th_core=th0, c_t=0.5,
                      p_t=0.0, arrival='date', eta=eta, phi=1.0)
            jobs.append((sc, reps or 4000, 20263000 + i))
    else:
        raise SystemExit(mode)

    def _job(a):
        sc, n, seed = a
        if sc.get('count_mode'):
            sc = dict(sc); sc['p_t'] = 1.0
            rng = np.random.default_rng(seed)
            by = {}
            for _ in range(n):
                w, op = draw(rng, sc); rd = readiness(op)
                lat = (math.sqrt(RHO[0]) * rng.standard_normal(WIN_DATES)[w['date']]
                       + math.sqrt(RHO[1]) * rng.standard_normal(S)[w['st']])
                _, ci = np.unique(w['date'] * 1000 + w['st'], return_inverse=True)
                lat = lat + math.sqrt(RHO[2]) * rng.standard_normal(ci.max() + 1)[ci] + math.sqrt(1 - sum(RHO)) * rng.standard_normal(w['c'].size)
                y = (ndtr(lat) < w['p']).astype(float)
                o = analyse(w, y); eo, _ = labels_old(o, rd['pce']); en, rw, rs, pex = labels_new(o, rd['pce'])
                k = min(o['n_rare'], 10)
                b = by.setdefault(k, [0, 0, 0, 0])
                b[0] += 1; b[1] += (eo == 'NET_VALUE_EXCLUDED'); b[2] += pex; b[3] += rs
            tp = theta_P(sc)
            return json.dumps(dict(name=sc['name'], theta_P=round(tp, 4), reps=n,
                                   by_observed_count={k: dict(n=v[0], old_NET_VALUE_EXCLUDED=round(v[1] / v[0], 4),
                                                              new_prospective_exclusion=v[2], new_rstar_rejected=v[3])
                                                      for k, v in sorted(by.items())}))
        return json.dumps(run(sc, n, seed))

    with Pool(4) as pool:
        for line in pool.imap(_job, jobs):
            print(line, flush=True)
