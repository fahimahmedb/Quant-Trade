# Robustesse — Overlay de régime par le range intra-séance (grille de plausibilité, PAS un retuning)

CAP pré-enregistré = 2.0x. Le verdict PASS officiel reste celui de cette valeur (`results/nonml_intraday_range_regime_overlay_result.md`) — ceci est diagnostique uniquement.

| CAP | Nb marchés PASS (Sharpe ET rendement) /5 |
|---|---|
| 1.5x | 5/5 |
| 2.0x | 5/5 ← CAP pré-enregistré |
| 2.5x | 5/5 |
| 3.0x | 5/5 |

**Lecture** : si les CAP voisins restent proches de 5/5, l'effet est un plateau plausible autour de 2.0x, pas un pic isolé sur ce niveau de levier précis.
