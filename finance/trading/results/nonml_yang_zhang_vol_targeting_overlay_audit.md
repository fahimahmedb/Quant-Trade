# Audit adversarial — Overlay de vol-targeting estimateur Yang-Zhang

## 1. Recalcul totalement indépendant (composantes recalculées bar par bar, variance manuelle)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 0.00e+00 |
| NDX (40 ans) | 0.00e+00 |
| Russell 2000 | 0.00e+00 |
| S&P 500 | 0.00e+00 |
| DAX | 0.00e+00 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur, OHLC)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
