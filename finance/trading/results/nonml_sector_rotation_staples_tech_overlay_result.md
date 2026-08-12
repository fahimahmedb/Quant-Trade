# Résultat — Rotation sectorielle défensive (XLP/XLK, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RatioMom_lag(t)=log(Ratio(t-1)/Ratio(t-1-21)) avec Ratio=XLP/XLK est dans son tercile expanding le plus HAUT (rotation défensive marquée), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 30.8% | +0.52 | +77.9% | -36.4% | +0.58 | +68.6% | -28.1% | OUI | non |
| NDX (40 ans) | 6907 | 28.9% | +0.36 | +1377.2% | -82.9% | +0.34 | +634.5% | -79.8% | non | non |
| Russell 2000 | 6907 | 28.9% | +0.29 | +599.3% | -59.9% | +0.32 | +433.7% | -53.0% | OUI | non |
| S&P 500 | 6907 | 28.9% | +0.34 | +508.7% | -56.8% | +0.32 | +270.8% | -51.4% | non | non |
| DAX | 6755 | 26.4% | +0.24 | +324.9% | -72.7% | +0.28 | +302.8% | -72.1% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
