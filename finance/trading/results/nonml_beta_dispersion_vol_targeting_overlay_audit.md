# Audit adversarial — Overlay vol-targeting gaté par la dispersion des betas individuels

## 1. Recalcul indépendant de la dispersion des betas (boucle Python explicite, ddof=1 manuel)

| Date (indice) | Écart absolu |
|---|---|
| 60 | 2.22e-16 |
| 160 | 1.17e-15 |
| 260 | 4.44e-16 |
| 360 | 0.00e+00 |
| 460 | 5.00e-16 |
| 560 | 9.99e-16 |
| 660 | 3.44e-15 |
| 760 | 3.00e-15 |
| 860 | 4.11e-15 |
| 960 | 3.55e-15 |
| 1060 | 3.77e-15 |
| 1160 | 1.91e-14 |
| 1260 | 1.53e-14 |
| 1360 | 1.08e-14 |

**OK — dispersion des betas confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la dispersion calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
