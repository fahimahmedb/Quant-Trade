# Audit adversarial — Overlay de vol-targeting estimateur EWMA

## 1. Recalcul totalement indépendant (récursion EWMA recalculée par boucle explicite)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 2.22e-16 |
| NDX (40 ans) | 2.22e-16 |
| Russell 2000 | 2.22e-16 |
| S&P 500 | 4.44e-16 |
| DAX | 2.22e-16 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
