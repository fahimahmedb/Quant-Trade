# Robustesse — Momentum de constance, univers point-in-time (grille de plausibilité, PAS un retuning)

Grille réutilisée telle quelle du #82 original : N_BLOCKS {10,12,14}, REBAL_EVERY {15,21,27}j, BLOCK_LEN=21j fixe. Le verdict PASS officiel reste celui de la spécification pré-enregistrée (`results/nonml_momentum_consistency_pit_universe_result.md`).

| N_BLOCKS | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe constance | Rendement total |
|---|---|---|---|---|---|
| 10 | 21 | non | OUI | +0.58 | +352.0% |
| 12 | 21 | non | OUI | +0.61 | +403.8% ← pré-enregistré |
| 14 | 21 | non | OUI | +0.60 | +388.9% |
| 12 | 15 | OUI | OUI | +0.65 | +431.8% |
| 12 | 27 | OUI | OUI | +0.71 | +504.4% |

**2/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible, pas un pic isolé.
