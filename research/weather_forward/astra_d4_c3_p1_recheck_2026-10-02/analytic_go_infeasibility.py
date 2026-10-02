"""Analytic cross-check (no simulation): can ANY CORE price distribution in [0.04, 0.89] (R* cannot buy at ask >= 0.90) with equal capital per
trade and m_bar <= 96 trades per date satisfy BOTH GO clauses of spec 10.3 at Z_EFF = 7.2 / SE_KAPPA_CEILING = 0.005?
SE0_theta^2 = g_bar * DEFF(m)/(120 m), g = (1-c)/c ;  SE0_kappa^2 = f_bar * DEFF(m)/(120 m_core), f = c(1-c) ;  DEFF(m) = 1.5 (1 + 0.03 (m-1)).
Tail (c < 0.04) trades add to g_bar and to DEFF's m but not to m_core: they cannot help.  Mixture grid search over two-point mixtures
plus the exact asymptote.  Writes out_analytic_go_infeasibility.txt"""
import numpy as np, math
cs = np.concatenate([np.arange(0.04, 0.90, 0.005), [0.89]])
f = cs * (1 - cs); g = (1 - cs) / cs
best = (1e9,)
for m in (8, 12, 17, 25, 35, 55, 80, 96):
    deff = 1.5 * (1 + 0.03 * (m - 1))
    for i, c1 in enumerate(cs):
        for j, c2 in enumerate(cs):
            for w in np.arange(0, 1.0001, 0.05):
                fb = w * f[i] + (1 - w) * f[j]; gb = w * g[i] + (1 - w) * g[j]
                sk = math.sqrt(fb * deff / (120 * m)); st = math.sqrt(gb * deff / (120 * m))
                # normalised violation of the joint clause: max(7.2 st / 0.10, sk / 0.005)
                v = max(7.2 * st / 0.10, sk / 0.005)
                if v < best[0]:
                    best = (v, m, c1, c2, w, sk, st, 7.2 * st)
print('min over two-point CORE mixtures, m<=96, of max(7.2*SE0_theta/0.10, SE0_kappa/0.005) = %.3f  (GO needs <= 1)' % best[0])
print('  at m=%d, c1=%.3f, c2=%.3f, w=%.2f: SE0_kappa=%.4f, SE0_theta=%.4f, 7.2*SE0_theta=%.3f' % best[1:])
print('exact asymptote m->inf, point mass 0.89: SE0_kappa -> %.5f (> 0.005)' % (math.sqrt(0.89 * 0.11 * 0.045 / 120)))
print('SE0_kappa needs mean c(1-c) <= %.4f at the asymptotic slope 0.045; c(1-c) >= %.4f for every c in [0.0725, 0.89]' % (0.005 ** 2 * 120 / 0.045, 0.89 * 0.11))
for m in (96,):
    deff = 1.5 * (1 + 0.03 * (m - 1))
    print('m=96 point mass 0.89: SE0_kappa = %.5f, SE0_theta = %.5f, theta_PCE = %.2f' % (math.sqrt(0.89 * 0.11 * deff / (120 * m)), math.sqrt(0.11 / 0.89 * deff / (120 * m)), math.ceil(round(100 * 7.2 * math.sqrt(0.11 / 0.89 * deff / (120 * m)), 9)) / 100))
