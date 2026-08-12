# Résultat — Inflation à la production US (FRED PPIACO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si PPIGrowth_lag(t-1)=log(PPIACO(t)/PPIACO(t-12)) est dans son tercile expanding le plus HAUT (inflation producteur la plus élevée observée à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 21.7% | +0.52 | +79.0% | -36.4% | +0.52 | +68.5% | -31.3% | non | non |
| NDX (40 ans) | 10272 | 40.2% | +0.53 | +26208.9% | -82.9% | +0.59 | +13619.5% | -72.6% | OUI | non |
| Russell 2000 | 9781 | 34.9% | +0.34 | +1646.9% | -59.9% | +0.36 | +1086.8% | -42.2% | OUI | non |
| S&P 500 | 14251 | 28.6% | +0.45 | +7977.0% | -56.8% | +0.52 | +7665.2% | -42.0% | OUI | non |
| DAX | 6776 | 30.7% | +0.25 | +353.5% | -72.7% | +0.28 | +319.3% | -67.0% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
