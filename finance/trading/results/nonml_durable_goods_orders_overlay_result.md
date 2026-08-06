# Résultat — Nouvelles commandes de biens durables US (FRED DGORDER), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DGOGrowth_lag(t-1)=log(DGORDER(t)/DGORDER(t-12)) est dans son tercile expanding le plus BAS (contraction des commandes = défavorable), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 68.2% | +0.52 | +57.6% | -36.4% | +0.45 | +33.6% | -23.9% | non | non |
| NDX (40 ans) | 8398 | 41.8% | +0.50 | +2441.9% | -82.9% | +0.51 | +1454.9% | -64.3% | OUI | non |
| Russell 2000 | 8398 | 41.8% | +0.35 | +468.9% | -59.9% | +0.32 | +289.5% | -44.7% | non | non |
| S&P 500 | 8398 | 41.8% | +0.46 | +864.5% | -56.8% | +0.43 | +465.8% | -36.9% | non | non |
| DAX | 6776 | 32.4% | +0.25 | +130.5% | -72.7% | +0.29 | +165.0% | -63.7% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
