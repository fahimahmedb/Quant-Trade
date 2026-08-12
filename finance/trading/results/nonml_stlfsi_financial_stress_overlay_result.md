# Résultat — Indice de stress financier St. Louis Fed STLFSI4, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si STLFSI4_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 30.6% | +0.52 | +79.0% | -36.4% | +0.48 | +55.4% | -32.6% | non | non |
| NDX (40 ans) | 8180 | 34.4% | +0.49 | +7188.6% | -82.9% | +0.61 | +4351.9% | -60.7% | OUI | non |
| Russell 2000 | 8180 | 34.4% | +0.33 | +1038.8% | -59.9% | +0.40 | +817.6% | -39.4% | OUI | non |
| S&P 500 | 8180 | 34.4% | +0.46 | +1498.5% | -56.8% | +0.56 | +1082.8% | -36.3% | OUI | non |
| DAX | 6776 | 21.4% | +0.25 | +353.5% | -72.7% | +0.28 | +279.7% | -65.4% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
