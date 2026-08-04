# Résultat — Force du dollar américain (DTWEXBGS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si USDChange(t)=log(DTWEXBGS(t)/DTWEXBGS(t-21)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 31.0% | +0.52 | +57.6% | -36.4% | +0.43 | +38.3% | -36.2% | non | non |
| NDX (40 ans) | 5142 | 37.6% | +0.62 | +930.7% | -53.7% | +0.65 | +641.5% | -38.3% | OUI | non |
| Russell 2000 | 5142 | 37.6% | +0.27 | +112.3% | -59.9% | +0.31 | +129.3% | -41.8% | OUI | OUI |
| S&P 500 | 5142 | 37.6% | +0.45 | +298.5% | -56.8% | +0.50 | +255.1% | -41.2% | OUI | non |
| DAX | 5185 | 37.7% | +0.35 | +181.5% | -54.8% | +0.36 | +150.3% | -43.5% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
