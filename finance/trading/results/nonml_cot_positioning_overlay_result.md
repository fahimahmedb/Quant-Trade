# Résultat — Positionnement spéculatif net CFTC (COT, NASDAQ-100), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si NetPctSpéc_lag(t) est dans son tercile expanding le plus HAUT (positionnement spéculatif net-long le plus extrême, trade « crowded »), `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 5j + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 44.6% | +0.52 | +57.6% | -36.4% | +0.31 | +22.1% | -35.7% | non | non |
| NDX (40 ans) | 4038 | 22.7% | +0.82 | +996.6% | -35.6% | +0.80 | +835.6% | -35.6% | non | non |
| Russell 2000 | 4038 | 22.7% | +0.41 | +196.0% | -43.1% | +0.43 | +200.2% | -38.8% | OUI | OUI |
| S&P 500 | 4038 | 22.7% | +0.69 | +431.9% | -33.9% | +0.70 | +406.3% | -29.9% | OUI | non |
| DAX | 4073 | 22.8% | +0.44 | +193.5% | -38.8% | +0.46 | +194.0% | -36.7% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
