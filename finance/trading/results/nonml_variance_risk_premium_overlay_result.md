# Résultat — Prime de risque de variance (VIX - vol réalisée), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si VRP(t)=VIX_lag(t)-RV_lag(t) est dans son tercile expanding le plus bas, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | 32.0% | +0.52 | +77.6% | -36.4% | +0.66 | +83.7% | -23.5% | OUI | OUI |
| NDX (40 ans) | 9197 | 30.9% | +0.51 | +12855.1% | -82.9% | +0.63 | +10784.8% | -61.2% | OUI | non |
| Russell 2000 | 9197 | 55.2% | +0.36 | +1636.8% | -59.9% | +0.28 | +416.4% | -37.9% | non | non |
| S&P 500 | 9197 | 41.2% | +0.46 | +1988.3% | -56.8% | +0.44 | +947.7% | -47.9% | non | non |
| DAX | 6756 | 25.3% | +0.24 | +325.5% | -72.7% | +0.11 | +72.7% | -68.0% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
