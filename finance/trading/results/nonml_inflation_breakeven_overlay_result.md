# Résultat — Anticipations d'inflation implicites (breakeven 10 ans), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si T10YIE_lag(t) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 21.4% | +0.52 | +57.6% | -36.4% | +0.63 | +71.4% | -24.7% | OUI | OUI |
| NDX (40 ans) | 5917 | 30.4% | +0.65 | +1516.1% | -53.7% | +0.74 | +1886.1% | -51.1% | OUI | OUI |
| Russell 2000 | 5917 | 30.4% | +0.36 | +278.1% | -59.9% | +0.45 | +465.5% | -57.9% | OUI | OUI |
| S&P 500 | 5917 | 30.4% | +0.48 | +446.8% | -56.8% | +0.54 | +518.4% | -53.4% | OUI | OUI |
| DAX | 5973 | 30.5% | +0.42 | +380.5% | -54.8% | +0.46 | +411.4% | -52.6% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
