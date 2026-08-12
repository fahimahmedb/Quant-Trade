# Robustesse — Momentum 12-1, univers point-in-time (grille de plausibilité, PAS un retuning)

Grille réutilisée telle quelle du #73 original : LOOKBACK {200,252,300}j, REBAL_EVERY {15,21,27}j, SKIP=21j fixe. Le verdict PASS officiel reste celui de la spécification pré-enregistrée (`results/nonml_momentum_12_1_pit_universe_result.md`).

| LOOKBACK | REBAL_EVERY | Sharpe>BH | Rendement>BH | Sharpe momentum | Rendement total |
|---|---|---|---|---|---|
| 200 | 21 | OUI | OUI | +0.64 | +509.6% |
| 252 | 21 | OUI | OUI | +0.64 | +511.1% ← pré-enregistré |
| 300 | 21 | non | OUI | +0.58 | +440.3% |
| 252 | 15 | OUI | OUI | +0.62 | +489.0% |
| 252 | 27 | non | OUI | +0.56 | +396.2% |

**3/5 variantes OUI/OUI.** Lecture : si la majorité des variantes voisines restent OUI/OUI, l'effet est un plateau plausible, pas un pic isolé.
