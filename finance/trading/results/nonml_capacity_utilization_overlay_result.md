# Résultat — Taux d'utilisation des capacités industrielles US (FRED TCU), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si TCU_lag(t-1) est dans son tercile expanding le plus BAS (taux d'utilisation le plus faible observé à ce jour = slack industriel élevé), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 73.9% | +0.52 | +79.0% | -36.4% | +0.19 | +18.0% | -35.7% | non | non |
| NDX (40 ans) | 10272 | 49.5% | +0.53 | +26208.9% | -82.9% | +0.57 | +9889.3% | -61.4% | OUI | non |
| Russell 2000 | 9781 | 61.3% | +0.34 | +1646.9% | -59.9% | +0.30 | +447.5% | -42.3% | non | non |
| S&P 500 | 14251 | 50.1% | +0.45 | +7977.0% | -56.8% | +0.38 | +1601.3% | -48.2% | non | non |
| DAX | 6776 | 36.9% | +0.25 | +353.5% | -72.7% | +0.28 | +285.9% | -56.7% | OUI | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
