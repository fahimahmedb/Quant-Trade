# Audit adversarial — Overlay vol-targeting gaté par la concentration du marché

## 1. Recalcul indépendant de l'indice de Herfindahl-Hirschman (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 0.00e+00 |
| 160 | 3.47e-18 |
| 260 | 0.00e+00 |
| 360 | 9.71e-17 |
| 460 | 1.39e-17 |
| 560 | 1.39e-17 |
| 660 | 1.04e-17 |
| 760 | 3.47e-18 |
| 860 | 0.00e+00 |
| 960 | 6.94e-18 |
| 1060 | 2.08e-17 |
| 1160 | 1.39e-17 |
| 1260 | 2.78e-17 |
| 1360 | 6.94e-18 |

**OK — HHI confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur le HHI calculé à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
