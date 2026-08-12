# Résultat — Positionnement spéculatif net CFTC (COT, NASDAQ-100), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si NetPctSpéc_lag(t) est dans son tercile expanding le plus HAUT (positionnement spéculatif net-long le plus extrême, trade « crowded »), `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 5j + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 44.6% | +0.52 | +79.0% | -36.4% | +0.31 | +33.4% | -35.7% | non | non |
| NDX (40 ans) | 4038 | 22.7% | +0.82 | +1456.2% | -35.6% | +0.80 | +1185.4% | -35.6% | non | non |
| Russell 2000 | 4038 | 22.7% | +0.41 | +347.2% | -43.1% | +0.43 | +332.2% | -38.8% | OUI | non |
| S&P 500 | 4038 | 22.7% | +0.69 | +574.8% | -33.9% | +0.70 | +526.6% | -29.9% | OUI | non |
| DAX | 4073 | 22.8% | +0.44 | +298.1% | -38.8% | +0.46 | +282.5% | -36.7% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
