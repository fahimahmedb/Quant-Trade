"""Weather Forward V2 — synthetic Monte Carlo of the inference procedure (2026-09-29).

SYNTHETIC ONLY. No market, forecast, order-book, settlement, resolution, wallet or P&L data is read or used.
Every input below is a declared scenario (prices, capital, dependence, true win probabilities).

Purpose: independent check by the V2 Architect of engine size/power, PINM vs two-way cluster-robust (CR)
inference, date-only vs two-way dependence, the cost of a Fable-style gate, tail detection, structured
upper-bound coverage and terminal-state distributions. Results are tabulated in
WEATHER_FORWARD_V2_POWER_TABLE_2026-09-29.md section 4.

Modes (RNG consumption is identical across modes, so seeds reproduce the tabulated numbers):
  python3 WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py fable 200   # run A: Fable-style (engine conjunction + gate)
  python3 WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py v2 200      # run B: V2 engines, product partition
  python3 WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py size 400 SEED   # run C: CR-only null size (seeds 1-4, 11-14)
Run B in the power table used NEG at one-sided 0.05 (NEG_ALPHA = 0.05); the frozen V2 rule is 0.025,
checked by run C with NEG_ALPHA = 0.025 (seeds 11-14) and NEG_ALPHA = 0.05 (seeds 1-4).
Requires numpy and scipy.
"""
import json
import math
import sys

import numpy as np
from scipy import stats
from scipy.special import ndtr

TAIL_CUT = 0.04                 # frozen stratum boundary (spec 5.2)
ERT = 0.02                      # theta_ERT
DECL = (0.10, 0.10, 0.10)       # declared PINM latent correlations (date, station, cell) (spec 8.2)
MODE = 'v2'
NEG_ALPHA = 0.05                # value used in run B; frozen V2 rule is 0.025


def make_design(rng, D=120, S=48, m=35, tail_share=0.16, mid_share=0.0):
    """Synthetic trade set: D dates, S stations (gamma activity), Poisson(m) trades per date."""
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    n = rng.poisson(m, D)
    date = np.repeat(np.arange(D), n)
    N = date.size
    st = rng.choice(S, N, p=act)
    u = rng.random(N)
    c = np.empty(N)
    tail = u < tail_share
    mid = (u >= tail_share) & (u < tail_share + mid_share)
    core = ~(tail | mid)
    c[tail] = np.exp(rng.uniform(np.log(0.002), np.log(0.04), tail.sum()))
    c[mid] = rng.uniform(0.04, 0.35, mid.sum())
    c[core] = rng.uniform(0.35, 0.80, core.sum())
    C = np.where(rng.random(N) < 0.68, 50.0, rng.uniform(10, 50, N))
    q = np.minimum(0.999, c + 0.10 + rng.uniform(0, 0.15, N))
    return dict(date=date, st=st, c=c, C=C, n=C / c, q=q, tail=c < TAIL_CUT, S=S, D=D)


def latent_u(rng, d, B, rho):
    """Latent Gaussian copula with date, station and (date, station) cell effects -> uniforms."""
    rd, rs, rc = rho
    date, st = d['date'], d['st']
    cell = date * 1000 + st
    _, cell_idx = np.unique(cell, return_inverse=True)
    nc = cell_idx.max() + 1
    N = date.size
    Ud = rng.standard_normal((B, d['D']))
    Us = rng.standard_normal((B, d['S']))
    Uc = rng.standard_normal((B, nc))
    E = rng.standard_normal((B, N))
    Z = (math.sqrt(rd) * Ud[:, date] + math.sqrt(rs) * Us[:, st] + math.sqrt(rc) * Uc[:, cell_idx]
         + math.sqrt(1 - rd - rs - rc) * E)
    return ndtr(Z)


def cr_se(e, groups_list, denom):
    """Spec 8.1: max-of-(block, station, two-way) CR1 standard error; df = min(G_B, G_S) - 1."""
    vs, Gs = [], []
    for g in groups_list:
        _, gi = np.unique(g, return_inverse=True)
        G = gi.max() + 1
        s = np.bincount(gi, weights=e, minlength=G)
        vs.append((s ** 2).sum() * G / (G - 1) / denom ** 2)
        Gs.append(G)
    vb, vst, vcell = vs
    v2 = vb + vst - vcell
    return math.sqrt(max(vb, vst, v2)), min(Gs[0], Gs[1]) - 1, math.sqrt(max(vb, 1e-300))


def poibin_sf(probs, k):
    """P(X >= k) for a Poisson-binomial variable."""
    pmf = np.zeros(len(probs) + 1); pmf[0] = 1
    for p in probs:
        pmf[1:] = pmf[1:] * (1 - p) + pmf[:-1] * p
        pmf[0] *= (1 - p)
    return pmf[k:].sum()


def analyse(d, y, rng, B=1000):
    c, C, n, tail, q = d['c'], d['C'], d['n'], d['tail'], d['q']
    blk = d['date'] // 5
    st = d['st']
    cellg = blk * 1000 + st
    core = ~tail
    N = n * (y - c)
    th = N.sum() / C.sum()
    tq = stats.t.ppf
    x = (y - c)[core]
    kap = x.mean()
    se_k, df_k, se_k_date = cr_se(x - kap, [blk[core], st[core], cellg[core]], core.sum())
    se_t, df_t, _ = cr_se(N - th * C, [blk, st, cellg], C.sum())
    thc = N[core].sum() / C[core].sum()
    se_tc, df_tc, _ = cr_se(N[core] - thc * C[core], [blk[core], st[core], cellg[core]], C[core].sum())
    # PINM under the sharp null p = c with the declared copula
    U = latent_u(rng, d, B, DECL)
    ys = (U < c).astype(float)
    th_s = (ys * n - n * c).sum(1) / C.sum()
    k_s = (ys[:, core] - c[core]).mean(1)
    W = y[tail].sum(); Wn = ys[:, tail].sum(1)
    Lam = c[tail].sum()
    p_T2 = (1 + (th_s >= th).sum()) / (B + 1)
    p_k_hi = (1 + (k_s >= kap).sum()) / (B + 1)
    p_k_lo = (1 + (k_s <= kap).sum()) / (B + 1)
    p_W = (1 + (Wn >= W).sum()) / (B + 1)
    if tail.sum() > 0:  # block-collapsed tail count (reported only in V2)
        tb = blk[tail]
        ub = np.unique(tb)
        pb = np.array([1 - np.prod(1 - c[tail][tb == b]) for b in ub])
        hits = np.array([y[tail][tb == b].max() for b in ub])
        p_blk = poibin_sf(pb, int(hits.sum()))
    else:
        p_blk = 1.0
    T1a_cr = kap - tq(0.975, df_k) * se_k > 0
    T1a_p = p_k_hi <= 0.025
    T1b_p = (tail.sum() > 0) and (p_W <= 0.025)
    T1b_blk = (tail.sum() > 0) and (p_blk <= 0.025)
    T2cr = th - tq(0.95, df_t) * se_t > 0
    T2p = p_T2 <= 0.05
    NEG_cr = kap + tq(1 - NEG_ALPHA, df_k) * se_k < 0
    if MODE == 'v2':
        T1a, T1b, T2, NEG = T1a_cr, T1b_p, T2cr, NEG_cr
    else:  # 'fable': reject only if both engines reject
        T1a, T1b, T2 = T1a_cr and T1a_p, T1b_p and T1b_blk, T2cr and T2p
        NEG = NEG_cr and (p_k_lo <= 0.05)
    T1 = T1a or T1b
    # structured upper bound (spec 8.5)
    wc = C[core].sum() / C.sum(); wt = 1 - wc
    Uc = thc + tq(0.975, df_tc) * se_tc
    Ut = 0.0
    if tail.sum() > 0:
        Ut_ = U[:, tail]
        ct, nt, qt, Ct = c[tail], n[tail], q[tail], C[tail].sum()

        def ok_l(lam):
            return ((Ut_ < np.minimum(1, lam * ct)).sum(1) <= W).mean() > 0.025
        lo, hi = 0.05, 200.0
        if not ok_l(lo):
            lamU = lo
        else:
            for _ in range(30):
                mid = math.sqrt(lo * hi)
                if ok_l(mid): lo = mid
                else: hi = mid
            lamU = lo
        th_tpm = (nt * np.minimum(1, lamU * ct)).sum() / Ct - 1

        def ok_m(mu):
            return ((Ut_ < np.minimum(1, ct + mu * (qt - ct))).sum(1) <= W).mean() > 0.025
        lo, hi = 0.0, 20.0
        if not ok_m(lo):
            muU = 0.0
        else:
            for _ in range(30):
                mid = (lo + hi) / 2
                if ok_m(mid): lo = mid
                else: hi = mid
            muU = lo
        th_shr = (nt * (np.minimum(1, ct + muU * (qt - ct)) - ct)).sum() / Ct
        Ut = max(th_tpm, th_shr)
    Ubound = wc * Uc + wt * Ut
    Unaive = th + tq(0.95, df_t) * se_t
    top5 = np.sort(N)[-5:].sum()
    gross = N[N > 0].sum()
    dshare = np.bincount(d['date'], weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    sshare = np.bincount(st, weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    gate = ((N.sum() - top5) / C.sum() > 0) and dshare <= 0.25 and sshare <= 0.20
    T1a_dateonly = kap - tq(0.975, df_k) * se_k_date > 0
    return dict(theta=th, kap=kap, se_k=se_k, se_t=se_t, T1a_cr=T1a_cr, T1a_p=T1a_p, T1b_p=T1b_p, T1b_blk=T1b_blk,
                NEG_cr=NEG_cr, T1a=T1a, T1b=T1b, T1=T1, T2cr=T2cr, T2p=T2p, T2=T2, NEG=NEG, U=Ubound,
                Unaive=Unaive, gate=gate, T1a_dateonly=T1a_dateonly, W=W, Lam=Lam, wt=wt)


def state(o, theta_hat):
    if MODE == 'v2':  # V2 product partition, no gate on theta (spec 17.2)
        info = 'DET' if o['T1'] else ('ADV' if o['NEG'] else 'ND')
        if o['U'] < ERT: eco = 'EXCL'
        elif o['T2'] and theta_hat >= ERT and o['gate']: eco = 'CONF'
        elif o['T2'] and theta_hat >= ERT: eco = 'NROB'
        else: eco = 'IND'
        return info + '|' + eco
    # Fable-style gated partition (Fable 8.2)
    if not o['T1']:
        return 'S1_NEG' if o['NEG'] else 'S2_NOINFO'
    if o['U'] < ERT: return 'S5_EXCL'
    if o['T2'] and theta_hat >= ERT and o['gate']: return 'S3_CONF'
    if o['T2'] and theta_hat >= ERT: return 'S4_NOTROB'
    return 'S6_INDET'


def pce_from_prices(d, dates=14):
    """Spec 10.2 on the first 14 synthetic dates (prices only)."""
    sel = d['date'] < dates
    c, C = d['c'][sel], d['C'][sel]
    mbar = sel.sum() / dates
    s2 = sel.sum() * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se = math.sqrt(s2) * math.sqrt(deff / (mbar * 120))
    ck = c[c >= TAIL_CUT]
    se_k = math.sqrt((ck * (1 - ck)).mean()) * math.sqrt(deff / (ck.size / dates * 120))
    return math.ceil(2.486 * se * 100) / 100, se_k, math.sqrt(s2)


def truth(d, scen):
    c = d['c']; tail = d['tail']; q = d['q']
    kind, par = scen
    p = c.copy()
    if kind == 'uniform':               # every dollar earns par in expectation
        p = c * (1 + par)
    elif kind == 'tail_mult':           # core fair, tail legs win par x their price
        p = np.where(tail, np.minimum(1, par * c), c)
    elif kind == 'core_plus_tail_over':  # core underpriced, tail overpriced (lottery bias)
        p = np.where(tail, c * 0.5, c * (1 + par))
    elif kind == 'hidden_lottery':      # only legs below 0.005 mispriced (par x)
        p = np.where(c < 0.005, np.minimum(1, par * c), c)
    elif kind == 'shrink':              # truth moves toward the forecast by par
        p = c + par * (q - c)
    p = np.clip(p, 0, 1)
    theta_true = (d['n'] * (p - c)).sum() / d['C'].sum()
    kap_true = (p - c)[~tail].mean()
    return p, theta_true, kap_true


def run(scen, mix, true_rho, reps, seed, m=35):
    rng = np.random.default_rng(seed)
    res = []
    for _ in range(reps):
        d = make_design(rng, m=m, tail_share=mix[0], mid_share=mix[1])
        p, tt, kt = truth(d, scen)
        y = (latent_u(rng, d, 1, true_rho)[0] < p).astype(float)
        o = analyse(d, y, rng)
        pce, sek, sig = pce_from_prices(d)
        o.update(state=state(o, o['theta']), pce=pce, sek_plan=sek, sig0=sig, theta_true=tt, kap_true=kt,
                 cover=tt <= o['U'], cover_naive=tt <= o['Unaive'], exclPCE=o['U'] < pce)
        res.append(o)
    mean = lambda f: round(float(np.mean([f(o) for o in res])), 3)
    agg = {k: mean(lambda o, k=k: o[k]) for k in
           ['T1a_cr', 'T1a_p', 'T1b_p', 'T1b_blk', 'NEG_cr', 'T1a', 'T1b', 'T1', 'T2', 'T2cr', 'T2p', 'NEG',
            'cover', 'cover_naive', 'exclPCE', 'T1a_dateonly']}
    agg['T2_given_gate'] = mean(lambda o: o['T1'] and o['T2'])
    agg['exclPCE_false'] = mean(lambda o: (o['U'] < o['pce']) and (o['theta_true'] >= o['pce']))
    agg['exclERT_false'] = mean(lambda o: (o['U'] < ERT) and (o['theta_true'] >= ERT))
    agg['conf_false'] = mean(lambda o: o['state'].endswith('CONF') and o['theta_true'] <= 0)
    agg['U_lt_ERT'] = mean(lambda o: o['U'] < ERT)
    agg['Unaive_lt_ERT'] = mean(lambda o: o['Unaive'] < ERT)
    agg['theta_true'] = round(float(np.mean([o['theta_true'] for o in res])), 4)
    agg['kap_true'] = round(float(np.mean([o['kap_true'] for o in res])), 4)
    agg['pce_med'] = float(np.median([o['pce'] for o in res]))
    for k, nm in [('sek_plan', 'sek_plan_med'), ('se_k', 'se_k_med'), ('se_t', 'se_t_med')]:
        agg[nm] = round(float(np.median([o[k] for o in res])), 4)
    agg['sig0_med'] = round(float(np.median([o['sig0'] for o in res])), 2)
    agg['Lam_med'] = round(float(np.median([o['Lam'] for o in res])), 1)
    agg['wt_med'] = round(float(np.median([o['wt'] for o in res])), 3)
    counts = {}
    for o in res: counts[o['state']] = counts.get(o['state'], 0) + 1
    agg['states'] = {k: round(v / reps, 3) for k, v in sorted(counts.items())}
    return agg


def size_only(seed, reps):
    """Run C: CR engine null size, core-only mix (5% mid legs), three dependence settings."""
    rng = np.random.default_rng(seed)
    tq = stats.t.ppf
    out = {}
    for name, rho in [('TRUE', (0.05, 0.05, 0.10)), ('SST', (0.02, 0.15, 0.10)), ('LOW', (0.0, 0.0, 0.0))]:
        r = []
        for _ in range(reps):
            d = make_design(rng, tail_share=0.0, mid_share=0.05)
            c = d['c']; y = (latent_u(rng, d, 1, rho)[0] < c).astype(float)
            blk = d['date'] // 5; st = d['st']; cell = blk * 1000 + st; core = ~d['tail']
            x = (y - c)[core]; k = x.mean()
            se_k, df_k, _ = cr_se(x - k, [blk[core], st[core], cell[core]], core.sum())
            N = d['n'] * (y - c); C = d['C']; th = N.sum() / C.sum()
            se_t, df_t, _ = cr_se(N - th * C, [blk, st, cell], C.sum())
            r.append((k - tq(0.975, df_k) * se_k > 0, k + tq(1 - NEG_ALPHA, df_k) * se_k < 0,
                      th - tq(0.95, df_t) * se_t > 0))
        a = np.array(r, float).mean(0)
        out[name] = dict(T1a_025=round(a[0], 4), NEG=round(a[1], 4), NEG_ALPHA=NEG_ALPHA, T2_05=round(a[2], 4), n=reps)
    return out


TRUE = (0.05, 0.05, 0.10)
STRESS = (0.15, 0.15, 0.10)
SST = (0.02, 0.15, 0.10)
MIXES = {'M16': (0.16, 0.0), 'M05': (0.05, 0.05), 'M00': (0.0, 0.05)}
PLAN_A = [  # run A (MODE = 'fable')
    ('uniform', 0.0, 'M00', TRUE), ('uniform', 0.02, 'M00', TRUE), ('uniform', 0.05, 'M00', TRUE),
    ('uniform', 0.10, 'M00', TRUE), ('uniform', 0.0, 'M05', TRUE), ('uniform', 0.05, 'M05', TRUE),
    ('uniform', 0.10, 'M05', TRUE), ('uniform', 0.0, 'M16', TRUE), ('uniform', 0.05, 'M16', TRUE),
    ('uniform', 0.10, 'M16', TRUE), ('tail_mult', 3.0, 'M16', TRUE), ('tail_mult', 1.0, 'M16', STRESS),
    ('core_plus_tail_over', 0.05, 'M16', TRUE), ('hidden_lottery', 10.0, 'M16', TRUE),
    ('uniform', -0.10, 'M16', TRUE), ('uniform', 0.0, 'M05', STRESS), ('shrink', 0.3, 'M16', TRUE),
]
PLAN_B = [  # run B (MODE = 'v2')
    ('uniform', 0.0, 'M00', TRUE), ('uniform', 0.0, 'M00', STRESS), ('uniform', 0.0, 'M00', SST),
    ('uniform', 0.05, 'M00', TRUE), ('uniform', 0.10, 'M00', TRUE),
    ('uniform', 0.0, 'M05', TRUE), ('uniform', 0.05, 'M05', TRUE), ('uniform', 0.10, 'M05', TRUE),
    ('uniform', 0.0, 'M16', TRUE), ('uniform', 0.10, 'M16', TRUE),
    ('tail_mult', 3.0, 'M16', TRUE), ('tail_mult', 2.0, 'M16', TRUE), ('tail_mult', 1.0, 'M16', STRESS),
    ('core_plus_tail_over', 0.05, 'M16', TRUE), ('hidden_lottery', 10.0, 'M16', TRUE),
    ('uniform', -0.10, 'M16', TRUE), ('uniform', -0.05, 'M00', TRUE), ('shrink', 0.1, 'M16', TRUE),
]


def _job(i):
    plan = PLAN_B if MODE == 'v2' else PLAN_A
    k, p, mx, rho = plan[i]
    a = run((k, p), MIXES[mx], rho, REPS, 1000 + i)
    a.update(scen=f'{k}({p})', mix=mx, true_rho=rho, mode=MODE)
    return json.dumps(a)


if __name__ == '__main__':
    MODE = sys.argv[1] if len(sys.argv) > 1 else 'v2'
    REPS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    if MODE == 'size':
        if len(sys.argv) > 4: NEG_ALPHA = float(sys.argv[4])
        print(json.dumps(size_only(int(sys.argv[3]), REPS)))
    else:
        from multiprocessing import Pool
        plan = PLAN_B if MODE == 'v2' else PLAN_A
        with Pool(min(len(plan), 8)) as pool:
            for line in pool.imap(_job, range(len(plan))):
                print(line, flush=True)
