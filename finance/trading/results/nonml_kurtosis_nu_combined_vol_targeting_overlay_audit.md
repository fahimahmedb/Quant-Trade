# Audit adversarial — Overlay vol-targeting gaté par la conjonction (ET) kurtosis + ν Student-t

Les deux sous-portes (kurtosis #219, ν Student-t #237) ont déjà été auditées intégralement à leurs propres cycles (0 désaccord pour la kurtosis ; fragilité numérique documentée mais anti-lookahead OK pour ν). Cet audit vérifie ce qui est nouveau : la conjonction logique ET et son application au mécanisme.

## 1. Recalcul indépendant de la conjonction (boucle explicite booléenne, sans l'opérateur `&` vectorisé)

| Marché | Désaccords conjonction (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 746 |
| NDX (40 ans) | 0 | 9768 |
| Russell 2000 | 0 | 9277 |
| S&P 500 | 0 | 13747 |
| DAX | 0 | 6272 |

**OK — conjonction confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, close, pipeline complet)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
