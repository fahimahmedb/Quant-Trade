# Audit adversarial — Overlay vol-targeting gaté par régime de vol faible

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

**Lecture économique du FAIL** : la porte est active 40-51% du temps sur les 5 marchés (fréquence comparable aux portes de tendance), mais contrairement au signal de tendance (#47), au calendrier (#54) ou à la breadth (#57), un régime de vol réalisée faible n'est pas systématiquement corrélé à un régime haussier -- il capture aussi des phases de consolidation baissière calme (ex. DAX, seul échec net des deux jambes). Le mécanisme hiérarchique amplifie donc parfois l'exposition sans biais directionnel favorable, ce qui explique le résultat mitigé (2/5) malgré un mécanisme de vol-targeting identique à celui qui a réussi ailleurs.
