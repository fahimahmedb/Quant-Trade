# Audit — lot 3 et clôture de la campagne de reproductibilité

Recalcul **indépendant** : cet audit n'importe rien du script de mesure.

## Contrôle 1 — trois tirages reproductibles et disjoints deux à deux

- vivier recompté : **290**
- échantillon du lot 3 redérivé identique au publié : **oui** ✔
- paires de lots ayant un script commun : **0** ✔

La disjonction **deux à deux** est ce qui autorise le cumul. Sans elle, un même
script compterait deux fois au dénominateur et la borne serait **fausse dans le
sens flatteur**. L'audit la vérifie sur les **trois** paires, pas seulement sur la
dernière.

## Contrôle 2 — régime tenu

- rapports publiés **modifiés** en fin de cycle : **0** ✔
- sentinelles subsistantes : **0** ✔

## Contrôle 3 — la borne cumulée, recalculée

Ce lot : **22** identiques, **1** structurelle(s), **0** substantielle(s), **1** non concluant(s).

| | Dénominateur | Borne à 95 % | Divergents encore possibles |
|---|---|---|---|
| cumul #438 + #440 | 47 | 6.2 % | ~17 |
| **cumul des trois lots** | 69 | 4.2 % | ~12 |

**Le chiffre bouge pour une raison arithmétique, pas parce que le dépôt serait
devenu plus reproductible** : 2 des 24 tirages sortent du
dénominateur (structurelle et non concluant). Un lot « meilleur » aurait retenu
24 tirages et donné une borne légèrement plus basse — cela n'aurait rien dit de
plus sur les rapports.

## Clôture de la campagne — selon la règle fixée avant le tirage

Le pré-enregistrement déclarait :

> « Ce lot est le **dernier** de la campagne, sauf si une divergence
> **substantielle** apparaît — auquel cas la campagne reprend pour l'instruire. »

**0 divergence substantielle** → la campagne est **CLOSE** à **p ≤ 4.2 %**.

La clôture n'était **pas conditionnée au chiffre obtenu** : elle valait pour
4,1 % comme pour 4,5 %. C'est ce qui la distingue d'un arrêt décidé une fois le
résultat connu.

## Bilan des huit cycles (#434 → #441)

| Cycle | Borne | Statut |
|---|---|---|
| #434 | 22,1 % | caduque (#436) |
| #435 | 8,0 % | **caduque** (#436) |
| #436 | — | divergence structurelle, borne annulée |
| #437 | — | critère incomplet, borne non publiée |
| #438 | 12,2 % | remplacée par le cumul |
| #440 | 6,2 % | remplacée par le cumul |
| **#441** | **4.2 %** | **finale** |

**Ce que la campagne a établi :**

1. Sur **69** tirages retenus, **aucune divergence substantielle** — aucun
   rapport de stratégie ne s'est révélé périmé par rapport à son code.
2. Il reste place pour **~12** divergences non détectées
   sur 290 rapports. « Jamais observée » n'est pas « inexistante ».
3. **Mon outillage de diagnostic**, lui, dérive par construction : les rapports
   qui comptent le dépôt changent à chaque cycle. Six sont désormais marqués
   (#439).

**Ce qu'elle a coûté :** trois remises à zéro, deux critères écrits trop vite, une
fuite de processus orphelins ayant réécrit un rapport publié. Aucun de ces défauts
n'a été trouvé par la mesure elle-même — tous par une relecture ou une inspection
de l'arbre. C'est la leçon que je retiens plutôt que le 4,2 %.

## Conclusion

| Critère pré-enregistré | Attendu | Obtenu | |
|---|---|---|---|
| tirage reproductible, disjoint des 48 | oui | oui | ✔ |
| divergents classés par le test | tous | 1 | ✔ |
| rapports modifiés / sentinelles | 0 / 0 | 0 / 0 | ✔ |
| borne publiée si 0 substantielle | oui | **4.2 %** | ✔ |
| clôture prononcée | oui si 0 substantielle | oui | ✔ |

**Les cinq contrôles passent. Campagne close.**

Ce cycle ne change aucun verdict de stratégie et n'en produit aucun.
