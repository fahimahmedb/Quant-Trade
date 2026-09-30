"""ASTRA D4-C2 recheck engine (2026-09-30). SYNTHETIC ONLY. Independent of the Architect's run-E code.

Prospective process: 14 OP dates + 120 window dates. Ordinary dates: Poisson(m) executed R* trades at 48 gamma(2)
stations (<= 96 events/date), CORE c ~ U(0.35, 0.80), p = c (1 + th0), capital C ~ cap model. Rare 'special' dates
(prob eta, independent): a jackpot (all K trades are c_t legs with win prob p_t) or a catastrophe (K trades, all lose).
theta_P is computed exactly from the generating process. Outcomes: latent copula (date, station, cell).
Labels follow spec @e45d2ce7 section 17 exactly (R2), plus the retired R1 E1 rule for the C2 reproduction."""
import math, json, sys
import numpy as np
from scipy import sparse, stats
from scipy.special import ndtr
ERT, CUT, Z80 = 0.02, 0.04, 2.4865
S, OPD, WD = 48, 14, 120
TQ = stats.t.ppf

def cap(rng, n, model):
    if model == 'full': return np.full(n, 50.0)
    if model == 'partial': return np.where(rng.random(n) < 0.68, 50.0, rng.uniform(10, 50, n))
    if model == 'thin': return rng.uniform(5, 25, n)      # ordinary fills thin; special dates fully filled

def draw(rng, sc):
    D = OPD + WD
    act = rng.gamma(2.0, 1.0, S); act /= act.sum()
    special = rng.random(D) < sc.get('eta', 0.0)
    if sc.get('special_in_window_only'): special[:OPD] = False
    cnt = rng.poisson(sc['m'], D)
    cnt[special] = sc.get('K', 96)
    date = np.repeat(np.arange(D), cnt); N = date.size
    sp = special[date]
    st = rng.choice(S, N, p=act)
    if sc.get('special_station_one'):                    # station-comonotone: special trades all at one station
        st[sp] = 0
    c = rng.uniform(0.35, 0.80, N)
    p = np.minimum(1, c * (1 + sc['th0']))
    C = cap(rng, N, sc.get('cap', 'full'))
    kind = sc.get('kind')
    if kind == 'jackpot':
        c[sp] = sc['c_t']; p[sp] = sc['p_t']
    elif kind == 'catastrophe':
        p[sp] = 0.0; C[sp] = 50.0
    elif kind == 'rare_tail_trade':                       # per-trade rare tail arrivals (Astra C2 S1 geometry)
        t = rng.random(N) < sc['r']; c[t] = sc['c_t']; p[t] = sc['p_t']
    d = dict(date=date, st=st, c=c, p=p, C=C, n=C / c, sp=sp)
    op = {k: v[date < OPD] for k, v in d.items()}
    w = {k: v[date >= OPD] for k, v in d.items()}; w['date'] = w['date'] - OPD
    return w, op

def theta_P_mc(sc, rng, reps=400):
    """Exact-in-expectation theta_P by Monte Carlo over the generating process (expected N / expected C)."""
    num = den = 0.0
    for _ in range(reps):
        w, op = draw(rng, sc)
        for x in (w, op):
            num += (x['n'] * (x['p'] - x['c'])).sum(); den += x['C'].sum()
    return num / den

def _ind(g):
    _, gi = np.unique(g, return_inverse=True); G = gi.max() + 1
    return sparse.csr_matrix((np.ones(gi.size), (np.arange(gi.size), gi)), shape=(gi.size, G)), G

def cr(e, blk, st, Q):
    V, G = [], []
    for g in (blk, st, blk * 1000 + st):
        M, n = _ind(g); s = M.T @ e
        V.append(n / (n - 1) * (s ** 2).sum() / Q ** 2); G.append(n)
    return math.sqrt(max(V[0], V[1], V[0] + V[1] - V[2])), min(G[0], G[1]) - 1

def ready(op):
    c, C, st = op['c'], op['C'], op['st']
    mbar = c.size / OPD
    s2 = c.size * (C ** 2 * (1 - c) / c).sum() / C.sum() ** 2
    deff = 1.5 * (1 + 0.03 * (mbar - 1)); se0 = math.sqrt(s2 * deff / (120 * mbar))
    core = c >= CUT
    se0k = math.sqrt((c[core] * (1 - c[core])).mean() * deff / (120 * core.sum() / OPD))
    k = np.bincount(st); k = k[k > 0]
    pce = math.ceil(round(100 * Z80 * se0, 9)) / 100
    return pce, bool(pce <= 0.10 and se0k <= 0.020 and k.size >= 25 and k.sum() ** 2 / (k ** 2).sum() >= 15)

def outcomes(rng, w, rho):
    _, ci = np.unique(w['date'] * 1000 + w['st'], return_inverse=True)
    z = (math.sqrt(rho[0]) * rng.standard_normal(WD)[w['date']] + math.sqrt(rho[1]) * rng.standard_normal(S)[w['st']]
         + math.sqrt(rho[2]) * rng.standard_normal(ci.max() + 1)[ci] + math.sqrt(1 - sum(rho)) * rng.standard_normal(w['c'].size))
    return (ndtr(z) < w['p']).astype(float)

def labels(w, y, pce, go):
    c, C, n, date, st = w['c'], w['C'], w['n'], w['date'], w['st']
    blk = date // 5; tail = c < CUT; core = ~tail
    N = n * (y - c); th = N.sum() / C.sum()
    se, df = cr(N - th * C, blk, st, C.sum()); T2 = th - TQ(0.95, df) * se > 0
    thc = N[core].sum() / C[core].sum(); sec, dfc = cr(N[core] - thc * C[core], blk[core], st[core], C[core].sum())
    x = (y - c)[core]; k = x.mean(); sek, dfk = cr(x - k, blk[core], st[core], core.sum())
    viid = core.sum() / (core.sum() - 1) * ((x - k) ** 2).sum() / core.sum() ** 2
    cnt = np.bincount(st); cnt = cnt[cnt > 0]
    info = (np.unique(blk).size >= 12 and cnt.size >= 25 and cnt.sum() ** 2 / (cnt ** 2).sum() >= 15
            and sek <= 0.025 and sek ** 2 / viid <= 6)
    NEG = k + TQ(0.975, dfk) * sek < 0
    T1a = k - TQ(0.975, dfk) * sek > 0
    wc = C[core].sum() / C.sum()
    Mt = (n[tail] - C[tail]).sum() / C.sum() if tail.any() else 0.0
    U_W = wc * (thc + TQ(0.975, dfc) * sec) + Mt
    cc = c + np.where(c < CUT, 0.001, 0.01); g1 = ((C / cc) * (y - cc)).sum() / C.sum() > 0
    pos = np.maximum(N, 0); gross = pos.sum()
    g2 = bool(gross > 0 and (N.sum() - np.sort(N)[-5:].sum()) / C.sum() > 0
              and np.bincount(date, weights=pos).max() <= 0.25 * gross and np.bincount(st, weights=pos).max() <= 0.20 * gross)
    gates = g1 and g2
    reach = go and info
    # ---- R2 (spec @e45d2ce7, 17.2 / 17.3 / 17.5 / 17.6)
    if not reach:                      # INFORMATION_INSUFFICIENT pre-empts (GO = False means no t0: treated as not run)
        eco = 'NOT_REACHED'
    elif T2 and th >= ERT:
        eco = 'PROSPECTIVE_VALUE_CONFIRMED' if gates else 'PROSPECTIVE_VALUE_NOT_ROBUST'
    else:
        eco = 'PROSPECTIVE_VALUE_INDETERMINATE'
    rw = ('REALIZED_WINDOW_LOSS_CONFIRMED' if U_W < 0 else 'REALIZED_WINDOW_RELEVANT_VALUE_EXCLUDED' if U_W < ERT
          else 'REALIZED_WINDOW_LARGE_VALUE_EXCLUDED' if U_W < max(pce, ERT) else 'REALIZED_WINDOW_NOT_EXCLUDED')
    fwd = reach and eco == 'PROSPECTIVE_VALUE_CONFIRMED' and not NEG          # VALID_COMPLETE, ACCESSIBLE assumed
    # ---- retired R1 (spec @24d2342): E1 U < ERT -> NET_VALUE_EXCLUDED -> R* rejected; LARGE if U < max(PCE, ERT)
    r1_excl = reach and U_W < ERT; r1_large = reach and U_W < max(pce, ERT)
    thW = float((n * (w['p'] - c)).sum() / C.sum())
    return dict(eco=eco, rw=rw, fwd=fwd, r1_excl=r1_excl, r1_large=r1_large, reach=reach, NEG=NEG, T1a=T1a,
                U_W=U_W, thW=thW, th=th, rstar_rejected=False, n_sp=int(w['sp'].sum()))

def mc(k, n):
    p = k / n; se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    return dict(p=round(p, 4), se=round(se, 4), ci=[round(max(0, p - 1.96 * se), 4), round(min(1, p + 1.96 * se), 4)], n=n)

def run(sc, reps, seed, rho=(0.05, 0.05, 0.10)):
    rng = np.random.default_rng(seed)
    thP = sc.get('thP') or theta_P_mc(sc, np.random.default_rng(seed + 7), 300)
    K = dict(conf=0, notrob=0, indet=0, reach=0, fwd=0, r1_excl=0, r1_large=0, rw_loss=0, zero_sp=0, prospective_excl=0, rstar=0,
             rw_neg_zero_sp=0)
    for _ in range(reps):
        w, op = draw(rng, sc); pce, go = ready(op)
        o = labels(w, outcomes(rng, w, sc.get('rho', rho)), pce, go)
        K['conf'] += o['eco'] == 'PROSPECTIVE_VALUE_CONFIRMED'; K['notrob'] += o['eco'] == 'PROSPECTIVE_VALUE_NOT_ROBUST'
        K['indet'] += o['eco'] == 'PROSPECTIVE_VALUE_INDETERMINATE'; K['reach'] += o['reach']; K['fwd'] += o['fwd']
        K['r1_excl'] += o['r1_excl']; K['r1_large'] += o['r1_large']
        K['rw_loss'] += o['reach'] and o['rw'] == 'REALIZED_WINDOW_LOSS_CONFIRMED'
        K['zero_sp'] += o['n_sp'] == 0
        K['rw_neg_zero_sp'] += o['reach'] and o['n_sp'] == 0 and o['U_W'] < 0
        K['prospective_excl'] += o['eco'] not in ('PROSPECTIVE_VALUE_CONFIRMED', 'PROSPECTIVE_VALUE_NOT_ROBUST',
                                                  'PROSPECTIVE_VALUE_INDETERMINATE', 'NOT_REACHED')
        K['rstar'] += o['rstar_rejected']
    return dict(sc=sc, reps=reps, seed=seed, theta_P=round(thP, 4), **{k: mc(v, reps) for k, v in K.items()})
