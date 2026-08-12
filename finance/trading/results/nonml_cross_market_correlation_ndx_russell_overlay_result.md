# Résultat — Corrélation cross-marché NDX-Russell 2000 (domestique), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si corr(t)=Pearson(NDX,Russell 2000) 60j est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 36.9% | +0.52 | +79.0% | -36.4% | +0.64 | +70.5% | -22.8% | OUI | non |
| NDX (40 ans) | 9721 | 36.6% | +0.54 | +22519.6% | -82.9% | +0.56 | +7831.7% | -73.5% | OUI | non |
| Russell 2000 | 9721 | 36.6% | +0.40 | +2671.5% | -59.9% | +0.39 | +971.6% | -48.3% | non | non |
| S&P 500 | 9721 | 36.6% | +0.51 | +3254.6% | -56.8% | +0.52 | +1357.6% | -49.6% | OUI | non |
| DAX | 6776 | 32.1% | +0.25 | +353.5% | -72.7% | +0.19 | +148.3% | -68.6% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
