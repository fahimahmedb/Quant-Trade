# Robustesse (7a) — re-mesure des grandeurs du dépôt

**Ce n'est pas un retuning.** Les six globs et l'univers restent ceux du
pré-enregistrement. On perturbe le **repère**, pas les définitions.

## 1. La convention d'épinglage — le test qui compte

Le seul résultat positif du cycle est le saut `batteries` **92 → 121** au
#457. S'il se déplace ou se fractionne quand on change de convention, ce
n'est pas un fait du dépôt mais **un artefact de mon repère**.

| Convention | Points | Sauts | Détail |
|---|---|---|---|
| commit de l'entrée *(déclarée)* | 18 | **1** | #456→#457 : 92→**121** (**+29**) |
| commit du `PREREG_` du même cycle | 18 | **1** | #457→#458 : 92→**121** (**+29**) |
| parent du commit de l'entrée | 18 | **1** | #456→#457 : 92→**121** (**+29**) |

- conventions **évaluables** : **3/3**
- donnant **un saut unique de +29** : **3/3**

**Le saut survit à toutes les conventions évaluables.** Il n'est pas un
artefact du repère : les 29 rapports de batterie existent dans le dépôt,
quel que soit le commit qu'on choisit pour regarder.

> **L'étiquette du saut change, sa taille non.** Épinglé au
> `PREREG_`, le saut apparaît une entrée plus loin : les fichiers
> d'un cycle arrivent **après** son pré-enregistrement et **avant**
> son entrée de backlog, donc le repère « PREREG » les voit au tour
> suivant. **C'est le même +29, vu un cran plus tard** — ce
> décalage confirme la mécanique au lieu de la contredire.

## 2. La borne de l'univers

Déclarée à **#443**. Élargie vers l'arrière : la table doit rester
**croissante** sur les six grandeurs, sinon mon comptage est en cause.

| Depuis | Entrées | Décroissances | `batteries` de → à |
|---|---|---|---|
| **#443** *(déclarée)* | 18 | **0** | 92 → 121 |
| **#430** | 31 | **0** | 88 → 121 |
| **#415** | 46 | **0** | 88 → 121 |
| **#400** | 61 | **0** | 83 → 121 |

- bornes sans aucune décroissance : **4/4**

**Plateau.** Le comptage se comporte de la même façon sur tout
l'intervalle testé — le dépôt n'ajoute que des fichiers.

## Ce que la robustesse **n'**établit pas

- Elle éprouve le **recomptage**, pas l'appariement de prose — que le
  rapport publie déjà comme un **échec**. Perturber une règle ratée ne la
  rendrait pas bonne.
- Elle ne rend pas recomptables les **trois** faux connus qui se
  définissent par le contenu ou par une relation entre globs.

Aucun paramètre n'a été modifié après lecture de ces résultats.