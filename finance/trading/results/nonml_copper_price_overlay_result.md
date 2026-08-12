# Résultat — Prix du cuivre "Dr. Copper" (PCOPPUSDM, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CopperGrowth(t)=log(PCOPPUSDM(t)/PCOPPUSDM(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 36.2% | +0.52 | +79.0% | -36.4% | +0.71 | +87.3% | -24.3% | OUI | OUI |
| NDX (40 ans) | 8417 | 28.8% | +0.49 | +7757.3% | -82.9% | +0.44 | +3071.6% | -81.8% | non | non |
| Russell 2000 | 8417 | 28.8% | +0.34 | +1188.8% | -59.9% | +0.38 | +967.1% | -45.6% | OUI | non |
| S&P 500 | 8417 | 28.8% | +0.46 | +1597.5% | -56.8% | +0.48 | +1010.4% | -47.1% | OUI | non |
| DAX | 6776 | 42.3% | +0.25 | +353.5% | -72.7% | +0.31 | +330.4% | -66.7% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
