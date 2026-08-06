# Résultat — Taux de défaut hypothécaire US (DRSFRMACBS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRSFRMACBS_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 14.9% | +0.52 | +57.6% | -36.4% | +0.48 | +50.1% | -36.4% | non | non |
| NDX (40 ans) | 8883 | 31.9% | +0.50 | +3129.3% | -82.9% | +0.51 | +2492.0% | -80.4% | OUI | non |
| Russell 2000 | 8883 | 31.9% | +0.37 | +634.7% | -59.9% | +0.40 | +627.4% | -43.3% | OUI | non |
| S&P 500 | 8883 | 31.9% | +0.47 | +1034.2% | -56.8% | +0.53 | +991.1% | -46.6% | OUI | non |
| DAX | 6776 | 32.4% | +0.25 | +130.5% | -72.7% | +0.31 | +200.1% | -62.2% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
