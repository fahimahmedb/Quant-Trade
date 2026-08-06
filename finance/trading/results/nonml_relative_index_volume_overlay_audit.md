# Audit adversarial — Volume RELATIF de l'indice (ratio à MA252)

## 1. Recalcul indépendant du ratio et de la porte (sans pandas.rolling/np.percentile)

Échantillon d'une date sur 250 (recalcul complet du ratio par boucle Python pure sur l'historique complet serait prohibitif — même logique d'échantillonnage que l'audit du #282/#296/#306).

| Marché | % actif | Dates échantillonnées | Désaccords ratio | Désaccords porte |
|---|---|---|---|---|
| NDX (40 ans) | 29.9% | 41 | 0 | 0 |
| Russell 2000 | 31.5% | 39 | 0 | 0 |
| S&P 500 | 29.7% | 56 | 0 | 0 |
| DAX | 27.2% | 27 | 0 | 0 |

**OK — recalcul indépendant identique sur l’échantillon (0 désaccord, ratio et porte).**

## 2. Confirmation que la normalisation corrige la non-stationnarité

Taux d'activation observés : NDX 29,9%, Russell 2000 31,5%, S&P 500 29,7%, DAX 27,2% — tous proches du niveau théorique attendu pour un tercile (33,3%), contrairement au #306 (volume brut) où NDX/Russell 2000/S&P 500 étaient à 83-93%. **Confirmé** : la normalisation par le volume moyen glissant 252j corrige bien l'effet de non-stationnarité identifié — le signal redevient un vrai tercile, mais reste FAIL sur le critère de rendement/Sharpe malgré cette correction (le problème n'était pas SEULEMENT la non-stationnarité, le signal lui-même ne porte pas d'edge exploitable).

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la porte sur le passé est inchangée quel que soit le futur tronqué.**
