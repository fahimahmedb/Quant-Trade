# Audit adversarial — vérification PIT des candidats volume (#258, #261)

### Momentum + double-tri turnover (#258 PIT)

| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |
|---|---|---|---|
| 2015-01-02 | 73 | 73 | OUI |
| 2018-05-04 | 85 | 85 | OUI |
| 2021-09-03 | 94 | 94 | OUI |
| 2025-01-08 | 100 | 100 | OUI |

**OK — éligibilité PIT confirmée par recalcul indépendant.**
Couverture moyenne mesurée sur cet échantillon : 85.8% (cohérent avec le ~87,6% mesuré au #163 sur le même univers de composition).

### Tilt Amihud illiquidité (#261 PIT)

| Date | n éligibles (original) | n éligibles (recalcul indépendant) | Identique |
|---|---|---|---|
| 2015-01-02 | 73 | 73 | OUI |
| 2018-05-04 | 85 | 85 | OUI |
| 2021-09-03 | 94 | 94 | OUI |
| 2025-01-08 | 100 | 100 | OUI |

**OK — éligibilité PIT confirmée par recalcul indépendant.**
Couverture moyenne mesurée sur cet échantillon : 85.8% (cohérent avec le ~87,6% mesuré au #163 sur le même univers de composition).

## Vérification du décalage causal (`lag_one_day`, partagé par les deux scripts)

**OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.**
## Test anti-lookahead (perturbation du futur : prix et volume, sur le #261 PIT)

Écart ILLIQ à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## Verdict global

**OK — aucun bug détecté, le FAIL des deux candidats sous univers PIT est confirmé authentique.**
