# Résultat — Taux d'épargne des ménages US (FRED PSAVERT), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si PSAVERT_lag(t-1) est dans son tercile expanding le plus HAUT (taux d'épargne le plus élevé observé à ce jour = comportement de précaution), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 13.3% | +0.52 | +57.6% | -36.4% | +0.43 | +41.8% | -36.4% | non | non |
| NDX (40 ans) | 10272 | 17.7% | +0.53 | +6599.5% | -82.9% | +0.46 | +2856.4% | -82.9% | non | non |
| Russell 2000 | 9781 | 21.6% | +0.34 | +602.0% | -59.9% | +0.33 | +495.7% | -59.9% | non | non |
| S&P 500 | 14251 | 7.9% | +0.45 | +3369.2% | -56.8% | +0.43 | +2648.7% | -56.8% | non | non |
| DAX | 6776 | 53.2% | +0.25 | +130.5% | -72.7% | +0.38 | +259.4% | -49.7% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
