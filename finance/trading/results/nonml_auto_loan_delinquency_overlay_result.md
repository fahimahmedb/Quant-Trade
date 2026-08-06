# Résultat — Taux de défaut prêts automobiles US (DRALACBN), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRALACBN_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 60.9% | +0.52 | +57.6% | -36.4% | +0.24 | +14.3% | -38.3% | non | non |
| NDX (40 ans) | 10272 | 19.1% | +0.53 | +6599.5% | -82.9% | +0.48 | +3293.9% | -82.9% | non | non |
| Russell 2000 | 9781 | 19.2% | +0.34 | +602.0% | -59.9% | +0.33 | +455.3% | -46.0% | non | non |
| S&P 500 | 10398 | 20.6% | +0.49 | +1968.1% | -56.8% | +0.48 | +1339.5% | -51.9% | non | non |
| DAX | 6776 | 31.2% | +0.25 | +130.5% | -72.7% | +0.38 | +297.6% | -57.8% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
