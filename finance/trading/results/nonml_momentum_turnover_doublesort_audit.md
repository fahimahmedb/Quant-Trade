# Audit adversarial — Momentum 12-1 + double-tri turnover/volume-dollars

## 1. Recalcul indépendant de la sélection à un échantillon de dates de rebalancement

| Date (indice) | Sélection finale identique | Emboîtement final⊆tercile momentum⊆éligibles |
|---|---|---|
| 252 | OUI | OUI |
| 462 | OUI | OUI |
| 672 | OUI | OUI |
| 882 | OUI | OUI |
| 1092 | OUI | OUI |
| 1302 | OUI | OUI |

**OK — sélection confirmée par recalcul indépendant sur toutes les dates échantillonnées.**
**OK — emboîtement final⊆tercile momentum⊆éligibles vérifié partout.**

## 2. Vérification du décalage causal (`lag_one_day`)

**OK — weights_après_lag[t] == weights_avant_lag[t-1] partout, ligne 0 nulle.**

## 3. Test anti-lookahead (perturbation du futur : prix et volume)

Écart momentum à une date antérieure à la mutation : 0.00e+00
Écart turnover moyen à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**
