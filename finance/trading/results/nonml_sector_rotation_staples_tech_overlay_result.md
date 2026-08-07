# Résultat — Rotation sectorielle défensive (XLP/XLK, log-return 21j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RatioMom_lag(t)=log(Ratio(t-1)/Ratio(t-1-21)) avec Ratio=XLP/XLK est dans son tercile expanding le plus HAUT (rotation défensive marquée), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1229 | 30.8% | +0.52 | +56.8% | -36.4% | +0.58 | +55.3% | -28.1% | OUI | non |
| NDX (40 ans) | 6907 | 28.9% | +0.36 | +426.4% | -82.9% | +0.34 | +293.2% | -79.8% | non | non |
| Russell 2000 | 6907 | 28.9% | +0.29 | +214.1% | -59.9% | +0.32 | +219.7% | -53.0% | OUI | OUI |
| S&P 500 | 6907 | 28.9% | +0.34 | +265.7% | -56.8% | +0.32 | +172.1% | -51.4% | non | non |
| DAX | 6755 | 26.4% | +0.24 | +116.2% | -72.7% | +0.28 | +153.2% | -72.1% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
