# Audit adversarial — Taux de défaut hypothécaire US (DRSFRMACBS), overlay défensif

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification dédiée du décalage d'un trimestre de publication

Dernière observation DRSFRMACBS : trimestre de 2026-01-01. Disponible dans la série décalée à partir de 2026-04-01 (90 jours calendaires après, cohérent avec le délai de publication réel de ~2-3 mois déclaré au PREREG).
**OK — la valeur du trimestre T n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Cohérence des taux de coupure par marché

Le tercile expanding est calculé INDÉPENDAMMENT par marché, à partir de la première date valide de CE marché (même convention que #191/#193/#195/#198/#199/#286). Contrairement au #286 (crédit carte, Composite anormalement élevé à 70% contre ~18% ailleurs), le taux de coupure Composite ici (14,9%) est du même ordre de grandeur — légèrement PLUS BAS que les autres marchés (~32%), pas un effet de fenêtre courte extrême cette fois. Cohérent avec le recalcul indépendant identique en §1, aucune anomalie de calcul.
**OK — pas d'anomalie de taux de coupure à investiguer, contrairement au #286.**

## 4. Test anti-lookahead (troncature de l'historique)

Troncature à 3000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 5000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 1500 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
