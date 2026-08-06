# Audit adversarial — Overlay avance-retard cross-marché DAX→marchés US

## 1. Recalcul indépendant du signal (searchsorted explicite)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |

**OK — signal confirmé par recalcul indépendant (0 désaccord).**

## 2. Test anti-lookahead (perturbation du futur DAX)

Mutation appliquée à partir de 2022-06-01, contrôle à 2018-06-01.
Écart de signal à une date antérieure à la mutation : 0.00e+00
**OK — aucune fuite, le passé est bien inchangé.**

## 3. Cohérence de la fenêtre testée

DAX démarre le 1999-11-01 — le test sur NDX (historique complet depuis 1985-10-01) est donc restreint à partir de cette date, PAS l'historique complet 40 ans. Signalé honnêtement, cohérent avec le nombre de séances test (6711, ≈26,7 ans) rapporté dans le résultat principal — pas un bug.
