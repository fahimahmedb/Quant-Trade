# Audit adversarial — Overlay défensif combiné (#115 + GARCH)/2

## 1. Recalcul indépendant de la moyenne (boucle Python explicite)

| Date (indice) | Écart absolu |
|---|---|
| 100 | 0.00e+00 |
| 1600 | 0.00e+00 |
| 3100 | 0.00e+00 |
| 4600 | 0.00e+00 |
| 6100 | 0.00e+00 |
| 7600 | 0.00e+00 |
| 9100 | 0.00e+00 |

**OK — moyenne confirmée par recalcul indépendant.**

## 2. Cohérence de l'actif sous-jacent entre les deux composants

Écart max entre les rendements NDX des deux pipelines (#115 vs GARCH) sur la fenêtre commune : 1.76e-15
**OK — même actif sous-jacent (écart = arrondis numériques uniquement).**

## 3. Test anti-lookahead (mutation du futur d'un composant, vérifie l'absence de fuite croisée)

Écart sur la position combinée passée (avant mutation, marge 10j) : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
