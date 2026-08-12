# Résultat — Corrélation cross-marché NDX-DAX, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si corr(t)=Pearson(NDX,DAX) 60j est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 35.0% | +0.52 | +79.0% | -36.4% | +0.40 | +48.0% | -32.8% | non | non |
| NDX (40 ans) | 6651 | 33.7% | +0.30 | +756.1% | -82.9% | +0.34 | +604.2% | -67.6% | OUI | non |
| Russell 2000 | 6651 | 33.7% | +0.27 | +484.9% | -59.9% | +0.31 | +372.2% | -46.9% | OUI | non |
| S&P 500 | 6651 | 33.7% | +0.34 | +452.3% | -56.8% | +0.38 | +362.3% | -44.9% | OUI | non |
| DAX | 6714 | 33.8% | +0.21 | +254.5% | -72.7% | +0.24 | +215.6% | -57.1% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
