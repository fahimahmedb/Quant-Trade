# Audit adversarial — Overlay vol-targeting gaté par le spread décile de momentum

## 1. Recalcul indépendant (boucle Python explicite + tri manuel, sans np.sort vectorisé sur la matrice)

| Date (indice) | Écart absolu |
|---|---|
| 252 | 2.22e-16 |
| 652 | 2.22e-16 |
| 1052 | 0.00e+00 |

**OK — spread décile confirmé par recalcul indépendant (3 dates).**

## 2. Test anti-lookahead (mutation des 20% de données les plus récentes)

Écart sur le spread calculé à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
