"""Calibration du moteur de risque: distribution prédictive des rendements
NDX à 21 jours sous variance HAR-X, évaluée en walk-forward sur fenêtres
mensuelles NON chevauchantes (tests Kupiec/Christoffersen valides).

Distribution prédictive: r_21d ~ mu + sigma * t_nu (standardisée),
  mu    = moyenne historique expansive du rendement 21j (drift humble)
  sigma = sqrt(prévision HAR-X convertie en unités log-rendement 21j)
  nu    = df Student estimé sur les résidus standardisés PASSÉS (expansif)

Tests: PIT (KS), Kupiec (couverture VaR 5%/1%), Christoffersen (indépendance).
"""
import numpy as np
import pandas as pd
from scipy import stats

DATA = "/home/user/Quant-Trade/data"
H = 21

fc = pd.read_parquet(f"{DATA}/vol_forecasts.parquet").dropna(subset=["target_var"])
master = pd.read_parquet(f"{DATA}/master.parquet")
lc = np.log(master["ndx_close"])
r_fwd = (lc.shift(-H) - lc).reindex(fc.index)          # rendement log 21j réalisé
sigma = np.sqrt(fc["harx"] / (252 / H)) / 100           # vol 21j en unités log-ret

d = pd.DataFrame({"r": r_fwd, "s": sigma}).dropna().iloc[::H]  # non chevauchant
n = len(d)
print(f"{n} fenêtres mensuelles non chevauchantes, "
      f"{d.index[0].date()} -> {d.index[-1].date()}")

pit = np.full(n, np.nan)
MIN0 = 36  # 3 ans de fenêtres pour amorcer mu et nu
z_hist = []
mu_run = 0.0
for i in range(n):
    if i >= MIN0:
        mu = d["r"].iloc[:i].mean()
        z_past = ((d["r"].iloc[:i] - d["r"].iloc[:i].expanding().mean().shift()
                   .fillna(0)) / d["s"].iloc[:i]).values
        # df Student par max de vraisemblance sur les z passés
        nu = max(2.5, stats.t.fit(z_past, floc=0)[0])
        z = (d["r"].iloc[i] - mu) / d["s"].iloc[i]
        scale = np.sqrt((nu - 2) / nu)  # variance unitaire
        pit[i] = stats.t.cdf(z / scale, df=nu)

p = pit[~np.isnan(pit)]
print(f"\n=== PIT (n={len(p)}) ===")
ks = stats.kstest(p, "uniform")
print(f"KS uniformité: stat={ks.statistic:.4f}, p={ks.pvalue:.3f} "
      f"({'calibré' if ks.pvalue > 0.05 else 'REJETÉ'})")
print("déciles PIT (attendu 0.10 chacun):",
      np.round(np.histogram(p, bins=10, range=(0, 1))[0] / len(p), 2))

def kupiec_christoffersen(viol, alpha):
    n, x = len(viol), viol.sum()
    pi = x / n
    if x == 0:
        lr_uc = -2 * n * np.log(1 - alpha)
    else:
        lr_uc = -2 * (np.log((1 - alpha) ** (n - x) * alpha ** x)
                      - np.log((1 - pi) ** (n - x) * pi ** x))
    p_uc = 1 - stats.chi2.cdf(lr_uc, 1)
    # indépendance (Markov ordre 1)
    v = viol.astype(int)
    n00 = ((v[:-1] == 0) & (v[1:] == 0)).sum(); n01 = ((v[:-1] == 0) & (v[1:] == 1)).sum()
    n10 = ((v[:-1] == 1) & (v[1:] == 0)).sum(); n11 = ((v[:-1] == 1) & (v[1:] == 1)).sum()
    p01 = n01 / max(n00 + n01, 1); p11 = n11 / max(n10 + n11, 1)
    ph = (n01 + n11) / (n00 + n01 + n10 + n11)
    if p01 in (0, 1) or ph in (0, 1) or n11 == 0:
        lr_ind, p_ind = 0.0, 1.0
    else:
        l0 = (n00 + n10) * np.log(1 - ph) + (n01 + n11) * np.log(ph)
        l1 = (n00 * np.log(1 - p01) + n01 * np.log(p01)
              + n10 * np.log(1 - p11) + n11 * np.log(p11))
        lr_ind = -2 * (l0 - l1)
        p_ind = 1 - stats.chi2.cdf(lr_ind, 1)
    return x, pi, p_uc, p_ind

print("\n=== VaR (queue gauche = perte du détenteur d'indice) ===")
for alpha in [0.05, 0.01]:
    viol = p < alpha
    x, pi, p_uc, p_ind = kupiec_christoffersen(viol, alpha)
    print(f"VaR {alpha:.0%}: {x} violations / {len(p)} ({pi:.1%} vs {alpha:.0%} attendu) "
          f"| Kupiec p={p_uc:.3f} | Christoffersen ind. p={p_ind:.3f}")
print("\n=== queue droite (rally: risque du VENDEUR de variance couvert) ===")
for alpha in [0.05, 0.01]:
    viol = p > 1 - alpha
    x, pi, p_uc, p_ind = kupiec_christoffersen(viol, alpha)
    print(f"quantile {1-alpha:.0%}: {x} dépassements ({pi:.1%}) "
          f"| Kupiec p={p_uc:.3f} | Christoffersen p={p_ind:.3f}")
