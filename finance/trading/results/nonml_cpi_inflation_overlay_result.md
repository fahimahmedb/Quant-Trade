# Résultat — Inflation réalisée US (FRED CPIAUCSL), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CPIGrowth_lag(t-1)=log(CPIAUCSL(t)/CPIAUCSL(t-12)) est dans son tercile expanding le plus HAUT (inflation réalisée la plus élevée observée à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 19.6% | +0.52 | +79.0% | -36.4% | +0.70 | +98.8% | -26.2% | OUI | OUI |
| NDX (40 ans) | 10272 | 28.3% | +0.53 | +26208.9% | -82.9% | +0.64 | +35685.8% | -72.1% | OUI | OUI |
| Russell 2000 | 9781 | 24.1% | +0.34 | +1646.9% | -59.9% | +0.44 | +2343.0% | -44.6% | OUI | OUI |
| S&P 500 | 14251 | 16.0% | +0.45 | +7977.0% | -56.8% | +0.51 | +9350.3% | -50.2% | OUI | OUI |
| DAX | 6776 | 33.7% | +0.25 | +353.5% | -72.7% | +0.30 | +385.6% | -67.2% | OUI | OUI |

**5/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**PASS — critère pré-enregistré atteint.**
