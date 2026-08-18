# Audit adversarial — les gardes sans témoin (#481)

**Recalcul par une route différente** : la garde est identifiée par
**indentation** et le témoin cherché par balayage textuel des lignes de
colonne 4, au lieu de l'arbre syntaxique.

| Grandeur | Audit (indentation) | Rapport (AST) | Verdict |
|---|---|---|---|
| AVEC TÉMOIN | **33** | 36 | **ÉCART** |
| SANS TÉMOIN | **12** | 14 | **ÉCART** |
| GARDE NON NOMMÉE | **13** | 8 | **ÉCART** |

- **total audit** : **58** — **total rapport** : **58**

> **Les deux routes trouvent exactement le même nombre de titres
> conditionnels.** L'écart n'est donc **pas de couverture** mais
> **d'attribution** : les mêmes cas sont rangés différemment.

La cause est identifiable : la route par indentation remonte à la
**ligne de bloc la plus proche**, et une branche `else:` n'a pas la
forme `if <var>:`. Elle tombe donc en « garde non nommée » là où
l'AST, qui remonte au nœud `ast.If` parent, retrouve la variable.

C'est exactement ce que montre le déplacement : **+5**
en « non nommée », compensé à l'unité près sur les deux autres
colonnes.

> **L'AST est la route juste ici**, et le backtest n'est pas réaligné.
> Un `else` appartient bien au `if` qui le gouverne.

## Le majorant annoncé est-il vérifiable ?

Le rapport annonce que son total de « sans témoin » est un **majorant**,
parce que sa règle compte les deux branches d'un `if/else` alors qu'une
section paraît toujours. **Contrôle par une voie propre** : compter les
`ast.If` dont **les deux branches** écrivent un titre.

- `if/else` écrivant un titre **des deux côtés** : **3**

> **Le majorant est confirmé par une route indépendante.** Au moins un
> `if/else` exhaustif existe, donc au moins deux entrées du total sont
> des branches d'une alternative où une section paraît toujours.

**Le backtest n'a pas été corrigé** — c'est la bonne décision : sa
règle était fixée avant mesure, et la corriger après aurait été un
retuning. Le majorant est publié **avec sa cause**, ce qui permet à un
lecteur de retrancher lui-même.

## L'examen à la main était-il déclaré ?

C'est le point que le **#480** avait manqué. Vérifié dans le
pré-enregistrement, **avant** le rapport :

| Contrôle | Résultat |
|---|---|
| l'examen à la main est déclaré dans le PREREG | **OUI** |
| l'ordre de l'échantillon y est fixé | **OUI** |
| le verdict binaire y est défini | **OUI** |
| le rapport publie un défaut de sa propre règle | **OUI** |
| le rapport refuse de corriger la règle après mesure | **OUI** |
| le contrôle positif du #475 est publié | **OUI** |

> **La leçon du #480 est appliquée.** L'examen faisait partie du
> protocole ; il a trouvé un défaut de la règle **sans que la règle
> soit changée**, et le rapport le publie contre lui-même.

## Effets de bord du backtest

- écritures : **2** (`OUT` seul)
- `subprocess` / `checkout` / suppression : **0**

**Aucun effet de bord — le script ne fait que lire le disque.**

## Verdict

**DISCORDANT SUR L'ATTRIBUTION** — **0/3** colonnes se retrouvent,
mais **le total est identique** (**58** = **58**),
et **6/6** contrôles de
protocole sont tenus.

**Le désaccord porte sur le rangement des mêmes 58 cas, pas sur leur
nombre** — et sa cause est établie plutôt que constatée.


> **Rapport dépendant du dépôt** — il décrit l'état des scripts à la date
> de son exécution (cycles #436-#438).