# Audit adversarial — Overlay levé proximité plus haut 52-semaines (indice)

## 1. Recalcul indépendant (boucle explicite vs pandas.rolling.max)

| Marché | Écart masque (nb j., hors 252 premiers) |
|---|---|
| Composite (5 ans) | 0 |
| NDX (40 ans) | 0 |
| Russell 2000 | 0 |
| S&P 500 | 0 |
| DAX | 0 |

**OK — masque confirmé par recalcul indépendant.**

## 2. Test anti-lookahead (perturbation du futur)

| Marché | Décisions passées identiques après perturbation future |
|---|---|
| Composite (5 ans) | OUI |
| NDX (40 ans) | OUI |
| Russell 2000 | OUI |
| S&P 500 | OUI |
| DAX | OUI |

**OK — aucune fuite de données futures.**

**Lecture** : le signal "proximité du plus haut" coupe le levier dès que le marché s'éloigne de 5% de son sommet -- plus réactif à la baisse que SMA200 (qui attend un croisement de moyenne), ce qui explique une meilleure préservation du MDD sur plusieurs marchés (ex. DAX -69,1%→-69,1%, quasi inchangé, contre une dégradation nette au #29).
