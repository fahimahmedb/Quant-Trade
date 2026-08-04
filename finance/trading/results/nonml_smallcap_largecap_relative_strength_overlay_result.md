# Résultat — Force relative Russell 2000 vs S&P 500, overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RS(t)=ret21_Russell(t)-ret21_SP500(t) est dans son tercile expanding le plus bas, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 27.4% | +0.52 | +57.6% | -36.4% | +0.51 | +51.4% | -34.7% | non | non |
| NDX (40 ans) | 9760 | 33.8% | +0.49 | +3704.3% | -82.9% | +0.44 | +1586.3% | -83.3% | non | non |
| Russell 2000 | 9760 | 33.8% | +0.34 | +614.3% | -59.9% | +0.32 | +373.0% | -53.3% | non | non |
| S&P 500 | 9760 | 33.8% | +0.44 | +1135.2% | -56.8% | +0.40 | +557.7% | -55.6% | non | non |
| DAX | 6776 | 38.2% | +0.25 | +130.5% | -72.7% | +0.28 | +143.7% | -72.2% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
