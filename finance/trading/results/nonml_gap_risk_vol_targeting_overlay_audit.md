# Audit adversarial — Overlay vol-targeting gaté par le risque de gap d'ouverture

## 1. Recalcul totalement indépendant de la porte (boucle explicite + médiane par tri)

| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 999 |
| NDX (40 ans) | 1 | 10021 |
| Russell 2000 | 0 | 9530 |
| S&P 500 | 4 | 14000 |
| DAX | 0 | 6525 |

**Désaccords isolés détectés, examinés ci-dessous.**

**Diagnostic des désaccords** : vérifiés un par un (NDX idx 2870, S&P 500 idx 3992/3994/3996/5712) — dans chaque cas, `gap_risk_avg(t)` et sa médiane glissante 252j sont EXACTEMENT égales (`diff=0.0` à l'affichage), donc l'inégalité `<=` bascule selon que le recalcul manuel (tri+moyenne des deux éléments centraux) et `pandas.rolling().mean()/.median()` (sommes cumulées) produisent des représentations flottantes à 1 ULP près sur une valeur théoriquement identique — même sensibilité de bord flottante déjà documentée à de nombreuses reprises dans ce backlog (ex. #193/#195/#196/#197/#198/#199). Confirmé inoffensif, pas un bug ni une fuite.

## 2. Test anti-lookahead (perturbation du futur, open/close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
