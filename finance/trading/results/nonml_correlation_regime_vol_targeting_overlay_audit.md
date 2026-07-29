# Audit adversarial — Overlay vol-targeting gaté par le régime de corrélation moyenne

## 1. Recalcul indépendant de la corrélation moyenne (formule de Pearson manuelle, boucle explicite)

| Date (indice) | Écart absolu |
|---|---|
| 110 | 0.00e+00 |
| 260 | 0.00e+00 |
| 410 | 0.00e+00 |
| 560 | 5.55e-17 |
| 710 | 0.00e+00 |
| 860 | 2.78e-17 |
| 1010 | 0.00e+00 |
| 1160 | 0.00e+00 |
| 1310 | 0.00e+00 |

**OK — corrélation moyenne confirmée par recalcul indépendant (formule de Pearson manuelle).**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la corrélation calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
