# Résultat — Spread de crédit corporate (Baa-10 ans), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BAA10Y_lag(t) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 20.3% | +0.52 | +79.0% | -36.4% | +0.53 | +63.8% | -31.9% | OUI | non |
| NDX (40 ans) | 10208 | 36.7% | +0.52 | +22376.6% | -82.9% | +0.60 | +11147.5% | -58.6% | OUI | non |
| Russell 2000 | 9781 | 40.8% | +0.34 | +1646.9% | -59.9% | +0.34 | +707.2% | -39.5% | OUI | non |
| S&P 500 | 10208 | 36.7% | +0.48 | +3483.9% | -56.8% | +0.55 | +2115.6% | -37.1% | OUI | non |
| DAX | 6776 | 28.5% | +0.25 | +353.5% | -72.7% | +0.40 | +520.4% | -48.8% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
