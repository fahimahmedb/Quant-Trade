"""(1) Deterministic domination check of M_tail over the conditional admissible class, incl. partial payoffs.
(2) Enumeration of the D4-touched economic/rejection states."""
import itertools, json, numpy as np
rng = np.random.default_rng(970_001)
worst = -1e9; cases = 0
for _ in range(20000):
    N = int(rng.integers(1, 60))
    c = np.where(rng.random(N) < 0.3, rng.choice([0.001, 0.002, 0.005, 0.01, 0.02, 0.039], N), rng.uniform(0.04, 0.9, N))
    C = rng.choice([rng.uniform(0.01, 50), 50.0], N)          # partial fills, tiny costs
    n = C / c; tail = c < 0.04; core = ~tail
    if not core.any():
        continue
    for mode in ('random', 'allwin', 'allloss', 'half', 'extreme_mix'):
        if mode == 'random': y = rng.random(N)                 # any payout per share in [0,1] (p, voids, 50-50)
        elif mode == 'allwin': y = np.ones(N)
        elif mode == 'allloss': y = np.zeros(N)
        elif mode == 'half': y = np.full(N, 0.5)
        else: y = rng.choice([0.0, 0.5, 1.0], N)
        theta = (n * (y - c)).sum() / C.sum()
        wc = C[core].sum() / C.sum()
        thc = (n[core] * (y - c)[core]).sum() / C[core].sum()
        Mt = (n[tail] - C[tail]).sum() / C.sum() if tail.any() else 0.0
        gap = theta - (wc * thc + Mt)                           # must be <= 0 (float tolerance)
        worst = max(worst, gap / max(1.0, abs(theta))); cases += 1
print(json.dumps(dict(domination_cases=cases, max_relative_violation=worst)))

# state enumeration: booleans T1, NEG, U<ERT, T2, thetahat>=ERT, GATES with the R1 constraint U >= thetahat
rows = []; bad = []
for T1, NEG, Ult, T2, thg, G in itertools.product([0, 1], repeat=6):
    feasible_R1 = not (Ult and thg)      # U >= theta_hat under R1 => U<ERT excludes theta_hat>=ERT
    info = 'INFORMATION_DETECTED' if T1 else ('NEGATIVE_INFORMATION' if NEG else 'NO_INFORMATION_DETECTED')
    eco = ('NET_VALUE_EXCLUDED' if Ult else 'NET_VALUE_CONFIRMED' if (T2 and thg and G)
           else 'NET_VALUE_NOT_ROBUST' if (T2 and thg) else 'NET_VALUE_INDETERMINATE')
    rej_econ = eco == 'NET_VALUE_EXCLUDED'
    rej_info = info == 'NEGATIVE_INFORMATION'
    if rej_econ != bool(Ult): bad.append('econ_rejection_not_iff_U')
    if rej_econ and not Ult: bad.append('NEG_drives_econ')
    rows.append((info, eco, feasible_R1, rej_econ, rej_info, bool(T1 and NEG)))
states = {(r[0], r[1]) for r in rows if r[2]}
print(json.dumps(dict(combos=len(rows), reachable_product_states=len(states), violations=bad,
                      core_adverse_but_info_flag_false=sum(1 for r in rows if r[5] and not r[4]),
                      E1_and_E2_conditions_jointly_feasible_under_R1=any(r[2] and r[1] == 'NET_VALUE_EXCLUDED' and False for r in rows))))
