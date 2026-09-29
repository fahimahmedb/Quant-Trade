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
  python3 WEATHER_FORWARD_V2_SYNTHETIC_SIM_2026-09-29.py d4           # run D: D4 repair R1 validation (power table 4.5)
Run B in the power table used NEG at one-sided 0.05 (NEG_ALPHA = 0.05); the frozen V2 rule is 0.025,
checked by run C with NEG_ALPHA = 0.025 (seeds 11-14) and NEG_ALPHA = 0.05 (seeds 1-4).

D4 repair R1 (after Astra V2 re-audit @7d95c00): `U` is now the repaired exclusion bound
w_core * U_core + M_tail (tail_worst_case); `U_retired` is the V2@94b5934 TPM v SHR bound, now computed with the
exact frozen numerical contract (LAMBDA_RANGE, MU_RANGE, BISECTION_ITERS; Astra MP1). Runs A/B in the power table
were produced by the 94b5934 version of this script (bisection 200 / 20 / 30); re-running them here reproduces every
non-bound column bit-for-bit (bisection consumes no randomness), while bound-driven states use the repaired U.
Run D uses the exact frozen PINM draw contract (B = 20,000, SeedSequence([20260929, 1]), per-draw order).
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


LAMBDA_RANGE = (0.05, 1000.0)   # frozen V2@94b5934 numerical contract of the RETIRED tail models
MU_RANGE = (0.0, 50.0)
BISECTION_ITERS = 40


def retired_sup(ok, lo, hi, log):
    """Exact frozen contract of the retired TPM/SHR bound: sup{x in [lo, hi] : ok(x)} by 40-step bisection
    (log-scale for lambda); a sup at an interval end is reported as that end."""
    if ok(hi):
        return hi
    if not ok(lo):
        return lo
    for _ in range(BISECTION_ITERS):
        mid = math.sqrt(lo * hi) if log else (lo + hi) / 2
        if ok(mid): lo = mid
        else: hi = mid
    return lo


def tail_worst_case(n, C, tail):
    """REPAIRED tail term (D4 repair R1): contribution of the TAIL stratum to theta if every TAIL leg wins,
    M_tail = sum_TAIL (n_j - C_j) / sum_all C_j. Valid for every p in [0,1]^TAIL and every dependence."""
    return float((n[tail] - C[tail]).sum() / C.sum()) if tail.any() else 0.0


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
    # upper bounds for exclusion claims
    wc = C[core].sum() / C.sum(); wt = 1 - wc
    Uc = thc + tq(0.975, df_tc) * se_tc
    Ut = 0.0   # RETIRED V2@94b5934 model-conditional tail term (TPM v SHR), exact frozen numerical contract
    if tail.sum() > 0:
        Ut_ = U[:, tail]
        ct, nt, qt, Ct = c[tail], n[tail], q[tail], C[tail].sum()
        lamU = retired_sup(lambda lam: ((Ut_ < np.minimum(1, lam * ct)).sum(1) <= W).mean() > 0.025, *LAMBDA_RANGE, log=True)
        th_tpm = (nt * np.minimum(1, lamU * ct)).sum() / Ct - 1
        muU = retired_sup(lambda mu: ((Ut_ < np.minimum(1, ct + mu * (qt - ct))).sum(1) <= W).mean() > 0.025, *MU_RANGE, log=False)
        th_shr = (nt * (np.minimum(1, ct + muU * (qt - ct)) - ct)).sum() / Ct
        Ut = max(th_tpm, th_shr)
    U_retired = wc * Uc + wt * Ut
    Ubound = wc * Uc + tail_worst_case(n, C, tail)   # REPAIRED bound (spec 8.5, D4 repair R1)
    Unaive = th + tq(0.95, df_t) * se_t
    top5 = np.sort(N)[-5:].sum()
    gross = N[N > 0].sum()
    dshare = np.bincount(d['date'], weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    sshare = np.bincount(st, weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    gate = ((N.sum() - top5) / C.sum() > 0) and dshare <= 0.25 and sshare <= 0.20
    T1a_dateonly = kap - tq(0.975, df_k) * se_k_date > 0
    return dict(theta=th, kap=kap, se_k=se_k, se_t=se_t, T1a_cr=T1a_cr, T1a_p=T1a_p, T1b_p=T1b_p, T1b_blk=T1b_blk,
                NEG_cr=NEG_cr, T1a=T1a, T1b=T1b, T1=T1, T2cr=T2cr, T2p=T2p, T2=T2, NEG=NEG, U=Ubound, U_retired=U_retired,
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


# ------------------------------------------------------------------------------------------------------------------
# Run D — D4 repair validation (Astra V2 re-audit @7d95c00, finding C1 and MP1). Synthetic only.
# ------------------------------------------------------------------------------------------------------------------
Z80 = 2.4865


def op_readiness(d, op_dates=14):
    """Spec 10.2 / 10.3 on the first 14 dates of a fixed design (prices, capital and stations only)."""
    sel = d['date'] < op_dates
    c, C, st = d['c'][sel], d['C'][sel], d['st'][sel]
    mbar = sel.sum() / op_dates
    s2 = sel.sum() * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1))
    se0 = math.sqrt(s2) * math.sqrt(deff / (120 * mbar))
    core = c >= TAIL_CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean()) * math.sqrt(deff / (120 * core.sum() / op_dates))
    cnt = np.bincount(st)
    cnt = cnt[cnt > 0]
    return dict(pce=math.ceil(100 * Z80 * se0) / 100, se0_theta=round(se0, 5), se0_kappa=round(se0k, 5),
                sigma0_sq=round(s2, 5), stations=int(cnt.size), kish=round(float(cnt.sum() ** 2 / (cnt ** 2).sum()), 2))


def astra_design(seed, D=120, m=35, S=48, n_tail_op=9, n_tail_rest=75, n_cheap=2, c_tail=0.039, c_cheap=0.001,
                 op_dates=14):
    """Astra C1 geometry: 35 trades/date, 48 gamma-activity stations, C = 50, 84 tail legs at 0.039 (9 inside the
    14 PRE_T0 dates) and 2 legs at 0.001 after the OP; core c ~ U(0.35, 0.80); q = min(0.999, c + 0.12)."""
    rng = np.random.default_rng(seed)
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), m)
    N = date.size
    st = rng.choice(S, N, p=act)
    c = rng.uniform(0.35, 0.80, N)
    op = np.flatnonzero(date < op_dates); rest = np.flatnonzero(date >= op_dates)
    t_op = rng.choice(op, n_tail_op, replace=False)
    pick = rng.choice(rest, n_tail_rest + n_cheap, replace=False)
    c[t_op] = c_tail; c[pick[:n_tail_rest]] = c_tail; c[pick[n_tail_rest:]] = c_cheap
    C = np.full(N, 50.0)
    cheap = np.zeros(N, bool); cheap[pick[n_tail_rest:]] = True
    return dict(date=date, st=st, c=c, C=C, n=C / c, q=np.minimum(0.999, c + 0.12), tail=c < TAIL_CUT,
                cheap=cheap, S=S, D=D)


def frozen_pinm_uniforms(d, cols, B=20000, chunk=1000):
    """Spec 8.2 exactly: Generator(PCG64(SeedSequence([20260929, 1]))), B = 20,000 in 20 chunks of 1,000; per draw the
    standard normals are laid out dates (asc), stations (asc), cells (asc date, ICAO), trades (canonical order = design
    order here); returns the copula uniforms of the requested trade columns."""
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([20260929, 1])))
    ud, di = np.unique(d['date'], return_inverse=True)
    us, si = np.unique(d['st'], return_inverse=True)
    uc, ci = np.unique(d['date'] * 1000 + d['st'], return_inverse=True)
    nD, nS, nC, N = len(ud), len(us), len(uc), d['date'].size
    rd, rs, rc = DECL
    out = []
    for _ in range(B // chunk):
        Z = rng.standard_normal((chunk, nD + nS + nC + N))
        lat = (math.sqrt(rd) * Z[:, di[cols]] + math.sqrt(rs) * Z[:, nD + si[cols]] + math.sqrt(rc) * Z[:, nD + nS + ci[cols]]
               + math.sqrt(1 - rd - rs - rc) * Z[:, nD + nS + nC + cols])
        out.append(ndtr(lat))
    return np.vstack(out)


def retired_tail_lookup(d, Ut):
    """RETIRED V2@94b5934 tail term U_tail(W) for W = 0..K under the exact frozen contract (lambda in [0.05, 1000]
    log-bisection, mu in [0, 50], 40 iterations, P* from 20,000 frozen PINM draws). ok(x) is evaluated through the
    per-draw order statistic of the trade thresholds, which is identical to counting W*(x) <= W."""
    tail = d['tail']
    ct, nt, qt, Ct = d['c'][tail], d['n'][tail], d['q'][tail], d['C'][tail].sum()
    T_l = np.sort(Ut / ct, axis=1)                      # y*_j(lambda) = 1{U < lambda c}
    T_m = np.sort((Ut - ct) / (qt - ct), axis=1)        # y*_j(mu) = 1{U < c + mu (q - c)}
    K = ct.size
    table = np.empty(K + 1)
    for w in range(K + 1):
        ok_l = (lambda x: True) if w >= K else (lambda x, col=T_l[:, w]: (col >= x).mean() > 0.025)
        ok_m = (lambda x: True) if w >= K else (lambda x, col=T_m[:, w]: (col >= x).mean() > 0.025)
        lamU = retired_sup(ok_l, *LAMBDA_RANGE, log=True)
        muU = retired_sup(ok_m, *MU_RANGE, log=False)
        table[w] = max((nt * np.minimum(1, lamU * ct)).sum() / Ct - 1,
                       (nt * (np.minimum(1, ct + muU * (qt - ct)) - ct)).sum() / Ct)
    return table


def attack_truth(d, name):
    c = d['c']; p = c.copy()
    if name == 'A1_positive_tail_negative_core':
        p[~d['tail']] = 0.95 * c[~d['tail']]; p[d['cheap']] = 0.170
    elif name == 'A2_pure_hidden_lottery':
        p[d['cheap']] = 0.18
    elif name == 'P3_negative_core_fair_tail':
        p[~d['tail']] = 0.90 * c[~d['tail']]
    return p


def core_stats(d, y, tq=stats.t.ppf):
    c, C, n, tail = d['c'], d['C'], d['n'], d['tail']
    blk = d['date'] // 5; st = d['st']; cell = blk * 1000 + st; core = ~tail
    N = n * (y - c)
    x = (y - c)[core]; kap = x.mean()
    se_k, df_k, _ = cr_se(x - kap, [blk[core], st[core], cell[core]], core.sum())
    thc = N[core].sum() / C[core].sum()
    se_tc, df_tc, _ = cr_se(N[core] - thc * C[core], [blk[core], st[core], cell[core]], C[core].sum())
    th = N.sum() / C.sum()
    se_t, df_t, _ = cr_se(N - th * C, [blk, st, cell], C.sum())
    wc = C[core].sum() / C.sum()
    top5 = np.sort(N)[-5:].sum(); gross = N[N > 0].sum()
    dsh = np.bincount(d['date'], weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    ssh = np.bincount(st, weights=np.maximum(N, 0)).max() / gross if gross > 0 else 1
    return dict(theta=th, T1a=kap - tq(0.975, df_k) * se_k > 0, NEG=kap + tq(0.975, df_k) * se_k < 0,
                T2=th - tq(0.95, df_t) * se_t > 0, core_part=wc * (thc + tq(0.975, df_tc) * se_tc),
                gate=((N.sum() - top5) / C.sum() > 0) and dsh <= 0.25 and ssh <= 0.20, W=int(y[tail].sum()))


def econ_result(U, T2, theta_hat, gate):
    if U < ERT: return 'EXCL'
    if T2 and theta_hat >= ERT: return 'CONF' if gate else 'NROB'
    return 'IND'


def run_attack(name, reps, seed, design_seed=424242):
    d = astra_design(design_seed)
    ready = op_readiness(d)
    tailcols = np.flatnonzero(d['tail'])
    Ut = frozen_pinm_uniforms(d, tailcols)
    lookup = retired_tail_lookup(d, Ut)
    W0 = (Ut < d['c'][tailcols]).sum(1)                 # sharp-null tail counts for T1b
    M_tail = tail_worst_case(d['n'], d['C'], d['tail'])
    p = attack_truth(d, name)
    th_true = float((d['n'] * (p - d['c'])).sum() / d['C'].sum())
    pce = ready['pce']
    rng = np.random.default_rng(seed)
    acc = {k: 0 for k in ['cov_old', 'cov_new', 'exERT_old', 'exERT_new', 'exPCE_old', 'exPCE_new',
                          'rej_old', 'rej_new', 'T2', 'NEG', 'T1']}
    for _ in range(reps):
        y = (latent_u(rng, d, 1, TRUE)[0] < p).astype(float)
        s = core_stats(d, y)
        T1 = s['T1a'] or ((1 + (W0 >= s['W']).sum()) / (W0.size + 1) <= 0.025)
        U_old = s['core_part'] + (1 - d['C'][~d['tail']].sum() / d['C'].sum()) * lookup[s['W']]
        U_new = s['core_part'] + M_tail
        e_old = econ_result(U_old, s['T2'], s['theta'], s['gate'])
        e_new = econ_result(U_new, s['T2'], s['theta'], s['gate'])
        info_neg = (not T1) and s['NEG']
        acc['cov_old'] += th_true <= U_old; acc['cov_new'] += th_true <= U_new
        acc['exERT_old'] += U_old < ERT; acc['exERT_new'] += U_new < ERT
        acc['exPCE_old'] += U_old < max(pce, ERT); acc['exPCE_new'] += U_new < max(pce, ERT)
        acc['rej_old'] += (e_old == 'EXCL') or (info_neg and e_old != 'CONF')   # V2@94b5934 rule 17.6
        acc['rej_new'] += e_new == 'EXCL'                                         # repaired rule 17.6
        acc['T2'] += s['T2']; acc['NEG'] += s['NEG']; acc['T1'] += T1
    out = {k: round(v / reps, 4) for k, v in acc.items()}
    out.update(scenario=name, reps=reps, theta_true=round(th_true, 4), pce=pce, M_tail=round(M_tail, 4),
               readiness=ready, GO=ready['pce'] <= 0.10 and ready['se0_kappa'] <= 0.020 and ready['stations'] >= 25
               and ready['kish'] >= 15, lookup_W0_to_4=[round(v, 4) for v in lookup[:5]])
    return out


def core_class_design(rng, kind, D=120, S=48, m=35):
    """Adversarial CORE geometries for the repaired bound (TAIL empty unless stated)."""
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    date = np.repeat(np.arange(D), rng.poisson(m, D)); N = date.size
    st = rng.choice(S, N, p=act)
    if kind == 'favourite':
        c = rng.uniform(0.60, 0.90, N)
    else:
        c = rng.uniform(0.35, 0.80, N)
        if kind in ('boundary_hidden', 'boundary_diffuse'):
            b = rng.random(N) < 0.06
            c[b] = rng.uniform(0.04, 0.06, b.sum())
        elif kind == 'mid5':
            b = rng.random(N) < 0.05
            c[b] = rng.uniform(0.04, 0.35, b.sum())
        elif kind == 'small_tail_allwin':
            t = rng.choice(N, 3, replace=False); c[t] = 0.039
    C = np.where(rng.random(N) < 0.68, 50.0, rng.uniform(10, 50, N))
    return dict(date=date, st=st, c=c, C=C, n=C / c, q=np.minimum(0.999, c + 0.12), tail=c < TAIL_CUT, S=S, D=D)


def core_class_truth(d, kind, target):
    c, n, C = d['c'], d['n'], d['C']
    if kind in ('uniform', 'favourite', 'min_geometry', 'mid5'):
        return c * (1 + target)
    if kind in ('boundary_hidden', 'boundary_diffuse'):
        p = 0.95 * c
        b = (c < 0.06) & (c >= TAIL_CUT)
        if kind == 'boundary_hidden':   # the edge sits in the first 10% of boundary legs only
            b = b & (np.cumsum(b) <= max(1, int(0.1 * b.sum())))
        base = (n * (p - c)).sum()
        need = target * C.sum() - base    # extra sum n (p - c) required on the chosen legs
        k = 1 + need / (n[b] * 0.95 * c[b]).sum() * 1.0
        p[b] = np.minimum(1.0, 0.95 * c[b] * k)
        return p
    if kind == 'small_tail_allwin':
        p = c * (1 + target); p[d['tail']] = 1.0
        return p
    raise ValueError(kind)


def run_core_class(kind, target, rho, reps, seed, D=120, S=48):
    rng = np.random.default_rng(seed)
    acc = dict(cov=0, exERT=0, exERT_false=0, T2=0); th_list = []; pce_list = []
    for _ in range(reps):
        d = core_class_design(rng, 'uniform' if kind == 'min_geometry' else kind, D=D, S=S)
        p = core_class_truth(d, kind, target)
        th_true = float((d['n'] * (p - d['c'])).sum() / d['C'].sum())
        y = (latent_u(rng, d, 1, rho)[0] < p).astype(float)
        s = core_stats(d, y)
        U = s['core_part'] + tail_worst_case(d['n'], d['C'], d['tail'])
        acc['cov'] += th_true <= U; acc['exERT'] += U < ERT
        acc['exERT_false'] += (U < ERT) and (th_true >= ERT); acc['T2'] += s['T2']
        th_list.append(th_true); pce_list.append(op_readiness(d)['pce'])
    out = {k: round(v / reps, 4) for k, v in acc.items()}
    out.update(kind=kind, target=target, rho=rho, reps=reps, D=D, S=S,
               theta_true_mean=round(float(np.mean(th_list)), 4), pce_median=float(np.median(pce_list)))
    return out


PLAN_D = [  # (label, callable args)
    ('attack', 'A1_positive_tail_negative_core', 8000),
    ('attack', 'A2_pure_hidden_lottery', 5000),
    ('attack', 'P3_negative_core_fair_tail', 2000),
    ('core', ('uniform', 0.02, 'TRUE'), 4000),
    ('core', ('uniform', 0.02, 'STRESS'), 4000),
    ('core', ('uniform', 0.02, 'SST'), 4000),
    ('core', ('favourite', 0.02, 'TRUE'), 4000),
    ('core', ('mid5', 0.02, 'TRUE'), 4000),
    ('core', ('boundary_hidden', 0.025, 'TRUE'), 4000),
    ('core', ('boundary_diffuse', 0.025, 'TRUE'), 4000),
    ('core', ('min_geometry', 0.02, 'TRUE'), 4000),
    ('core', ('min_geometry', 0.02, 'SST'), 4000),
    ('core', ('small_tail_allwin', -0.05, 'TRUE'), 4000),
    ('core', ('uniform', -0.05, 'TRUE'), 2000),
    ('core', ('uniform', -0.10, 'TRUE'), 2000),
]


def _job_d(i):
    rho_map = {'TRUE': TRUE, 'STRESS': STRESS, 'SST': SST}
    kind, arg, reps = PLAN_D[i]
    if kind == 'attack':
        return json.dumps(run_attack(arg, reps, 5000 + i))
    k, target, rho = arg
    D, S = (60, 25) if k == 'min_geometry' else (120, 48)
    out = run_core_class(k, target, rho_map[rho], reps, 5000 + i, D=D, S=S)
    out['rho_name'] = rho
    return json.dumps(out)


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
    elif MODE == 'd4':   # run D: python3 ... d4   (replication counts are fixed in PLAN_D)
        from multiprocessing import Pool
        with Pool(4) as pool:
            for line in pool.imap(_job_d, range(len(PLAN_D))):
                print(line, flush=True)
    else:
        from multiprocessing import Pool
        plan = PLAN_B if MODE == 'v2' else PLAN_A
        with Pool(min(len(plan), 8)) as pool:
            for line in pool.imap(_job, range(len(plan))):
                print(line, flush=True)
