"""Weather Forward V2 — D4-C3 transport repair validation (run F), 2026-09-30.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.

Purpose (spec 8.5c, 17): reproduce Astra C3 (false PROSPECTIVE_VALUE_CONFIRMED when a rare, high-capital loss regime is
absent from the 120-date window) with an implementation independent of Astra's, and validate the frozen R3 architecture:
  - the economic axis is about the realised-window value theta_W (sampling inference only, T2 / L_W);
  - no unconditional prospective label exists (PROSPECTIVE_CONFIRMATION = NOT_ESTABLISHED_UNCONDITIONALLY);
  - the prospective content is the transport frontier eps*(delta, tau) = (L_W - delta - tau) / (1 + L_W - delta)
    over the cost-mass contamination class of spec 8.5c, plus the H-epoch translation k*(H) and concentration report.

Process per replication: 14 OP dates + 120 window dates. Ordinary dates: Poisson(m) executed trades (<= 96), 48 gamma(2)
stations x {HIGHEST, LOWEST}, CORE c ~ U(0.35, 0.80), p = c (1 + th0), capital 'full' (C = 50) or 'thin' (C ~ U(5, 25)).
Loss-regime dates (probability eta, independent across dates, identical in the OP where only prices are seen):
  cap96    : all 96 events execute at C = 50 and lose (maximum date exposure)
  template : the 48 LOWEST events execute at C = 50 and lose (market-template comonotone)
  stations : both events of 24 random stations execute at C = 50 and lose (station-cluster comonotone)
  hidden   : ordinary count and capital model, every trade loses (identical observable covariates)
Optional rare positive tail per trade (Astra C2 regression): c_t = 0.001, win probability p_t.
Outcomes: latent Gaussian copula (date, station, cell) = (0.05, 0.05, 0.10).

Usage:
  python3 WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py scenarios [REPS]   # power table 4.7 scenario table (default 4000)
  python3 WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py c3 [REPS]          # Astra C3 reproduction cells (default 20000)
  python3 WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py grid [REPS]        # loss-regime grid (default 1000 per cell)
  python3 WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py coverage [REPS]    # L_W sampling coverage, stable designs (default 20000)
  python3 WEATHER_FORWARD_V2_D4_C3_SIM_2026-09-30.py frontier           # algebraic frontier checks (no randomness)
Requires numpy and scipy.
"""
import json
import math
import sys

import numpy as np
from scipy import sparse, stats
from scipy.special import ndtr

ERT, CUT, Z80 = 0.02, 0.04, 2.4865
S, OPD, WD = 48, 14, 120
RHO = (0.05, 0.05, 0.10)
C_TRADE_MAX = 50.0 * 1.05          # spec 8.5c: notional <= S_ref = 50, fee <= 0.05 per dollar of notional
C_CAP_DATE = 2 * S * C_TRADE_MAX   # 96 events x 52.5 = 5,040 USD
H_GRID = (14, 30, 60, 120)
DELTA_GRID = (0.0, 0.01, 0.02, 0.05)
TQ = stats.t.ppf


# ------------------------------------------------------------------------------------------------ process
def cap_draw(rng, n, model):
    return np.full(n, 50.0) if model == 'full' else rng.uniform(5.0, 25.0, n)


def draw(rng, sc):
    D = OPD + WD
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    bad = rng.random(D) < sc.get('eta', 0.0)
    rows = []
    for d in range(D):
        if bad[d] and sc['kind'] != 'hidden':
            if sc['kind'] == 'cap96':
                st = np.repeat(np.arange(S), 2)
            elif sc['kind'] == 'template':
                st = np.arange(S)
            else:                                    # 'stations'
                st = np.repeat(rng.choice(S, 24, replace=False), 2)
            k = st.size
            c = rng.uniform(0.35, 0.80, k); p = np.zeros(k); C = np.full(k, 50.0)
        else:
            k = min(96, rng.poisson(sc['m']))
            st = rng.choice(S, k, p=act)
            c = rng.uniform(0.35, 0.80, k); p = np.minimum(1.0, c * (1 + sc['th0']))
            C = cap_draw(rng, k, sc['cap'])
            if bad[d]:                                # hidden: same covariates, every trade loses
                p = np.zeros(k)
            if sc.get('r', 0.0) > 0:                  # rare positive tail (C2 regression)
                t = rng.random(k) < sc['r']
                c[t] = sc['c_t']; p[t] = sc['p_t']
        rows.append((np.full(k, d), st, c, p, C, np.full(k, bad[d])))
    date, st, c, p, C, b = (np.concatenate(x) for x in zip(*rows))
    d = dict(date=date, st=st, c=c, p=p, C=C, n=C / c, bad=b)
    op = {k: v[date < OPD] for k, v in d.items()}
    w = {k: v[date >= OPD] for k, v in d.items()}
    w['date'] = w['date'] - OPD
    return w, op


def theta_P(sc):
    """Exact prospective theta = E[N]/E[C] per date of the generating process."""
    EC_ord = 50.0 if sc['cap'] == 'full' else 15.0
    m_eff = sc['m']                                   # Poisson mean; truncation at 96 is negligible for m <= 35
    A = m_eff * EC_ord
    t = sc.get('r', 0.0)
    ord_ret = (1 - t) * sc['th0'] + t * (sc.get('p_t', 0.0) / sc.get('c_t', 1.0) - 1) if t else sc['th0']
    eta = sc.get('eta', 0.0)
    if eta == 0.0:
        return ord_ret
    B = {'cap96': 96 * 50.0, 'template': 48 * 50.0, 'stations': 48 * 50.0, 'hidden': A}[sc['kind']]
    return ((1 - eta) * A * ord_ret - eta * B) / ((1 - eta) * A + eta * B)


def eta_for(target, th0, m, cap, kind):
    A = m * (50.0 if cap == 'full' else 15.0)
    B = {'cap96': 96 * 50.0, 'template': 48 * 50.0, 'stations': 48 * 50.0, 'hidden': A}[kind]
    # ((1-eta) A th0 - eta B) / ((1-eta) A + eta B) = target
    return A * (th0 - target) / (A * (th0 - target) + B * (1 + target))


def cost_share_bad(sc):
    """Cost-mass share of the loss regime in the prospective process (the true epsilon of spec 8.5c)."""
    eta = sc.get('eta', 0.0)
    if eta == 0.0:
        return 0.0
    A = sc['m'] * (50.0 if sc['cap'] == 'full' else 15.0)
    B = {'cap96': 96 * 50.0, 'template': 48 * 50.0, 'stations': 48 * 50.0, 'hidden': A}[sc['kind']]
    return eta * B / ((1 - eta) * A + eta * B)


# ------------------------------------------------------------------------------------------------ engines
def _ind(g):
    _, gi = np.unique(g, return_inverse=True); G = gi.max() + 1
    return sparse.csr_matrix((np.ones(gi.size), (np.arange(gi.size), gi)), shape=(gi.size, G)), G


def cr(e, blk, st, Q):
    V, G = [], []
    for g in (blk, st, blk * 1000 + st):
        M, n = _ind(g); s = M.T @ e
        V.append(n / (n - 1) * (s ** 2).sum() / Q ** 2); G.append(n)
    return math.sqrt(max(V[0], V[1], V[0] + V[1] - V[2])), min(G[0], G[1]) - 1


def readiness(op):
    c, C, st = op['c'], op['C'], op['st']
    mbar = c.size / OPD
    s2 = c.size * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1)); se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean() * deff / (120 * core.sum() / OPD))
    k = np.bincount(st); k = k[k > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    return pce, bool(pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and k.sum() ** 2 / (k ** 2).sum() >= 15)


def outcomes(rng, w):
    _, ci = np.unique(w['date'] * 1000 + w['st'], return_inverse=True)
    z = (math.sqrt(RHO[0]) * rng.standard_normal(WD)[w['date']] + math.sqrt(RHO[1]) * rng.standard_normal(S)[w['st']]
         + math.sqrt(RHO[2]) * rng.standard_normal(ci.max() + 1)[ci] + math.sqrt(1 - sum(RHO)) * rng.standard_normal(w['c'].size))
    return (ndtr(z) < w['p']).astype(float)


def frontier(L, delta, tau):
    """Spec 8.5c: largest cost-mass epsilon with (1 - eps)(L - delta) - eps >= tau; 0 if none."""
    x = L - delta
    return max(0.0, (x - tau) / (1 + x)) if x > -1 else 0.0


def k_star(eps, H, Cbar):
    """Spec 8.5c: number of maximum-exposure adverse dates an H-date epoch absorbs at cost-mass budget eps."""
    return eps * H * Cbar / (C_CAP_DATE * (1 - eps) + eps * Cbar) if eps > 0 else 0.0


def analyse(w, y, pce, go):
    c, C, n, date, st = w['c'], w['C'], w['n'], w['date'], w['st']
    blk = date // 5; tail = c < CUT; core = ~tail
    N = n * (y - c); th = N.sum() / C.sum()
    se, df = cr(N - th * C, blk, st, C.sum())
    L_W = th - TQ(0.95, df) * se                     # T2 <=> L_W > 0 (spec 6.1, 8.1)
    T2 = L_W > 0
    thc = N[core].sum() / C[core].sum()
    sec, dfc = cr(N[core] - thc * C[core], blk[core], st[core], C[core].sum())
    x = (y - c)[core]; k = x.mean(); sek, dfk = cr(x - k, blk[core], st[core], core.sum())
    viid = core.sum() / (core.sum() - 1) * ((x - k) ** 2).sum() / core.sum() ** 2
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    info = bool(np.unique(blk).size >= 12 and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
                and sek <= 0.025 and sek ** 2 / viid <= 6)
    NEG = k + TQ(0.975, dfk) * sek < 0
    wc = C[core].sum() / C.sum()
    Mt = (n[tail] - C[tail]).sum() / C.sum() if tail.any() else 0.0
    U_W = wc * (thc + TQ(0.975, dfc) * sec) + Mt
    cc = c + np.where(c < CUT, 0.001, 0.01); g1 = ((C / cc) * (y - cc)).sum() / C.sum() > 0
    pos = np.maximum(N, 0); gross = pos.sum()
    g2 = bool(gross > 0 and (N.sum() - np.sort(N)[-5:].sum()) / C.sum() > 0
              and np.bincount(date, weights=pos).max() <= 0.25 * gross and np.bincount(st, weights=pos).max() <= 0.20 * gross)
    gates = bool(g1 and g2)
    reach = go and info
    # date-level economic concentration (spec 17.3 TRANSPORT_ROBUSTNESS_REPORT)
    Cd = np.bincount(date, weights=C, minlength=WD); Cd = Cd[Cd > 0]
    Cbar = Cd.mean()
    conc = dict(Cbar=Cbar, Cmax=Cd.max(), n_eff_C=Cd.sum() ** 2 / (Cd ** 2).sum(), cap_ratio=C_CAP_DATE / Cbar,
                eps_one_cap_date_120=C_CAP_DATE / (C_CAP_DATE + 119 * Cbar))
    # ---- R2 (spec @e45d2ce7) economic axis and forward signal
    if not reach: eco_r2 = 'NOT_REACHED'
    elif T2 and th >= ERT: eco_r2 = 'PROSPECTIVE_VALUE_CONFIRMED' if gates else 'PROSPECTIVE_VALUE_NOT_ROBUST'
    else: eco_r2 = 'PROSPECTIVE_VALUE_INDETERMINATE'
    fwd_r2 = eco_r2 == 'PROSPECTIVE_VALUE_CONFIRMED' and not NEG
    # ---- R3 (frozen here): economic axis on theta_W; prospective content only via the frontier
    if not reach: eco = 'NOT_REACHED'
    elif T2 and th >= ERT: eco = 'REALIZED_WINDOW_VALUE_SUPPORTED' if gates else 'REALIZED_WINDOW_VALUE_NOT_ROBUST'
    else: eco = 'REALIZED_WINDOW_VALUE_INDETERMINATE'
    shadow = eco == 'REALIZED_WINDOW_VALUE_SUPPORTED' and not NEG      # SHADOW_CONTINUATION_SIGNAL (17.5)
    unconditional_prospective_label = False                               # none exists in R3 (17.2, 17.3)
    prospective_exclusion_label = False                                   # none exists since R2
    eps0 = frontier(L_W, 0.0, 0.0)
    thW = float((n * (w['p'] - c)).sum() / C.sum())
    return dict(reach=reach, eco_r2=eco_r2, fwd_r2=fwd_r2, eco=eco, shadow=shadow, L_W=L_W, thW=thW, th=th, U_W=U_W,
                eps0=eps0, epsERT=frontier(L_W, 0.0, ERT), conc=conc,
                kstar={H: k_star(eps0, H, Cbar) for H in H_GRID}, unc=unconditional_prospective_label,
                pex=prospective_exclusion_label, n_bad=int(np.unique(w['date'][w['bad']]).size) if w['bad'].any() else 0,
                Cmax_ordinary=float(np.bincount(date[~w['bad']], weights=C[~w['bad']], minlength=WD).max()))


def mc(k, n):
    p = k / n if n else float('nan'); se = math.sqrt(max(p * (1 - p), 0) / n) if n else float('nan')
    return [round(p, 4), round(se, 4), [round(max(0, p - 1.96 * se), 4), round(min(1, p + 1.96 * se), 4)]]


def run(sc, reps, seed):
    rng = np.random.default_rng(seed)
    tP = theta_P(sc); eps_true = cost_share_bad(sc)
    K = dict(reach=0, r2_conf=0, r2_conf_false=0, r2_fwd=0, r2_pos_false=0, r3_support=0, r3_pos=0, r3_pos_false_W=0,
             LW_miss=0, cond_claim_false=0, shadow=0, unc=0, pex=0, zero_bad=0, eps_true_le_eps0=0, obs_flag=0)
    K_bad = {'cap96': 96, 'template': 48, 'stations': 48}.get(sc['kind'])
    by = {}
    eps0s, k120, kin, epsone = [], [], [], []
    for _ in range(reps):
        w, op = draw(rng, sc); pce, go = readiness(op)
        o = analyse(w, outcomes(rng, w), pce, go)
        pos_r2 = o['eco_r2'] in ('PROSPECTIVE_VALUE_CONFIRMED', 'PROSPECTIVE_VALUE_NOT_ROBUST')
        pos_r3 = o['eco'] in ('REALIZED_WINDOW_VALUE_SUPPORTED', 'REALIZED_WINDOW_VALUE_NOT_ROBUST')
        K['reach'] += o['reach']
        K['r2_conf'] += o['eco_r2'] == 'PROSPECTIVE_VALUE_CONFIRMED'
        K['r2_conf_false'] += o['eco_r2'] == 'PROSPECTIVE_VALUE_CONFIRMED' and tP <= 0
        K['r2_pos_false'] += pos_r2 and tP <= 0
        K['r2_fwd'] += o['fwd_r2']
        K['r3_support'] += o['eco'] == 'REALIZED_WINDOW_VALUE_SUPPORTED'
        K['r3_pos'] += pos_r3
        K['r3_pos_false_W'] += pos_r3 and o['thW'] <= 0                  # false realised-window positive claim
        K['LW_miss'] += o['reach'] and o['L_W'] > o['thW']                # sampling miss of the source bound
        # conditional prospective claim at the true loss-regime cost share (delta = 0): false iff premise holds
        # (represented mass earns >= theta_W, true by construction here) and (1-eps)L_W - eps > theta_P
        K['cond_claim_false'] += o['reach'] and (1 - eps_true) * o['L_W'] - eps_true > tP + 1e-12
        K['shadow'] += o['shadow']; K['unc'] += o['unc']; K['pex'] += o['pex']
        K['zero_bad'] += o['n_bad'] == 0
        # would a future loss-regime date trip the outcome-blind COST_EXCEEDS_EVIDENCE flag (17.3)? never for 'hidden'
        K['obs_flag'] += sc.get('eta', 0) > 0 and K_bad is not None and K_bad * 50.0 > o['Cmax_ordinary']
        K['eps_true_le_eps0'] += o['reach'] and pos_r3 and eps_true <= o['eps0']
        b = by.setdefault(min(o['n_bad'], 10), [0, 0, 0])
        b[0] += 1; b[1] += o['eco_r2'] == 'PROSPECTIVE_VALUE_CONFIRMED'; b[2] += pos_r3 and o['thW'] <= 0
        if o['reach'] and pos_r3:
            eps0s.append(o['eps0']); k120.append(o['kstar'][120])
        kin.append(o['conc']['cap_ratio']); epsone.append(o['conc']['eps_one_cap_date_120'])
    q = lambda v, p: round(float(np.quantile(v, p)), 4) if len(v) else None
    out = dict(sc=sc, reps=reps, seed=seed, theta_P=round(tP, 4), eps_true_cost_share=round(eps_true, 4),
               E_bad_dates_window=round(sc.get('eta', 0.0) * WD, 2),
               **{k: mc(v, reps) for k, v in K.items()},
               r2_conf_false_given_reach=mc(K['r2_conf_false'], K['reach']),
               eps0_when_supported=dict(q10=q(eps0s, 0.1), q50=q(eps0s, 0.5), q90=q(eps0s, 0.9)),
               kstar120_when_supported=dict(q10=q(k120, 0.1), q50=q(k120, 0.5), q90=q(k120, 0.9)),
               cap_ratio_median=q(kin, 0.5), eps_one_cap_date_120_median=q(epsone, 0.5),
               by_bad_dates_in_window={k: dict(n=v[0], r2_confirmed=round(v[1] / v[0], 4),
                                               r3_false_window_positive=round(v[2] / v[0], 4)) for k, v in sorted(by.items())})
    return out


# ------------------------------------------------------------------------------------------------ plans
def mk(name, target, th0=None, m=35, cap='full', kind='cap96', **kw):
    sc = dict(name=name, m=m, cap=cap, kind=kind, **kw)
    if th0 is None:
        sc['th0'] = target; sc['eta'] = 0.0
    else:
        sc['th0'] = th0; sc['eta'] = eta_for(target, th0, m, cap, kind)
    return sc


def scenario_plan():
    """Mission set (power table 4.7). eta solved so theta_P hits the stated target exactly."""
    def stable(name, th0, m=35, cap='full', **kw):
        return dict(name=name, m=m, cap=cap, kind='cap96', th0=th0, eta=0.0, **kw)
    eta10 = 10 / WD
    return [
        stable('01 C2 regression: rare 0.001 tail p=0.17, core -0.05, thP=0.025, no loss regime', -0.05,
               r=(0.025 + 0.05) / (0.17 / 0.001 - 1 + 0.05), c_t=0.001, p_t=0.17),
        mk('02 C3 thin fills: cap96 loss dates, m=17, core 0.10, thP=-0.005', -0.005, th0=0.10, m=17, cap='thin'),
        mk('03 C3 full fills: cap96 loss dates, m=17, core 0.05, thP=-0.005', -0.005, th0=0.05, m=17, cap='full'),
        mk('04 thP=0 exactly: cap96, m=35, thin, core 0.08', 0.0, th0=0.08, m=35, cap='thin'),
        stable('05 strong positive stable: core 0.10, m=35, full, no loss regime', 0.10),
        mk('06 hidden catastrophe (identical covariates), m=17, full, core 0.04, thP=-0.005', -0.005, th0=0.04, m=17,
           cap='full', kind='hidden'),
        mk('07 high date concentration: cap96, m=17, thin, core 0.05, thP=-0.005', -0.005, th0=0.05, m=17, cap='thin'),
        mk('08 low date concentration: cap96, m=35, full, core 0.03, thP=-0.005', -0.005, th0=0.03, m=35, cap='full'),
        mk('09 template-comonotone (48 LOWEST), m=17, full, core 0.04, thP=-0.005', -0.005, th0=0.04, m=17, cap='full',
           kind='template'),
        mk('10 station-cluster (24 stations x 2), m=17, full, core 0.04, thP=-0.005', -0.005, th0=0.04, m=17, cap='full',
           kind='stations'),
        dict(name='11 frequent loss regime (E=10 in window): cap96, m=35, full, thP=0', m=35, cap='full', kind='cap96',
             eta=eta10, th0=eta10 * 96 * 50.0 / ((1 - eta10) * 35 * 50.0)),
        stable('12 tail-free stable baseline, core 0.00 (thP=0)', 0.0),
        stable('13 tail-free stable baseline, core 0.10, m=17, thin (confirmation power, thin)', 0.10, m=17, cap='thin'),
    ]


def c3_plan():
    return [mk('C3-thin: cap96, m=17, thin, core 0.10, thP=-0.005', -0.005, th0=0.10, m=17, cap='thin'),
            mk('C3-full: cap96, m=17, full, core 0.05, thP=-0.005', -0.005, th0=0.05, m=17, cap='full')]


def grid_plan():
    out = []
    for E in (0.25, 1, 2, 5, 10):                      # expected loss-regime dates in the 120-date window
        eta = E / WD
        for kind in ('cap96', 'template', 'stations', 'hidden'):
            for m, cap in ((17, 'thin'), (17, 'full'), (35, 'thin'), (35, 'full')):
                for target in (-0.005, 0.0, ERT, 0.08):
                    A = m * (50.0 if cap == 'full' else 15.0)
                    B = {'cap96': 96 * 50.0, 'template': 48 * 50.0, 'stations': 48 * 50.0, 'hidden': A}[kind]
                    th0 = (target * ((1 - eta) * A + eta * B) + eta * B) / ((1 - eta) * A)
                    if th0 > 0.5:
                        continue                      # ordinary-date effect implausibly large; skip cell
                    out.append(dict(name=f'grid E={E} {kind} m={m} {cap} thP={target}', m=m, cap=cap, kind=kind,
                                    th0=th0, eta=eta))
    return out


def frontier_checks():
    rows = []
    for L in (-0.5, -0.05, 0.0, 0.03, 0.10, 0.30):
        for delta in DELTA_GRID:
            eps = np.linspace(0, 1, 101)
            LT = (1 - eps) * (L - delta) - eps
            rows.append(dict(L_W=L, delta=delta, monotone_decreasing=bool(np.all(np.diff(LT) <= 1e-15)),
                             LT_eps0=round(float(LT[0]), 6), LT_eps1=round(float(LT[-1]), 6),
                             eps_star_tau0=round(frontier(L, delta, 0.0), 6), eps_star_tauERT=round(frontier(L, delta, ERT), 6)))
    ks = [dict(eps=e, H=H, Cbar=Cb, k_star=round(k_star(e, H, Cb), 4))
          for e in (0.01, 0.05, 0.091) for H in H_GRID for Cb in (17 * 15.0, 17 * 50.0, 35 * 50.0)]
    one = [dict(H=H, Cbar=Cb, eps_one_cap_date=round(C_CAP_DATE / (C_CAP_DATE + (H - 1) * Cb), 4))
           for H in H_GRID for Cb in (17 * 15.0, 17 * 50.0, 35 * 50.0)]
    return dict(frontier=rows, k_star=ks, one_cap_date=one, C_TRADE_MAX=C_TRADE_MAX, C_CAP_DATE=C_CAP_DATE)


def _job(a):
    sc, n, seed = a
    return json.dumps(run(sc, n, seed))


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'frontier'
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if mode == 'frontier':
        print(json.dumps(frontier_checks()))
        sys.exit()
    from multiprocessing import Pool
    if mode == 'scenarios':
        jobs = [(sc, reps or 4000, 20261001 + i) for i, sc in enumerate(scenario_plan())]
    elif mode == 'c3':
        jobs = [(sc, reps or 20000, 20262001 + i) for i, sc in enumerate(c3_plan())]
    elif mode == 'grid':
        jobs = [(sc, reps or 1000, 20263001 + i) for i, sc in enumerate(grid_plan())]
    elif mode == 'coverage':   # scenarios 05, 12, 13 of the scenario plan: the source bound's sampling coverage
        plan = scenario_plan()
        jobs = [(plan[k], reps or 20000, 20264001 + k) for k in (4, 11, 12)]
    else:
        raise SystemExit(mode)
    with Pool(4) as pool:
        for line in pool.imap(_job, jobs):
            print(line, flush=True)
