# Résultat — Force du dollar américain (DTWEXBGS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si USDChange(t)=log(DTWEXBGS(t)/DTWEXBGS(t-21)) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 31.0% | +0.52 | +79.0% | -36.4% | +0.43 | +51.9% | -36.2% | non | non |
| NDX (40 ans) | 5142 | 37.6% | +0.62 | +1624.6% | -53.7% | +0.65 | +911.6% | -38.3% | OUI | non |
| Russell 2000 | 5142 | 37.6% | +0.27 | +302.6% | -59.9% | +0.31 | +236.3% | -41.8% | OUI | non |
| S&P 500 | 5142 | 37.6% | +0.45 | +486.8% | -56.8% | +0.50 | +341.3% | -41.2% | OUI | non |
| DAX | 5185 | 37.7% | +0.35 | +341.6% | -54.8% | +0.36 | +229.0% | -43.5% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
