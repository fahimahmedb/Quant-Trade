# Audit adversarial — Effet lunaire (nouvelle lune)

## 1. Recalcul indépendant de la fenêtre (itération des nouvelles lunes successives, sans modulo vectorisé)

| Marché | % temps en fenêtre | Désaccords | Séances |
|---|---|---|---|
| Composite (5 ans) | 47.5% | 0 | 1251 |
| NDX (40 ans) | 47.5% | 0 | 10273 |
| Russell 2000 | 47.5% | 0 | 9782 |
| S&P 500 | 47.6% | 0 | 14252 |
| DAX | 47.8% | 0 | 6777 |

**OK — recalcul indépendant (méthode différente, itération explicite) identique sur toutes les dates (0 désaccord).**

## 2. Cohérence interne de la fréquence théorique

Fraction théorique attendue : 2×7/29.530589 = 47.4%. Les fractions observées ci-dessus (47,4-47,8%) sont cohérentes avec cette valeur théorique (légère variation due au calendrier de bourse, pas une anomalie).

## 3. Absence de fuite par construction

Le masque `new_moon_window_mask` ne dépend QUE de la date (formule astronomique déterministe), jamais du prix, du volume ni d'aucune donnée de marché — aucune fuite temporelle possible par construction (contrairement aux signaux dérivés de prix/macro qui nécessitent un test de troncature). Confirmé par le recalcul indépendant ci-dessus utilisant une méthode de calcul de date totalement distincte (itération vs modulo).
