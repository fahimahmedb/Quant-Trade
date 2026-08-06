# Résultat — Prix du cuivre "Dr. Copper" (PCOPPUSDM, glissement annuel), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CopperGrowth(t)=log(PCOPPUSDM(t)/PCOPPUSDM(t-12)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 36.2% | +0.52 | +57.6% | -36.4% | +0.71 | +73.1% | -24.3% | OUI | OUI |
| NDX (40 ans) | 8417 | 28.8% | +0.49 | +2258.9% | -82.9% | +0.44 | +1147.2% | -81.8% | non | non |
| Russell 2000 | 8417 | 28.8% | +0.34 | +451.9% | -59.9% | +0.38 | +496.3% | -45.6% | OUI | OUI |
| S&P 500 | 8417 | 28.8% | +0.46 | +862.9% | -56.8% | +0.48 | +655.9% | -47.1% | OUI | non |
| DAX | 6776 | 42.3% | +0.25 | +130.5% | -72.7% | +0.31 | +181.9% | -66.7% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
