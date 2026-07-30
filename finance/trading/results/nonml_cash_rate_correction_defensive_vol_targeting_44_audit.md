# Audit adversarial — Correction taux réaliste appliquée au #44 (#149)

## 1. Recalcul indépendant de la position équity (formule fermée indépendante)

| Indice séance | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | 1.0000 | 1.0000 | OUI |
| 1314 | 0.7817 | 0.7817 | OUI |
| 2598 | 0.4223 | 0.4223 | OUI |
| 3882 | 0.3490 | 0.3490 | OUI |
| 5166 | 1.0000 | 1.0000 | OUI |
| 6450 | 1.0000 | 1.0000 | OUI |
| 7734 | 1.0000 | 1.0000 | OUI |
| 9018 | 1.0000 | 1.0000 | OUI |

**OK — position équity confirmée par recalcul indépendant.**

## 2. Recalcul indépendant du rendement obligataire (échantillon)

| Date | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | -0.002099 | -0.002099 | OUI |
| 1314 | 0.002334 | 0.002334 | OUI |
| 2598 | 0.001716 | 0.001716 | OUI |
| 3882 | -0.001342 | -0.001342 | OUI |
| 5166 | 0.004882 | 0.004882 | OUI |

**OK**

## 3. Test anti-lookahead

Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141/#146 (déjà audité, 0 fuite détectée). Position équity recalculée indépendamment ci-dessus (formule identique au #115/#134, déjà auditée à l'origine sous ce même schéma). Pas de nouvelle surface de fuite introduite par cette correction.
