# Résultat — Différentiel de taux US-Allemagne (DGS10-DE10Y), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si RateDiff(t)=DGS10_lag(t)-DE10Y_lag_décalé(t) est dans son tercile expanding le plus haut, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 30.5% | +0.52 | +57.6% | -36.4% | +0.72 | +81.9% | -23.5% | OUI | OUI |
| NDX (40 ans) | 10272 | 41.4% | +0.53 | +6599.5% | -82.9% | +0.47 | +2535.6% | -82.2% | non | non |
| Russell 2000 | 9781 | 49.2% | +0.34 | +602.0% | -59.9% | +0.31 | +339.7% | -60.2% | non | non |
| S&P 500 | 14251 | 40.9% | +0.45 | +3369.2% | -56.8% | +0.40 | +1447.0% | -57.3% | non | non |
| DAX | 6776 | 56.8% | +0.25 | +130.5% | -72.7% | +0.14 | +24.1% | -71.7% | non | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
