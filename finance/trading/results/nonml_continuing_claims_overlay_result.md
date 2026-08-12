# Résultat — Demandes continues d'allocations chômage (CCSA), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ClaimsContinuingYoY(t)=log(MA4(t)/MA4(t-52)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 58.7% | +0.52 | +79.0% | -36.4% | +0.52 | +53.6% | -25.6% | OUI | non |
| NDX (40 ans) | 10272 | 32.5% | +0.53 | +26208.9% | -82.9% | +0.59 | +16317.8% | -65.7% | OUI | non |
| Russell 2000 | 9781 | 36.3% | +0.34 | +1646.9% | -59.9% | +0.37 | +1071.1% | -46.4% | OUI | non |
| S&P 500 | 14251 | 25.1% | +0.45 | +7977.0% | -56.8% | +0.49 | +5456.8% | -38.6% | OUI | non |
| DAX | 6776 | 34.6% | +0.25 | +353.5% | -72.7% | +0.28 | +299.6% | -67.7% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
