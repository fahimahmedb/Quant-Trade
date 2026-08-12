# Résultat — Momentum de l'or (GLD, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si GoldMom_lag(t)=log(GLD(t-1)/GLD(t-1-21)) est dans son tercile expanding le plus HAUT (hausse marquée de l'or, flight-to-quality), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 45.7% | +0.52 | +77.9% | -36.4% | +0.44 | +48.0% | -33.3% | non | non |
| NDX (40 ans) | 5422 | 31.8% | +0.62 | +1753.2% | -53.7% | +0.66 | +1259.9% | -43.5% | OUI | non |
| Russell 2000 | 5422 | 31.8% | +0.29 | +362.6% | -59.9% | +0.35 | +365.4% | -48.3% | OUI | OUI |
| S&P 500 | 5422 | 31.8% | +0.45 | +528.8% | -56.8% | +0.51 | +473.2% | -44.1% | OUI | non |
| DAX | 5472 | 32.0% | +0.40 | +499.1% | -54.8% | +0.53 | +634.3% | -39.6% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
