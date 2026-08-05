# Audit adversarial — Tilt Amihud illiquidité

## 1. Recalcul indépendant de l'ILLIQ moyen (boucle Python explicite)

| Date (indice) | Écart max absolu (titres avec historique complet) |
|---|---|
| 126 | 1.65e-24 |
| 336 | 4.14e-25 |
| 546 | 4.14e-25 |
| 756 | 4.14e-25 |
| 966 | 5.17e-25 |
| 1176 | 4.14e-25 |
| 1386 | 4.17e-25 |

**OK — ILLIQ confirmé par recalcul indépendant sur toutes les dates échantillonnées.**

## 2. Vérification du décalage causal (`lag_one_day`)

**OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.**

## 3. Test anti-lookahead (perturbation du futur : prix et volume)

Écart ILLIQ à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
