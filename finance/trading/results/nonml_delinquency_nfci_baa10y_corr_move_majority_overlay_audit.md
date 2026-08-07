# Audit adversarial — Panel élargi à 5 signaux (défaut carte + NFCI + BAA10Y + corrélation NDX-DAX + MOVE), vote ≥4/5

## 1. Recalcul indépendant du vote majoritaire (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298/#299/#301/#304).

| Marché | % actif ≥4/5 | % actif ET (5/5) | % actif OU (≥1/5) | ET⊆maj ? | maj⊆OU ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 17.6% | 7.5% | 91.1% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 9.0% | 4.3% | 59.9% | OUI | OUI | 24 | 0 |
| Russell 2000 | 8.8% | 4.3% | 60.9% | OUI | OUI | 24 | 0 |
| S&P 500 | 6.6% | 4.1% | 59.6% | OUI | OUI | 24 | 0 |
| DAX | 9.3% | 4.2% | 50.7% | OUI | OUI | 25 | 0 |

**OK — vote majoritaire confirmé cohérent avec les relations ET(5)⊆majorité⊆OU(5), recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 5000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
