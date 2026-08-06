# Résultat — Indice d'incertitude de politique économique US (FRED USEPUINDXD), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si EPU_lag(t-1) est dans son tercile expanding le plus HAUT (incertitude de politique économique la plus élevée observée à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 51.5% | +0.52 | +57.6% | -36.4% | +0.27 | +17.4% | -38.3% | non | non |
| NDX (40 ans) | 10272 | 39.0% | +0.53 | +6599.5% | -82.9% | +0.40 | +1055.0% | -83.9% | non | non |
| Russell 2000 | 9781 | 40.4% | +0.34 | +602.0% | -59.9% | +0.23 | +149.6% | -46.8% | non | non |
| S&P 500 | 10460 | 37.5% | +0.50 | +2163.5% | -56.8% | +0.37 | +456.0% | -49.1% | non | non |
| DAX | 6776 | 44.4% | +0.25 | +130.5% | -72.7% | +0.12 | +18.3% | -65.3% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
