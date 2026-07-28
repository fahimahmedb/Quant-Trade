# Audit adversarial — Overlay de vol-targeting continu

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.std)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 7.99e-15 |
| NDX (40 ans) | 1.06e-13 |
| Russell 2000 | 4.40e-14 |
| S&P 500 | 1.76e-13 |
| DAX | 7.28e-14 |

**OK — position confirmée par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture** : le FAIL (3/5, critère renforcé ≥4/5 non atteint) masque un profil de risque nettement amélioré -- le MDD est réduit de façon spectaculaire sur tous les marchés (ex. NDX -82,9%→-48,3%, Composite -36,4%→-24,8%), et le Sharpe s'améliore sur 4/5 marchés. Seul le rendement total échoue à dépasser Buy&Hold sur 2 marchés (Composite, DAX) -- cohérent avec la règle renforcée qui exige les DEUX jambes simultanément, et illustre bien pourquoi le vol-targeting est un outil de gestion du RISQUE plutôt qu'un générateur d'edge de rendement pur (même conclusion que l'Étape C du projet : "utile pour le risk management, pas pour prédire une direction").
