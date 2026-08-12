# Robustesse — Momentum 52-semaines (grille de plausibilité, PAS un retuning)

Spécification pré-enregistrée : LOOKBACK=252, REBAL_EVERY=21 (marquée ci-dessous). Le verdict PASS officiel reste celui de cette spécification (`results/nonml_momentum_52w_high_result.md`) — ceci est diagnostique uniquement.

| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe leaders | Rendement total leaders |
|---|---|---|---|---|---|
| 200 | 21 | OUI | OUI | +1.20 | +196.1% |
| 252 | 21 | OUI | OUI | +1.04 | +145.8% ← LOOKBACK pré-enregistré |
| 300 | 21 | OUI | non | +1.17 | +169.3% |
| 252 | 15 | OUI | OUI | +1.21 | +188.7% |
| 252 | 27 | OUI | OUI | +0.99 | +145.5% |

**Lecture** : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible autour de la spécification 252j/21j, pas un pic isolé.
