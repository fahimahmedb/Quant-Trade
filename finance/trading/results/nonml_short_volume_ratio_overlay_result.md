# Résultat — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ShortVolRatio_lag(t) (QQQ, ShortVolume/TotalVolume) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 2j + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 27.2% | +0.52 | +79.0% | -36.4% | +0.51 | +67.2% | -29.2% | non | non |
| NDX (40 ans) | 1993 | 32.2% | +0.72 | +298.9% | -35.6% | +0.63 | +197.1% | -28.0% | non | non |
| Russell 2000 | 1993 | 32.2% | +0.28 | +76.4% | -43.1% | +0.22 | +49.7% | -42.7% | non | non |
| S&P 500 | 1993 | 32.2% | +0.63 | +164.5% | -33.9% | +0.50 | +103.0% | -33.9% | non | non |
| DAX | 2013 | 31.8% | +0.44 | +98.6% | -38.8% | +0.32 | +53.5% | -39.0% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
