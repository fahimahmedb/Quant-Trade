# Robustesse — Tilt Amihud illiquidité (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : ILLIQ_WINDOW=126j (seul paramètre nouveau de ce cycle). REBAL_EVERY=21j hérité de #4/#73/#78/#82 (Règle 7, non reperturbé). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_amihud_illiquidity_tilt_result.md`) — ceci est diagnostique uniquement.

| ILLIQ_WINDOW | Sharpe>BH | Rendement>BH | Sharpe tilt | Rendement total tilt |
|---|---|---|---|---|
| 90j | OUI | OUI | +1.29 | +406.7% |
| 108j | OUI | OUI | +1.23 | +361.0% |
| 126j | OUI | OUI | +1.19 | +334.1% ← pré-enregistré |
| 144j | OUI | OUI | +1.10 | +283.3% |
| 162j | OUI | OUI | +1.08 | +272.3% |

**5/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de 126j, pas un pic isolé.
