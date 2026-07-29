# Audit adversarial — Overlay vol-targeting gaté par la breadth d'avance journalière

## 1. Recalcul indépendant de la breadth d'avance (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 6 | 1.11e-16 |
| 106 | 5.55e-17 |
| 206 | 0.00e+00 |
| 306 | 0.00e+00 |
| 406 | 0.00e+00 |
| 506 | 1.11e-16 |
| 606 | 1.11e-16 |
| 706 | 5.55e-17 |
| 806 | 5.55e-17 |
| 906 | 0.00e+00 |
| 1006 | 0.00e+00 |
| 1106 | 1.11e-16 |
| 1206 | 0.00e+00 |
| 1306 | 0.00e+00 |

**OK — breadth d'avance confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la breadth calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
