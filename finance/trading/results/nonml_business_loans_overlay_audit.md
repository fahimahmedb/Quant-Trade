# Audit adversarial — Croissance des prêts commerciaux et industriels US (BUSLOANS), overlay défensif

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

Dernière observation BUSLOANS : mois de 2026-06-01. Disponible dans la série décalée à partir de 2026-07-01 (30 jours calendaires après, cohérent avec le délai de publication réel de ~1 mois déclaré au PREREG).
**OK — la valeur du mois M n’apparaît jamais avant sa date de disponibilité décalée.**

## 3. Investigation du MDD identique à Buy&Hold (Composite, Russell 2000, S&P 500)

- **Composite (5 ans)** : pire drawdown Buy&Hold atteint à l'indice 368 (sur 1250). Porte défensive active à ce point précis : NON.
- **Russell 2000** : pire drawdown Buy&Hold atteint à l'indice 5418 (sur 9781). Porte défensive active à ce point précis : NON.
- **S&P 500** : pire drawdown Buy&Hold atteint à l'indice 9888 (sur 14251). Porte défensive active à ce point précis : NON.

**Explication** : quand la porte n'est PAS active au pic du pire drawdown (cas ci-dessus), le MDD de l'overlay et de Buy&Hold coïncident exactement PAR CONSTRUCTION — l'overlay est à 1,0x (identique à Buy&Hold) précisément pendant la pire chute historique. Ce n'est pas un bug, c'est une conséquence directe et attendue de la définition de la porte (elle réagit à la faiblesse du crédit bancaire, pas nécessairement synchrone avec le pic exact du drawdown de l'indice).
**OK — comportement cohérent avec la construction de la porte, pas une anomalie de calcul.**

## 4. Test anti-lookahead (troncature de l'historique)

Troncature à 4000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 7000 séances, comparaison sur les 2000 premières positions : identique.
Troncature à 9000 séances, comparaison sur les 2000 premières positions : identique.

**OK — aucune fuite, la position sur le passé est inchangée quel que soit le futur tronqué.**
