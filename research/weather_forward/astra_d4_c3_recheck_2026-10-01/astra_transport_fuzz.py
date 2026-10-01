"""ASTRA D4-C3 recheck: cost-mass transport algebra, worst-case loss, frontier and k*(H) fuzz. Deterministic seeds.
Epoch law Q = finite mixture of 'worlds'; each world is a list of executed trades (shares n, all-in cost C incl. fee).
theta_F = E_Q[N]/E_Q[C] computed exactly (N = n p - C in expectation given the world's win probabilities p)."""
import json, math
import numpy as np
rng = np.random.default_rng(2026100101)
out = {}

def world(rng, K):
    a = np.exp(rng.uniform(np.log(0.001), np.log(0.90), K))              # best ask
    notional = np.where(rng.random(K) < 0.5, 50.0, rng.uniform(0.01, 50.0, K))   # partial / thin / full fills
    n = notional / a
    fee = n * 0.05 * a * (1 - a)
    C = notional + fee
    p = rng.random(K) ** rng.choice([0.2, 1, 5])                          # arbitrary true win probabilities
    return n, C, p

# 1. Proposition 1 exactness + Theorem 2 implication over random mixtures and adversarial partitions
viol_id = viol_bound = checked = 0; maxerr = 0.0; minthB = 9
for it in range(20000):
    M = rng.integers(1, 6); pis = rng.dirichlet(np.ones(M))
    worlds = [world(rng, rng.integers(1, 120)) for _ in range(M)]
    EN = EC = ENA = ECA = ENB = ECB = 0.0
    mode = rng.choice(['random', 'worst', 'cap_date'])
    for pi, (n, C, p) in zip(pis, worlds):
        N = n * p - C
        if mode == 'random': B = rng.random(n.size) < rng.random()
        elif mode == 'worst': B = (N / C) < np.quantile(N / C, rng.random())       # adversary takes the worst trades
        else: B = np.zeros(n.size, bool); B[np.argmax(C)] = True                    # one high-cost item
        EN += pi * N.sum(); EC += pi * C.sum()
        ENA += pi * N[~B].sum(); ECA += pi * C[~B].sum(); ENB += pi * N[B].sum(); ECB += pi * C[B].sum()
    if ECA <= 0 or ECB <= 0: continue
    thF = EN / EC; epsQ = ECB / EC; thA = ENA / ECA; thB = ENB / ECB
    err = abs(thF - ((1 - epsQ) * thA + epsQ * thB)); maxerr = max(maxerr, err / max(1, abs(thF)))
    minthB = min(minthB, thB)
    viol_id += err > 1e-9 * max(1, abs(thF))
    # random source quantities with L_W <= theta_W and premise theta_A >= theta_W - delta
    for _ in range(5):
        delta = rng.choice([0, 0.01, 0.02, 0.05, rng.uniform(0, 0.5)])
        thW = thA + delta - rng.exponential(0.05)                          # premise holds by construction
        LW = thW - rng.exponential(0.05)
        eps = min(1.0, epsQ + rng.exponential(0.02) * rng.integers(0, 2))   # eps >= eps_Q (premise T1)
        if LW - delta <= -1: continue
        LT = (1 - eps) * (LW - delta) - eps
        checked += 1; viol_bound += thF < LT - 1e-12
out['prop1_theorem2'] = dict(cases=checked, identity_violations=int(viol_id), max_rel_identity_error=maxerr,
                             bound_violations=int(viol_bound), min_theta_B=round(minthB, 6))

# 2. Worst-case loss per unit of C (exchange-level N = payout - C): exhaustive over payouts y in {0, 0.5, 1}
mn = 9
for _ in range(200000):
    a = math.exp(rng.uniform(math.log(0.001), math.log(0.999))); notional = rng.uniform(0.0001, 50)
    n = notional / a; C = notional + n * 0.05 * a * (1 - a); y = rng.choice([0, 0.5, 1])
    mn = min(mn, (n * y - C) / C)
out['worst_return_per_C'] = mn

# 3. Trade-count vs cost-mass counterexample (the C3 lever)
H, m, Cord, Ccap = 120, 17, 15.0, 96 * 52.5
ordN = H * m * Cord * 0.10                       # ordinary dates earn +0.10 per dollar
k = 1                                            # one adverse date at the cap, all legs lose
C_tot = (H - k) * m * Cord + k * Ccap
N_tot = (H - k) * m * Cord * 0.10 - k * Ccap
thF = N_tot / C_tot
eps_trades = k * 96 / ((H - k) * m + k * 96); eps_dates = k / H; eps_cost = k * Ccap / C_tot
LW = 0.10
out['count_vs_cost'] = dict(theta_F=round(thF, 5), eps_dates=round(eps_dates, 5), eps_trades=round(eps_trades, 5),
                            eps_cost=round(eps_cost, 5),
                            bound_with_eps_dates=round((1 - eps_dates) * LW - eps_dates, 5),
                            bound_with_eps_trades=round((1 - eps_trades) * LW - eps_trades, 5),
                            bound_with_eps_cost=round((1 - eps_cost) * LW - eps_cost, 5))

# 4. Frontier closed form vs brute force + monotonicity
bad_form = bad_mono = out_dom = 0
grid = np.linspace(0, 1, 200001)
for _ in range(3000):
    LW = rng.uniform(-0.9, 0.6); d = rng.uniform(0, 0.3); tau = rng.choice([0.0, 0.02, 0.05, 0.08, 0.10])
    x = LW - d
    form = max(0.0, (x - tau) / (1 + x)) if x > -1 else 0.0
    ok = (1 - grid) * x - grid >= tau
    brute = grid[ok].max() if ok.any() else 0.0
    bad_form += abs(form - brute) > 1e-5
    # monotone: increasing d, tau never increases eps*; L_T decreasing in eps
    f2 = max(0.0, (x - 0.01 - tau) / (1 + x - 0.01)) if x - 0.01 > -1 else 0.0
    f3 = max(0.0, (x - tau - 0.01) / (1 + x)) if x > -1 else 0.0
    v = (f2 > form + 1e-12) or (f3 > form + 1e-12) or np.any(np.diff((1 - grid[::1000]) * x - grid[::1000]) > 1e-12)
    if x > -1: bad_mono += v
    else: out_dom += 1
out['frontier'] = dict(cases=3000, closed_form_mismatches=int(bad_form), monotonicity_violations_in_domain=int(bad_mono),
                       out_of_domain_cases_LW_minus_delta_le_minus1=out_dom,
                       note='for L_W - delta <= -1 the slope of L_T in eps is >= 0; spec Theorem 2 requires delta < 1 + L_W and the frontier formula returns 0 there')

# 5. k*(H) vs brute force (real-valued solution of eps(k) = eps*)
bad_k = 0
for _ in range(3000):
    e = rng.uniform(0.0001, 0.5); Hh = rng.choice([14, 30, 60, 120]); Cb = rng.uniform(50, 5000)
    ks = e * Hh * Cb / (Ccap * (1 - e) + e * Cb)
    epsk = ks * Ccap / (ks * Ccap + (Hh - ks) * Cb)
    bad_k += abs(epsk - e) > 1e-9
out['k_star'] = dict(cases=3000, mismatches=int(bad_k))
print(json.dumps(out, indent=1))
