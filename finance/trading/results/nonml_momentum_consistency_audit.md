# Audit adversarial — Momentum de constance

## 1. Recalcul indépendant à un échantillon de dates de rebalancement

| Date (indice) | Écart max absolu (titres avec historique complet) |
|---|---|
| 252 | 0.00e+00 |
| 462 | 0.00e+00 |
| 672 | 0.00e+00 |
| 882 | 0.00e+00 |
| 1092 | 0.00e+00 |
| 1302 | 0.00e+00 |

**OK — constance confirmée par recalcul indépendant sur toutes les dates échantillonnées.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la constance calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Taille de l'univers éligible au fil du temps

Min 91, max 99, médiane 95 titres cotés simultanément sur les 1396 séances.
