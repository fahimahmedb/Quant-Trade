# Audit adversarial — Overlay vol-targeting gaté par la profondeur de drawdown glissante

## 1. Recalcul totalement indépendant (maximum glissant et drawdown par boucle explicite, médiane par tri manuel)

| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 938 |
| NDX (40 ans) | 0 | 9960 |
| Russell 2000 | 0 | 9469 |
| S&P 500 | 0 | 13939 |
| DAX | 0 | 6464 |

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
