# Résultat — Structure par terme du VIX (VXV 3-mois − VIX 30j), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si Slope_lag(t)=VXV_lag(t)-VIX_lag(t) est dans son tercile expanding le plus BAS (backwardation la plus prononcée), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 41.2% | +0.52 | +79.0% | -36.4% | +0.45 | +45.1% | -33.2% | non | non |
| NDX (40 ans) | 4678 | 24.1% | +0.63 | +1332.8% | -51.5% | +0.68 | +827.4% | -40.9% | OUI | non |
| Russell 2000 | 4678 | 24.1% | +0.29 | +292.5% | -56.9% | +0.29 | +196.9% | -46.7% | OUI | non |
| S&P 500 | 4678 | 24.1% | +0.44 | +413.5% | -55.4% | +0.47 | +261.4% | -48.6% | OUI | non |
| DAX | 4715 | 24.2% | +0.29 | +220.8% | -54.6% | +0.46 | +321.5% | -44.6% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
