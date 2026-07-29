# Audit adversarial — Overlay vol-targeting gaté par la confirmation multi-marché élargie

## 1. Recalcul indépendant de la breadth 5-marchés (boucle Python explicite)

| Date NDX (indice) | Écart absolu |
|---|---|
| 9400 | 0.00e+00 |
| 9600 | 0.00e+00 |
| 9800 | 0.00e+00 |
| 10000 | 0.00e+00 |
| 10200 | 0.00e+00 |

**OK — breadth 5-marchés confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données NDX les plus récentes)

Tendance NDX calculée à une date antérieure à la mutation : avant=True, après=True.
**OK — aucune fuite.**
