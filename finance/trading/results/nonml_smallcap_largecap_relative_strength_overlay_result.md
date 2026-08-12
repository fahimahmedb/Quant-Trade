# Résultat — Force relative Russell 2000 vs S&P 500, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RS(t)=ret21_Russell(t)-ret21_SP500(t) est dans son tercile expanding le plus bas, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 27.4% | +0.52 | +79.0% | -36.4% | +0.51 | +67.9% | -34.7% | non | non |
| NDX (40 ans) | 9760 | 33.8% | +0.49 | +14472.1% | -82.9% | +0.44 | +4141.7% | -83.3% | non | non |
| Russell 2000 | 9760 | 33.8% | +0.34 | +1676.8% | -59.9% | +0.32 | +743.6% | -53.3% | non | non |
| S&P 500 | 9760 | 33.8% | +0.44 | +2314.8% | -56.8% | +0.40 | +919.5% | -55.6% | non | non |
| DAX | 6776 | 38.2% | +0.25 | +353.5% | -72.7% | +0.28 | +273.4% | -72.2% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
