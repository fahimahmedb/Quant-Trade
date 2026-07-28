# Audit adversarial — Overlay de vol-targeting défensif uniquement

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.std)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 2.33e-15 |
| NDX (40 ans) | 1.57e-14 |
| Russell 2000 | 8.66e-15 |
| S&P 500 | 2.42e-14 |
| DAX | 1.01e-14 |

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

**Lecture économique du FAIL (0/5)** : en retirant toute possibilité de levier (CAP=1.0x au lieu de 2.0x au #43), le mécanisme perd exactement les épisodes d'exposition amplifiée qui permettaient au #43 de battre le rendement Buy&Hold sur 3/5 marchés -- confirme le même écueil structurel déjà identifié en tout début de backlog (cycles #2/#6/#8) : un design qui ne peut JAMAIS dépasser 1.0x d'exposition ne peut pas battre le rendement composé de Buy&Hold, même en réduisant fortement le MDD (ici Sharpe amélioré sur 5/5, MDD massivement réduit partout, mais rendement systématiquement inférieur).
