# Audit adversarial — Position graduée par nombre de votes (défaut carte + NFCI + BAA10Y)

## 1. Recalcul indépendant du nombre de votes et de la position (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298/#299).

| Marché | Dates échantillonnées | Désaccords votes | Désaccords position |
|---|---|---|---|
| Composite (5 ans) | 5 | 0 | 0 |
| NDX (40 ans) | 36 | 0 | 0 |
| Russell 2000 | 36 | 0 | 0 |
| S&P 500 | 36 | 0 | 0 |
| DAX | 28 | 0 | 0 |

**OK — recalcul indépendant identique sur l’échantillon (0 désaccord, votes et position).**

## 2. Monotonie de la fonction position(votes)

| Votes | Position attendue |
|---|---|
| 0 | 1.0000x |
| 1 | 0.8333x |
| 2 | 0.6667x |
| 3 | 0.5000x |

**OK — strictement décroissante sur les 4 valeurs possibles.**

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
