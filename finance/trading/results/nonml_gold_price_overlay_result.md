# Résultat — Momentum de l'or (GLD, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si GoldMom_lag(t)=log(GLD(t-1)/GLD(t-1-21)) est dans son tercile expanding le plus HAUT (hausse marquée de l'or, flight-to-quality), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 45.7% | +0.52 | +56.8% | -36.4% | +0.44 | +36.4% | -33.3% | non | non |
| NDX (40 ans) | 5422 | 31.8% | +0.62 | +995.5% | -53.7% | +0.66 | +839.8% | -43.5% | OUI | non |
| Russell 2000 | 5422 | 31.8% | +0.29 | +140.6% | -59.9% | +0.35 | +193.2% | -48.3% | OUI | OUI |
| S&P 500 | 5422 | 31.8% | +0.45 | +324.5% | -56.8% | +0.51 | +335.9% | -44.1% | OUI | OUI |
| DAX | 5472 | 32.0% | +0.40 | +278.5% | -54.8% | +0.53 | +433.1% | -39.6% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
