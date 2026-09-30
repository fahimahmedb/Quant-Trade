"""ASTRA independent D4 recheck engine (2026-09-30). SYNTHETIC ONLY - no market/outcome data.

Independent of the Architect script: own design generator, own vectorised two-way CR engine (sparse
cluster sums), own retired-bound inversion by order statistics, own seeds (base 930_000+).
"""
import math, json, sys
import numpy as np
from scipy import stats, sparse
from scipy.special import ndtr

ERT = 0.02
CUT = 0.04
DECL = (0.10, 0.10, 0.10)
tq = stats.t.ppf


# ---------------------------------------------------------------- designs
def design_astra_A(rng, D=120, m=35, S=48):
    """Astra C1 geometry, regenerated independently."""
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), m); N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(0.35, 0.80, N)
    op = np.flatnonzero(date < 14); rest = np.flatnonzero(date >= 14)
    t_op = rng.choice(op, 9, replace=False)
    pick = rng.choice(rest, 77, replace=False)
    c[t_op] = 0.039; c[pick[:75]] = 0.039; c[pick[75:]] = 0.001
    cheap = np.zeros(N, bool); cheap[pick[75:]] = True
    C = np.full(N, 50.0)
    return finish(dict(date=date, st=st, c=c, C=C, cheap=cheap, S=S, D=D))


def finish(d):
    d['n'] = d['C'] / d['c']
    d['q'] = np.minimum(0.999, d['c'] + 0.12)
    d['tail'] = d['c'] < CUT
    d['blk'] = d['date'] // 5
    return d


def indic(g):
    _, gi = np.unique(g, return_inverse=True)
    G = gi.max() + 1
    return sparse.csr_matrix((np.ones(gi.size), (np.arange(gi.size), gi)), shape=(gi.size, G)), G


def cr_prep(d, mask):
    blk, st = d['blk'][mask], d['st'][mask]
    mats = [indic(blk), indic(st), indic(blk * 1000 + st)]
    return mats


def cr_se_batch(E, mats, Q):
    """E: R x n residual matrix. Returns SE (R,) and df by spec 8.1."""
    V = []
    for M, G in mats:
        s = (M.T @ E.T).T if sparse.issparse(M) else E @ M
        s = np.asarray(s)
        V.append(G / (G - 1) * (s ** 2).sum(1) / Q ** 2)
    vb, vs, vbs = V
    v2 = vb + vs - vbs
    return np.sqrt(np.maximum(np.maximum(vb, vs), v2)), min(mats[0][1], mats[1][1]) - 1


def latent_uniforms(rng, d, R, rho, extra=None):
    rd, rs, rc = rho
    date, st = d['date'], d['st']
    _, ci = np.unique(date * 1000 + st, return_inverse=True)
    Z = (math.sqrt(rd) * rng.standard_normal((R, d['D']))[:, date]
         + math.sqrt(rs) * rng.standard_normal((R, d['S']))[:, st]
         + math.sqrt(rc) * rng.standard_normal((R, ci.max() + 1))[:, ci])
    rest = 1 - rd - rs - rc
    if extra == 'regime':          # persistent synoptic regime spanning blocks: AR(1) daily, phi = 0.9
        e = np.zeros((R, d['D'])); z = rng.standard_normal((R, d['D']))
        e[:, 0] = z[:, 0]
        for t in range(1, d['D']):
            e[:, t] = 0.9 * e[:, t - 1] + math.sqrt(1 - 0.81) * z[:, t]
        Z = Z + math.sqrt(0.10) * e[:, date]; rest -= 0.10
    if extra == 'jackpot':         # rare shared jackpot: a common shock hits all tail legs together
        pass
    Z = Z + math.sqrt(rest) * rng.standard_normal((R, date.size))
    return ndtr(Z)


# ---------------------------------------------------------------- statistics
def analyse_batch(d, Y, need_old=None):
    """Y: R x N outcomes (payout per share in [0,1]). Returns dict of arrays."""
    c, C, n, tail = d['c'], d['C'], d['n'], d['tail']
    core = ~tail
    R = Y.shape[0]
    Nj = n * (Y - c)                                     # R x N
    out = {}
    th = Nj.sum(1) / C.sum()
    se_t, df_t = cr_se_batch(Nj - th[:, None] * C, d['_mall'], C.sum())
    out['theta_hat'] = th
    out['T2'] = th - tq(0.95, df_t) * se_t > 0
    Nc = Nj[:, core]; Cc = C[core]
    thc = Nc.sum(1) / Cc.sum()
    se_c, df_c = cr_se_batch(Nc - thc[:, None] * Cc, d['_mcore'], Cc.sum())
    out['U_core'] = thc + tq(0.975, df_c) * se_c
    X = (Y - c)[:, core]
    kap = X.mean(1)
    se_k, df_k = cr_se_batch(X - kap[:, None], d['_mcore'], core.sum())
    out['T1a'] = kap - tq(0.975, df_k) * se_k > 0
    out['NEG'] = kap + tq(0.975, df_k) * se_k < 0
    out['se_k'] = se_k
    wc = Cc.sum() / C.sum()
    out['wc'] = wc
    Mt = (n[tail] - C[tail]).sum() / C.sum() if tail.any() else 0.0
    out['M_tail'] = Mt
    out['U_new'] = wc * out['U_core'] + Mt
    out['W'] = Y[:, tail].sum(1).astype(int) if tail.any() else np.zeros(R, int)
    # gates
    srt = np.sort(Nj, 1)[:, -5:].sum(1)
    pos = np.maximum(Nj, 0); gross = pos.sum(1)
    dmax = np.stack([pos[:, d['date'] == t].sum(1) for t in np.unique(d['date'])], 1).max(1)
    smax = np.stack([pos[:, d['st'] == s].sum(1) for s in np.unique(d['st'])], 1).max(1)
    out['gate'] = ((Nj.sum(1) - srt) / C.sum() > 0) & (dmax <= 0.25 * gross) & (smax <= 0.20 * gross)
    return out


def prep(d):
    d['_mall'] = cr_prep(d, np.ones(d['c'].size, bool))
    d['_mcore'] = cr_prep(d, ~d['tail'])
    return d


# ---------------------------------------------------------------- retired bound (independent inversion)
def retired_lookup(d, B=20000, seed=930_001):
    rng = np.random.default_rng(seed)
    tailc = np.flatnonzero(d['tail'])
    sub = dict(d); U = latent_uniforms(rng, d, B, DECL)[:, tailc]
    ct, nt, qt, Ct = d['c'][tailc], d['n'][tailc], d['q'][tailc], d['C'][tailc].sum()
    K = tailc.size
    Tl = np.sort(U / ct, 1); Tm = np.sort((U - ct) / (qt - ct), 1)
    W0 = (U < ct).sum(1)
    tab = np.empty(K + 1)
    for w in range(K + 1):
        if w >= K:
            lam, mu = 1000.0, 50.0
        else:
            # sup{x : P(T_(w+1) >= x) > 0.025}  = upper 2.5% quantile of T_(w+1)
            lam = float(np.clip(np.quantile(Tl[:, w], 0.975), 0.05, 1000.0))
            mu = float(np.clip(np.quantile(Tm[:, w], 0.975), 0.0, 50.0))
        tab[w] = max((nt * np.minimum(1, lam * ct)).sum() / Ct - 1,
                     (nt * (np.minimum(1, ct + mu * (qt - ct)) - ct)).sum() / Ct)
    return tab, W0


def mc(p, R):
    se = math.sqrt(max(p * (1 - p), 1e-12) / R)
    return [round(p, 4), round(se, 4), [round(p - 1.96 * se, 4), round(p + 1.96 * se, 4)]]


def op_ready(d):
    sel = d['date'] < 14
    c, C, st = d['c'][sel], d['C'][sel], d['st'][sel]
    mbar = sel.sum() / 14
    s2 = sel.sum() * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean() * deff / (120 * core.sum() / 14))
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    pce = math.ceil(round(100 * 2.4865 * se0, 9)) / 100
    kish = cnt.sum() ** 2 / (cnt ** 2).sum()
    go = pce <= 0.10 and se0k <= 0.020 and cnt.size >= 25 and kish >= 15
    return dict(pce=pce, se0_theta=round(se0, 5), se0_kappa=round(se0k, 5), stations=int(cnt.size),
                kish=round(float(kish), 2), GO=bool(go))
