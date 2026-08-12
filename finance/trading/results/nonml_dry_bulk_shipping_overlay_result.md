# Résultat — Momentum du fret maritime en vrac sec (BDRY, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BDRYmom_lag(t)=log(BDRY(t-1)/BDRY(t-1-21)) est dans son tercile expanding le plus BAS (chute marquée du fret maritime), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 27.2% | +0.52 | +77.9% | -36.4% | +0.57 | +71.3% | -26.7% | OUI | non |
| NDX (40 ans) | 2065 | 32.4% | +0.75 | +343.7% | -35.6% | +0.85 | +279.1% | -30.7% | OUI | non |
| Russell 2000 | 2065 | 32.4% | +0.31 | +89.0% | -43.1% | +0.44 | +104.2% | -29.9% | OUI | OUI |
| S&P 500 | 2065 | 32.4% | +0.65 | +181.3% | -33.9% | +0.81 | +164.4% | -20.4% | OUI | non |
| DAX | 2084 | 32.3% | +0.44 | +99.6% | -38.8% | +0.49 | +85.9% | -21.8% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
