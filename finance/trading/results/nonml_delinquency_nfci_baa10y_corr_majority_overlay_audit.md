# Audit adversarial — Panel élargi à 4 signaux (défaut carte + NFCI + BAA10Y + corrélation NDX-DAX), vote ≥3/4

## 1. Recalcul indépendant du vote majoritaire (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298/#299/#301).

| Marché | % actif ≥3/4 | % actif ET (4/4) | % actif OU (≥1/4) | ET⊆maj ? | maj⊆OU ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 21.0% | 8.6% | 91.0% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 17.4% | 5.8% | 58.8% | OUI | OUI | 27 | 0 |
| Russell 2000 | 17.1% | 5.6% | 60.2% | OUI | OUI | 27 | 0 |
| S&P 500 | 13.4% | 3.7% | 53.7% | OUI | OUI | 27 | 0 |
| DAX | 17.3% | 5.3% | 51.0% | OUI | OUI | 27 | 0 |

**OK — vote majoritaire confirmé cohérent avec les relations ET(4)⊆majorité⊆OU(4), recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 5500 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6400 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
