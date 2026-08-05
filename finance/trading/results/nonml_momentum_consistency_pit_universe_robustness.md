# Robustesse — Momentum de constance, univers point-in-time (grille de plausibilité, PAS un retuning)

Grille réutilisée telle quelle du #82 original : N_BLOCKS {10,12,14}, REBAL_EVERY {15,21,27}j, BLOCK_LEN=21j fixe. Le verdict PASS officiel reste celui de la spécification pré-enregistrée (`results/nonml_momentum_consistency_pit_universe_result.md`).

| N_BLOCKS | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe constance | Rendement total |
|---|---|---|---|---|---|
| 10 | 21 | OUI | OUI | +0.45 | +138.6% |
| 12 | 21 | OUI | OUI | +0.45 | +139.9% ← pré-enregistré |
| 14 | 21 | OUI | OUI | +0.45 | +142.0% |
| 12 | 15 | OUI | OUI | +0.50 | +170.5% |
| 12 | 27 | OUI | OUI | +0.54 | +195.0% |

**5/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible, pas un pic isolé.
