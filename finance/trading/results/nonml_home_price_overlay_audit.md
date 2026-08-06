# Audit adversarial — Indice des prix immobiliers Case-Shiller US, overlay défensif

## 1. Recalcul indépendant (searchsorted explicite, side="right" inclusif)

| Marché | Séances | Désaccords |
|---|---|---|
| Composite (5 ans) | 1251 | 0 |
| NDX (40 ans) | 10273 | 0 |
| Russell 2000 | 9782 | 0 |
| S&P 500 | 14252 | 0 |
| DAX | 6777 | 0 |

**OK — position confirmée par recalcul indépendant (0 désaccord).**

## 2. Vérification dédiée du décalage de 2 mois de publication

Dernière observation CSUSHPISA : mois de 2026-05-01. Disponible dans la série décalée à partir de 2026-07-01 (61 jours calendaires après, cohérent avec le délai de publication réel de ~2 mois déclaré au PREREG).
**OK — la valeur du mois M n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Investigation du taux de coupure élevé sur Composite (72,0%)

Le tercile expanding est calculé INDÉPENDAMMENT par marché, à partir de la première date valide de CE marché (même convention que #191/#193/#195/#198/#199/#286/#289). Même schéma que le #286 (70,0%) et le #289 (60,9%) : la fenêtre courte Composite (2021-2026) coïncide avec un ralentissement réel et documenté du marché immobilier américain (hausse des taux hypothécaires post-2022), plaçant mécaniquement la majorité des trimestres récents dans le tercile expanding le plus bas de LEUR PROPRE fenêtre.
**OK — comportement attendu de la méthodologie tercile expanding sur fenêtre courte, cohérent avec un contexte macro réel (3e occurrence du même schéma), pas une anomalie de calcul.**

## 4. Test anti-lookahead (troncature de l'historique)

Troncature à 3000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 5000 séances, comparaison sur les 1500 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 1500 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
