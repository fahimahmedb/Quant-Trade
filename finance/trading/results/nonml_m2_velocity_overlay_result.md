# Résultat — Vitesse de circulation de M2 (FRED M2V), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si M2V_lag(t-1) est dans son tercile expanding le plus BAS (vitesse faible = thésaurisation/stress), `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 4.6% | +0.52 | +57.6% | -36.4% | +0.52 | +58.4% | -36.4% | OUI | OUI |
| NDX (40 ans) | 10272 | 48.4% | +0.53 | +6599.5% | -82.9% | +0.42 | +1509.0% | -82.9% | non | non |
| Russell 2000 | 9781 | 50.1% | +0.34 | +602.0% | -59.9% | +0.33 | +343.7% | -46.0% | non | non |
| S&P 500 | 14251 | 39.3% | +0.45 | +3369.2% | -56.8% | +0.37 | +1048.1% | -56.8% | non | non |
| DAX | 6776 | 84.7% | +0.25 | +130.5% | -72.7% | +0.29 | +114.2% | -52.0% | OUI | non |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
