# Résultat — Momentum du fret maritime en vrac sec (BDRY, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si BDRYmom_lag(t)=log(BDRY(t-1)/BDRY(t-1-21)) est dans son tercile expanding le plus BAS (chute marquée du fret maritime), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 27.2% | +0.52 | +56.8% | -36.4% | +0.57 | +56.2% | -26.7% | OUI | non |
| NDX (40 ans) | 2065 | 32.4% | +0.75 | +248.8% | -35.6% | +0.85 | +226.2% | -30.7% | OUI | non |
| Russell 2000 | 2065 | 32.4% | +0.31 | +45.6% | -43.1% | +0.44 | +73.5% | -29.9% | OUI | OUI |
| S&P 500 | 2065 | 32.4% | +0.65 | +141.1% | -33.9% | +0.81 | +142.0% | -20.4% | OUI | OUI |
| DAX | 2084 | 32.3% | +0.44 | +71.3% | -38.8% | +0.49 | +68.5% | -21.8% | OUI | non |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
