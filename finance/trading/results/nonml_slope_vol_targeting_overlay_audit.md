# Audit adversarial — Overlay vol-targeting gaté par pente SMA200

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

**Lecture économique du PASS** : la porte pente SMA200 est active 51,8-68,5% du temps, une fréquence comparable au golden cross (#67, 48,8-66,8%) mais avec un résultat net supérieur (4/5 contre 3/5) -- le signal de pente semble mieux capturer les régimes réellement porteurs pour le vol-targeting que le croisement de moyennes. Complète la famille des 5 signaux de tendance testés comme porte du mécanisme hiérarchique : 52w-high (#47, PASS 4/5) et pente SMA200 (#68, PASS 4/5) sont les deux signaux les plus robustes, le golden cross (#67, FAIL 3/5) le moins performant des trois signaux de tendance testés dans ce rôle.
