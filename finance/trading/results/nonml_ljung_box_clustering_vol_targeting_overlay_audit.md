# Audit adversarial — Overlay vol-targeting gaté par la statistique de Ljung-Box glissante

## 1. Formule de Q (boucles Python pures, sans numpy vectorisé, sous-échantillon représentatif : 100 premières + 100 dernières fenêtres testables)

| Marché | Écart relatif max sur Q | Fenêtres vérifiées |
|---|---|---|
| Composite (5 ans) | 2.77e-15 | 200 |
| NDX (40 ans) | 3.27e-15 | 200 |
| Russell 2000 | 5.62e-15 | 200 |
| S&P 500 | 4.83e-15 | 200 |
| DAX | 6.22e-15 | 200 |

**OK — formule Q confirmée (boucles pures Python, sous-échantillon).**

## 2. Logique de porte (médiane glissante par tri manuel, historique complet)

| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 746 |
| NDX (40 ans) | 0 | 9768 |
| Russell 2000 | 0 | 9277 |
| S&P 500 | 0 | 13747 |
| DAX | 0 | 6272 |

**OK — porte confirmée par recalcul indépendant de la médiane (tri manuel).**

## 3. Test anti-lookahead (perturbation du futur, close)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**
