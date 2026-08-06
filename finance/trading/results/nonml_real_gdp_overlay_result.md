# Résultat — Croissance du PIB réel US (FRED GDPC1), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si GDPGrowth_lag(t-1)=log(GDPC1(t)/GDPC1(t-4)) est dans son tercile expanding le plus BAS, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 65.0% | +0.52 | +57.6% | -36.4% | +0.60 | +48.6% | -24.3% | OUI | non |
| NDX (40 ans) | 10272 | 46.0% | +0.53 | +6599.5% | -82.9% | +0.50 | +2665.6% | -72.2% | non | non |
| Russell 2000 | 9781 | 45.4% | +0.34 | +602.0% | -59.9% | +0.32 | +338.0% | -47.1% | non | non |
| S&P 500 | 14251 | 35.5% | +0.45 | +3369.2% | -56.8% | +0.46 | +2060.6% | -38.3% | OUI | non |
| DAX | 6776 | 32.4% | +0.25 | +130.5% | -72.7% | +0.33 | +212.0% | -56.4% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
