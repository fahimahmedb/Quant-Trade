# Robustesse (7a) — vérification des chiffres du backlog

**Ce n'est pas un retuning.** La règle d'extraction, les exclusions et le
critère restent ceux du pré-enregistrement. On perturbe la **borne** de
l'univers et les **lectures d'explication**.

## 1. La borne de l'univers

Déclarée à **#443**. Élargie vers l'arrière, sur des entrées que le
pré-enregistrement ne couvrait pas — **avec le risque réel que la
conclusion n'y survive pas.**

| Depuis | Entrées | Jetons | Typo | Frères | Citation | **Résidu** | Résidu / jeton |
|---|---|---|---|---|---|---|---|
| **#443** *(pré-enregistrée)* | 18 | 273 | 28 | 7 | 31 | **4** | 1,47 % |
| **#430** | 29 | 476 | 41 | 16 | 45 | **6** | 1,26 % |
| **#415** | 29 | 476 | 41 | 16 | 45 | **6** | 1,26 % |
| **#400** | 30 | 494 | 41 | 20 | 45 | **7** | 1,42 % |

Taux de résidu : de **1,26 %** à **1,47 %**, étendue **0,20 point**.

> **L'élargissement élargit moins qu'il n'y paraît.** Les bornes
> testées donnent **18, 29, 29, 30** entrées
> retenues : deux d'entre elles rendent le **même** nombre. Les
> entrées anciennes ne suivent pas toutes la convention « un
> `PREREG_` par entrée » et sortent du périmètre — le test porte donc
> sur **30** entrées au mieux, pas sur les 60 de l'intervalle.

C'est un **plateau** : la conclusion ne tient pas au choix de la borne.

> **Réserve, dite tout de suite :** les résidus des entrées antérieures à
> #443 **n'ont pas été vérifiés à la main**, contrairement aux quatre de
> l'univers déclaré. Ce tableau montre que leur *nombre* ne dérape pas ; il
> ne dit **pas** qu'aucun n'est une erreur.

## 2. Les lectures d'explication

Deux des quatre classifications ont été ajoutées **après** avoir vu le
résultat. Il faut donc montrer **de combien** le résidu en dépend, sur
l'univers pré-enregistré.

| Lecture | Jetons | **Résidu** |
|---|---|---|
| déclarée + freres + citation | 273 | **4** |
| sans les fichiers frères | 273 | **9** |
| sans les sections de citation | 273 | **35** |
| règle stricte seule | 273 | **42** |

Le résidu passe de **4** (toutes lectures) à **42** (règle
stricte seule), soit **×10**.

**C'est le chiffre le plus inconfortable de ce cycle, et il est publié.**

Ce que cela veut dire — et ne veut pas dire : les jetons que ces lectures
expliquent **ont bien été retrouvés**, dans un fichier frère du même cycle
ou dans une section qui cite un autre cycle. Ce ne sont pas des erreurs.
Mais **c'est moi qui ai décidé, après coup, que ces endroits comptaient** —
et un lecteur en droit d'être méfiant doit voir les deux colonnes.

## Ce que la robustesse établit

- **Borne de l'univers** : plateau
  (étendue 0,20 point de taux de résidu), mais sur
  **30** entrées au mieux, pas sur tout l'intervalle.
- **Lectures d'explication** : le résidu passe de **4** à
  **42** quand on les retire — la conclusion **dépend** de
  classifications posées après mesure. Publié, pas masqué.

Aucun paramètre n'a été modifié après lecture de ces résultats.