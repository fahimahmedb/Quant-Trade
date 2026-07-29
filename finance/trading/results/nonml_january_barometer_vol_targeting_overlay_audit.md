# Audit adversarial — Overlay vol-targeting gaté par January Barometer

## 1. Recalcul indépendant (porte annuelle + position, boucle explicite)

| Marché | Écart porte (nb j.) | Écart position max |
|---|---|---|
| Composite (5 ans) | 0 | 7.99e-15 |
| NDX (40 ans) | 0 | 6.35e-14 |
| Russell 2000 | 0 | 3.33e-14 |
| S&P 500 | 0 | 9.88e-14 |
| DAX | 0 | 3.82e-14 |

**OK — porte et position confirmées par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures (ni sur la porte annuelle ni sur le vol-targeting).**
