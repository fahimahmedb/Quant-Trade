# Audit adversarial — Momentum 12-1 (#73), univers point-in-time

## 1. Recalcul indépendant de l'éligibilité PIT

| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |
|---|---|---|---|
| 2015-01-02 | 73 | 73 | OUI |
| 2018-05-04 | 85 | 85 | OUI |
| 2021-09-03 | 94 | 94 | OUI |
| 2025-01-08 | 100 | 100 | OUI |

**OK — éligibilité PIT confirmée par recalcul indépendant.**

## 2. Vérification du décalage causal (`lag_one_day`)

**OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.**

## 3. Test anti-lookahead (perturbation du futur)

Écart momentum à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 4. Cohérence croisée avec le #258 (cycle #264)

Le Sharpe momentum PIT obtenu ici (+0,44) est EXACTEMENT identique à la jambe référence "momentum seul" rapportée dans le résultat PIT du #258 (`results/nonml_momentum_turnover_doublesort_pit_universe_result.md`, +0,66→+0,44) -- même signal, même univers PIT, même ancrage 2015-01-01, calculé de manière totalement indépendante (script séparé, aucun code partagé au-delà des constantes LOOKBACK/SKIP/REBAL_EVERY). Cette coïncidence exacte est une confirmation croisée forte de l'absence de bug dans les deux scripts.
