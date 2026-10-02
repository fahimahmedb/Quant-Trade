"""Weather V3 / S0 - NumPy-first Monte-Carlo engine for the Weather Forward V2 D4-C3 simulation family.

SYNTHETIC ONLY. No market, forecast, order-book, settlement, wallet or P&L data is read or used (OUTCOME_INFORMATION_USED=FALSE).

Reproduces the *statistical object* of WEATHER_FORWARD_V2_D4_C3_P1_GATE_SIM (`one_rep_p1`, itself proved identical to the M2
`one_rep` by V2's own check()): OP design record + GO gate modes, window generator (copula + persistent component), the
two-way CR statistics, INFO_SUFFICIENT, SUPPORTED gates, and the per-lambda decision counts.

Architecture (Blue plan s.3): Python loops over cells / plans / rep-blocks only. Replications are array axes: trades of all
reps in a block are flattened with a `rep` index; per-rep reductions are np.bincount; calendar x station sums are (R, T, S)
arrays; block sums are reshapes. No pandas.

RNG: SeedSequence([BASE_SEED, PLAN_ID, CELL_ID, STREAM_ID]) per (cell, stream) with spawn_key=(block,) for rep-blocks.
`rep_block(g)` is a pure function of the cell spec, so the result for a cell depends on nothing but (seed tuple, cell spec,
reps): not on slice, CPU count, processes or completion order.

The old engine consumes its RNG sequentially per replication; a vectorised generator cannot reproduce that stream. Equivalence
is therefore statistical for the generator (wf_equiv.py layer B) and exact for the statistics kernel (layer A: the same
injected inputs give the same outputs).
"""
import math

import numpy as np
from scipy import stats
from scipy.signal import lfilter
from scipy.special import ndtr, ndtri

ENGINE_VERSION = 'wf_engine/1.0'
SCHEMA_VERSION = 'wf_cell_record/1'

ERT, CUT, Z80 = 0.02, 0.04, 2.4865
OPD = 14
RHO = (0.05, 0.05, 0.10)
BL = (5, 10, 20, 30)
GRID3 = tuple(round(1.0 + 0.05 * i, 2) for i in range(51))          # 1.00 .. 3.50
_T95 = np.array([np.inf] + [float(stats.t.ppf(0.95, d)) for d in range(1, 2001)])
_T975 = np.array([np.inf] + [float(stats.t.ppf(0.975, d)) for d in range(1, 2001)])
BASE = dict(D=120, S=48, m=17, cap='thin', th=0.0, pr='mid', P=0, lay='rand')


def G(**kw):
    g = dict(BASE)
    g.update(kw)
    return g


# ------------------------------------------------------------------------------------------------ price / fill laws
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
    if kind == 'fav80':
        return rng.uniform(0.80, 0.90, n)
    if kind == 'fav85':
        return rng.uniform(0.85, 0.90, n)
    if kind == 'pm89':
        return np.full(n, 0.89)
    if kind.startswith('pmmix'):                       # share s of point mass 0.89, rest U(0.35, 0.80)
        s = int(kind[5:]) / 100.0
        u = rng.random(n) < s
        return np.where(u, 0.89, rng.uniform(0.35, 0.80, n))
    if kind == 'pm899':
        return np.full(n, 0.899)
    if kind == 'pm85':
        return np.full(n, 0.85)
    if kind == 'pm80':
        return np.full(n, 0.80)
    if kind == 'fav88':
        return rng.uniform(0.88, 0.90, n)
    if kind == 'fav60':
        return rng.uniform(0.60, 0.90, n)
    raise ValueError(kind)


def fills(rng, cap, n):
    return rng.uniform(5.0, 25.0, n) if cap == 'thin' else np.full(n, 50.0)


_MKQ = {}


def _mk_table(rv):
    if rv not in _MKQ:
        a = math.sqrt(rv)
        sg = math.sqrt(1 - rv)
        pg = np.linspace(1e-7, 1 - 1e-7, 40001)
        q = ndtri(pg)
        for _ in range(60):
            F = 0.5 * ndtr((q - a) / sg) + 0.5 * ndtr((q + a) / sg)
            f = 0.5 * (np.exp(-0.5 * ((q - a) / sg) ** 2) + np.exp(-0.5 * ((q + a) / sg) ** 2)) / (sg * math.sqrt(2 * math.pi))
            q = q - (F - pg) / f
        _MKQ[rv] = (pg, q)
    return _MKQ[rv]


def thresholds(p, g):
    if g.get('pk') != 'mk':
        return ndtri(p)
    pg, qg = _mk_table(g['rv'])
    return np.where(p >= 1.0, np.inf, np.interp(p, pg, qg))


BLOCK_TRADES = 120_000        # target trades per block (cache-sized; tuned in the benchmark, see BENCHMARK_REPORT.md)
BLOCK_CELLS = 400_000         # target R*T*S cells per block


def rep_block(g):
    """Logical rep-block size: a pure function of the cell spec (never of hardware). Bounds peak RAM and keeps working arrays
    cache-sized; part of the reproducibility contract (recorded in every record)."""
    tc = g['D'] + g.get('P', 0)
    per_rep = max(1.0, min(g['m'], 2 * g['S']) * tc)
    r = min(BLOCK_TRADES / per_rep, BLOCK_CELLS / (tc * g['S']))
    return int(min(500, max(10, r // 10 * 10)))


# ------------------------------------------------------------------------------------------------ batched primitives
def draw_stations(rng, rep, act, R):
    """Inverse-CDF station draw, per-rep activity weights `act` (R, S); equals rng.choice(S, p=act_r) in distribution."""
    S = act.shape[1]
    cdf = np.cumsum(act, axis=1)
    cdf /= cdf[:, -1:]
    cdf[:, -1] = 1.0
    flat = (cdf + np.arange(R)[:, None]).ravel()
    u = rng.random(rep.size)
    idx = np.searchsorted(flat, rep + u, side='right') - rep * S
    return np.minimum(idx, S - 1)


def design_arrays(rep, c, C, st, R, S, zeff):
    """Spec 10.2 on the OP trades, per replication: se0, se0k, stn, pce_old, pce_new, valid (=d is not None)."""
    J = np.bincount(rep, minlength=R).astype(float)
    sC = np.bincount(rep, weights=C, minlength=R)
    snum = np.bincount(rep, weights=C * C * (1 - c) / c, minlength=R)
    core = c >= CUT
    nco = np.bincount(rep[core], minlength=R).astype(float)
    mcv = np.bincount(rep[core], weights=(c * (1 - c))[core], minlength=R)
    with np.errstate(all='ignore'):
        mbar = J / OPD
        s2 = J * snum / sC ** 2
        deff = 1.5 * (1 + 0.03 * (mbar - 1))
        se0 = np.sqrt(s2 * deff / (120 * mbar))
        se0k = np.sqrt((mcv / nco) * deff / (120 * nco / OPD))
        k = np.bincount(rep * S + st, minlength=R * S).reshape(R, S).astype(float)
        ks = k.sum(1)
        stn = ((k > 0).sum(1) >= 25) & (ks ** 2 / (k * k).sum(1) >= 15)
        pce_old = np.ceil(np.round(100 * Z80 * se0, 9)) / 100
        pce_new = np.ceil(np.round(100 * zeff * se0, 9)) / 100 if zeff else np.full(R, np.nan)
    valid = (J > 0) & (nco > 0)
    return dict(se0=se0, se0k=se0k, stn=stn, pce_old=pce_old, pce_new=pce_new, valid=valid)


def go_pass(mode, d, K):
    v = d['valid']
    if mode == 'none':
        return v.copy()
    with np.errstate(invalid='ignore'):
        if mode == 'old':
            return v & (d['pce_old'] <= 0.10) & (d['se0k'] <= 0.020) & d['stn']
        if mode == 'th_old':
            return v & (d['pce_old'] <= 0.10) & d['stn']
        if mode == 'th_new':
            return v & (d['pce_new'] <= 0.10) & d['stn']
        if mode == 'new':
            return v & (d['pce_new'] <= 0.10) & (d['se0k'] <= K['se_kappa_ceiling']) & d['stn']
    raise ValueError(mode)


def _cr_from_b5(M5, C5, Q, b):
    """Two-way CR (spec 8.1, max-of-three, CR1 per dimension) for every replication at once, from sums over fixed 5-date
    calendar blocks. M5, C5: (R, NB5, S) with NB5 padded with empty blocks to a multiple of 12 (=60 dates); every b in BL
    is a multiple of 5 that divides 60, so block-b sums are exact regroupings and empty padded blocks add nothing
    (G counts non-empty clusters; sums unchanged), i.e. identical to the V2 zero-padding of the last partial block."""
    R, NB5, S = M5.shape
    f = b // 5
    if f == 1:
        Mb, Cb = M5, C5
    else:
        Mb = M5.reshape(R, NB5 // f, f, S).sum(axis=2)
        Cb = C5.reshape(R, NB5 // f, f, S).sum(axis=2)
    sB = Mb.sum(axis=2)
    sS = Mb.sum(axis=1)
    GB = np.count_nonzero(Cb.sum(axis=2), axis=1)
    GS = np.count_nonzero(Cb.sum(axis=1), axis=1)
    GBS = np.count_nonzero(Cb.reshape(R, -1), axis=1)
    q2 = Q * Q
    with np.errstate(all='ignore'):
        VB = GB / (GB - 1.0) * (sB * sB).sum(axis=1) / q2
        VS = GS / (GS - 1.0) * (sS * sS).sum(axis=1) / q2
        VBS = GBS / (GBS - 1.0) * (Mb * Mb).sum(axis=(1, 2)) / q2
        se = np.sqrt(np.maximum(np.maximum(VB, VS), VB + VS - VBS))
    return se, np.minimum(GB, GS) - 1, GB


def _mats(key5, w, R, NB5, S, sel=None):
    if sel is not None:
        key5 = key5[sel]
        w = w[sel]
    n = R * NB5 * S
    M5 = np.bincount(key5, weights=w, minlength=n).reshape(R, NB5, S)
    C5 = np.bincount(key5, minlength=n).reshape(R, NB5, S)
    return M5, C5


def _halfwidths(key5, r, R, NB5, S, Q, sel=None):
    M5, C5 = _mats(key5, r, R, NB5, S, sel)
    return {b: _cr_from_b5(M5, C5, Q, b) for b in BL}


def _t(tab, df):
    return tab[np.clip(df, 0, 2000)]


def _H(hw, tab):
    return np.max([_t(tab, hw[b][1]) * hw[b][0] for b in BL], axis=0)


def window_stats(rep, day, st, c, C, y, p, R, Tc, S, D):
    """Statistics kernel (the part of one_rep_p1 after the window is generated), exact semantics.
    Inputs are flat trade arrays with a replication index. Returns dict of per-rep arrays + `info` mask."""
    NB5 = 12 * (-(-Tc // 60))
    key = ((rep * NB5 + day // 5) * S + st)
    nsh = C / c
    N = nsh * (y - c)
    bc = lambda w: np.bincount(rep, weights=w, minlength=R)
    n = np.bincount(rep, minlength=R).astype(float)
    Q = bc(C)
    sumN = bc(N)
    with np.errstate(all='ignore'):
        th = sumN / Q
        thW = bc(nsh * (p - c)) / Q
    hw = _halfwidths(key, N - th[rep] * C, R, NB5, S, Q)
    core = c >= CUT
    tail = ~core
    nk = np.bincount(rep[core], minlength=R).astype(float)
    x = y - c
    with np.errstate(all='ignore'):
        kap = np.bincount(rep[core], weights=x[core], minlength=R) / nk
        kt = np.bincount(rep[core], weights=(p - c)[core], minlength=R) / nk
        hk = _halfwidths(key, x - kap[rep], R, NB5, S, nk, sel=core)
        sek5 = hk[5][0]
        dev = np.where(core, (x - kap[rep]) ** 2, 0.0)
        viid = nk / (nk - 1.0) * bc(dev) / nk ** 2
        sc = np.bincount(rep * S + st, minlength=R * S).reshape(R, S).astype(float)
        scs = sc.sum(1)
        info = ((D >= 60) & (hw[5][2] >= 12) & ((sc > 0).sum(1) >= 25) & (scs ** 2 / (sc * sc).sum(1) >= 15)
                & (sek5 <= 0.025) & ((viid <= 0.0) | (sek5 * sek5 / viid <= 6.0)))
        Cc = np.where(core, C, 0.0)
        Qc = bc(Cc)
        Nc = np.where(core, N, 0.0)
        thc = bc(Nc) / Qc
        hc = _halfwidths(key, N - thc[rep] * C, R, NB5, S, Qc, sel=core)
        Mt = bc(np.where(tail, nsh - C, 0.0)) / Q
        w = Qc / Q
    cc = c + 0.01
    with np.errstate(all='ignore'):
        g1 = bc((C / cc) * (y - cc)) / Q > 0
    pos = np.maximum(N, 0.0)
    gross = bc(pos)
    # top-5 per replication: segments are contiguous (trades are generated rep-major); pad to (R, max n) and partition
    ends = np.cumsum(n).astype(np.int64)
    starts = ends - n.astype(np.int64)
    nmax = int(n.max()) if R else 0
    pad = np.full((R, max(nmax, 5)), -np.inf)
    pad[rep, np.arange(rep.size) - starts[rep]] = N
    top5 = np.where(n >= 5, np.partition(pad, -5, axis=1)[:, -5:].sum(axis=1), sumN)
    day_pos = np.bincount(rep * Tc + day, weights=pos, minlength=R * Tc).reshape(R, Tc).max(axis=1)
    st_pos = np.bincount(rep * S + st, weights=pos, minlength=R * S).reshape(R, S).max(axis=1)
    g2 = (gross > 0) & ((sumN - top5) / Q > 0) & (day_pos <= 0.25 * gross) & (st_pos <= 0.20 * gross)
    return dict(info=info, th=th, thW=thW, kap=kap, kt=kt, thc=thc, w=w, Mt=Mt, gates=(g1 & g2).astype(float),
                H_A=_H(hw, _T95), HkA=_H(hk, _T975), HcA=_H(hc, _T975),
                H_R0=_t(_T95, hw[5][1]) * hw[5][0], Hk5=_t(_T975, hk[5][1]) * hk[5][0],
                ntail=np.bincount(rep[tail], minlength=R).astype(float))


# ------------------------------------------------------------------------------------------------ generator
def gen_window_batch(rng, g, R):
    S, D, m = g['S'], g['D'], g['m']
    P = g.get('P', 0)
    Tc = D + P
    paused = np.zeros((R, Tc), bool)
    if P:
        if g.get('lay', 'rand') == 'rand':
            pick = np.argsort(rng.random((R, Tc - 2)), axis=1)[:, :P] + 1       # P distinct interior positions
            paused[np.arange(R)[:, None], pick] = True
        else:
            s0 = rng.integers(1, Tc - P, R)
            pos = s0[:, None] + np.arange(P)[None, :]
            paused[np.arange(R)[:, None], pos] = True
    cnt = np.minimum(rng.poisson(m, (R, Tc)), 2 * S)
    cnt[paused] = 0
    cell = np.repeat(np.arange(R * Tc), cnt.ravel())
    return Tc, cell // Tc, cell % Tc


def persistent_batch(rng, g, R, Tc, S):
    """Unit-variance persistent date-level component on the Tc calendar days: (R, Tc) or (R, Tc, k)."""
    kind = g.get('pk')
    if kind is None:
        return None
    par = g['pp']
    if kind in ('ar', 'hemi', 'stn'):
        k = 1 if kind == 'ar' else (2 if kind == 'hemi' else S)
        u = rng.standard_normal((R, Tc, k))
        e = np.empty((R, Tc, k))
        e[:, 0] = u[:, 0]
        if Tc > 1:
            e[:, 1:] = lfilter([math.sqrt(1 - par * par)], [1.0, -par], u[:, 1:], axis=1, zi=(par * u[:, 0])[:, None, :])[0]
        return e[:, :, 0] if kind == 'ar' else e
    if kind == 'mk':
        stay = (1 + par) / 2
        flips = rng.random((R, Tc)) > stay
        flips[:, 0] = False
        s0 = np.where(rng.random(R) < 0.5, 1.0, -1.0)
        return np.cumprod(np.where(flips, -1.0, 1.0), axis=1) * s0[:, None]
    if kind == 'box':
        L = int(par)
        u = rng.standard_normal((R, Tc + L - 1))
        cs = np.concatenate((np.zeros((R, 1)), np.cumsum(u, axis=1)), axis=1)
        return (cs[:, L:] - cs[:, :-L]) / math.sqrt(L)
    raise ValueError(kind)


def simulate_block(rng, g, K, R):
    """R replications. Returns (design arrays for all R, rec arrays for the reached replications or None)."""
    S = g['S']
    m = g['m']
    # --- OP phase (outcome-free design check)
    n_op_rep = np.minimum(rng.poisson(m, (R, OPD)), 2 * S).sum(axis=1)
    act = rng.gamma(2.0, 1.0, (R, S))
    act /= act.sum(axis=1, keepdims=True)
    rep_op = np.repeat(np.arange(R), n_op_rep)
    st_op = draw_stations(rng, rep_op, act, R)
    c_op = prices(rng, g['pr'], rep_op.size)
    C_op = fills(rng, g['cap'], rep_op.size)
    zeff = K.get('z_eff') if K else None
    mode = g.get('go', 'old')
    if (mode in ('th_new', 'new') or g['th'] == 'pce_new') and not zeff:
        raise ValueError('gate mode / theta needs constants K with z_eff (pass --K)')
    if mode == 'new' and not (K and K.get('se_kappa_ceiling')):
        raise ValueError("go='new' needs K['se_kappa_ceiling']")
    d = design_arrays(rep_op, c_op, C_op, st_op, R, S, zeff)
    go = go_pass(mode, d, K)
    if not go.any():
        return d, None
    # --- window phase, only for GO-passing replications (replications are independent)
    ids = np.flatnonzero(go)
    R2 = ids.size
    thv = g['th']
    if isinstance(thv, str):
        thv = d['pce_old'][ids] if thv == 'pce_old' else d['pce_new'][ids]
    else:
        thv = np.full(R2, float(thv))
    Tc, rep, day = gen_window_batch(rng, g, R2)
    act2 = act[ids]
    st = draw_stations(rng, rep, act2, R2)
    c = prices(rng, g['pr'], rep.size)
    C = fills(rng, g['cap'], rep.size)
    p = np.minimum(1.0, c * (1.0 + thv[rep]))
    z = (math.sqrt(RHO[0]) * rng.standard_normal((R2, Tc))[rep, day]
         + math.sqrt(RHO[1]) * rng.standard_normal((R2, S))[rep, st]
         + math.sqrt(RHO[2]) * rng.standard_normal((R2, Tc, S))[rep, day, st])
    used = sum(RHO)
    e = persistent_batch(rng, g, R2, Tc, S)
    if e is not None:
        rv = g['rv']
        if g['pk'] == 'hemi':
            z = z + math.sqrt(rv) * e[rep, day, (st >= S // 2).astype(int)]
        elif g['pk'] == 'stn':
            z = z + math.sqrt(rv) * e[rep, day, st]
        else:
            z = z + math.sqrt(rv) * e[rep, day]
        used += rv
    z = z + math.sqrt(1 - used) * rng.standard_normal(rep.size)
    y = (z < thresholds(p, g)).astype(float)
    r = window_stats(rep, day, st, c, C, y, p, R2, Tc, S, g['D'])
    keep = r.pop('info')
    return d, {k: v[keep] for k, v in r.items()}, int(R2)


# ------------------------------------------------------------------------------------------------ counts (schema = V2 P1 `counts`)
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


def counts_from_records(A, reps):
    """Per-lambda decision counts from concatenated per-rep record arrays (A is a dict of 1-D arrays of the reached reps)."""
    th, thW, kap, kt = A['th'], A['thW'], A['kap'], A['kt']
    lam = np.array(GRID3)[:, None]
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
    T1a = (kap - lam * A['HkA'] > 0)
    NEG = (kap + lam * A['HkA'] < 0)
    by_lam = dict(miss=miss.tolist(), fpos=fpos.tolist(), sup=sup.tolist(), t2=t2.tolist(), uw_miss=uw_miss.tolist(),
                  uw_loss=uw_loss.tolist(), iv_miss=iv_miss.tolist(), T1a=T1a.sum(axis=1).tolist(), NEG=NEG.sum(axis=1).tolist(),
                  T1a_null=(T1a & (kt <= 0)).sum(axis=1).tolist(), NEG_null=(NEG & (kt >= 0)).sum(axis=1).tolist())
    mean = dict(th=round(float(th.mean()), 5), thW=round(float(thW.mean()), 5), kap=round(float(kap.mean()), 5),
                kt=round(float(kt.mean()), 5), HA=round(float(A['H_A'].mean()), 5), HkA=round(float(A['HkA'].mean()), 5),
                Hk5=round(float(A['Hk5'].mean()), 5))
    return by_lam, mean, round(float(A['ntail'].mean()), 2)


def run_cell_stream(g, K, base_seed, plan_id, cell_id, stream_id, reps):
    """One (cell, stream): returns (record-core dict, rec arrays). Deterministic in (seed tuple, g, K, reps)."""
    seed = [int(base_seed), int(plan_id), int(cell_id), int(stream_id)]
    rb = rep_block(g)
    nblocks = -(-reps // rb)
    recs = []
    dsum = dict(n=0, se0=0.0, se0k=0.0, pce_old=0.0, pce_new=0.0, n_go=0)
    for b in range(nblocks):
        R = min(rb, reps - b * rb)
        ss = np.random.SeedSequence(entropy=seed, spawn_key=(b,))
        rng = np.random.default_rng(ss)
        out = simulate_block(rng, g, K, R)
        d = out[0]
        v = d['valid']
        dsum['n'] += int(v.sum())
        dsum['se0'] += float(d['se0'][v].sum())
        dsum['se0k'] += float(d['se0k'][v].sum())
        dsum['pce_old'] += float(d['pce_old'][v].sum())
        if K and K.get('z_eff'):
            dsum['pce_new'] += float(d['pce_new'][v].sum())
        if len(out) == 3:
            dsum['n_go'] += out[2]
            recs.append(out[1])
    A = {k: np.concatenate([r[k] for r in recs]) for k in recs[0]} if recs else None
    return seed, rb, dsum, A


def stream_record(plan, idx, g, reps, seed, rb, dsum, A):
    out = dict(plan=plan, idx=idx, g=g, reps=reps, seed=seed, rep_block=rb,
               reach=rate(0 if A is None else A['th'].size, reps), design=dsum)
    if A is None or A['th'].size == 0:
        out['empty'] = True
        return out
    by_lam, mean, tt = counts_from_records(A, reps)
    out['grid'] = list(GRID3)
    out['by_lam'] = by_lam
    out['mean'] = mean
    out['tail_trades_mean'] = tt
    return out


def combine(parts, plan, idx, g):
    """Combine independent streams (CONFIRM): same arithmetic as V2 `combine`."""
    comb = dict(plan=plan, idx=idx, g=g, reps=sum(x['reps'] for x in parts), seed=[x['seed'] for x in parts],
                rep_block=parts[0]['rep_block'], combined_streams=True)
    comb['reach'] = rate(sum(x['reach']['k'] for x in parts), comb['reps'])
    comb['design'] = {k: sum(x['design'][k] for x in parts) for k in parts[0]['design']}
    ok = [x for x in parts if 'by_lam' in x]
    if not ok:
        comb['empty'] = True
        return comb
    comb['grid'] = list(GRID3)
    comb['by_lam'] = {k: [sum(x['by_lam'][k][i] for x in ok) for i in range(len(GRID3))] for k in ok[0]['by_lam']}
    tot = max(1, sum(x['reach']['k'] for x in ok))
    comb['mean'] = {k: round(sum(x['mean'][k] * x['reach']['k'] for x in ok) / tot, 5) for k in ok[0]['mean']}
    return comb
