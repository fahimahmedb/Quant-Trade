# Résultat — Effet du changement d'heure DST, overlay défensif (pré-enregistré)

`position(t) = 0.5x` le premier jour de bourse suivant chaque transition DST (printemps et automne, règles US ou UE selon le marché), `1.0x` sinon. Coûts 5 bps.

| Marché | Séances test. | % temps coupé | BH Sharpe | BH Rdt total | BH MDD | Overlay Sharpe | Overlay Rdt total | Overlay MDD | Sharpe>BH | Rdt>BH |
|---|---|---|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 1250 | 0.88% | +0.52 | +79.0% | -36.4% | +0.49 | +72.6% | -37.5% | non | non |
| NDX (40 ans) | 10272 | 0.81% | +0.53 | +26208.9% | -82.9% | +0.52 | +22543.0% | -82.2% | non | non |
| Russell 2000 | 9781 | 0.81% | +0.34 | +1646.9% | -59.9% | +0.33 | +1476.9% | -61.4% | non | non |
| S&P 500 | 14251 | 0.80% | +0.45 | +7977.0% | -56.8% | +0.43 | +6559.1% | -58.7% | non | non |
| DAX | 6776 | 0.80% | +0.25 | +353.5% | -72.7% | +0.23 | +285.8% | -72.4% | non | non |

**0/5 marchés où l'overlay bat Buy&Hold en Sharpe ET rendement (critère renforcé : ≥4/5).**

**FAIL — critère pré-enregistré NON atteint.**
