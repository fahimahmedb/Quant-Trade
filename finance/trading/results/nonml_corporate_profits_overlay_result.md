# Résultat — Profits des entreprises US (FRED CP), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CPGrowth_lag(t-1)=log(CP(t)/CP(t-4)) est dans son tercile expanding le plus BAS (contraction des profits = défavorable), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 59.9% | +0.52 | +79.0% | -36.4% | +0.61 | +63.3% | -24.3% | OUI | non |
| NDX (40 ans) | 10272 | 35.7% | +0.53 | +26208.9% | -82.9% | +0.58 | +12313.5% | -72.6% | OUI | non |
| Russell 2000 | 9781 | 45.8% | +0.34 | +1646.9% | -59.9% | +0.38 | +1064.9% | -42.1% | OUI | non |
| S&P 500 | 14251 | 36.7% | +0.45 | +7977.0% | -56.8% | +0.47 | +3848.3% | -48.2% | OUI | non |
| DAX | 6776 | 33.4% | +0.25 | +353.5% | -72.7% | +0.25 | +243.8% | -72.3% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
