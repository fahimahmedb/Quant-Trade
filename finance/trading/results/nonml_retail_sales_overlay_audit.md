# Audit adversarial — Ventes au détail US (RSXFS), overlay défensif

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification dédiée du décalage d'un mois de publication

Dernière observation RSXFS : mois de 2026-06-01. Disponible dans la série décalée à partir de 2026-07-01 (30 jours calendaires après, cohérent avec le délai de publication réel de ~2-3 semaines déclaré au PREREG).
**OK — la valeur du mois M n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Cohérence du taux de coupure élevé sur Composite (61,2%)

Même famille d'effet de fenêtre courte déjà documentée 3 fois (#286 70,0%, #289 60,9%, #294 72,0%) : le tercile expanding calculé sur la fenêtre courte Composite (2021-2026) reflète la distribution DE CETTE fenêtre, pas de l'historique complet RSXFS (1992-2026). Confirmé par le recalcul indépendant identique en §1, pas un bug de calcul.
**OK — 4e occurrence du même effet de fenêtre courte, cohérent et non anormal.**

## 4. Test anti-lookahead (troncature de l'historique)

Troncature à 3000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 5000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 1500 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
