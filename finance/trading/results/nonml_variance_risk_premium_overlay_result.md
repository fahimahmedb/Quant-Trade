# Résultat — Prime de risque de variance (VIX - vol réalisée), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si VRP(t)=VIX_lag(t)-RV_lag(t) est dans son tercile expanding le plus bas, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | 32.0% | +0.52 | +56.5% | -36.4% | +0.66 | +68.3% | -23.5% | OUI | OUI |
| NDX (40 ans) | 9197 | 30.9% | +0.51 | +3540.5% | -82.9% | +0.63 | +4973.6% | -61.2% | OUI | OUI |
| Russell 2000 | 9197 | 55.2% | +0.36 | +627.5% | -59.9% | +0.28 | +223.0% | -37.9% | non | non |
| S&P 500 | 9197 | 41.2% | +0.46 | +1052.1% | -56.8% | +0.44 | +612.7% | -47.9% | non | non |
| DAX | 6756 | 25.3% | +0.24 | +116.5% | -72.7% | +0.11 | +7.3% | -68.0% | non | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
