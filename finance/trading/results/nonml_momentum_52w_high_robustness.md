# Robustesse — Momentum 52-semaines (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : LOOKBACK=252, REBAL_EVERY=21 (marquée ci-dessous). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_momentum_52w_high_result.md`) — ceci est diagnostique uniquement.

| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe leaders | Rendement total leaders |
|---|---|---|---|---|---|
| 200 | 21 | OUI | OUI | +0.95 | +115.9% |
| 252 | 21 | OUI | OUI | +0.78 | +81.6% ← LOOKBACK pré-enregistré |
| 300 | 21 | OUI | OUI | +0.92 | +101.1% |
| 252 | 15 | OUI | OUI | +0.95 | +111.9% |
| 252 | 27 | OUI | OUI | +0.74 | +79.0% |

**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de la spécification 252j/21j, pas un pic isolé.
