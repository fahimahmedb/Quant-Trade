"""Weather Forward V2 — D4-C3-M2 cycle-2 calibration (run H), 2026-10-01.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.
OUTCOME_INFORMATION_USED = FALSE.

Purpose (Astra @ac777a87, blockers M1-R and M2, proof gap T1b):
  M1-R  the 8.1b multi-block L_W = theta_hat - max_{b in {5,10,20,30}} t_{df_b,0.95} SE_2w(b) holds <= 0.05 only on the
        run-G grid (c ~ U(0.35, 0.80), no pauses, Gaussian AR(1)); it fails inside the class as the spec writes it
        (favourite CORE prices, 30 paused dates, two-state regime, the literal spec-9 30-date trailing-mean mechanism).
  M2    T1a / NEG (kappa_core) and U_W (theta_core) keep 5-date blocks and undercover inside the persistence class.
  T1b   PINM tail count under cross-block persistence was never measured.

DECLARED BEFORE ANY RUN OF THIS FILE (nothing below was chosen from a run of this file):

  CLASS  D_P* (the completely stated class over which every level is stated; replaces run G's grid D_P):
    dependence  latent Gaussian copula (date, station, cell) = (0.05, 0.05, 0.10)  [V2 simulation dependence]
                plus at most ONE persistent date-level component of latent variance rv in {0.02, 0.05, 0.10}, running on
                calendar days (paused days included), shared by every trade of the date, of one of the shapes:
                  'ar'   stationary Gaussian AR(1), phi in {0.5, 0.7, 0.8, 0.9}
                  'mk'   two-state +-1 Markov regime with autocorrelation phi^k, phi in {0.8, 0.9} (non-Gaussian)
                  'box'  trailing L-date mean of iid date shocks (MA(L-1), unit variance), L in {15, 30}
                         (L = 30 is the literal error of the 30-date trailing-mean bias correction that spec 9 names)
                  'hemi' two independent AR(1) regimes, each shared by one half of the stations (phi 0.9)
                  'stn'  station-specific AR(1) drifts (phi 0.9)
                or none (the 5-date-block model).  Latent thresholds are exact for every shape: P(y = 1) = p.
    calendar    D counted dates in {120, 90, 60} (60 = IF1 floor, truncated window, spec 11.4 / 17.1) plus P paused calendar
                dates, P in {0, 30} (30 = the DATA_FAILURE limit, 11.3), laid out either at uniformly random interior
                positions ('rand') or as one contiguous run at a random interior start ('run');  blocks are calendar blocks
                floor((D - D_0)/b) from the first forward date (never paused).
    stations    48 with gamma(2) activity.  Trades: Poisson(m) per counted date (cap 96), m in {17, 35}.
    fills       thin C ~ U(5, 25) USD or full C = 50 USD.
    prices      the same law for OP and window:  'mid' c ~ U(0.35, 0.80) (run G);  'fav' c ~ U(0.70, 0.90) (favourite-heavy
                CORE, left-skewed per-trade return; R* cannot buy above 0.90, spec 5.2);  'favmix' half 'fav' half 'mid';
                'wide' log-uniform on [0.04, 0.90];  'low' U(0.04, 0.35);  'tail1' / 'tail3' = 'mid' with a 1% / 3% TAIL share
                c ~ U(0.02, 0.039).  ('wide', 'low' are expected NO_GO; they are run, not assumed.)
    effect      p = min(1, c (1 + theta)), theta in {0, 0.05, 0.10} (and -0.12 / 0.06 for information power).
  Everything outside D_P* (phi >= 0.95, two-component memories, rv > 0.10, more than one persistent component) is
  disclosure only.

  CONSTRUCTION FAMILY (frozen form; one constant per axis):
    H_theta(b-set, q)  = max_{b in b-set} t_{df_b, q} SE_2w(b; e = N - theta_hat C, Q = sum C)
    L_W      = theta_hat - lam_theta * H_theta({5,10,20,30}, 0.95)                         (T2 iff L_W > 0)
    U_W      = w_core (theta_core_hat + lam_theta * H_core({5,10,20,30}, 0.975)) + M_tail   (spec 8.5 structure kept)
    T1a      = kappa_hat - lam_kappa * H_kappa({5,10,20,30}, 0.975) > 0
    NEG      = kappa_hat + lam_kappa * H_kappa({5,10,20,30}, 0.975) < 0
    HEADLINE = [L_W, U_W]
    IF4 / IF5 (INFO_SUFFICIENT) and GO stay on their frozen 5-date-block / design definitions (reach unchanged).
    lam in GRID = {1.00, 1.05, ..., 2.50}.  lam = 1 is the cycle-1 rule for L_W (8.1b).
  SELECTION CRITERION (declared with the family):
    lam_theta = the smallest GRID value such that, in EVERY D_P* cell at 20,000 replications,
                P(reach AND L_W > theta_W) <= 0.040, P(reach AND false positive REALIZED_WINDOW claim) <= 0.040 and
                P(reach AND U_W < theta_W) <= 0.040;
    lam_kappa = the smallest GRID value such that, in every D_P* cell with kappa_core = 0 (theta = 0),
                P(reach AND T1a) <= 0.020 and P(reach AND NEG) <= 0.020;
    CONFIRMATION: the 3 worst cells per surface at the selected lam are re-run at 100,000 fresh replications
                (streams 1..5); the 95% Wilson upper bound must be <= 0.050 (L_W, U_W) / <= 0.025 (T1a, NEG).
                If a confirmation fails, lam moves to the next GRID value and the confirmation is repeated (never down).
    Targets 0.040 / 0.020 are 80% of the nominal levels: a margin, because a class is never exhaustive (Astra 5).
  PUBLISHED COMPARATORS (same replications; never selected unless they meet the criterion and dominate in power):
    C1   cycle-1 8.1b rule (lam = 1) for L_W; cycle-0 5-date-block T1a / NEG / U_W (Astra's M2 objects)
    C2   block set {5, 10, 20, 30, 40}, lam = 1
    C3   reference quantile 0.975 for L_W (lam = 1)
  T1b (proof gap, measured, not changed): PINM exactly as spec 8.2 / 8.3 with B = 2,000 draws per replication
    (the finite-B p-value (1 + #{W* >= W}) / (B + 1) is valid under the declared copula for any B; spec B = 20,000).

Usage:
  python3 <this file> PLAN [REPS]       PLAN in {class, fav35, geo, outside, t1b, power, astra}  (default 20000)
  python3 <this file> cell PLAN IDX REPS   one cell, independent streams 1..5 of REPS/5 each (confirmation)
Seeds: SeedSequence([20261101, plan_code, cell_index, stream]).  Requires numpy, scipy.  Set OMP_NUM_THREADS=1.
"""
import json
import math
import os
import sys

import numpy as np
from scipy import stats
from scipy.signal import lfilter
from scipy.special import ndtr, ndtri

ERT, CUT, Z80 = 0.02, 0.04, 2.4865
OPD = 14
RHO = (0.05, 0.05, 0.10)
BL = (5, 10, 20, 30)
BL40 = (5, 10, 20, 30, 40)
GRID = tuple(round(1.0 + 0.05 * i, 2) for i in range(31))     # 1.00 .. 2.50
SEED_BASE = 20261101
PLAN_CODE = dict(class_=1, fav35=2, geo=3, outside=4, t1b=5, power=6, astra=7)
PINM_B = 2000
PINM_RHO = (0.10, 0.10, 0.10)

_T95 = np.array([np.inf] + [float(stats.t.ppf(0.95, d)) for d in range(1, 2001)])
_T975 = np.array([np.inf] + [float(stats.t.ppf(0.975, d)) for d in range(1, 2001)])


# ------------------------------------------------------------------------------------------------ process
def prices(rng, kind, n):
    if kind == 'mid':
        return rng.uniform(0.35, 0.80, n)
    if kind == 'fav':
        return rng.uniform(0.70, 0.90, n)
    if kind == 'favmix':
        u = rng.random(n) < 0.5
        return np.where(u, rng.uniform(0.70, 0.90, n), rng.uniform(0.35, 0.80, n))
    if kind == 'wide':
        return np.exp(rng.uniform(math.log(0.04), math.log(0.90), n))
    if kind == 'low':
        return rng.uniform(0.04, 0.35, n)
    if kind in ('tail1', 'tail3'):
        s = 0.01 if kind == 'tail1' else 0.03
        u = rng.random(n) < s
        return np.where(u, rng.uniform(0.02, 0.039, n), rng.uniform(0.35, 0.80, n))
    raise ValueError(kind)


def fills(rng, cap, n):
    return rng.uniform(5.0, 25.0, n) if cap == 'thin' else np.full(n, 50.0)


def go_check(c, C, st, S):
    """Spec 10.2 / 10.3 on the OP trades (outcome-free)."""
    J = c.size
    if J == 0:
        return False
    mbar = J / OPD
    s2 = J * float((C * C * (1 - c) / c).sum()) / float(C.sum()) ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    if not core.any():
        return False
    se0k = math.sqrt(float((c[core] * (1 - c[core])).mean()) * deff / (120 * core.sum() / OPD))
    k = np.bincount(st, minlength=S); k = k[k > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    return bool(pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and k.sum() ** 2 / float((k * k).sum()) >= 15)


def gen_window(rng, g):
    S, D, m = g['S'], g['D'], g['m']
    P = g.get('P', 0)
    Tc = D + P
    paused = np.zeros(Tc, bool)
    if P:
        if g.get('lay', 'rand') == 'rand':
            paused[rng.choice(np.arange(1, Tc - 1), P, replace=False)] = True
        else:
            s0 = int(rng.integers(1, Tc - P))
            paused[s0:s0 + P] = True
    cnt = np.minimum(rng.poisson(m, Tc), 2 * S)
    cnt[paused] = 0
    day = np.repeat(np.arange(Tc), cnt)
    return Tc, day


def persistent(rng, g, Tc, S):
    """Unit-variance persistent date-level component on the Tc calendar days (or (Tc, k) for hemi / stn)."""
    kind = g.get('pk')
    if kind is None:
        return None
    par = g['pp']
    if kind in ('ar', 'hemi', 'stn'):
        k = 1 if kind == 'ar' else (2 if kind == 'hemi' else S)
        u = rng.standard_normal((Tc, k))
        e = np.empty((Tc, k)); e[0] = u[0]               # stationary start, unit variance
        if Tc > 1:
            e[1:] = lfilter([math.sqrt(1 - par * par)], [1.0, -par], u[1:], axis=0, zi=(par * u[0])[None, :])[0]
        return e[:, 0] if kind == 'ar' else e
    if kind == 'mk':
        stay = (1 + par) / 2
        flips = rng.random(Tc) > stay
        flips[0] = False
        s0 = 1.0 if rng.random() < 0.5 else -1.0
        return np.cumprod(np.where(flips, -1.0, 1.0)) * s0
    if kind == 'box':
        L = int(par)
        u = rng.standard_normal(Tc + L - 1)
        cs = np.concatenate(([0.0], np.cumsum(u)))
        return (cs[L:] - cs[:-L]) / math.sqrt(L)
    raise ValueError(kind)


_MKQ = {}


def _mk_table(rv):
    """Exact inverse of the two-state mixture CDF 0.5 Phi((q - a)/s) + 0.5 Phi((q + a)/s) on a fine p grid (Newton to
    machine precision); used by linear interpolation (grid step 2.5e-5 in p; interpolation error < 1e-8 in p)."""
    if rv not in _MKQ:
        a = math.sqrt(rv); sg = math.sqrt(1 - rv)
        pg = np.linspace(1e-7, 1 - 1e-7, 40001)
        q = ndtri(pg)
        for _ in range(60):
            F = 0.5 * ndtr((q - a) / sg) + 0.5 * ndtr((q + a) / sg)
            f = 0.5 * (np.exp(-0.5 * ((q - a) / sg) ** 2) + np.exp(-0.5 * ((q + a) / sg) ** 2)) / (sg * math.sqrt(2 * math.pi))
            q = q - (F - pg) / f
        _MKQ[rv] = (pg, q)
    return _MKQ[rv]


def thresholds(p, g):
    """q with P(Z < q) = p for the latent law (Gaussian unless the two-state component is present)."""
    if g.get('pk') != 'mk':
        return ndtri(p)
    pg, qg = _mk_table(g['rv'])
    return np.where(p >= 1.0, np.inf, np.interp(p, pg, qg))


# ------------------------------------------------------------------------------------------------ engine (spec 8.1)
def cr_b(M, Cn, Q, b):
    """Two-way CR (spec 8.1, max-of-three, CR1 per dimension) from calendar-day x station sums, blocks of length b."""
    T, S = M.shape
    nb = -(-T // b)
    pad = nb * b - T
    if pad:
        M = np.vstack([M, np.zeros((pad, S))]); Cn = np.vstack([Cn, np.zeros((pad, S))])
    Mb = M.reshape(nb, b, S).sum(axis=1)
    Cb = Cn.reshape(nb, b, S).sum(axis=1)
    sB = Mb.sum(axis=1); sS = Mb.sum(axis=0)
    GB = int(np.count_nonzero(Cb.sum(axis=1))); GS = int(np.count_nonzero(Cb.sum(axis=0))); GBS = int(np.count_nonzero(Cb))
    q2 = Q * Q
    VB = GB / (GB - 1.0) * float(sB @ sB) / q2
    VS = GS / (GS - 1.0) * float(sS @ sS) / q2
    VBS = GBS / (GBS - 1.0) * float((Mb * Mb).sum()) / q2
    return math.sqrt(max(VB, VS, VB + VS - VBS)), min(GB, GS) - 1, GB


def mats(day, st, r, Tc, S):
    key = day * S + st
    return (np.bincount(key, weights=r, minlength=Tc * S).reshape(Tc, S),
            np.bincount(key, minlength=Tc * S).reshape(Tc, S).astype(float))


def halfwidths(day, st, r, Tc, S, Q):
    """Returns dict b -> (SE, df); blocks 5..40."""
    M, Cn = mats(day, st, r, Tc, S)
    out = {}
    for b in BL40:
        se, df, GB = cr_b(M, Cn, Q, b)
        out[b] = (se, df, GB)
    return out


def H(hw, bset, tab):
    return max(tab[hw[b][1]] * hw[b][0] for b in bset)


def pinm_t1b(rng_p, day, st, c_t, y_t, S):
    """Spec 8.2 / 8.3: PINM upper-tail p-value of W_tail under the declared copula (0.10, 0.10, 0.10), B = PINM_B."""
    n = c_t.size
    if n == 0:
        return False, 1.0
    W = float(y_t.sum())
    ud, di = np.unique(day, return_inverse=True)
    us, si = np.unique(st, return_inverse=True)
    uc, ci = np.unique(day * S + st, return_inverse=True)
    q = ndtri(c_t)
    rd, rs, rc = PINM_RHO
    re_ = math.sqrt(1 - rd - rs - rc)
    cnt = 0
    for _ in range(PINM_B // 1000):
        A = rng_p.standard_normal((1000, ud.size)); Sx = rng_p.standard_normal((1000, us.size))
        K = rng_p.standard_normal((1000, uc.size)); E = rng_p.standard_normal((1000, n))
        Z = math.sqrt(rd) * A[:, di] + math.sqrt(rs) * Sx[:, si] + math.sqrt(rc) * K[:, ci] + re_ * E
        Ws = (Z < q).sum(axis=1)
        cnt += int((Ws >= W).sum())
    pval = (1 + cnt) / (PINM_B + 1)
    return pval <= 0.025, pval


def one_rep(rng, g, do_pinm):
    S = g['S']
    # OP (outcome-free design check)
    n_op = int(np.minimum(rng.poisson(g['m'], OPD), 2 * S).sum())
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    st_op = rng.choice(S, n_op, p=act)
    c_op = prices(rng, g['pr'], n_op); C_op = fills(rng, g['cap'], n_op)
    go = go_check(c_op, C_op, st_op, S)
    if not go:
        return None
    Tc, day = gen_window(rng, g)
    n = day.size
    st = rng.choice(S, n, p=act)
    c = prices(rng, g['pr'], n); C = fills(rng, g['cap'], n)
    p = np.minimum(1.0, c * (1.0 + g['th']))
    # latent
    z = (math.sqrt(RHO[0]) * rng.standard_normal(Tc)[day] + math.sqrt(RHO[1]) * rng.standard_normal(S)[st]
         + math.sqrt(RHO[2]) * rng.standard_normal(Tc * S)[day * S + st])
    used = sum(RHO)
    e = persistent(rng, g, Tc, S)
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
    y = (z < thresholds(p, g)).astype(float)
    # statistics
    nsh = C / c
    Q = float(C.sum())
    N = nsh * (y - c)
    th = float(N.sum()) / Q
    thW = float((nsh * (p - c)).sum()) / Q
    hw = halfwidths(day, st, N - th * C, Tc, S, Q)
    core = c >= CUT
    tail = ~core
    # kappa_core
    x = (y - c)[core]
    nk = x.size
    kap = float(x.mean()); kap_true = float((p - c)[core].mean())
    hk = halfwidths(day[core], st[core], x - kap, Tc, S, float(nk))
    sek5 = hk[5][0]
    viid = nk / (nk - 1.0) * float(((x - kap) ** 2).sum()) / float(nk) ** 2
    blocks5 = hw[5][2]
    sc = np.bincount(st, minlength=S); sc = sc[sc > 0]
    info = bool(g['D'] >= 60 and blocks5 >= 12 and sc.size >= 25 and sc.sum() ** 2 / float((sc * sc).sum()) >= 15
                and sek5 <= 0.025 and sek5 * sek5 / viid <= 6.0)
    if not info:
        return None
    # theta_core (U_W)
    if tail.any():
        Cc = C[core]; Qc = float(Cc.sum())
        thc = float(N[core].sum()) / Qc
        hc = halfwidths(day[core], st[core], N[core] - thc * Cc, Tc, S, Qc)
        M_tail = float((nsh[tail] - C[tail]).sum()) / Q
        w = Qc / Q
    else:
        thc, hc, M_tail, w = th, hw, 0.0, 1.0
    # gates G1, G2 (G3 implied in synthetic data), for SUPPORTED
    cc = c + 0.01
    g1 = float(((C / cc) * (y - cc)).sum()) / Q > 0
    pos = np.maximum(N, 0.0); gross = float(pos.sum())
    top5 = float(np.partition(N, -5)[-5:].sum()) if n >= 5 else float(N.sum())
    g2 = bool(gross > 0 and (float(N.sum()) - top5) / Q > 0
              and np.bincount(day, weights=pos).max() <= 0.25 * gross
              and np.bincount(st, weights=pos, minlength=S).max() <= 0.20 * gross)
    rec = dict(th=th, thW=thW, kap=kap, kt=kap_true, thc=thc, w=w, Mt=M_tail, gates=bool(g1 and g2),
               H_R0=_T95[hw[5][1]] * hw[5][0], H_A=H(hw, BL, _T95), H_B40=H(hw, BL40, _T95), H_Q=H(hw, BL, _T975),
               Hk5=_T975[hk[5][1]] * hk[5][0], HkA=H(hk, BL, _T975),
               Hc5=_T975[hc[5][1]] * hc[5][0], HcA=H(hc, BL, _T975),
               ntail=int(tail.sum()))
    if do_pinm:
        rec['T1b'], rec['pinm_p'] = pinm_t1b(rng, day[tail], st[tail], c[tail], y[tail], S)
    return rec


# ------------------------------------------------------------------------------------------------ cell runner
def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    ph = k / n
    den = 1 + z * z / n
    cen = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [round(max(0.0, cen - hw), 5), round(min(1.0, cen + hw), 5)]


def rate(k, n):
    return dict(p=round(k / n, 5) if n else None, k=int(k), n=int(n), ci=wilson(k, n))


def run_cell(plan, idx, g, reps, stream):
    seed = [SEED_BASE, PLAN_CODE[plan], idx, stream]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    do_pinm = bool(g.get('pinm'))
    recs = []
    for _ in range(reps):
        r = one_rep(rng, g, do_pinm)
        if r is not None:
            recs.append(r)
    return counts(plan, idx, g, reps, seed, recs)


def counts(plan, idx, g, reps, seed, recs):
    out = dict(plan=plan, idx=idx, g=g, reps=reps, seed=seed, reach=rate(len(recs), reps))
    if not recs:
        out['empty'] = True
        return out
    A = {k: np.array([r[k] for r in recs], float) for k in recs[0] if k not in ('T1b', 'pinm_p')}
    th, thW, kap, kt = A['th'], A['thW'], A['kap'], A['kt']
    lam = np.array(GRID)[:, None]
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
    old_up = th + lam * A['H_A']
    incons_old = ((U < 0) & (old_up >= 0)).sum(axis=1)
    T1a = (kap - lam * A['HkA'] > 0)
    NEG = (kap + lam * A['HkA'] < 0)
    T1a_null = (T1a & (kt <= 0)).sum(axis=1); NEG_null = (NEG & (kt >= 0)).sum(axis=1)
    out['grid'] = list(GRID)
    out['by_lam'] = dict(miss=miss.tolist(), fpos=fpos.tolist(), sup=sup.tolist(), t2=t2.tolist(),
                         uw_miss=uw_miss.tolist(), uw_loss=uw_loss.tolist(), iv_miss=iv_miss.tolist(),
                         incons_old_headline=incons_old.tolist(), T1a=T1a.sum(axis=1).tolist(), NEG=NEG.sum(axis=1).tolist(),
                         T1a_null=T1a_null.tolist(), NEG_null=NEG_null.tolist())
    # comparators at lam = 1 and the frozen 5-date objects (Astra M2)
    def c(x):
        return int(np.sum(x))
    out['cmp'] = dict(
        miss_R0=c(th - A['H_R0'] > thW), fpos_R0=c((th - A['H_R0'] > 0) & (th >= ERT) & (thW <= 0)),
        sup_R0=c((th - A['H_R0'] > 0) & (th >= ERT) & (A['gates'] > 0)),
        miss_B40=c(th - A['H_B40'] > thW), fpos_B40=c((th - A['H_B40'] > 0) & (th >= ERT) & (thW <= 0)),
        sup_B40=c((th - A['H_B40'] > 0) & (th >= ERT) & (A['gates'] > 0)),
        miss_Q975=c(th - A['H_Q'] > thW), fpos_Q975=c((th - A['H_Q'] > 0) & (th >= ERT) & (thW <= 0)),
        sup_Q975=c((th - A['H_Q'] > 0) & (th >= ERT) & (A['gates'] > 0)),
        T1a_5=c((kap - A['Hk5'] > 0) & (kt <= 0)), NEG_5=c((kap + A['Hk5'] < 0) & (kt >= 0)),
        T1a_5_all=c(kap - A['Hk5'] > 0), NEG_5_all=c(kap + A['Hk5'] < 0),
        uw_miss_5=c(A['w'] * (A['thc'] + A['Hc5']) + A['Mt'] < thW))
    out['ratio_HkA_Hk5_median'] = round(float(np.median(A['HkA'] / A['Hk5'])), 4)
    out['ratio_HA_HR0_median'] = round(float(np.median(A['H_A'] / A['H_R0'])), 4)
    out['tail_trades_mean'] = round(float(A['ntail'].mean()), 2)
    if g.get('pinm'):
        t1b = np.array([r['T1b'] for r in recs], bool)
        out['T1b'] = int(t1b.sum())
        T1a5 = kap - A['Hk5'] > 0
        out['T1_old'] = int((t1b | T1a5).sum())
        out['T1_by_lam'] = (t1b[None, :] | (kap - lam * A['HkA'] > 0)).sum(axis=1).tolist()
    return out


# ------------------------------------------------------------------------------------------------ plans
BASE = dict(D=120, S=48, m=17, cap='thin', th=0.0, pr='mid', P=0, lay='rand')


def G(**kw):
    g = dict(BASE); g.update(kw); return g


def DEPS(full=True):
    d = [dict()]
    for phi in ((0.5, 0.7, 0.8, 0.9) if full else (0.8, 0.9)):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='ar', pp=phi, rv=rv))
    for phi in (0.8, 0.9):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='mk', pp=phi, rv=rv))
    for L in (15, 30):
        for rv in (0.02, 0.05, 0.10):
            d.append(dict(pk='box', pp=L, rv=rv))
    return d


def plan_class():
    """Main D_P* grid at m = 17 (where every run-G / Astra worst cell lies): 25 dependence x 3 CORE price laws x 3 calendars
    x 2 fills x theta {0, 0.10}."""
    cells = []
    for dep in DEPS(True):
        for pr in ('mid', 'fav', 'favmix'):
            for cal in (dict(P=0), dict(P=30, lay='rand'), dict(P=30, lay='run')):
                for cap in ('thin', 'full'):
                    for th in (0.0, 0.10):
                        cells.append(G(m=17, cap=cap, th=th, pr=pr, **cal, **dep))
    return cells


def plan_fav35():
    """m = 35 slice (IF5 screens most persistent windows) and the theta = 0.05 slice, worst-shape dependence only."""
    cells = []
    deps = [dict()] + [dict(pk='ar', pp=0.9, rv=rv) for rv in (0.02, 0.05, 0.10)] + \
        [dict(pk='mk', pp=0.9, rv=rv) for rv in (0.05, 0.10)] + [dict(pk='box', pp=30, rv=rv) for rv in (0.05, 0.10)]
    for dep in deps:
        for pr in ('mid', 'fav'):
            for cal in (dict(P=0), dict(P=30, lay='rand')):
                for cap in ('thin', 'full'):
                    cells.append(G(m=35, cap=cap, th=0.0, pr=pr, **cal, **dep))
                    cells.append(G(m=35, cap=cap, th=0.10, pr=pr, **cal, **dep))
                cells.append(G(m=17, cap='thin', th=0.05, pr=pr, **cal, **dep))
    return cells


def plan_geo():
    """Other class geometries: truncated windows (D 60 / 90), price laws 'wide' / 'low', hemisphere / station regimes,
    tail mixes (U_W with M_tail > 0)."""
    cells = []
    deps = [dict(), dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10), dict(pk='box', pp=30, rv=0.05)]
    for D in (60, 90):
        for dep in deps:
            for pr in ('mid', 'fav'):
                for th in (0.0, 0.10):
                    cells.append(G(D=D, th=th, pr=pr, **dep))
    for pr in ('wide', 'low'):
        for dep in deps:
            cells.append(G(th=0.0, pr=pr, **dep))
    for pk in ('hemi', 'stn'):
        for rv in (0.05, 0.10):
            for pr in ('mid', 'fav'):
                for th in (0.0, 0.10):
                    cells.append(G(th=th, pr=pr, pk=pk, pp=0.9, rv=rv))
    for pr, m, cap in (('tail1', 17, 'thin'), ('tail3', 35, 'full')):
        for dep in deps:
            for th in (0.0, 0.10):
                cells.append(G(m=m, cap=cap, th=th, pr=pr, **dep))
    return cells


def plan_outside():
    """Outside D_P* (disclosure only): phi 0.95 / 0.97, rv 0.20, two-component memory."""
    cells = []
    for pr in ('mid', 'fav'):
        for phi, rv in ((0.95, 0.05), (0.95, 0.10), (0.97, 0.05)):
            for th in (0.0, 0.10):
                cells.append(G(th=th, pr=pr, pk='ar', pp=phi, rv=rv))
        for th in (0.0, 0.10):
            cells.append(G(th=th, pr=pr, pk='ar', pp=0.9, rv=0.20))
            cells.append(G(th=th, pr=pr, pk='box', pp=60, rv=0.05))
    return cells


def plan_t1b():
    """T1b (PINM) and T1 FWER under the sharp null on TAIL and kappa_core = 0 (theta = 0), with persistence."""
    cells = []
    deps = [dict(), dict(pk='ar', pp=0.8, rv=0.05), dict(pk='ar', pp=0.9, rv=0.05), dict(pk='ar', pp=0.9, rv=0.10),
            dict(pk='mk', pp=0.9, rv=0.10), dict(pk='box', pp=30, rv=0.10)]
    for pr, m, cap in (('tail3', 35, 'full'), ('tail1', 17, 'thin')):
        for dep in deps:
            cells.append(G(m=m, cap=cap, th=0.0, pr=pr, pinm=True, **dep))
    return cells


def plan_power():
    """Power / feasibility cost (no persistence unless stated): T2 / SUPPORTED at theta_PCE, 0.10, 0.12, 0.15;
    T1a at kappa ~ +0.035 (theta 0.06 on 'mid'); NEG at kappa ~ -0.07 (theta -0.12 on 'mid')."""
    cells = []
    for m, cap, pce in ((17, 'thin', 0.09), (17, 'full', 0.08), (35, 'thin', 0.07), (35, 'full', 0.07)):
        for th in sorted({pce, 0.10, 0.12, 0.15, 0.20}):
            cells.append(G(m=m, cap=cap, th=th))
        cells.append(G(m=m, cap=cap, th=0.06))
        cells.append(G(m=m, cap=cap, th=-0.12))
        cells.append(G(m=m, cap=cap, th=-0.06))
        cells.append(G(m=m, cap=cap, th=pce, pk='ar', pp=0.8, rv=0.05))
    return cells


def plan_astra():
    """Astra @ac777a87 counterexample cells, verbatim geometry (m 17), run here at 20,000 (and by `cell` at 100,000)."""
    return [
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.9, rv=0.05),          # miss 0.0635 @100k
        G(cap='thin', th=0.0, pr='fav', pk='ar', pp=0.9, rv=0.05),           # false positive 0.0605 @100k
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.9, rv=0.10),          # miss 0.0852
        G(cap='thin', th=0.0, pr='fav', pk='ar', pp=0.9, rv=0.10),           # size 0.0721
        G(cap='thin', th=0.10, pr='mid', pk='ar', pp=0.9, rv=0.05, P=30, lay='rand'),   # 30 paused 0.0531 @100k
        G(cap='thin', th=0.10, pr='mid', pk='mk', pp=0.9, rv=0.05),          # two-state 0.0526
        G(cap='thin', th=0.10, pr='mid', pk='box', pp=30, rv=0.05),          # literal spec-9 boxcar 0.0597
        G(cap='thin', th=0.0, pr='mid', pk='box', pp=30, rv=0.05),           # boxcar size 0.0522
        G(cap='thin', th=0.0, pr='mid', pk='ar', pp=0.9, rv=0.05),           # M2: T1a / NEG / U_W at kappa = 0
        G(cap='thin', th=0.0, pr='mid', pk='ar', pp=0.9, rv=0.10),
        G(cap='thin', th=0.10, pr='mid', pk='ar', pp=0.9, rv=0.05),          # run-G worst grid cell 0.0471 @100k (Astra)
        G(cap='thin', th=0.10, pr='fav', pk='ar', pp=0.95, rv=0.05),         # outside: phi 0.95 0.0769
    ]


PLANS = dict(class_=plan_class, fav35=plan_fav35, geo=plan_geo, outside=plan_outside, t1b=plan_t1b, power=plan_power,
             astra=plan_astra)


def _job(a):
    plan, idx, g, reps, stream = a
    return json.dumps(run_cell(plan, idx, g, reps, stream))


if __name__ == '__main__':
    from multiprocessing import Pool
    procs = int(os.environ.get('WF_PROCS', '4'))
    if sys.argv[1] == 'cell':
        plan, idx, reps = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        plan = 'class_' if plan == 'class' else plan
        g = PLANS[plan]()[idx]
        jobs = [(plan, idx, g, reps // 5, s) for s in (1, 2, 3, 4, 5)]
        with Pool(procs) as pool:
            parts = [json.loads(x) for x in pool.map(_job, jobs)]
        comb = dict(plan=plan, idx=idx, g=g, reps=sum(x['reps'] for x in parts), seed=[x['seed'] for x in parts],
                    combined_streams=True)
        comb['reach'] = rate(sum(x['reach']['k'] for x in parts), comb['reps'])
        comb['grid'] = list(GRID)
        comb['by_lam'] = {k: [sum(x['by_lam'][k][i] for x in parts if 'by_lam' in x) for i in range(len(GRID))]
                          for k in parts[0]['by_lam']}
        comb['cmp'] = {k: sum(x['cmp'][k] for x in parts if 'cmp' in x) for k in parts[0]['cmp']}
        for key in ('T1b', 'T1_old'):
            if key in parts[0]:
                comb[key] = sum(x[key] for x in parts)
        print(json.dumps(comb), flush=True)
        sys.exit()
    plan = sys.argv[1] if sys.argv[1] != 'class' else 'class_'
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    cells = PLANS[plan]()
    jobs = [(plan, i, g, reps, 0) for i, g in enumerate(cells)]
    with Pool(procs) as pool:
        for line in pool.imap(_job, jobs):
            print(line, flush=True)
