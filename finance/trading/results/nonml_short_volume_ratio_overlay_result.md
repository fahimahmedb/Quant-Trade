# Résultat — Ratio de volume vendu à découvert QQQ (FINRA Reg SHO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si ShortVolRatio_lag(t) (QQQ, ShortVolume/TotalVolume) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps. Décalage de publication 2j + alignement causal quotidien standard.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 27.2% | +0.52 | +57.6% | -36.4% | +0.51 | +50.9% | -29.2% | non | non |
| NDX (40 ans) | 1993 | 32.2% | +0.72 | +214.5% | -35.6% | +0.63 | +145.5% | -28.0% | non | non |
| Russell 2000 | 1993 | 32.2% | +0.28 | +36.2% | -43.1% | +0.22 | +21.7% | -42.7% | non | non |
| S&P 500 | 1993 | 32.2% | +0.63 | +126.9% | -33.9% | +0.50 | +79.0% | -33.9% | non | non |
| DAX | 2013 | 31.8% | +0.44 | +70.9% | -38.8% | +0.32 | +36.6% | -39.0% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
