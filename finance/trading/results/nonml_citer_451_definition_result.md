# Reconstituer la **définition de « citer » du #451** (pré-enregistré)

Le **#469** puis le **#472** ont cherché à reproduire **par une règle** le
compte du #451 — **« 1 rapport qui cite l'encart sans le porter »** — et ont
trouvé **0**. Le #472 a laissé **deux lectures** ouvertes sans pouvoir les
départager. **Ce cycle cesse de deviner cette règle et va la lire.**

## Le commit épinglé : `1d7649637137`

- rapport du #451 lu : **oui**
- script du #451 lu : **oui**

## Volet A — le **rapport** du #451 nomme-t-il son citeur ?

Le #472 avait relu l'**entrée de backlog**, non le rapport — écart entre
son pré-enregistrement et son script, déclaré dans le pré-enregistrement
de ce cycle-ci. **Le voici comblé.**

La ligne portant la catégorie, **verbatim** :

```
| rapport qui **cite** l'encart sans le porter | **1** |
```

- rapports `.md` nommés **dans cette ligne** : **0**
- rapports `.md` nommés **ailleurs dans le rapport** : **0**
- scripts `.py` nommés dans le rapport : **5**
  - `nonml_capitulation_gate_floor_sweep_backtest.py`
  - `nonml_empty_pass_basket_extension_backtest.py`
  - `nonml_empty_pass_requalification_backtest.py`
  - `nonml_protocol_inventory_backtest.py`
  - `nonml_reproducibility_campaign_v2_backtest.py`

> **Le rapport ne nomme pas son citeur** — et il ne nomme **aucun**
> rapport `.md`, nulle part. Les seuls fichiers qu'il cite sont les
> **5 scripts** qu'il modifie. La catégorie est une
> **ligne de tableau sans fichier attaché**.

## Volet B — la règle du #451, lue dans son **code**

L'engagement 3 impose le **verbatim**, jamais la paraphrase — leçon des
#446 à #449, « code contre discours sur le code ».

Lignes du script produisant la catégorie : **1**

```python
105:    L.append("| rapport qui **cite** l'encart sans le porter | **1** |")
```

### Ce nombre est-il **calculé** ou **écrit à la main** ?

| Test | Résultat |
|---|---|
| la ligne interpole une variable (`f"`, `.format`, `%`, `+`) | **non** |
| le script **énumère** `results/` quelque part | **non** |
| **le nombre est un littéral** | **OUI** |

> **Il n'y a aucune règle à reconstituer.**

Le « 1 » est une **chaîne de caractères écrite à la main** dans le code
qui rédige le rapport. Aucune variable ne le porte, aucun calcul ne le
produit. Et le script **n'énumère jamais** `results/` : il ne travaille
que sur une liste de **cinq cibles codées en dur**. **Il n'a donc
classé aucun rapport du dépôt.**

Le #451 le disait lui-même, et je ne l'avais pas entendu :

> « Rétabli **par lecture** »

**Par lecture** — c'est-à-dire à la main, par moi, hors du code. Le
compte était **honnête et déclaré tel quel** ; il n'a simplement jamais
été le produit d'un programme.

## La confrontation — quelle lecture ?

Le pré-enregistrement en proposait **trois**, plus l'aveu qu'aucune ne
s'applique. Elles supposaient toutes que le #451 **avait une règle**.

| Lecture pré-enregistrée | Verdict |
|---|---|
| **1** — deux définitions différentes de « citer » | **écartée** |
| **2** — un angle mort de plus dans ma règle | **écartée** |
| **3** — un périmètre de fichiers différent | **écartée** |

> **Aucune des trois.** Le désaccord ne vient pas de deux règles qui
> divergent : il vient de ce qu'**il n'y en avait qu'une**. Le #451 a
> compté à la main ; le #469 et le #472 ont cherché à reproduire par
> programme un nombre qu'aucun programme n'avait produit.

**Mon menu de trois lectures était lui-même trop étroit**, et je
l'inscris : il présupposait ce qu'il fallait vérifier.

## Ce que cela dit des trois cycles

- Le **#451** n'est **pas** en faute : son rapport annonçait « rétabli
  par lecture », donc un comptage manuel, et il l'a écrit.
- Le **#469** et le **#472** ont posé une question **mal formée** :
  « quelle règle donne ce nombre ? », alors qu'il n'y en avait pas.
- Le **#472** a conclu « c'est **ma méthode** qui est en cause ». **Il
  avait raison, mais pas pour la raison qu'il croyait** : le défaut
  n'était pas un angle mort de la règle, c'était de supposer qu'une
  règle existait.

> Trois cycles pour découvrir qu'un chiffre de rapport avait été écrit
> à la main. **La leçon utile n'est pas sur « citer » : elle est sur ce
> que coûte un nombre publié sans le code qui le produit.**

## Mes trois prédictions, confrontées

| Prédiction | Annoncé | Mesuré | Verdict |
|---|---|---|---|
| le rapport du #451 nomme son citeur | nomme | ne nomme pas | **réfutée** |
| c'est `selfref_reports_marking` | oui | aucun nom | **réfutée** |
| la lecture retenue est la **1** | lecture 1 | aucune des trois | **réfutée** |

**Les trois sont réfutées.** Elles l'ont été par la même erreur : j'ai
prédit le contenu d'une règle avant d'avoir vérifié qu'il y en avait une.

## La question est close

Le pré-enregistrement interdisait une quatrième tentative. **Elle n'aurait
plus d'objet** : la question « quelle règle donne 1 ? » n'a pas de réponse
parce qu'elle n'a pas de sujet.

La dette change d'énoncé plutôt que de disparaître :

> ~~Le compte du #451 n'est pas reproductible.~~ **Le compte du #451 a été
> établi à la main et déclaré tel ; il n'est pas reproductible par
> programme, et n'a jamais prétendu l'être.**

## Critères de succès

1. Commit du #451 retrouvé et publié — **OUI** (`1d7649637137`).
2. Rapport de résultat du #451 lu, et le fait qu'il nomme ou non publié — **OUI**.
3. Lignes de code de la catégorie citées verbatim — **OUI**.
4. Une lecture explicitement nommée — **OUI**, et c'est
   **« aucune des trois »**, dit sans détour.

**PASS** — le critère porte sur le
**procédé** : un cycle qui réfute ses trois prédictions et publie pourquoi
réussit.


> **Rapport épinglé** — tout est lu au commit `1d7649637137`.
> Réexécuté dans dix cycles, il doit rendre les mêmes chiffres.