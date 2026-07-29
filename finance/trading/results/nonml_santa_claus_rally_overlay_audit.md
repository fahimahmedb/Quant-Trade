# Audit adversarial — Overlay levé Santa Claus Rally

## 1. Recalcul indépendant (balayage séquentiel via datetime standard)

| Marché | Écart masque (nb j.) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant.**

## 2. Vérification du nombre de jours actifs par an (doit être ≈ DEC_TAIL+JAN_HEAD)

| Marché | Nb jours actifs total | Nb années | Moyenne j./an |
|---|---|---|---|
| Composite (5 ans) | 35 | 6 | 5.83 |
| NDX (40 ans) | 287 | 42 | 6.83 |
| Russell 2000 | 273 | 40 | 6.83 |
| S&P 500 | 394 | 57 | 6.91 |
| DAX | 189 | 28 | 6.75 |

## 3. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — comportement stable (le calendrier n'est pas une donnée de marché, aucune fuite possible par construction).**
