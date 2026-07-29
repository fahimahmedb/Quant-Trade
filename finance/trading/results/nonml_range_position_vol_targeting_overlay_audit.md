# Audit adversarial — Overlay vol-targeting gaté par la position moyenne dans le range annuel

## 1. Recalcul indépendant de la position moyenne (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 252 | 1.11e-16 |
| 352 | 1.67e-16 |
| 452 | 5.55e-17 |
| 552 | 1.67e-16 |
| 652 | 0.00e+00 |
| 752 | 1.11e-16 |
| 852 | 3.33e-16 |
| 952 | 0.00e+00 |
| 1052 | 0.00e+00 |
| 1152 | 0.00e+00 |
| 1252 | 1.11e-16 |
| 1352 | 1.11e-16 |

**OK — position moyenne confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la position calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
