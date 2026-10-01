"""ASTRA D4-C3-M1 recheck: independent re-verification of the R3 transport algebra (spec 8.5c at 4423c5c3).
SYNTHETIC / ALGEBRA ONLY. Seed 2026100177.
Checks:
 P1  Proposition 1: theta_F = E[N]/E[C] = (1 - eps_Q) theta_A + eps_Q theta_B exactly, for random epoch laws (finite mixtures of
     'worlds', each a finite list of executed trades with fee-inclusive costs and arbitrary win probabilities) and random /
     adversarial / outcome-dependent partitions; theta_B >= -1.
 T2  Theorem 2: for laws in T_H(eps, delta) (eps_Q <= eps, theta_A >= theta_W - delta) and any L_W <= theta_W,
     theta_F >= (1 - eps)(L_W - delta) - eps.
 W   Worst-case return: min N/C over fee-inclusive trades with y in {0, 0.5, 1} is exactly -1.
 C   Counterexample: cost-mass vs date / trade share.
 F   Frontier eps*(delta, tau) closed form (with the 8.5c domain guard) vs brute force on a fine grid; monotonicity;
     the unguarded max(0, .) form's failure for L_W - delta < -1.
 K   k*(H) solves eps(k) = eps* exactly.
"""
import json
import math
import numpy as np

rng = np.random.default_rng(2026100177)
out = {}


def fee(p):
    return 0.05 * p * (1 - p)        # per share, V1 fee schedule form (fee <= 0.0125 per share)


def random_world(rng):
    k = int(rng.integers(1, 121))
    ask = np.exp(rng.uniform(math.log(0.001), math.log(0.90), k))
    shares = rng.uniform(1, 60, k) * np.where(rng.random(k) < 0.3, rng.uniform(0.05, 1.0, k), 1.0)   # partial fills
    c = ask + fee(ask)                # all-in cost per share incl. fee
    C = shares * c
    pwin = rng.random(k)
    return shares, c, C, pwin


# ---------------------------------------------------------------- P1 / T2
viol_id = 0
viol_bound = 0
max_rel = 0.0
minB = 1e9
cases = 0
for it in range(60000):
    nw = int(rng.integers(1, 6))
    worlds = [random_world(rng) for _ in range(nw)]
    wp = rng.dirichlet(np.ones(nw))
    EN = sum(wp[i] * float(np.sum(w[0] * w[3] - w[2])) for i, w in enumerate(worlds))     # E[N] with N = n y - C
    EC = sum(wp[i] * float(np.sum(w[2])) for i, w in enumerate(worlds))
    thF = EN / EC
    mode = it % 3
    # partition: random / worst-return-first / single highest-cost item (per world, may differ by world = outcome-dependent)
    ENA = ECA = ENB = ECB = 0.0
    for i, (n, c, C, pw) in enumerate(worlds):
        ret = (n * pw - C) / C
        if mode == 0:
            inB = rng.random(n.size) < rng.random()
        elif mode == 1:
            q = rng.random()
            inB = ret <= np.quantile(ret, q)
        else:
            inB = np.zeros(n.size, bool); inB[np.argmax(C)] = True
        ENA += wp[i] * float(np.sum((n * pw - C)[~inB])); ECA += wp[i] * float(np.sum(C[~inB]))
        ENB += wp[i] * float(np.sum((n * pw - C)[inB])); ECB += wp[i] * float(np.sum(C[inB]))
    if ECA <= 0 or ECB <= 0:
        continue
    cases += 1
    epsQ = ECB / EC
    thA, thB = ENA / ECA, ENB / ECB
    minB = min(minB, thB)
    rhs = (1 - epsQ) * thA + epsQ * thB
    rel = abs(rhs - thF) / max(1e-12, abs(thF))
    max_rel = max(max_rel, rel if abs(thF) > 1e-9 else abs(rhs - thF))
    if abs(rhs - thF) > 1e-9 * max(1.0, abs(thF)):
        viol_id += 1
    # Theorem 2: any eps >= epsQ, any delta with theta_A >= theta_W - delta, any L_W <= theta_W, delta < 1 + L_W
    thW = thA + rng.uniform(-0.2, 0.3)          # the window value the represented part is compared with
    delta = max(0.0, thW - thA) + rng.uniform(0, 0.05)
    L_W = thW - rng.uniform(0, 0.3)
    eps = min(1.0, epsQ + rng.uniform(0, 0.2))
    if delta < 1 + L_W:
        LT = (1 - eps) * (L_W - delta) - eps
        if thF < LT - 1e-12:
            viol_bound += 1
out['P1_T2'] = dict(cases=cases, identity_violations=viol_id, max_rel_error=max_rel, theorem2_violations=viol_bound,
                    min_theta_B=round(minB, 6))

# ---------------------------------------------------------------- W: worst-case return per dollar of C
a = np.exp(rng.uniform(math.log(0.001), math.log(0.90), 300000))
c = a + fee(a)
y = rng.choice([0.0, 0.5, 1.0], a.size)
ret = (y - c) / c
out['W'] = dict(trades=int(a.size), min_N_over_C=float(ret.min()), all_ge_minus1=bool((ret >= -1 - 1e-15).all()))

# ---------------------------------------------------------------- C: counterexample (cost mass vs dates / trades)
C_cap = 5040.0
ordinary_dates, m, cost = 119, 17, 15.0
EN = ordinary_dates * m * cost * 0.10 - C_cap
EC = ordinary_dates * m * cost + C_cap
thF = EN / EC
L_W = 0.10
rows = {}
for name, e in (('dates', 1 / 120), ('trades', 96 / (96 + ordinary_dates * m)), ('cost_mass', C_cap / EC)):
    rows[name] = dict(eps=round(e, 4), bound=round((1 - e) * L_W - e, 4), valid=bool((1 - e) * L_W - e <= thF + 1e-12))
out['C'] = dict(theta_F=round(thF, 4), rows=rows)

# ---------------------------------------------------------------- F: frontier
def eps_star(L, d, t):
    return (L - d - t) / (1 + L - d) if L - d > t else 0.0


def eps_star_unguarded(L, d, t):
    return max(0.0, (L - d - t) / (1 + L - d))


grid = np.linspace(0, 1, 400001)
mism = 0
mono = 0
for _ in range(3000):
    L = rng.uniform(-0.5, 0.5); d = rng.choice([0, 0.01, 0.02, 0.05]); t = rng.choice([0, 0.02])
    LT = (1 - grid) * (L - d) - grid
    ok = grid[LT >= t - 1e-15]
    bf = ok.max() if ok.size else 0.0
    if abs(bf - eps_star(L, d, t)) > 5e-6:
        mism += 1
    if eps_star(L, d + 0.01, t) > eps_star(L, d, t) + 1e-15 or eps_star(L, d, t + 0.01) > eps_star(L, d, t) + 1e-15 \
            or eps_star(L + 0.01, d, t) < eps_star(L, d, t) - 1e-15:
        mono += 1
bad = [(L, eps_star_unguarded(L, 0, 0), eps_star(L, 0, 0)) for L in (-1.5, -1.2)]
out['F'] = dict(cases=3000, closed_form_mismatches=mism, monotonicity_violations=mono,
                unguarded_vs_guarded_at_LW_lt_minus1=[dict(L_W=L, unguarded=round(u, 4), guarded=g) for L, u, g in bad],
                sanity_LW_0p10=round(eps_star(0.10, 0, 0), 4))

# ---------------------------------------------------------------- K: k*(H)
km = 0
for _ in range(3000):
    es = rng.uniform(0, 0.5); H = rng.choice([14, 30, 60, 120]); Cd = rng.uniform(50, 3000)
    k = es * H * Cd / (C_cap * (1 - es) + es * Cd)
    e_k = k * C_cap / (k * C_cap + (H - k) * Cd)
    if abs(e_k - es) > 1e-10:
        km += 1
out['K'] = dict(cases=3000, mismatches=km)
print(json.dumps(out, indent=1))
