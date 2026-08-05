# Robustesse — Momentum 12-1 + double-tri turnover/volume-dollars (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : TURNOVER_WINDOW=126j (seul paramètre nouveau de ce cycle). LOOKBACK=252j, SKIP=21j, REBAL_EVERY=21j, TERCILE=1/3 hérités de #73/#79 (Règle 7, non reperturbés). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_momentum_turnover_doublesort_result.md`) — ceci est diagnostique uniquement.

| TURNOVER_WINDOW | Sharpe>référence | Rendement>référence | Sharpe double-tri | Rendement total double-tri |
|---|---|---|---|---|
| 90j | OUI | OUI | +0.97 | +158.1% |
| 108j | OUI | OUI | +0.97 | +158.2% |
| 126j | OUI | OUI | +1.04 | +178.3% ← pré-enregistré |
| 144j | OUI | OUI | +1.01 | +174.4% |
| 162j | OUI | OUI | +1.04 | +179.2% |

**5/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de 126j, pas un pic isolé.
