# Audit adversarial — Tilt sur l'asymétrie (skewness) individuelle

## 1. Recalcul indépendant (formule G1 explicite vs pandas.rolling().skew())

| Date (indice) | Écart max absolu (titres avec historique complet) |
|---|---|
| 60 | 1.33e-15 |
| 270 | 8.88e-16 |
| 480 | 2.22e-15 |
| 690 | 7.55e-15 |
| 900 | 2.94e-14 |
| 1110 | 4.66e-15 |
| 1320 | 6.44e-14 |

**OK — skewness confirmée par recalcul indépendant (formule G1) sur toutes les dates échantillonnées.**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur la skewness calculée à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Taille de l'univers éligible au fil du temps

Min 91, max 99, médiane 95 titres cotés simultanément sur les 1396 séances.
