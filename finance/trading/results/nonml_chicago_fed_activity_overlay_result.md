# Résultat — Indice d'activité nationale de la Fed de Chicago (CFNAI), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si CFNAI_lag(t) est dans son tercile expanding le plus BAS (activité économique faible), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 50.6% | +0.52 | +57.6% | -36.4% | +0.40 | +32.4% | -32.2% | non | non |
| NDX (40 ans) | 10272 | 39.1% | +0.53 | +6599.5% | -82.9% | +0.53 | +3576.7% | -72.9% | OUI | non |
| Russell 2000 | 9781 | 40.1% | +0.34 | +602.0% | -59.9% | +0.30 | +315.9% | -40.3% | non | non |
| S&P 500 | 14251 | 35.6% | +0.45 | +3369.2% | -56.8% | +0.43 | +1598.5% | -42.4% | non | non |
| DAX | 6776 | 31.1% | +0.25 | +130.5% | -72.7% | +0.30 | +187.1% | -58.2% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
