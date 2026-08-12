# Résultat — Déficit budgétaire fédéral US (FRED MTSDS133FMS), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DeficitTTM_lag(t-1) (somme glissante 12 mois, décalage 1 mois) est dans son tercile expanding le plus BAS (déficit cumulé le plus large observé à ce jour), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 17.6% | +0.52 | +79.0% | -36.4% | +0.53 | +72.4% | -36.4% | OUI | non |
| NDX (40 ans) | 10272 | 65.8% | +0.53 | +26208.9% | -82.9% | +0.42 | +3286.0% | -82.9% | non | non |
| Russell 2000 | 9781 | 68.6% | +0.34 | +1646.9% | -59.9% | +0.28 | +352.8% | -45.4% | non | non |
| S&P 500 | 11283 | 70.1% | +0.52 | +6315.8% | -56.8% | +0.43 | +1086.8% | -51.4% | non | non |
| DAX | 6776 | 71.6% | +0.25 | +353.5% | -72.7% | +0.24 | +152.5% | -58.5% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
