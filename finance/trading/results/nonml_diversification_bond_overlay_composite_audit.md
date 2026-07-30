# Audit adversarial — Diversification obligataire sur le Composite (#143)

## 1. Recalcul indépendant de la position équity

| Indice séance | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | 1.0000 | 1.0000 | OUI |
| 186 | 0.6615 | 0.6615 | OUI |
| 342 | 0.5243 | 0.5243 | OUI |
| 498 | 1.0000 | 1.0000 | OUI |
| 654 | 1.0000 | 1.0000 | OUI |
| 810 | 1.0000 | 1.0000 | OUI |
| 966 | 0.9640 | 0.9640 | OUI |
| 1122 | 1.0000 | 1.0000 | OUI |

**OK — position équity confirmée par recalcul indépendant.**

## 2. Recalcul indépendant du rendement obligataire (échantillon)

| Date | Original | Indépendant | Concorde |
|---|---|---|---|
| 30 | -0.005544 | -0.005544 | OUI |
| 186 | -0.004248 | -0.004248 | OUI |
| 342 | -0.003953 | -0.003953 | OUI |
| 498 | 0.004204 | 0.004204 | OUI |
| 654 | -0.000627 | -0.000627 | OUI |

**OK**

## 3. Test anti-lookahead

Mécanisme obligataire strictement identique au #134/#136/#137/#139/#141 (déjà audité, 0 fuite détectée). Position équity recalculée indépendamment ci-dessus. Pas de nouvelle surface de fuite introduite par ce marché.
