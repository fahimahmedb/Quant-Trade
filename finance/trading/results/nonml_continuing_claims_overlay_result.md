# Résultat — Demandes continues d'allocations chômage (CCSA), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ClaimsContinuingYoY(t)=log(MA4(t)/MA4(t-52)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 58.7% | +0.52 | +57.6% | -36.4% | +0.52 | +43.5% | -25.6% | OUI | non |
| NDX (40 ans) | 10272 | 32.5% | +0.53 | +6599.5% | -82.9% | +0.59 | +6436.4% | -65.7% | OUI | non |
| Russell 2000 | 9781 | 36.3% | +0.34 | +602.0% | -59.9% | +0.37 | +551.4% | -46.4% | OUI | non |
| S&P 500 | 14251 | 25.1% | +0.45 | +3369.2% | -56.8% | +0.49 | +2952.4% | -38.6% | OUI | non |
| DAX | 6776 | 34.6% | +0.25 | +130.5% | -72.7% | +0.28 | +150.5% | -67.7% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
