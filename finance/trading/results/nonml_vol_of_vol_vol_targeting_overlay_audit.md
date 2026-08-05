# Audit adversarial — Overlay vol-targeting gaté par la vol-de-la-vol glissante

## 1. Recalcul totalement indépendant de la porte (boucle explicite, écart-type et médiane manuels)

| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 726 |
| NDX (40 ans) | 0 | 9748 |
| Russell 2000 | 0 | 9257 |
| S&P 500 | 0 | 13727 |
| DAX | 0 | 6252 |

**OK — porte confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
