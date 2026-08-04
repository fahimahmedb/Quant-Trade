# Résultat — Corrélation cross-marché NDX-DAX, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si corr(t)=Pearson(NDX,DAX) 60j est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 35.0% | +0.52 | +57.6% | -36.4% | +0.40 | +34.5% | -32.8% | non | non |
| NDX (40 ans) | 6651 | 33.7% | +0.30 | +225.5% | -82.9% | +0.34 | +279.3% | -67.6% | OUI | OUI |
| Russell 2000 | 6651 | 33.7% | +0.27 | +166.1% | -59.9% | +0.31 | +188.8% | -46.9% | OUI | OUI |
| S&P 500 | 6651 | 33.7% | +0.34 | +237.6% | -56.8% | +0.38 | +241.1% | -44.9% | OUI | OUI |
| DAX | 6714 | 33.8% | +0.21 | +81.5% | -72.7% | +0.24 | +107.5% | -57.1% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
