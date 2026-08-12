# Résultat — Indice CBOE SKEW (risque de queue), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si SKEW_lag(t) est dans son tercile expanding le plus HAUT (risque de krach implicite le plus élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 38.3% | +0.52 | +79.0% | -36.4% | +0.20 | +23.2% | -36.6% | non | non |
| NDX (40 ans) | 9197 | 57.4% | +0.51 | +12855.1% | -82.9% | +0.42 | +2803.7% | -82.1% | non | non |
| Russell 2000 | 9197 | 57.4% | +0.36 | +1636.8% | -59.9% | +0.38 | +913.4% | -51.3% | OUI | non |
| S&P 500 | 9197 | 57.4% | +0.46 | +1988.3% | -56.8% | +0.43 | +882.0% | -55.0% | non | non |
| DAX | 6776 | 65.8% | +0.25 | +353.5% | -72.7% | +0.12 | +77.3% | -72.9% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
