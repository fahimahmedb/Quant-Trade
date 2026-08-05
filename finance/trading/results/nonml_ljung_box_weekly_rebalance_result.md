# Résultat — Rebalancement hebdomadaire de la porte Ljung-Box (#242), correction ciblée Règle 9 (pré-enregistré)

Position quotidienne du #242 échantillonnée tous les 5j et maintenue constante entre deux rebalancements (`weekly_hold_position`, réutilisée du #154/#167, Règle 7). Signal Ljung-Box et mécanisme #46 sous-jacent INCHANGÉS. Marché : NDX (40 ans), 9768 séances testables.

| | Sharpe ann. | Rendement total net | MDD | Turnover moyen/j |
|---|---|---|---|---|
| Buy&Hold | +0.49 | +3669.6% | -82.9% | — |
| Porte Ljung-Box, quotidien (#242) | +0.52 | +5724.0% | -82.9% | 0.0188 |
| **Porte Ljung-Box, hebdomadaire** | **+0.52** | **+5670.6%** | -82.9% | 0.0106 |

Réduction du turnover moyen : 43.6%.

1. Sharpe hebdomadaire > BH : OUI
2. Rendement hebdomadaire > BH : OUI

**PASS niveau 1 maintenu après passage à un rebalancement hebdomadaire.**
