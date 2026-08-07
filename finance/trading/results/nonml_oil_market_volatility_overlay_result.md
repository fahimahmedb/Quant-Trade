# Résultat — Indice OVX (volatilité implicite pétrolière), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si OVX_lag(t) est dans son tercile expanding le plus HAUT (stress pétrolier implicite le plus élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 28.6% | +0.52 | +57.6% | -36.4% | +0.50 | +46.5% | -26.0% | non | non |
| NDX (40 ans) | 4822 | 34.8% | +0.63 | +854.4% | -53.7% | +0.73 | +662.7% | -33.7% | OUI | non |
| Russell 2000 | 4822 | 34.8% | +0.26 | +93.7% | -59.9% | +0.26 | +79.0% | -40.8% | non | non |
| S&P 500 | 4822 | 34.8% | +0.42 | +244.3% | -56.8% | +0.51 | +216.0% | -37.1% | OUI | non |
| DAX | 4862 | 34.9% | +0.30 | +118.6% | -54.8% | +0.33 | +115.9% | -37.0% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
