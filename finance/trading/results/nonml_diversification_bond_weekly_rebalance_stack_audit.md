# Audit adversarial — Empilement diversification obligataire + rebalancement hebdomadaire (#137)

## 1. Recalcul indépendant du rendement combiné (formule fermée indépendante)

| Indice séance | pos_eq | Original | Indépendant | Concorde |
|---|---|---|---|---|
| 10 | 1.224 | -0.003111 | -0.003111 | OUI |
| 1200 | 1.250 | -0.020270 | -0.020270 | OUI |
| 2390 | 1.142 | -0.052341 | -0.052341 | OUI |
| 3580 | 0.563 | -0.016207 | -0.016207 | OUI |
| 4770 | 0.920 | 0.008945 | 0.008945 | OUI |
| 5960 | 1.112 | -0.001976 | -0.001976 | OUI |
| 7150 | 1.250 | -0.001236 | -0.001236 | OUI |
| 8340 | 1.233 | 0.012267 | 0.012267 | OUI |

**OK — recalcul indépendant confirmé.**

## 2. Test anti-lookahead

Mécanisme obligataire strictement identique au #134/#136 (déjà audité, 0 fuite détectée). La position équity provient du #131 (déjà auditée, anti-lookahead confirmé au cycle #131). Aucune nouvelle surface de fuite introduite par cet empilement — pas ré-audité en double.
