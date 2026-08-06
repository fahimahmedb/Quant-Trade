# Audit adversarial — Porte majoritaire (≥2/3) défaut carte + NFCI + BAA10Y

## 1. Recalcul indépendant du vote majoritaire (tri manuel, sans np.percentile)

Échantillon d'une date sur 250 par marché (tri Python pur sur l'historique complet à chaque pas serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#298).

| Marché | % actif ≥2/3 | % actif ET (3/3) | % actif OU (≥1/3) | ET⊆maj ? | maj⊆OU ? | Dates échantillonnées | Désaccords |
|---|---|---|---|---|---|---|---|
| Composite (5 ans) | 28.1% | 16.5% | 78.0% | OUI | OUI | 5 | 0 |
| NDX (40 ans) | 19.7% | 5.8% | 51.0% | OUI | OUI | 36 | 0 |
| Russell 2000 | 19.4% | 5.6% | 53.9% | OUI | OUI | 36 | 0 |
| S&P 500 | 14.5% | 4.1% | 45.4% | OUI | OUI | 36 | 0 |
| DAX | 20.9% | 7.8% | 40.6% | OUI | OUI | 28 | 0 |

**OK — vote majoritaire confirmé cohérent avec les relations ET(3)⊆majorité⊆OU(3), recalcul indépendant identique sur l’échantillon (0 désaccord).**

## 2. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
