# Audit adversarial — Porte combinée (ET) défaut carte de crédit + NFCI

## 1. Recalcul indépendant de la porte ET (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282, vitesse des taux).

| Marché | % actif ET | % actif défaut seul | % actif NFCI seul | ET ⊆ défaut ? | ET ⊆ NFCI ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 24.3% | 70.0% | 32.2% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 5.8% | 18.5% | 18.3% | OUI | OUI | 36 | 0 |
| Russell 2000 | 5.6% | 18.5% | 17.6% | OUI | OUI | 36 | 0 |
| S&P 500 | 4.1% | 18.5% | 5.9% | OUI | OUI | 36 | 0 |
| DAX | 8.5% | 18.1% | 22.7% | OUI | OUI | 28 | 0 |

**OK — porte ET confirmée sous-ensemble strict des deux portes individuelles, recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
