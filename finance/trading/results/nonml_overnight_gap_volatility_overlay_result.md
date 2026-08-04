# Résultat — Volatilité du gap d'ouverture (composante overnight isolée), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si GapVol_lag(t)=sqrt(max(CCVar_roll-ParkVar_roll,0)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1230 | 30.8% | +0.52 | +56.5% | -36.4% | +0.73 | +77.8% | -20.4% | OUI | OUI |
| NDX (40 ans) | 10252 | 39.9% | +0.53 | +6416.7% | -82.9% | +0.56 | +2947.5% | -69.8% | OUI | non |
| Russell 2000 | 9761 | 47.4% | +0.34 | +610.3% | -59.9% | +0.30 | +265.0% | -41.8% | non | non |
| S&P 500 | 14231 | 69.5% | +0.46 | +3696.8% | -56.8% | +0.42 | +790.3% | -42.0% | non | non |
| DAX | 6756 | 32.5% | +0.24 | +116.5% | -72.7% | +0.19 | +58.8% | -63.9% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
