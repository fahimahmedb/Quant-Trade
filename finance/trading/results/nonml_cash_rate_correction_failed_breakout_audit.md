# Audit adversarial — Correction taux réaliste appliquée au #55 (#146)

## 1. Vérification : la position équity ne prend que les valeurs {FLOOR, 1.0}

Valeurs uniques observées : [0.5, 1.0]
**OK — conforme au mécanisme #55 (FLOOR=0.5 ou 1.0 uniquement).**

## 2. Recalcul indépendant du rendement combiné (formule fermée indépendante)

| Indice séance | pos_eq | Original | Indépendant | Concorde |
|---|---|---|---|---|
| 10 | 1.000 | 0.008257 | 0.008257 | OUI |
| 1294 | 0.500 | 0.007303 | 0.007303 | OUI |
| 2578 | 1.000 | -0.018745 | -0.018745 | OUI |
| 3862 | 1.000 | -0.007252 | -0.007252 | OUI |
| 5146 | 1.000 | 0.002514 | 0.002514 | OUI |
| 6430 | 1.000 | 0.001057 | 0.001057 | OUI |
| 7714 | 1.000 | 0.002551 | 0.002551 | OUI |
| 8998 | 1.000 | -0.006946 | -0.006946 | OUI |

**OK — recalcul indépendant confirmé.**

## 3. Test anti-lookahead

Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141 (déjà audité, 0 fuite détectée). Position équity #55 (déjà auditée à l'origine, cycle #55). Aucune nouvelle surface de fuite introduite par cette correction — pas ré-audité en double.
