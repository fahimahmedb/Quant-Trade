# Robustesse — Tilt Amihud illiquidité (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : ILLIQ_WINDOW=126j (seul paramètre nouveau de ce cycle). REBAL_EVERY=21j hérité de #4/#73/#78/#82 (Règle 7, non reperturbé). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_amihud_illiquidity_tilt_result.md`) — ceci est diagnostique uniquement.

| ILLIQ_WINDOW | Sharpe>BH | Rendement>BH | Sharpe tilt | Rendement total tilt |
|---|---|---|---|---|
| 90j | OUI | OUI | +0.94 | +181.4% |
| 108j | OUI | OUI | +0.88 | +156.6% |
| 126j | OUI | OUI | +0.84 | +142.8% ← pré-enregistré |
| 144j | OUI | OUI | +0.74 | +113.9% |
| 162j | OUI | OUI | +0.73 | +108.9% |

**5/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de 126j, pas un pic isolé.
