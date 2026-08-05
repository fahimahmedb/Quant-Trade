# Audit adversarial — Overlay de vol-targeting estimateur Rogers-Satchell

## 1. Recalcul totalement indépendant (variance Rogers-Satchell recalculée depuis OHLC)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 1.11e-15 |
| NDX (40 ans) | 8.88e-16 |
| Russell 2000 | 1.11e-15 |
| S&P 500 | 1.33e-15 |
| DAX | 2.22e-15 |

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
