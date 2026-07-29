# Audit adversarial — Overlay vol-targeting gaté par la breadth de rebond rapide post-creux

## 1. Recalcul indépendant (boucle Python explicite, sans vectorisation)

| Date (indice) | Écart absolu |
|---|---|
| 20 | 0.00e+00 |
| 420 | 0.00e+00 |
| 820 | 0.00e+00 |
| 1220 | 0.00e+00 |

**OK — breadth confirmée par recalcul indépendant (4 dates).**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la breadth calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
