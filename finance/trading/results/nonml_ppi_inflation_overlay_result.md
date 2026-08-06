# Résultat — Inflation à la production US (FRED PPIACO), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si PPIGrowth_lag(t-1)=log(PPIACO(t)/PPIACO(t-12)) est dans son tercile expanding le plus HAUT (inflation producteur la plus élevée observée à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 21.7% | +0.52 | +57.6% | -36.4% | +0.52 | +52.1% | -31.3% | non | non |
| NDX (40 ans) | 10272 | 40.2% | +0.53 | +6599.5% | -82.9% | +0.59 | +5721.8% | -72.6% | OUI | non |
| Russell 2000 | 9781 | 34.9% | +0.34 | +602.0% | -59.9% | +0.36 | +544.6% | -42.2% | OUI | non |
| S&P 500 | 14251 | 28.6% | +0.45 | +3369.2% | -56.8% | +0.52 | +4051.3% | -42.0% | OUI | OUI |
| DAX | 6776 | 30.7% | +0.25 | +130.5% | -72.7% | +0.28 | +155.1% | -67.0% | OUI | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
