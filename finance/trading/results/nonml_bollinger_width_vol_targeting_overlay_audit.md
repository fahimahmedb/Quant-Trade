# Audit adversarial — Overlay vol-targeting gaté par la largeur de bande de Bollinger glissante

## 1. Recalcul totalement indépendant (moyenne/écart-type par boucle explicite, médiane par tri manuel)

| Marché | Désaccords porte (hors marge de fenêtre) | Séances comparées |
|---|---|---|
| Composite (5 ans) | 0 | 978 |
| NDX (40 ans) | 0 | 10000 |
| Russell 2000 | 0 | 9509 |
| S&P 500 | 0 | 13979 |
| DAX | 0 | 6504 |

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
