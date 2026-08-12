# Résultat — Demandes initiales d'allocations chômage (ICSA), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ClaimsYoY(t)=log(MA4(t)/MA4(t-52)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 62.9% | +0.52 | +79.0% | -36.4% | +0.42 | +38.5% | -28.2% | non | non |
| NDX (40 ans) | 10272 | 33.6% | +0.53 | +26208.9% | -82.9% | +0.56 | +12398.6% | -68.7% | OUI | non |
| Russell 2000 | 9781 | 33.1% | +0.34 | +1646.9% | -59.9% | +0.30 | +692.8% | -45.8% | non | non |
| S&P 500 | 14251 | 24.5% | +0.45 | +7977.0% | -56.8% | +0.50 | +6005.3% | -40.9% | OUI | non |
| DAX | 6776 | 31.5% | +0.25 | +353.5% | -72.7% | +0.20 | +186.5% | -67.3% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
