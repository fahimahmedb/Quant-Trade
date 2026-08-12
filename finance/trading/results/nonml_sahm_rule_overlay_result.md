# Résultat — Règle de Sahm en temps réel (FRED SAHMREALTIME), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si SahmRule_lag(t) >= 0.5 (seuil FIXE externe, Sahm 2019, jamais estimé sur ces données), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 5.2% | +0.52 | +79.0% | -36.4% | +0.50 | +73.8% | -36.4% | non | non |
| NDX (40 ans) | 10272 | 17.0% | +0.53 | +26208.9% | -82.9% | +0.56 | +20330.4% | -74.2% | OUI | non |
| Russell 2000 | 9781 | 17.8% | +0.34 | +1646.9% | -59.9% | +0.34 | +1095.1% | -43.1% | non | non |
| S&P 500 | 14251 | 23.3% | +0.45 | +7977.0% | -56.8% | +0.46 | +4889.2% | -41.5% | OUI | non |
| DAX | 6776 | 18.2% | +0.25 | +353.5% | -72.7% | +0.32 | +436.2% | -63.3% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
