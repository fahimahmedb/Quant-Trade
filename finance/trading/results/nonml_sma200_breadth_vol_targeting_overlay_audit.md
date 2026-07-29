# Audit adversarial — Overlay vol-targeting gaté par la breadth SMA200

## 1. Recalcul indépendant de la breadth SMA200 (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 200 | 0.00e+00 |
| 300 | 0.00e+00 |
| 400 | 0.00e+00 |
| 500 | 0.00e+00 |
| 600 | 0.00e+00 |
| 700 | 0.00e+00 |
| 800 | 0.00e+00 |
| 900 | 0.00e+00 |
| 1000 | 0.00e+00 |
| 1100 | 0.00e+00 |
| 1200 | 0.00e+00 |
| 1300 | 0.00e+00 |

**OK — breadth SMA200 confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la breadth calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
