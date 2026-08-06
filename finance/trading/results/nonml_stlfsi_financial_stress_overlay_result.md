# Résultat — Indice de stress financier St. Louis Fed STLFSI4, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si STLFSI4_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 30.6% | +0.52 | +57.6% | -36.4% | +0.48 | +42.6% | -32.6% | non | non |
| NDX (40 ans) | 8180 | 34.4% | +0.49 | +2118.1% | -82.9% | +0.61 | +2349.2% | -60.7% | OUI | OUI |
| Russell 2000 | 8180 | 34.4% | +0.33 | +389.5% | -59.9% | +0.40 | +469.6% | -39.4% | OUI | OUI |
| S&P 500 | 8180 | 34.4% | +0.46 | +810.0% | -56.8% | +0.56 | +779.8% | -36.3% | OUI | non |
| DAX | 6776 | 21.4% | +0.25 | +130.5% | -72.7% | +0.28 | +148.2% | -65.4% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
