# Résultat — Régime de niveau du taux LONG DGS10 (pré-enregistré, complète le #175)

`position(t) = 0.5x` si taux(t-1) > taux(t-1-63) (hausse), `2.0x` si baisse, `1.0x` si égal. Coûts 5 bps.

| Marché | Séances test. | % temps régime hausse | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1186 | 64.0% | +0.55 | +81.6% | -36.4% | +0.81 | +195.4% | -36.6% | OUI | OUI |
| NDX (40 ans) | 10208 | 47.8% | +0.52 | +22376.6% | -82.9% | +0.46 | +214423.6% | -95.3% | non | OUI |
| Russell 2000 | 9717 | 47.6% | +0.40 | +2617.4% | -59.9% | +0.33 | +7818.4% | -84.3% | non | OUI |
| S&P 500 | 14187 | 50.2% | +0.46 | +8362.8% | -56.8% | +0.47 | +103207.1% | -76.7% | OUI | OUI |
| DAX | 6712 | 47.9% | +0.21 | +255.4% | -72.7% | +0.21 | +709.3% | -83.9% | non | OUI |

**2/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
