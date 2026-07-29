# Robustesse — Momentum de constance (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : N_BLOCKS=12, REBAL_EVERY=21 (BLOCK_LEN=21 fixe, cœur de la construction). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_momentum_consistency_result.md`) — ceci est diagnostique uniquement.

| N_BLOCKS | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe constance | Rendement total constance |
|---|---|---|---|---|---|
| 10 | 21 | OUI | OUI | +0.77 | +108.1% |
| 12 | 21 | OUI | OUI | +0.67 | +81.7% ← N_BLOCKS pré-enregistré |
| 14 | 21 | non | non | +0.68 | +78.2% |
| 12 | 15 | OUI | OUI | +0.76 | +99.2% |
| 12 | 27 | OUI | OUI | +0.67 | +81.5% |

**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de la spécification N_BLOCKS=12/REBAL_EVERY=21j, pas un pic isolé.
