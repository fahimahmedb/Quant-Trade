# Audit adversarial — Panel élargi à 6 signaux (défaut carte + NFCI + BAA10Y + corrélation NDX-DAX + MOVE + CPI), vote ≥5/6

## 1. Recalcul indépendant du vote majoritaire (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298/#299/#301/#304/#363).

| Marché | % actif ≥5/6 | % actif ET (6/6) | % actif OU (≥1/6) | ET⊆maj ? | maj⊆OU ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 12.6% | 4.3% | 91.1% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 6.1% | 1.0% | 70.0% | OUI | OUI | 24 | 0 |
| Russell 2000 | 6.1% | 1.0% | 71.0% | OUI | OUI | 24 | 0 |
| S&P 500 | 5.0% | 0.5% | 63.0% | OUI | OUI | 24 | 0 |
| DAX | 7.0% | 1.1% | 66.2% | OUI | OUI | 25 | 0 |

**OK — vote majoritaire confirmé cohérent avec les relations ET(6)⊆majorité⊆OU(6), recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 5000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
