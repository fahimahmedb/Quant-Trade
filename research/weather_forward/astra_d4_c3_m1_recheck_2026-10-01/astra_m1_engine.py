"""ASTRA D4-C3-M1 recheck engine (independent; written from the spec text at 4423c5c3, not from the Architect's run-G code).
SYNTHETIC ONLY: no market, forecast, settlement, wallet or P&L data is read.

Per replication:
  OP (14 dates) -> GO (spec 10.2/10.3, outcome-free).  Window: D counted dates (+ optional paused calendar dates).
  Outcomes: latent Gaussian copula (date, station, cell) + optional persistent components (AR(1) date regime shared by all
  trades of a calendar date; or hemisphere / station-specific AR(1); or two-component mixture), unit latent variance,
  y = 1{Z < Phi^-1(p)} so that P(y = 1) = p exactly.
  INFO_SUFFICIENT (11.4 IF1-IF5), reach = GO and INFO.
  Two-way CR (8.1) computed from a date x station matrix of residual sums (calendar-day blocks of any length b).
  L_old = theta_hat - t_{df5,.95} SE_2w(5)          (R3 / 341e0b7a)
  L_new = theta_hat - max_b t_{df_b,.95} SE_2w(b), b in {5,10,20,30}   (8.1b at 4423c5c3)
  T1a, NEG on kappa_core (5-date blocks, 0.975), U_W = w_core U_core + M_tail (8.5, 5-date blocks, 0.975)
  theta_W = sum n (p - c) / sum C (exact).
"""
import math
import numpy as np
from scipy import stats
from scipy.special import ndtri

ERT = 0.02
CUT = 0.04
Z80 = 2.4865
OPD = 14
BLOCKS_NEW = (5, 10, 20, 30)
BLOCKS_RM = (5, 10, 20)
_TQ = {}
_CHOL = {}


def tq(p, df):
    key = (p, df)
    v = _TQ.get(key)
    if v is None:
        v = float(stats.t.ppf(p, df))
        _TQ[key] = v
    return v


def ar_chol(phi, T):
    """Cholesky factor of the stationary AR(1) correlation matrix phi^|i-j| (unit marginal variance)."""
    key = (round(phi, 6), T)
    L = _CHOL.get(key)
    if L is None:
        idx = np.arange(T)
        R = phi ** np.abs(idx[:, None] - idx[None, :])
        L = np.linalg.cholesky(R + 1e-12 * np.eye(T))
        _CHOL[key] = L
    return L


def prices(rng, g, n):
    pr = g.get('prices', 'std')
    if pr == 'std':                       # same CORE range as the declared class
        return rng.uniform(0.35, 0.80, n)
    if pr == 'fav':                       # favourite-heavy CORE (left-skewed per-trade return)
        return rng.uniform(0.70, 0.90, n)
    if pr == 'low':                       # cheap CORE legs (right-skewed)
        return rng.uniform(0.04, 0.35, n)
    if pr == 'wide':                      # whole CORE range 0.04-0.90, log-uniform
        return np.exp(rng.uniform(math.log(0.04), math.log(0.90), n))
    if pr == 'favmix':                    # half favourites (0.70-0.90), half the class range (0.35-0.80)
        u = rng.random(n)
        return np.where(u < 0.5, rng.uniform(0.70, 0.90, n), rng.uniform(0.35, 0.80, n))
    if pr == 'barbell':                   # half favourites, half cheap CORE legs
        u = rng.random(n)
        return np.where(u < 0.5, rng.uniform(0.75, 0.90, n), rng.uniform(0.05, 0.20, n))
    raise ValueError(pr)


def fills(rng, g, n):
    f = g.get('cap', 'thin')
    if f == 'thin':
        return rng.uniform(5.0, 25.0, n)
    if f == 'full':
        return np.full(n, 50.0)
    raise ValueError(f)


def generate(rng, g):
    S, D, m = g['S'], g['D'], g['m']
    act = rng.gamma(2.0, 1.0, S)
    act = act / act.sum()
    if g.get('dom_st'):
        rest = np.delete(act, 0)
        rest = rest / rest.sum() * (1.0 - g['dom_st'])
        act = np.concatenate(([g['dom_st']], rest))
    # calendar layout of the window: D counted dates plus P paused calendar dates (no trades), positions random
    P = int(g.get('pause', 0))
    Tcal = D + P
    paused = np.zeros(Tcal, bool)
    if P:
        paused[rng.choice(np.arange(1, Tcal - 1), P, replace=False)] = True
    cnt_op = np.minimum(rng.poisson(m, OPD), 2 * S)
    cnt_w = np.minimum(rng.poisson(m, Tcal), 2 * S)
    cnt_w[paused] = 0
    if g.get('dom_date'):
        live = np.flatnonzero(~paused)
        cnt_w[live[rng.integers(live.size)]] = 2 * S
    # OP trades
    n_op = int(cnt_op.sum())
    st_op = rng.choice(S, n_op, p=act)
    c_op = prices(rng, g, n_op)
    C_op = fills(rng, g, n_op)
    # window trades
    day = np.repeat(np.arange(Tcal), cnt_w)
    n_w = day.size
    st = rng.choice(S, n_w, p=act)
    c = prices(rng, g, n_w)
    C = fills(rng, g, n_w)
    th = g['th']
    if g.get('het'):
        th = th + rng.normal(0.0, g['het'], S)[st]
    p = np.clip(c * (1.0 + th), 1e-9, 1.0 - 1e-9) if g.get('het') else np.minimum(c * (1.0 + th), 1.0)
    return dict(S=S, Tcal=Tcal, op=(st_op, c_op, C_op), day=day, st=st, c=c, C=C, p=p)


def go_check(op, S):
    st, c, C = op
    J = c.size
    mbar = J / OPD
    sigma2 = J * float(np.sum(C * C * (1.0 - c) / c)) / float(C.sum()) ** 2
    deff = 1.5 * (1.0 + 0.03 * (mbar - 1.0))
    se0 = math.sqrt(sigma2 * deff / (120.0 * mbar))
    pce = math.ceil(round(100.0 * Z80 * se0, 9)) / 100.0
    core = c >= CUT
    se0k = math.sqrt(float(np.mean(c[core] * (1.0 - c[core]))) * deff / (120.0 * core.sum() / OPD))
    k = np.bincount(st, minlength=S)
    k = k[k > 0]
    kish = k.sum() ** 2 / float(np.sum(k * k))
    return (pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and kish >= 15), pce


def latent(rng, w, g):
    """Unit-variance latent Z for every window trade."""
    S, Tcal = w['S'], w['Tcal']
    day, st = w['day'], w['st']
    rd, rs, rc = g.get('rho', (0.05, 0.05, 0.10))
    n = day.size
    cell = day * S + st
    uc, ci = np.unique(cell, return_inverse=True)
    z = (math.sqrt(rd) * rng.standard_normal(Tcal)[day] + math.sqrt(rs) * rng.standard_normal(S)[st]
         + math.sqrt(rc) * rng.standard_normal(uc.size)[ci])
    used = rd + rs + rc
    for comp in g.get('persist', ()):
        kind, phi, rv = comp
        L = ar_chol(phi, Tcal)
        if kind == 'date':                    # one regime shared by every trade of a calendar date (the class 𝒟_P)
            e = L @ rng.standard_normal(Tcal)
            z = z + math.sqrt(rv) * e[day]
        elif kind == 'hemi':                  # two independent regimes, each shared by half of the stations
            E = L @ rng.standard_normal((Tcal, 2))
            z = z + math.sqrt(rv) * E[day, (st >= S // 2).astype(int)]
        elif kind == 'station':               # station-specific persistent bias drift
            E = L @ rng.standard_normal((Tcal, S))
            z = z + math.sqrt(rv) * E[day, st]
        else:
            raise ValueError(kind)
        used += rv
    for comp in g.get('persist2', ()):
        kind, par, rv = comp
        if kind == 'boxcar':                  # date regime = trailing par-date mean of iid date shocks (MA(par-1), unit var):
            Lb = int(par)                     # the error of a par-date trailing-mean bias correction (spec 9 mechanism)
            u = rng.standard_normal(Tcal + Lb - 1)
            cs = np.concatenate(([0.0], np.cumsum(u)))
            e = (cs[Lb:] - cs[:-Lb]) / math.sqrt(Lb)
            z = z + math.sqrt(rv) * e[day]
        elif kind == 'markov':                # two-state +-1 date regime, stay probability par: corr (2 par - 1)^k, non-Gaussian
            s = np.empty(Tcal)
            s[0] = 1.0 if rng.random() < 0.5 else -1.0
            flips = rng.random(Tcal) > par
            for t in range(1, Tcal):
                s[t] = -s[t - 1] if flips[t] else s[t - 1]
            z = z + math.sqrt(rv) * s[day]
        else:
            raise ValueError(kind)
        used += rv
    z = z + math.sqrt(1.0 - used) * rng.standard_normal(n)
    return z


def thresholds(p, g):
    """q_j with P(Z_j < q_j) = p_j for the configured latent law (Gaussian unless a Markov +-a component is present)."""
    mk = [c for c in g.get('persist2', ()) if c[0] == 'markov']
    if not mk:
        return ndtri(p)
    a = math.sqrt(mk[0][2])
    sg = math.sqrt(1.0 - a * a)
    from scipy.special import ndtr
    pc = np.clip(p, 1e-12, 1 - 1e-12)
    q = ndtri(pc)
    for _ in range(50):
        F = 0.5 * ndtr((q - a) / sg) + 0.5 * ndtr((q + a) / sg)
        f = 0.5 * (np.exp(-0.5 * ((q - a) / sg) ** 2) + np.exp(-0.5 * ((q + a) / sg) ** 2)) / (sg * math.sqrt(2 * math.pi))
        q = q - (F - pc) / f
    return np.where(p >= 1.0, np.inf, q)


def cr_from_matrix(M, Cnt, Q, b, S_used=None):
    """Two-way CR (spec 8.1) from date x station residual sums M and trade counts Cnt, calendar blocks of length b.
    Returns (SE, df, VB, VS, V2w)."""
    T, S = M.shape
    nb = -(-T // b)
    pad = nb * b - T
    if pad:
        M = np.vstack([M, np.zeros((pad, S))])
        Cnt = np.vstack([Cnt, np.zeros((pad, S), Cnt.dtype)])
    Mb = M.reshape(nb, b, S).sum(axis=1)          # block x station sums
    Cb = Cnt.reshape(nb, b, S).sum(axis=1)
    sB = Mb.sum(axis=1)
    sS = Mb.sum(axis=0)
    GB = int(np.count_nonzero(Cb.sum(axis=1)))
    GS = int(np.count_nonzero(Cb.sum(axis=0)))
    GBS = int(np.count_nonzero(Cb))
    q2 = Q * Q
    VB = GB / (GB - 1.0) * float(sB @ sB) / q2
    VS = GS / (GS - 1.0) * float(sS @ sS) / q2
    VBS = GBS / (GBS - 1.0) * float(np.sum(Mb * Mb)) / q2
    V2 = VB + VS - VBS
    return math.sqrt(max(VB, VS, V2)), min(GB, GS) - 1, VB, VS, V2


def mats(day, st, r, Tcal, S):
    key = day * S + st
    M = np.bincount(key, weights=r, minlength=Tcal * S).reshape(Tcal, S)
    Cn = np.bincount(key, minlength=Tcal * S).reshape(Tcal, S)
    return M, Cn


def analyse(w, y):
    S, Tcal = w['S'], w['Tcal']
    day, st, c, C, p = w['day'], w['st'], w['c'], w['C'], w['p']
    n = C / c
    Q = float(C.sum())
    N = n * (y - c)
    th = float(N.sum()) / Q
    thW = float(np.sum(n * (p - c))) / Q
    r = N - th * C
    M, Cn = mats(day, st, r, Tcal, S)
    half = {}
    se_b = {}
    for b in BLOCKS_NEW:
        se, df, _, _, _ = cr_from_matrix(M, Cn, Q, b)
        half[b] = tq(0.95, df) * se
        se_b[b] = (se, df)
    L_old = th - half[5]
    L_rm = th - max(half[b] for b in BLOCKS_RM)
    L_new = th - max(half.values())
    up_new = th + max(half.values())                 # upper end of the 8.1b headline two-sided 90% interval
    # information axis: kappa_core with 5-date blocks
    core = c >= CUT
    x = (y - c)[core]
    nk = x.size
    kap = float(x.mean())
    kap_true = float(np.mean((p - c)[core]))
    Mk, Ck = mats(day[core], st[core], x - kap, Tcal, S)
    sek, dfk, VBk, VSk, V2k = cr_from_matrix(Mk, Ck, float(nk), 5)
    viid = nk / (nk - 1.0) * float(np.sum((x - kap) ** 2)) / float(nk) ** 2
    deffk = max(VBk, VSk, V2k) / viid
    blocks5 = np.unique(day // 5).size
    sc = np.bincount(st, minlength=S)
    sc = sc[sc > 0]
    kish = sc.sum() ** 2 / float(np.sum(sc * sc))
    info = bool(blocks5 >= 12 and sc.size >= 25 and kish >= 15 and sek <= 0.025 and deffk <= 6.0)
    t975k = tq(0.975, dfk)
    T1a = kap - t975k * sek > 0
    NEG = kap + t975k * sek < 0
    # U_W (8.5): core CR at one-sided 0.975 with 5-date blocks + deterministic tail supremum
    Cc = C[core]
    Qc = float(Cc.sum())
    thc = float(N[core].sum()) / Qc
    Mc, Ccn = mats(day[core], st[core], N[core] - thc * Cc, Tcal, S)
    sec, dfc, _, _, _ = cr_from_matrix(Mc, Ccn, Qc, 5)
    U_core = thc + tq(0.975, dfc) * sec
    tail = ~core
    M_tail = float(np.sum(n[tail] - C[tail])) / Q if tail.any() else 0.0
    U_W = (Qc / Q) * U_core + M_tail
    return dict(th=th, thW=thW, L_old=L_old, L_rm=L_rm, L_new=L_new, up_new=up_new, info=info, T1a=T1a, NEG=NEG,
                kap_true=kap_true, U_W=U_W, se5=se_b[5][0], se30=se_b[30][0], df30=se_b[30][1])


KEYS = ('go', 'info', 'reach',
        'miss_old', 'miss_rm', 'miss_new', 'miss_old_all', 'miss_new_all',
        'pos_old', 'pos_new', 'fpos_old', 'fpos_new', 'T2_new', 'T2_old',
        'T1a', 'NEG', 'T1a_null', 'NEG_null', 'UW_miss', 'UW_loss_false', 'UW_loss', 'UW_loss_vs_headline',
        'new_above_old')


def run(g, reps, seed):
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    K = dict.fromkeys(KEYS, 0)
    for _ in range(reps):
        w = generate(rng, g)
        go, _ = go_check(w['op'], w['S'])
        z = latent(rng, w, g)
        y = (z < thresholds(w['p'], g)).astype(float)
        o = analyse(w, y)
        reach = go and o['info']
        K['go'] += go
        K['info'] += o['info']
        K['reach'] += reach
        K['miss_old_all'] += o['L_old'] > o['thW']
        K['miss_new_all'] += o['L_new'] > o['thW']
        K['new_above_old'] += o['L_new'] > o['L_old'] + 1e-15
        if not reach:
            continue
        K['miss_old'] += o['L_old'] > o['thW']
        K['miss_rm'] += o['L_rm'] > o['thW']
        K['miss_new'] += o['L_new'] > o['thW']
        po = o['L_old'] > 0 and o['th'] >= ERT
        pn = o['L_new'] > 0 and o['th'] >= ERT
        K['pos_old'] += po
        K['pos_new'] += pn
        K['fpos_old'] += po and o['thW'] <= 0
        K['fpos_new'] += pn and o['thW'] <= 0
        K['T2_new'] += o['L_new'] > 0
        K['T2_old'] += o['L_old'] > 0
        K['T1a'] += o['T1a']
        K['NEG'] += o['NEG']
        K['T1a_null'] += o['T1a'] and o['kap_true'] <= 0
        K['NEG_null'] += o['NEG'] and o['kap_true'] >= 0
        K['UW_miss'] += o['U_W'] < o['thW']
        K['UW_loss'] += o['U_W'] < 0
        K['UW_loss_false'] += o['U_W'] < 0 and o['thW'] >= 0
        K['UW_loss_vs_headline'] += o['U_W'] < 0 and o['up_new'] >= 0
    return K


def mc(k, n):
    if n <= 0:
        return dict(p=None, se=None, ci=None, k=int(k), n=int(n))
    p = k / n
    se = math.sqrt(max(p * (1.0 - p), 0.0) / n)
    return dict(p=round(p, 5), se=round(se, 5), ci=[round(max(0.0, p - 1.96 * se), 5), round(min(1.0, p + 1.96 * se), 5)],
                k=int(k), n=int(n))


def summarise(name, g, reps, seeds, K):
    out = dict(name=name, g={k: v for k, v in g.items()}, reps=reps, seeds=seeds)
    for k, v in K.items():
        out[k] = mc(v, reps)
    out['miss_new_given_reach'] = mc(K['miss_new'], K['reach'])
    out['miss_old_given_reach'] = mc(K['miss_old'], K['reach'])
    out['T1a_given_reach'] = mc(K['T1a'], K['reach'])
    out['NEG_given_reach'] = mc(K['NEG'], K['reach'])
    out['UW_miss_given_reach'] = mc(K['UW_miss'], K['reach'])
    return out
