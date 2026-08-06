# Audit adversarial — Mises en chantier de logements US (HOUST), overlay défensif

## 1. Recalcul indépendant (searchsorted explicite)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification dédiée du décalage d'un mois de publication

Dernière observation HOUST : mois de 2026-06-01. Disponible dans la série décalée à partir de 2026-07-01 (30 jours calendaires après, cohérent avec le délai de publication réel de ~3 semaines déclaré au PREREG).
**OK — la valeur du mois M n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
