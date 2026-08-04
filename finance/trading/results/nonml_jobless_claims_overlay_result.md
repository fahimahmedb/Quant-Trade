# Résultat — Demandes initiales d'allocations chômage (ICSA), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ClaimsYoY(t)=log(MA4(t)/MA4(t-52)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 62.9% | +0.52 | +57.6% | -36.4% | +0.42 | +30.4% | -28.2% | non | non |
| NDX (40 ans) | 10272 | 33.6% | +0.53 | +6599.5% | -82.9% | +0.56 | +4882.6% | -68.7% | OUI | non |
| Russell 2000 | 9781 | 33.1% | +0.34 | +602.0% | -59.9% | +0.30 | +328.9% | -45.8% | non | non |
| S&P 500 | 14251 | 24.5% | +0.45 | +3369.2% | -56.8% | +0.50 | +3203.2% | -40.9% | OUI | non |
| DAX | 6776 | 31.5% | +0.25 | +130.5% | -72.7% | +0.20 | +75.2% | -67.3% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
