# Résultat — Indice OVX (volatilité implicite pétrolière), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si OVX_lag(t) est dans son tercile expanding le plus HAUT (stress pétrolier implicite le plus élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 28.6% | +0.52 | +79.0% | -36.4% | +0.50 | +60.0% | -26.0% | non | non |
| NDX (40 ans) | 4822 | 34.8% | +0.63 | +1473.3% | -53.7% | +0.73 | +887.4% | -33.7% | OUI | non |
| Russell 2000 | 4822 | 34.8% | +0.26 | +260.6% | -59.9% | +0.26 | +147.5% | -40.8% | non | non |
| S&P 500 | 4822 | 34.8% | +0.42 | +403.6% | -56.8% | +0.51 | +279.2% | -37.1% | OUI | non |
| DAX | 4862 | 34.9% | +0.30 | +237.9% | -54.8% | +0.33 | +173.5% | -37.0% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
