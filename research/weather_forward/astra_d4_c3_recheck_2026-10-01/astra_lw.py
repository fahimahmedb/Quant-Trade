"""ASTRA D4-C3 recheck: L_W sampling coverage of theta_W and R3 labels under adversarial geometries. SYNTHETIC ONLY.
Independent of the Architect's run-F code. theta_W = sum n (p - c) / sum C over the realised window (exact, from p).
Counts P(reach AND L_W > theta_W), reach = GO (14 OP dates, spec 10.3) AND INFO_SUFFICIENT (IF2-IF5)."""
import math, json, sys
import numpy as np
from scipy import sparse, stats
from scipy.special import ndtr
ERT, CUT, Z80 = 0.02, 0.04, 2.4865
TQ = stats.t.ppf

def draw(rng, g):
    D = 14 + g['D']; S = g['S']
    act = rng.gamma(g.get('shape', 2.0), 1.0, S); act /= act.sum()
    if g.get('dom_st'):
        act = act * (1 - g['dom_st']) / (1 - act[0]); act[0] = g['dom_st']; act /= act.sum()
    cnt = np.minimum(2 * S, rng.poisson(g['m'], D))
    if g.get('dom_date'):                       # one window date carries a large share of trades (capped at 2S)
        cnt[14 + rng.integers(g['D'])] = 2 * S
    date = np.repeat(np.arange(D), cnt); N = date.size
    st = rng.choice(S, N, p=act)
    pr = g.get('prices', 'std')
    if pr == 'std': c = rng.uniform(0.35, 0.80, N)
    elif pr == 'wide': c = np.exp(rng.uniform(np.log(0.04), np.log(0.90), N))
    elif pr == 'boundary': c = np.where(rng.random(N) < 0.10, rng.uniform(0.04, 0.06, N), rng.uniform(0.35, 0.80, N))
    if g.get('cap') == 'thin': C = rng.uniform(5, 25, N)
    elif g.get('cap') == 'mixed': C = np.where(rng.random(N) < 0.5, 50.0, rng.uniform(1, 10, N))
    else: C = np.full(N, 50.0)
    th = g['th0']
    if g.get('het'):                             # heterogeneous expected returns by station, mean th
        th = th + rng.normal(0, g['het'], S)[st]
    p = np.clip(c * (1 + th), 0, 1)
    d = dict(date=date, st=st, c=c, p=p, C=C, n=C / c)
    op = {k: v[date < 14] for k, v in d.items()}
    w = {k: v[date >= 14] for k, v in d.items()}; w['date'] = w['date'] - 14
    return w, op

def _ind(gr):
    _, gi = np.unique(gr, return_inverse=True); G = gi.max() + 1
    return sparse.csr_matrix((np.ones(gi.size), (np.arange(gi.size), gi)), shape=(gi.size, G)), G

def cr(e, blk, st, Q):
    V, G = [], []
    for gr in (blk, st, blk * 1000 + st):
        M, n = _ind(gr); s = M.T @ e
        V.append(n / (n - 1) * (s ** 2).sum() / Q ** 2); G.append(n)
    return math.sqrt(max(V[0], V[1], V[0] + V[1] - V[2])), min(G[0], G[1]) - 1

def ready(op):
    c, C, st = op['c'], op['C'], op['st']
    mbar = c.size / 14
    s2 = c.size * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1)); se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean() * deff / (120 * core.sum() / 14))
    k = np.bincount(st); k = k[k > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    return bool(pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and k.sum() ** 2 / (k ** 2).sum() >= 15)

def outcomes(rng, w, g):
    rho = g.get('rho', (0.05, 0.05, 0.10)); D = g['D']; S = g['S']
    _, ci = np.unique(w['date'] * 1000 + w['st'], return_inverse=True)
    z = (math.sqrt(rho[0]) * rng.standard_normal(D)[w['date']] + math.sqrt(rho[1]) * rng.standard_normal(S)[w['st']]
         + math.sqrt(rho[2]) * rng.standard_normal(ci.max() + 1)[ci])
    rest = 1 - sum(rho)
    if g.get('regime'):                          # AR(1) daily regime spanning blocks (default phi=0.9, latent var 0.10)
        phi = g.get('phi', 0.9); rv = g.get('regime_var', 0.10)
        e = np.zeros(D); zz = rng.standard_normal(D); e[0] = zz[0]
        for t in range(1, D): e[t] = phi * e[t - 1] + math.sqrt(1 - phi ** 2) * zz[t]
        z = z + math.sqrt(rv) * e[w['date']]; rest -= rv
    z = z + math.sqrt(rest) * rng.standard_normal(w['c'].size)
    return (ndtr(z) < w['p']).astype(float)

def one(rng, g):
    w, op = draw(rng, g); go = ready(op)
    y = outcomes(rng, w, g)
    c, C, n, date, st = w['c'], w['C'], w['n'], w['date'], w['st']
    blk = date // 5; core = c >= CUT
    N = n * (y - c); th = N.sum() / C.sum()
    se, df = cr(N - th * C, blk, st, C.sum()); L_W = th - TQ(0.95, df) * se
    x = (y - c)[core]; k = x.mean(); sek, _ = cr(x - k, blk[core], st[core], core.sum())
    viid = core.sum() / (core.sum() - 1) * ((x - k) ** 2).sum() / core.sum() ** 2
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    info = bool(np.unique(blk).size >= 12 and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
                and sek <= 0.025 and sek ** 2 / viid <= 6)
    thW = float((n * (w['p'] - c)).sum() / C.sum())
    return go and info, L_W, thW, th

def mc(k, n):
    p = k / n; se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return dict(p=round(p, 4), se=round(se, 4), ci=[round(max(0, p - 1.96 * se), 4), round(p + 1.96 * se, 4)], n=n)

def run(g, reps, seed):
    rng = np.random.default_rng(seed)
    miss = reach = miss_any = pos = pos_false = 0
    for _ in range(reps):
        r, L, tW, th = one(rng, g)
        reach += r; miss += r and L > tW; miss_any += L > tW
        p_ = r and L > 0 and th >= 0.02            # REALIZED_WINDOW_VALUE_SUPPORTED or NOT_ROBUST (gates not applied)
        pos += p_; pos_false += p_ and tW <= 0
    return dict(g=g, seed=seed, reach=mc(reach, reps), miss_joint=mc(miss, reps), miss_unconditional_on_reach=mc(miss_any, reps),
                miss_given_reach=mc(miss, max(reach, 1)), positive_window_claim=mc(pos, reps), false_positive_window_claim=mc(pos_false, reps))
