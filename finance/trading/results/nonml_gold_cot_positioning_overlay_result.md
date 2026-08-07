# Résultat — Positionnement spéculatif net CFTC sur l'or (COT), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si NetPctSpécOr_lag(t) est dans son tercile expanding le plus HAUT (positionnement spéculatif net-long le plus extrême sur l'or, trade « crowded »), `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 10j (conservateur) + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 51.8% | +0.52 | +57.6% | -36.4% | +0.39 | +30.7% | -33.4% | non | non |
| NDX (40 ans) | 10191 | 61.1% | +0.52 | +5662.5% | -82.9% | +0.43 | +1339.4% | -72.6% | non | non |
| Russell 2000 | 9781 | 62.5% | +0.34 | +602.0% | -59.9% | +0.37 | +395.5% | -36.7% | OUI | non |
| S&P 500 | 10191 | 61.1% | +0.48 | +1715.7% | -56.8% | +0.44 | +636.1% | -41.0% | non | non |
| DAX | 6776 | 57.0% | +0.25 | +130.5% | -72.7% | +0.26 | +115.2% | -58.8% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
