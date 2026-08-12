# Résultat — Durée hebdomadaire moyenne du travail, secteur manufacturier US (FRED AWHMAN), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si AWHMAN_lag(t-1) est dans son tercile expanding le plus BAS (durée hebdomadaire la plus faible observée à ce jour = signal avant-coureur), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 56.2% | +0.52 | +79.0% | -36.4% | +0.46 | +49.1% | -26.6% | non | non |
| NDX (40 ans) | 10272 | 29.0% | +0.53 | +26208.9% | -82.9% | +0.54 | +12848.8% | -72.2% | OUI | non |
| Russell 2000 | 9781 | 31.1% | +0.34 | +1646.9% | -59.9% | +0.34 | +1010.8% | -43.9% | OUI | non |
| S&P 500 | 14251 | 16.7% | +0.45 | +7977.0% | -56.8% | +0.40 | +3505.0% | -56.8% | non | non |
| DAX | 6776 | 29.1% | +0.25 | +353.5% | -72.7% | +0.18 | +151.5% | -64.2% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
