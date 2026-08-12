# Résultat — Emplois non-agricoles US (FRED PAYEMS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si PayrollsGrowth_lag(t-1)=log(PAYEMS(t)/PAYEMS(t-12)) est dans son tercile expanding le plus BAS (ralentissement de l'emploi = défavorable), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 88.3% | +0.52 | +79.0% | -36.4% | +0.18 | +14.2% | -32.9% | non | non |
| NDX (40 ans) | 10272 | 44.8% | +0.53 | +26208.9% | -82.9% | +0.58 | +11598.1% | -61.4% | OUI | non |
| Russell 2000 | 9781 | 39.0% | +0.34 | +1646.9% | -59.9% | +0.36 | +939.3% | -43.9% | OUI | non |
| S&P 500 | 14251 | 36.8% | +0.45 | +7977.0% | -56.8% | +0.45 | +3219.8% | -47.8% | non | non |
| DAX | 6776 | 29.9% | +0.25 | +353.5% | -72.7% | +0.30 | +334.4% | -59.2% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
