# Robustesse — Momentum 12-1 mois (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : LOOKBACK=252, REBAL_EVERY=21, SKIP=21 (fixe, non perturbé — cœur de la construction Jegadeesh & Titman). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_momentum_12_1_result.md`) — ceci est diagnostique uniquement.

| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe momentum | Rendement total momentum |
|---|---|---|---|---|---|
| 200 | 21 | OUI | OUI | +0.74 | +120.5% |
| 252 | 21 | OUI | OUI | +0.67 | +96.2% ← LOOKBACK pré-enregistré |
| 300 | 21 | non | non | +0.67 | +87.2% |
| 252 | 15 | OUI | OUI | +0.72 | +107.6% |
| 252 | 27 | OUI | OUI | +0.74 | +111.9% |

**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de la spécification 252j/21j, pas un pic isolé.
