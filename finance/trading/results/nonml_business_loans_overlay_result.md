# Résultat — Croissance des prêts commerciaux et industriels US (BUSLOANS, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BusLoanGrowth(t)=log(BUSLOANS(t)/BUSLOANS(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 26.3% | +0.52 | +79.0% | -36.4% | +0.45 | +58.1% | -36.4% | non | non |
| NDX (40 ans) | 10272 | 39.2% | +0.53 | +26208.9% | -82.9% | +0.52 | +10533.1% | -75.5% | non | non |
| Russell 2000 | 9781 | 36.9% | +0.34 | +1646.9% | -59.9% | +0.32 | +908.8% | -59.9% | non | non |
| S&P 500 | 14251 | 40.3% | +0.45 | +7977.0% | -56.8% | +0.45 | +3955.2% | -56.8% | non | non |
| DAX | 6776 | 36.6% | +0.25 | +353.5% | -72.7% | +0.31 | +368.8% | -54.8% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
