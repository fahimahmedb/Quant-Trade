# Audit adversarial — Overlay vol-targeting gaté par la breadth nette hauts-bas

## 1. Recalcul indépendant de la breadth nette (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 252 | 0.00e+00 |
| 352 | 0.00e+00 |
| 452 | 0.00e+00 |
| 552 | 0.00e+00 |
| 652 | 0.00e+00 |
| 752 | 0.00e+00 |
| 852 | 0.00e+00 |
| 952 | 0.00e+00 |
| 1052 | 0.00e+00 |
| 1152 | 0.00e+00 |
| 1252 | 0.00e+00 |
| 1352 | 0.00e+00 |

**OK — breadth nette confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la breadth calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
