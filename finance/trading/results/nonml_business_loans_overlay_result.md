# Résultat — Croissance des prêts commerciaux et industriels US (BUSLOANS, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BusLoanGrowth(t)=log(BUSLOANS(t)/BUSLOANS(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 26.3% | +0.52 | +57.6% | -36.4% | +0.45 | +42.5% | -36.4% | non | non |
| NDX (40 ans) | 10272 | 39.2% | +0.53 | +6599.5% | -82.9% | +0.52 | +3772.5% | -75.5% | non | non |
| Russell 2000 | 9781 | 36.9% | +0.34 | +602.0% | -59.9% | +0.32 | +416.6% | -59.9% | non | non |
| S&P 500 | 14251 | 40.3% | +0.45 | +3369.2% | -56.8% | +0.45 | +2098.8% | -56.8% | non | non |
| DAX | 6776 | 36.6% | +0.25 | +130.5% | -72.7% | +0.31 | +197.4% | -54.8% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
