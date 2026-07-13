"""Itération v2 du moteur de risque: innovations skew-t de Hansen (1994)
au lieu de la Student symétrique. Même protocole walk-forward non chevauchant.
"""
import numpy as np
import pandas as pd
from scipy import stats, optimize

DATA = "/home/user/Quant-Trade/data"
H = 21

# --- skew-t de Hansen (1994): densité et CDF standardisées ---
def _abc(eta, lam):
    c = np.exp(stats.gamma.logpdf(0, 1))  # placeholder évité: calcul direct
    from scipy.special import gammaln
    logc = gammaln((eta + 1) / 2) - gammaln(eta / 2) - 0.5 * np.log(np.pi * (eta - 2))
    c = np.exp(logc)
    a = 4 * lam * c * (eta - 2) / (eta - 1)
    b = np.sqrt(1 + 3 * lam ** 2 - a ** 2)
    return a, b, c

def skewt_logpdf(z, eta, lam):
    a, b, c = _abc(eta, lam)
    denom = np.where(z < -a / b, 1 - lam, 1 + lam)
    core = 1 + ((b * z + a) / denom) ** 2 / (eta - 2)
    return np.log(b * c) - (eta + 1) / 2 * np.log(core)

def skewt_cdf(z, eta, lam):
    a, b, c = _abc(eta, lam)
    s = np.sqrt(eta / (eta - 2))
    z = np.asarray(z, dtype=float)
    lo = (1 - lam) * stats.t.cdf(s * (b * z + a) / (1 - lam), df=eta)
    hi = (1 + lam) * stats.t.cdf(s * (b * z + a) / (1 + lam), df=eta) - lam
    return np.where(z < -a / b, lo, hi)

def fit_skewt(z):
    """MLE (loc, scale, eta, lam) sur résidus z."""
    def nll(p):
        loc, lsc, leta, alam = p
        eta = 2.1 + np.exp(leta)
        lam = np.tanh(alam)
        u = (z - loc) / np.exp(lsc)
        return -(skewt_logpdf(u, eta, lam).sum() - len(z) * lsc)
    res = optimize.minimize(nll, x0=[0.0, 0.0, np.log(6.0), 0.0],
                            method="Nelder-Mead",
                            options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-5})
    loc, lsc, leta, alam = res.x
    return loc, np.exp(lsc), 2.1 + np.exp(leta), np.tanh(alam)

fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet").dropna(subset=["target_var"])
master = pd.read_parquet(f"{DATA}/master.parquet")
lc = np.log(master["ndx_close"])
r_fwd = (lc.shift(-H) - lc).reindex(fc.index)
sigma = np.sqrt(fc["harx"] / (252 / H)) / 100

d = pd.DataFrame({"r": r_fwd, "s": sigma}).dropna().iloc[::H]
n = len(d)
MIN0 = 36
pit = np.full(n, np.nan)
params_last = None
for i in range(n):
    if i < MIN0:
        continue
    mu = d["r"].iloc[:i].mean()
    z_past = ((d["r"].iloc[:i] - mu) / d["s"].iloc[:i]).values
    if (i - MIN0) % 12 == 0 or params_last is None:  # re-fit annuel (coût MLE)
        params_last = fit_skewt(z_past)
    loc, sc, eta, lam = params_last
    z = (d["r"].iloc[i] - mu) / d["s"].iloc[i]
    pit[i] = skewt_cdf((z - loc) / sc, eta, lam)

p = pit[~np.isnan(pit)]
print(f"n={len(p)} fenêtres | derniers params skew-t: loc={loc:+.3f}, scale={sc:.3f}, "
      f"eta={eta:.1f}, lambda={lam:+.3f}")
ks = stats.kstest(p, "uniform")
print(f"\nPIT KS: stat={ks.statistic:.4f}, p={ks.pvalue:.3f} "
      f"({'calibré' if ks.pvalue > 0.05 else 'REJETÉ'})")
print("déciles:", np.round(np.histogram(p, bins=10, range=(0, 1))[0] / len(p), 2))

def kupiec_christoffersen(viol, alpha):
    n, x = len(viol), int(viol.sum())
    pi = x / n
    if x == 0:
        lr_uc = -2 * n * np.log(1 - alpha)
    else:
        lr_uc = -2 * (np.log((1 - alpha) ** (n - x) * alpha ** x)
                      - np.log((1 - pi) ** (n - x) * pi ** x))
    p_uc = 1 - stats.chi2.cdf(lr_uc, 1)
    v = viol.astype(int)
    n00 = ((v[:-1] == 0) & (v[1:] == 0)).sum(); n01 = ((v[:-1] == 0) & (v[1:] == 1)).sum()
    n10 = ((v[:-1] == 1) & (v[1:] == 0)).sum(); n11 = ((v[:-1] == 1) & (v[1:] == 1)).sum()
    p01 = n01 / max(n00 + n01, 1); p11 = n11 / max(n10 + n11, 1)
    ph = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
    if p01 in (0, 1) or ph in (0, 1) or n11 == 0:
        p_ind = 1.0
    else:
        l0 = (n00 + n10) * np.log(1 - ph) + (n01 + n11) * np.log(ph)
        l1 = (n00 * np.log(1 - p01) + n01 * np.log(p01)
              + n10 * np.log(1 - p11) + n11 * np.log(p11))
        p_ind = 1 - stats.chi2.cdf(-2 * (l0 - l1), 1)
    return x, pi, p_uc, p_ind

print("\nVaR queue gauche:")
for alpha in [0.05, 0.01]:
    x, pi, p_uc, p_ind = kupiec_christoffersen(p < alpha, alpha)
    print(f"  {alpha:.0%}: {x} violations ({pi:.1%}) | Kupiec p={p_uc:.3f} "
          f"| Christoffersen p={p_ind:.3f}")
print("queue droite:")
for alpha in [0.05, 0.01]:
    x, pi, p_uc, p_ind = kupiec_christoffersen(p > 1 - alpha, alpha)
    print(f"  {1-alpha:.0%}: {x} dépassements ({pi:.1%}) | Kupiec p={p_uc:.3f} "
          f"| Christoffersen p={p_ind:.3f}")
