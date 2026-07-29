# Audit adversarial — Overlay vol-targeting gaté par la breadth de surperformance petites caps (proxy)

## 1. Recalcul indépendant (boucle Python explicite, médianes manuelles, sans vectorisation)

| Date (indice) | Écart absolu |
|---|---|
| 81 | 0.00e+00 |
| 481 | 0.00e+00 |
| 881 | 0.00e+00 |
| 1281 | 0.00e+00 |

**OK — breadth confirmée par recalcul indépendant (4 dates).**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la breadth calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
