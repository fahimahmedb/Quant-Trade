# Résultat — Taux de défaut cartes de crédit US (DRCCLACBS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRCCLACBS_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 70.0% | +0.52 | +57.6% | -36.4% | +0.43 | +30.6% | -27.1% | non | non |
| NDX (40 ans) | 8883 | 18.5% | +0.50 | +3129.3% | -82.9% | +0.55 | +3352.9% | -77.5% | OUI | OUI |
| Russell 2000 | 8883 | 18.5% | +0.37 | +634.7% | -59.9% | +0.44 | +907.0% | -43.1% | OUI | OUI |
| S&P 500 | 8883 | 18.5% | +0.47 | +1034.2% | -56.8% | +0.57 | +1304.0% | -38.5% | OUI | OUI |
| DAX | 6776 | 18.1% | +0.25 | +130.5% | -72.7% | +0.35 | +264.9% | -62.7% | OUI | OUI |

**4/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
