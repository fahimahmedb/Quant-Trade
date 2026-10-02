"""ASTRA cycle-3 (D4-C3-P1) recheck engine — extends Astra's own cycle-2 engine (astra_m2_engine.py, committed in 8874dc54..b7522b84).
Cycle-3 changes (written from the spec text at 0cfdd4d2, sections 8.1d, 10.1-10.4): enlarged near-cap price laws, lambda 2.15 / 1.80,
Z_EFF 7.2 / SE_KAPPA_CEILING 0.005 gate, per-replication design record, gate modes. Does not import or copy the Architect run-J code.
(Original header follows.)
ASTRA cycle-2 (D4-C3-M2) recheck engine — independent; written by Astra from the spec text at 61f4904f
(sections 8.1, 8.1c, 8.5, 9, 10.2, 10.3, 11.4), extending Astra's own cycle-1 engine (astra_m1_engine.py). It does not import
or copy the Architect's run-H code.  SYNTHETIC ONLY: no market, forecast, settlement, wallet or P&L data is read.
OUTCOME_INFORMATION_USED = FALSE.

Per replication:
  OP (14 dates; same price law and station activity as the window) -> GO (spec 10.2 / 10.3, outcome-free).
  Window: D counted dates + P paused calendar dates (layout: random interior / one contiguous run / two runs / at start).
  Latent Z = copula (date, station, cell) = (0.05, 0.05, 0.10) + persistent components (unit-variance shapes scaled by rv)
  + idiosyncratic, unit total variance; y = 1{Z < q(p)} with q the exact quantile of Z's marginal (Gaussian, or the
  two-state mixture), so P(y = 1) = p exactly.
  Reach = GO and INFO_SUFFICIENT (IF1..IF5 on 5-date blocks, 11.4).
  Two-way CR (8.1) at calendar blocks b in {5,10,20,30} from date x station residual sums; df_b = min(G_B(b), G_S) - 1.
  OLD rule (4423c5c3): L_W = th - H95;  U_W = w (thc + t975(5) SE5_c) + M_tail;  T1a / NEG: kap -/+ t975(5) SE5_k.
  NEW rule (61f4904f, 8.1c): L_W = th - 1.70 H95;  U_W = w (thc + 1.70 Hc975) + M_tail;  T1a / NEG: kap -/+ 1.60 Hk975,
  with H_q = max_b t_{df_b,q} SE_2w(b).  Rates on a lambda grid are also recorded (1.00 .. 2.50 step 0.05).
"""
import math
import numpy as np
from scipy import stats
from scipy.special import ndtri, ndtr

ERT = 0.02
CUT = 0.04
Z80 = 2.4865
OPD = 14
BL = (5, 10, 20, 30)
RHO = (0.05, 0.05, 0.10)
LAM2_T, LAM2_K = 1.70, 1.60            # cycle-2 constants (61f4904f)
LAM_T, LAM_K = 2.15, 1.80              # cycle-3 constants (0cfdd4d2)
ZEFF, SEK_CEIL = 7.2, 0.005
GRID = np.round(1.0 + 0.05 * np.arange(51), 2)
_TQ = {}


def tq(p, df):
    v = _TQ.get((p, df))
    if v is None:
        v = float(stats.t.ppf(p, df)) if df >= 1 else float('inf')
        _TQ[(p, df)] = v
    return v


# ------------------------------------------------------------------ design
def prices(rng, kind, n):
    """kind: legacy string, or a tuple spec: ('U', a, b) uniform; ('PM', v) point mass; ('MIX', s, A, B) share s of law A else law B."""
    if isinstance(kind, (tuple, list)):
        t = kind[0]
        if t == 'U':
            return rng.uniform(kind[1], kind[2], n)
        if t == 'PM':
            return np.full(n, float(kind[1]))
        if t == 'MIX':
            u = rng.random(n) < kind[1]
            return np.where(u, prices(rng, kind[2], n), prices(rng, kind[3], n))
        raise ValueError(kind)
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
    if kind == 'fav80':
        return rng.uniform(0.80, 0.90, n)
    if kind == 'fav85':
        return rng.uniform(0.85, 0.90, n)
    if kind == 'pm89':
        return np.full(n, 0.89)
    if kind.startswith('pmmix'):            # share s % point mass 0.89, rest U(0.35, 0.80)
        return prices(rng, ('MIX', int(kind[5:]) / 100.0, ('PM', 0.89), ('U', 0.35, 0.80)), n)
    if kind == 'pt90':
        return np.full(n, 0.90)
    if kind == 'fav60':
        return rng.uniform(0.60, 0.90, n)
    if kind.startswith('tail') or kind.startswith('favtail') or kind.startswith('pmtail'):
        base = 'fav' if kind.startswith('favtail') else ('pm89' if kind.startswith('pmtail') else 'mid')
        share = float(kind.replace('favtail', '').replace('pmtail', '').replace('tail', '')) / 100.0
        u = rng.random(n) < share
        return np.where(u, rng.uniform(0.02, 0.039, n), prices(rng, base, n))
    raise ValueError(kind)


def fills(rng, cap, n):
    return rng.uniform(5.0, 25.0, n) if cap == 'thin' else np.full(n, 50.0)


def calendar(rng, D, P, lay):
    T = D + P
    paused = np.zeros(T, bool)
    if P:
        if lay == 'rand':
            paused[rng.choice(np.arange(1, T - 1), P, replace=False)] = True
        elif lay == 'run':
            s0 = int(rng.integers(1, T - P))
            paused[s0:s0 + P] = True
        elif lay == 'two':                      # two contiguous runs of P/2 at random interior non-overlapping starts
            h = P // 2
            while True:
                a, b = sorted(rng.integers(1, T - h, 2))
                if b >= a + h:
                    break
            paused[a:a + h] = True
            paused[b:b + (P - h)] = True
        elif lay == 'early':                    # one contiguous run right after the first forward date
            paused[1:1 + P] = True
        elif lay == 'late':
            paused[T - 1 - P:T - 1] = True
        else:
            raise ValueError(lay)
    return T, paused


def design_stats(c, C, st, S):
    """Spec 10.2 / 10.3 on the OP trades (outcome-free). Returns None if no trade / no CORE trade."""
    J = c.size
    if J == 0:
        return None
    mbar = J / OPD
    s2 = J * float(np.sum(C * C * (1.0 - c) / c)) / float(C.sum()) ** 2
    deff = 1.5 * (1.0 + 0.03 * (mbar - 1.0))
    se0 = math.sqrt(s2 * deff / (120.0 * mbar))
    core = c >= CUT
    if not core.any():
        return None
    se0k = math.sqrt(float(np.mean(c[core] * (1.0 - c[core]))) * deff / (120.0 * core.sum() / OPD))
    k = np.bincount(st, minlength=S)
    k = k[k > 0]
    kish = k.sum() ** 2 / float(np.sum(k * k))
    stn = bool(k.size >= 25 and kish >= 15)
    return dict(se0=se0, se0k=se0k, stn=stn,
                pce_old=math.ceil(round(100.0 * Z80 * se0, 9)) / 100.0,
                pce_new=math.ceil(round(100.0 * ZEFF * se0, 9)) / 100.0)


def gate(mode, d):
    """none | go2 (cycle-2 GO, superset) | go3 (cycle-3 GO) | th_old | th_new (theta-side clause only, incl. stations)."""
    if mode == 'none':
        return True
    if d is None:
        return False
    if mode == 'go2':
        return d['pce_old'] <= 0.10 and d['se0k'] <= 0.020 and d['stn']
    if mode == 'go3':
        return d['pce_new'] <= 0.10 and d['se0k'] <= SEK_CEIL and d['stn']
    if mode == 'th_old':
        return d['pce_old'] <= 0.10 and d['stn']
    if mode == 'th_new':
        return d['pce_new'] <= 0.10 and d['stn']
    raise ValueError(mode)


# ------------------------------------------------------------------ persistence (unit-variance shapes)
def ar_path(rng, phi, T, k=1):
    u = rng.standard_normal((T, k))
    e = np.empty((T, k))
    e[0] = u[0]
    s = math.sqrt(1.0 - phi * phi)
    for t in range(1, T):
        e[t] = phi * e[t - 1] + s * u[t]
    return e


def comp_path(rng, comp, T, S):
    kind, par = comp[0], comp[1]
    if kind == 'ar':
        return ar_path(rng, par, T)[:, 0], 'date'
    if kind == 'hemi':
        return ar_path(rng, par, T, 2), 'hemi'
    if kind == 'stn':
        return ar_path(rng, par, T, S), 'stn'
    if kind == 'mk':                            # two-state +-1, autocorrelation par^k: stay probability (1 + par)/2
        stay = (1.0 + par) / 2.0
        flips = rng.random(T) > stay
        flips[0] = False
        s0 = 1.0 if rng.random() < 0.5 else -1.0
        return s0 * np.cumprod(np.where(flips, -1.0, 1.0)), 'date'
    if kind == 'box':                           # trailing par-date mean of iid shocks, unit variance, acf 1 - k/par
        L = int(par)
        u = rng.standard_normal(T + L - 1)
        cs = np.concatenate(([0.0], np.cumsum(u)))
        return (cs[L:] - cs[:-L]) / math.sqrt(L), 'date'
    raise ValueError(kind)


_MKQ = {}


def mk_quantile(p, a):
    """Exact quantile of 0.5 N(a, 1-a^2) + 0.5 N(-a, 1-a^2) (Newton, vectorised)."""
    sg = math.sqrt(1.0 - a * a)
    pc = np.clip(p, 1e-12, 1 - 1e-12)
    q = ndtri(pc)
    for _ in range(60):
        F = 0.5 * ndtr((q - a) / sg) + 0.5 * ndtr((q + a) / sg)
        f = 0.5 * (np.exp(-0.5 * ((q - a) / sg) ** 2) + np.exp(-0.5 * ((q + a) / sg) ** 2)) / (sg * math.sqrt(2 * math.pi))
        q = q - (F - pc) / f
    return np.where(p >= 1.0, np.inf, q)


# ------------------------------------------------------------------ CR engine (spec 8.1)
def cr_all(day, st, r, T, S, Q):
    """dict b -> (SE_2w(b), df_b, G_B(b)) for b in BL, calendar blocks floor(day / b)."""
    key = day * S + st
    M = np.bincount(key, weights=r, minlength=T * S).reshape(T, S)
    Cn = np.bincount(key, minlength=T * S).reshape(T, S)
    out = {}
    q2 = Q * Q
    for b in BL:
        nb = -(-T // b)
        pad = nb * b - T
        Mp = np.vstack([M, np.zeros((pad, S))]) if pad else M
        Cp = np.vstack([Cn, np.zeros((pad, S), Cn.dtype)]) if pad else Cn
        Mb = Mp.reshape(nb, b, S).sum(axis=1)
        Cb = Cp.reshape(nb, b, S).sum(axis=1)
        sB = Mb.sum(axis=1)
        sS = Mb.sum(axis=0)
        GB = int(np.count_nonzero(Cb.sum(axis=1)))
        GS = int(np.count_nonzero(Cb.sum(axis=0)))
        GBS = int(np.count_nonzero(Cb))
        VB = GB / (GB - 1.0) * float(sB @ sB) / q2 if GB > 1 else float('inf')
        VS = GS / (GS - 1.0) * float(sS @ sS) / q2
        VBS = GBS / (GBS - 1.0) * float(np.sum(Mb * Mb)) / q2
        out[b] = (math.sqrt(max(VB, VS, VB + VS - VBS)), min(GB, GS) - 1, GB)
    return out


def H(cr, q):
    return max(tq(q, cr[b][1]) * cr[b][0] for b in BL)


# ------------------------------------------------------------------ one replication
def one_rep(rng, g):
    """returns (d, gated, rec): d = OP design record (or None); gated = passed g['gate']; rec = window record if gated and INFO_SUFFICIENT."""
    S, D, m = g.get('S', 48), g.get('D', 120), g.get('m', 17)
    pr, cap, th = g.get('pr', 'mid'), g.get('cap', 'thin'), g.get('th', 0.0)
    act = rng.gamma(2.0, 1.0, S)
    act = act / act.sum()
    n_op = int(np.minimum(rng.poisson(m, OPD), 2 * S).sum())
    st_op = rng.choice(S, n_op, p=act)
    d = design_stats(prices(rng, g.get('pr_op', pr), n_op), fills(rng, cap, n_op), st_op, S)
    if not gate(g.get('gate', 'go2'), d):
        return d, False, None
    if th == 'own_new':
        th = d['pce_new']
    elif th == 'own_old':
        th = d['pce_old']
    pce = d['pce_old'] if d else 0.0
    T, paused = calendar(rng, D, g.get('P', 0), g.get('lay', 'rand'))
    cnt = np.minimum(rng.poisson(m, T), 2 * S)
    cnt[paused] = 0
    day = np.repeat(np.arange(T), cnt)
    n = day.size
    st = rng.choice(S, n, p=act)
    c = prices(rng, pr, n)
    C = fills(rng, cap, n)
    p = np.minimum(1.0, c * (1.0 + th))
    # latent
    rd, rs, rc = RHO
    z = (math.sqrt(rd) * rng.standard_normal(T)[day] + math.sqrt(rs) * rng.standard_normal(S)[st]
         + math.sqrt(rc) * rng.standard_normal(T * S)[day * S + st])
    used = rd + rs + rc
    mk_a = None
    for comp in g.get('comps', ()):
        e, kind = comp_path(rng, comp, T, S)
        rv = comp[2]
        if kind == 'date':
            z = z + math.sqrt(rv) * e[day]
        elif kind == 'hemi':
            z = z + math.sqrt(rv) * e[day, (st >= S // 2).astype(int)]
        else:
            z = z + math.sqrt(rv) * e[day, st]
        if comp[0] == 'mk':
            if mk_a is not None:
                raise ValueError('one two-state component only')
            mk_a = math.sqrt(rv)
        used += rv
    z = z + math.sqrt(1.0 - used) * rng.standard_normal(n)
    if mk_a is None:
        qthr = ndtri(p)
    else:   # Z = a s + G, G ~ N(0, 1 - a^2): mixture quantile
        qthr = mk_quantile(p, mk_a)
    y = (z < qthr).astype(float)
    # statistics
    nsh = C / c
    Q = float(C.sum())
    N = nsh * (y - c)
    tht = float(N.sum()) / Q
    thW = float(np.sum(nsh * (p - c))) / Q
    crT = cr_all(day, st, N - tht * C, T, S, Q)
    core = c >= CUT
    tail = ~core
    x = (y - c)[core]
    nk = x.size
    kap = float(x.mean())
    kt = float(np.mean((p - c)[core]))
    crK = cr_all(day[core], st[core], x - kap, T, S, float(nk))
    sek5 = crK[5][0]
    viid = nk / (nk - 1.0) * float(np.sum((x - kap) ** 2)) / float(nk) ** 2
    sc = np.bincount(st, minlength=S)
    sc = sc[sc > 0]
    kish = sc.sum() ** 2 / float(np.sum(sc * sc))
    info = bool(D >= 60 and crT[5][2] >= 12 and sc.size >= 25 and kish >= 15 and sek5 <= 0.025 and sek5 * sek5 / viid <= 6.0)
    if not info:
        return d, True, None
    if tail.any():
        Cc = C[core]
        Qc = float(Cc.sum())
        thc = float(N[core].sum()) / Qc
        crC = cr_all(day[core], st[core], N[core] - thc * Cc, T, S, Qc)
        M_tail = float(np.sum(nsh[tail] - C[tail])) / Q
        w = Qc / Q
    else:
        thc, crC, M_tail, w = tht, crT, 0.0, 1.0
    return d, True, (tht, thW, kap, kt, thc, w, M_tail,
            H(crT, 0.95), tq(0.95, crT[5][1]) * crT[5][0],
            H(crC, 0.975), tq(0.975, crC[5][1]) * crC[5][0],
            H(crK, 0.975), tq(0.975, crK[5][1]) * crK[5][0], pce, d['se0'], d['se0k'], d['pce_new'],
            float(d['pce_old'] <= 0.10 and d['se0k'] <= 0.020 and d['stn']),
            float(d['pce_new'] <= 0.10 and d['se0k'] <= SEK_CEIL and d['stn']),
            float(d['pce_new'] <= 0.10 and d['stn']), nk, th)


FIELDS = ('th', 'thW', 'kap', 'kt', 'thc', 'w', 'Mt', 'H95', 'H95_5', 'Hc975', 'Hc975_5', 'Hk975', 'Hk975_5', 'pce', 'se0', 'se0k', 'pce_new', 'go2', 'go3', 'thnew', 'nk', 'thused')


def run_chunk(g, reps, seed):
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    recs = []
    ngate = 0
    sse0 = sse0k = 0.0
    nd = 0
    for _ in range(reps):
        d, gated, r = one_rep(rng, g)
        if d is not None:
            nd += 1
            sse0 += d['se0']
            sse0k += d['se0k']
        ngate += int(gated)
        if r is not None:
            recs.append(r)
    out = counts(np.array(recs, float).reshape(-1, len(FIELDS)), reps)
    out.update(ngate=ngate, nd=nd, sum_se0_op=sse0, sum_se0k_op=sse0k)
    return out


def counts(A, reps):
    out = dict(reps=reps, reach=int(A.shape[0]))
    if A.shape[0] == 0:
        return out
    th, thW, kap, kt, thc, w, Mt, H95, H95_5, Hc, Hc5, Hk, Hk5, pce, se0r, se0kr, pcenew, go2r, go3r, thnewr, nkr, thused = A.T
    lam = GRID[:, None]
    Lg = th[None, :] - lam * H95[None, :]
    Ug = w[None, :] * (thc[None, :] + lam * Hc[None, :]) + Mt[None, :]
    out['g_miss'] = (Lg > thW).sum(1).tolist()
    out['g_fpos'] = ((Lg > 0) & (th >= ERT) & (thW <= 0)).sum(1).tolist()
    out['g_t2'] = (Lg > 0).sum(1).tolist()
    out['g_uwmiss'] = (Ug < thW).sum(1).tolist()
    out['g_uwloss'] = (Ug < 0).sum(1).tolist()
    out['g_T1a_null'] = ((kap - lam * Hk > 0) & (kt <= 0)).sum(1).tolist()
    out['g_NEG_null'] = ((kap + lam * Hk < 0) & (kt >= 0)).sum(1).tolist()
    out['g_T1a'] = (kap - lam * Hk > 0).sum(1).tolist()
    out['g_NEG'] = (kap + lam * Hk < 0).sum(1).tolist()
    # OLD (61f4904f: 1.70 / 1.60) and NEW (0cfdd4d2: 2.15 / 1.80) rules on the same replications
    Lo = th - LAM2_T * H95
    Uo = w * (thc + LAM2_T * Hc) + Mt
    Ln = th - LAM_T * H95
    Un = w * (thc + LAM_T * Hc) + Mt

    def s(x):
        return int(np.sum(x))
    out['old'] = dict(miss=s(Lo > thW), fpos=s((Lo > 0) & (th >= ERT) & (thW <= 0)), t2=s(Lo > 0),
                      uwmiss=s(Uo < thW), uwloss=s(Uo < 0), uwloss_false=s((Uo < 0) & (thW >= 0)),
                      T1a_null=s((kap - LAM2_K * Hk > 0) & (kt <= 0)), NEG_null=s((kap + LAM2_K * Hk < 0) & (kt >= 0)),
                      T1a=s(kap - LAM2_K * Hk > 0), NEG=s(kap + LAM2_K * Hk < 0),
                      head_noncov=s((Lo > thW) | (Uo < thW)),
                      loss_vs_headline=s((Uo < 0) & (Lo > Uo)))
    out['new'] = dict(miss=s(Ln > thW), fpos=s((Ln > 0) & (th >= ERT) & (thW <= 0)), t2=s(Ln > 0),
                      uwmiss=s(Un < thW), uwloss=s(Un < 0), uwloss_false=s((Un < 0) & (thW >= 0)),
                      T1a_null=s((kap - LAM_K * Hk > 0) & (kt <= 0)), NEG_null=s((kap + LAM_K * Hk < 0) & (kt >= 0)),
                      T1a=s(kap - LAM_K * Hk > 0), NEG=s(kap + LAM_K * Hk < 0),
                      head_noncov=s((Ln > thW) | (Un < thW)), loss_vs_headline=s((Un < 0) & (Ln > Un)),
                      LW_above_old=s(Ln > Lo + 1e-15), UW_below_old=s(Un < Uo - 1e-15))
    # moments (for oracle power / information analysis)
    out['sum_err'] = float(np.sum(th - thW))
    out['sum_err2'] = float(np.sum((th - thW) ** 2))
    out['sum_H95'] = float(np.sum(H95))
    out['sum_H95_5'] = float(np.sum(H95_5))
    out['sum_Hk'] = float(np.sum(Hk))
    out['sum_Hk5'] = float(np.sum(Hk5))
    out['sum_kerr2'] = float(np.sum((kap - kt) ** 2))
    out['sum_pce'] = float(np.sum(pce))
    out['sum_thW'] = float(np.sum(thW)); out['sum_kt'] = float(np.sum(kt)); out['sum_kap'] = float(np.sum(kap))
    out['sum_se0_rec'] = float(np.sum(se0r)); out['sum_se0k_rec'] = float(np.sum(se0kr))
    out['n_go2'] = int(np.sum(go2r)); out['n_go3'] = int(np.sum(go3r)); out['n_thnew'] = int(np.sum(thnewr))
    out['sum_thused'] = float(np.sum(thused))
    # T2 / NEG / T1a at the adopted constants, restricted to the theta-side-new GO and to the full cycle-3 GO
    m_th = thnewr > 0.5
    out['t2_at_adopted_given_thnew'] = int(np.sum((Ln > 0) & m_th))
    out['pce_hist'] = {str(k): int(v) for k, v in zip(*np.unique(np.round(pce, 2), return_counts=True))}
    return out


def merge(parts):
    out = dict(reps=0, reach=0)
    for p_ in parts:
        out['reps'] += p_['reps']
        out['reach'] += p_['reach']
        for k, v in p_.items():
            if k in ('reps', 'reach'):
                continue
            if isinstance(v, list):
                out[k] = [a + b for a, b in zip(out[k], v)] if k in out else list(v)
            elif isinstance(v, dict):
                d = out.setdefault(k, {})
                for kk, vv in v.items():
                    d[kk] = d.get(kk, 0) + vv
            else:
                out[k] = out.get(k, 0.0) + v
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    ph = k / n
    den = 1 + z * z / n
    cen = (ph + z * z / (2 * n)) / den
    hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [round(max(0.0, cen - hw), 5), round(min(1.0, cen + hw), 5)]
