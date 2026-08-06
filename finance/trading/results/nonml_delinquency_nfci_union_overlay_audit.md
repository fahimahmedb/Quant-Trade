# Audit adversarial — Porte combinée (OU) défaut carte de crédit + NFCI

## 1. Recalcul indépendant de la porte OU (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296).

| Marché | % actif OU | % actif défaut seul | % actif NFCI seul | défaut ⊆ OU ? | NFCI ⊆ OU ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 77.9% | 70.0% | 32.2% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 30.9% | 18.5% | 18.3% | OUI | OUI | 36 | 0 |
| Russell 2000 | 30.5% | 18.5% | 17.6% | OUI | OUI | 36 | 0 |
| S&P 500 | 20.2% | 18.5% | 5.9% | OUI | OUI | 36 | 0 |
| DAX | 32.3% | 18.1% | 22.7% | OUI | OUI | 28 | 0 |

**OK — porte OU confirmée sur-ensemble des deux portes individuelles, recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
