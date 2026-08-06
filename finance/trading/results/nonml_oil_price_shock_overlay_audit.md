# Audit adversarial — Choc de prix du pétrole WTI (DCOILWTICO), overlay défensif

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Épisode du prix négatif du 20/04/2020 (événement COVID réel, pas un bug)

Valeur négative confirmée dans la source FRED brute : [{'observation_date': Timestamp('2020-04-20 00:00:00'), 'DCOILWTICO': -36.98}] (crise de stockage COVID, 20/04/2020, documentée publiquement — pas une erreur de données).
`log(WTI(t)/WTI(t-21))` autour de cet épisode produit bien `NaN` (valeur négative au dénominateur ou numérateur) plutôt qu'un résultat numérique erroné : NaN confirmé.
**OK — le NaN se propage correctement, exclu du calcul du tercile (np.isfinite), aucune valeur aberrante silencieuse.**

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 6000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 8500 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
