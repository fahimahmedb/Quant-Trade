# Résultat — Déficit budgétaire fédéral US (FRED MTSDS133FMS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DeficitTTM_lag(t-1) (somme glissante 12 mois, décalage 1 mois) est dans son tercile expanding le plus BAS (déficit cumulé le plus large observé à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 17.6% | +0.52 | +57.6% | -36.4% | +0.53 | +54.8% | -36.4% | OUI | non |
| NDX (40 ans) | 10272 | 65.8% | +0.53 | +6599.5% | -82.9% | +0.42 | +1298.1% | -82.9% | non | non |
| Russell 2000 | 9781 | 68.6% | +0.34 | +602.0% | -59.9% | +0.28 | +206.5% | -45.4% | non | non |
| S&P 500 | 11283 | 70.1% | +0.52 | +2985.1% | -56.8% | +0.43 | +718.9% | -51.4% | non | non |
| DAX | 6776 | 71.6% | +0.25 | +130.5% | -72.7% | +0.24 | +90.1% | -58.5% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
