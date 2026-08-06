# Audit adversarial — Overlay défensif vitesse du taux court DGS3MO

## 1. Recalcul indépendant (tri+interpolation manuelle, sans np.percentile)

Échantillon d'une date sur 300 (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que les audits PIT (`check_dates = post_2015[::400]`)).

| Marché | Séances | Dates échantillonnées | Désaccords |
|---|---|---|---|
| Composite (5 ans) | 1251 | 4 | 0 |
| NDX (40 ans) | 10273 | 35 | 0 |
| Russell 2000 | 9782 | 33 | 0 |
| S&P 500 | 14252 | 38 | 0 |
| DAX | 6777 | 23 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord sur l’échantillon).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
