# Audit adversarial — Momentum de constance (#82), univers point-in-time

## 1. Recalcul indépendant de l'éligibilité PIT

| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |
|---|---|---|---|
| 2015-01-02 | 73 | 73 | OUI |
| 2018-05-04 | 83 | 83 | OUI |
| 2021-09-03 | 94 | 94 | OUI |
| 2025-01-08 | 100 | 100 | OUI |

**OK — éligibilité PIT confirmée par recalcul indépendant.**

## 2. Vérification du décalage causal (`lag_one_day`)

**OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.**

## 3. Test anti-lookahead (perturbation du futur)

Écart de constance à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
