# Résultat — Indice CBOE SKEW (risque de queue), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si SKEW_lag(t) est dans son tercile expanding le plus HAUT (risque de krach implicite le plus élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 38.3% | +0.52 | +57.6% | -36.4% | +0.20 | +10.5% | -36.6% | non | non |
| NDX (40 ans) | 9197 | 57.4% | +0.51 | +3540.5% | -82.9% | +0.42 | +1089.5% | -82.1% | non | non |
| Russell 2000 | 9197 | 57.4% | +0.36 | +627.5% | -59.9% | +0.38 | +502.9% | -51.3% | OUI | non |
| S&P 500 | 9197 | 57.4% | +0.46 | +1052.1% | -56.8% | +0.43 | +567.7% | -55.0% | non | non |
| DAX | 6776 | 65.8% | +0.25 | +130.5% | -72.7% | +0.12 | +14.4% | -72.9% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
