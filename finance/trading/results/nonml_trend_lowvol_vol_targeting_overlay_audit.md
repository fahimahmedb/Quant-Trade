# Audit adversarial — Overlay vol-targeting gaté par double porte tendance+vol faible

## 1. Recalcul totalement indépendant (boucle explicite jour par jour)

| Marché | Écart position max (hors marge de fenêtre) |
|---|---|
| Composite (5 ans) | 7.99e-15 |
| NDX (40 ans) | 6.35e-14 |
| Russell 2000 | 3.33e-14 |
| S&P 500 | 1.04e-13 |
| DAX | 4.22e-14 |

**OK — position confirmée par recalcul totalement indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture économique du FAIL** : la porte combinée (intersection tendance ET vol faible) est active 29-46% du temps, nettement moins que la tendance seule (#47, 55-75%) -- le filtre de vol faible retire des jours de tendance haussière PENDANT lesquels la vol est déjà remontée (souvent des rallyes tardifs de cycle), réduisant l'exposition amplifiée précisément quand elle aurait le plus profité au rendement composé. Contrairement au calendrier (#54) et à la breadth (#57), qui PORTENT une information directionnelle propre en plus de la tendance, le filtre de vol faible (#58) n'en porte aucune -- l'ajouter en AND ne fait que rétrécir la fenêtre d'exposition sans ajouter de sélectivité utile.
