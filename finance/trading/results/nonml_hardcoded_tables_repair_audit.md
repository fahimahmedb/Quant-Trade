# Audit adversarial — le cycle qui refuse ses deux modifications (#482)

**Un cycle de modification qui ne modifie rien est le cas où la
complaisance est la plus facile** : il suffit de déclarer la réparation
impossible. Cet audit ne vérifie donc pas des chiffres — **il vérifie les
deux refus**, chacun par une route propre.

## Refus 1 — « ce n'est pas un défaut, c'est une citation »

Route indépendante : compter les délimiteurs ` ``` ` écrits par le script
et déterminer si les lignes incriminées tombent **à l'intérieur** d'un
bloc ouvert.

| Motif | Dans un bloc de citation | Hors de tout bloc |
|---|---|---|
| large — « couverture non-ML » | **2** | **1** |
| **précis** — la ligne portant le chiffre | **2** | **0** |

**Le motif large capte une occurrence de trop** : la ligne 72 du
script nomme « la couverture non-ML » **en prose**, sans chiffre. Ce
n'est pas un tableau, et le #479 ne l'avait pas incriminée.

**C'est mon motif d'audit qui était trop lâche**, et je publie les
deux comptes plutôt que le seul qui m'arrange.

> **Le refus est fondé.** Toutes les occurrences sont à l'intérieur
> d'un bloc de citation. Les réparer aurait falsifié un texte cité —
> et le point décimal de `73.2 %`, que le #479 tenait pour un indice
> à charge, en est au contraire la **preuve**.

## Refus 2 — « la grandeur n'est pas recalculable depuis ce script »

Route indépendante : énumérer par **AST** tous les noms liés du module —
ce que le script « sait » — et chercher ceux qui pourraient porter
l'univers du balayage #415.

- noms liés dans le module : **34**
- noms évoquant un univers de candidats / un balayage : **0**
- imports du module : **Path, np, sys**

> **Le refus est fondé.** Aucun nom du module ne porte l'univers du
> balayage, et le module n'importe aucun script du dépôt qui le
> fournirait. La grandeur est **historique** : son univers n'est plus
> reconstructible depuis ce fichier.

**Ce n'est pas une excuse commode** : le pré-enregistrement
interdisait de changer la population, et substituer un décompte
moderne aurait produit **un chiffre qui mesure autre chose**.

## Le dépôt est-il réellement intact ?

Le cycle annonce **0 ligne de code modifiée**. Vérifié par `git diff`,
hors ses propres fichiers :

- fichiers modifiés sous `scripts/` ou `results/` : **0**

> **Aucune modification.** L'annonce est vérifiée, pas crue.

## Les prédictions ont-elles été réinterprétées après coup ?

Les trois prédictions supposaient que la réparation aurait lieu. Un cycle
qui ne répare pas est tenté de les déclarer « sans objet ».

| Contrôle | Résultat |
|---|---|
| les 3 prédictions sont confrontées, pas annulées | **OUI** |
| le rapport dit qu'il ne les réinterprète pas | **OUI** |
| le total du #479 est corrigé à la baisse et dit | **OUI** |
| le rapport publie ce que l'idempotence ne prouve pas | **OUI** |
| aucun rapport régénéré n'est committé | **OUI** |

> **Les prédictions sont confrontées telles qu'écrites**, sur les
> scripts non modifiés — la lecture la plus défavorable.

## Verdict

**CONCORDANT** — les **deux refus** sont fondés par une route indépendante, le dépôt
est vérifié intact, et **5/5** contrôles de protocole sont tenus.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).