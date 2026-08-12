# Résultat — Taux de défaut cartes de crédit US (DRCCLACBS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRCCLACBS_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 70.0% | +0.52 | +79.0% | -36.4% | +0.43 | +38.4% | -27.1% | non | non |
| NDX (40 ans) | 8883 | 18.5% | +0.50 | +11049.9% | -82.9% | +0.55 | +8710.8% | -77.5% | OUI | non |
| Russell 2000 | 8883 | 18.5% | +0.37 | +1633.1% | -59.9% | +0.44 | +1838.5% | -43.1% | OUI | OUI |
| S&P 500 | 8883 | 18.5% | +0.47 | +1923.0% | -56.8% | +0.57 | +2021.3% | -38.5% | OUI | OUI |
| DAX | 6776 | 18.1% | +0.25 | +353.5% | -72.7% | +0.35 | +500.5% | -62.7% | OUI | OUI |

**3/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
