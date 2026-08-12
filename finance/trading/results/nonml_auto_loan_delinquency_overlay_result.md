# Résultat — Taux de défaut prêts automobiles US (DRALACBN), overlay défensif (pré-enregistré)

`position(t) = 0.5x` si DRALACBN_lag(t-1) est dans son tercile expanding le plus HAUT, `1.0x` sinon. Design purement défensif. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 60.9% | +0.52 | +79.0% | -36.4% | +0.24 | +24.0% | -38.3% | non | non |
| NDX (40 ans) | 10272 | 19.1% | +0.53 | +26208.9% | -82.9% | +0.48 | +11292.6% | -82.9% | non | non |
| Russell 2000 | 9781 | 19.2% | +0.34 | +1646.9% | -59.9% | +0.33 | +1014.9% | -46.0% | non | non |
| S&P 500 | 10398 | 20.6% | +0.49 | +4043.9% | -56.8% | +0.48 | +2409.7% | -51.9% | non | non |
| DAX | 6776 | 31.2% | +0.25 | +353.5% | -72.7% | +0.38 | +505.9% | -57.8% | OUI | OUI |

**1/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
