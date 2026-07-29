# Audit adversarial — Overlay vol-targeting gaté par la dispersion du momentum

## 1. Recalcul indépendant de la dispersion (boucle Python explicite, ddof=1 manuel)

| Date (indice) | Écart absolu |
|---|---|
| 252 | 0.00e+00 |
| 352 | 5.55e-17 |
| 452 | 0.00e+00 |
| 552 | 1.11e-16 |
| 652 | 5.55e-17 |
| 752 | 0.00e+00 |
| 852 | 5.55e-17 |
| 952 | 5.55e-17 |
| 1052 | 0.00e+00 |
| 1152 | 0.00e+00 |
| 1252 | 1.11e-16 |
| 1352 | 0.00e+00 |

**OK — dispersion du momentum confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la dispersion calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
