# Pré-enregistrement — reconstituer la **définition de « citer » du #451**

**Écrit et committé AVANT toute mesure.** `n_trials = 1`.

**Cycle de VÉRIFICATION**, troisième piste de la file ouverte au #472 — et la
seule qui reste pour clore la question.

## L'état de la question

Le **#451** comptait **« 1 rapport qui cite l'encart sans le porter »**. Le
**#469** (dépôt d'aujourd'hui) puis le **#472** (au commit même du #451) ont
trouvé **0 citeur établi** avec le croisement rapport ↔ script émetteur.

Le #472 a conclu, comme son pré-enregistrement l'y obligeait :

> C'est **ma méthode** qui est en cause, pas l'histoire du dépôt.

Et il a laissé **deux lectures ouvertes, sans pouvoir les départager** :

1. le #451 employait une **définition de « citer »** que je n'ai pas
   reconstituée ;
2. ma règle littérale a **un angle mort de plus** que celui du #469.

**Ce cycle cesse de deviner cette définition et va la lire dans le code.**

## Un défaut du #472, trouvé en préparant celui-ci et déclaré ici

Le pré-enregistrement du #472 annonçait relire « **le rapport du #451** ». Son
script a en réalité relu **l'entrée de backlog** du #451
(`bt.texte_entree(BACKLOG, 451)`) — **pas** son rapport de résultat
`nonml_marker_emitted_by_scripts_result.md`.

Sa conclusion « le #451 ne nomme nominativement aucun rapport » porte donc sur
**l'entrée de backlog seule**. Elle reste vraie de ce qu'elle a mesuré, et le
#472 la publie honnêtement — **mais elle n'épuise pas la question posée**, car
le rapport de résultat n'a jamais été lu.

**Ce cycle le lit.** C'est un écart entre le texte d'un pré-enregistrement et ce
que son script a fait : il est inscrit comme tel, et non corrigé rétroactivement
dans le #472.

## Inventaire de structure fait avant d'écrire ceci

Aucune mesure : seulement l'existence des objets.

- Le #451 est pré-enregistré dans `PREREG_marker_emitted_by_scripts.md`.
- Son script est `scripts/nonml_marker_emitted_by_scripts_backtest.py`,
  introduit au commit `afe8ea1`.

**Ni le code de classement, ni le rapport de résultat n'ont été ouverts.**

## Le protocole — au commit du #451, épinglé

Le commit introducteur de l'entrée #451 est retrouvé par `git log -S` sur son
titre, occurrence la plus ancienne — **même méthode qu'aux #461, #462, #465,
#472**.

À ce commit, deux volets, tous deux publiés quoi qu'ils donnent.

### Volet A — le rapport du #451 nomme-t-il son citeur ?

Lecture de `results/nonml_marker_emitted_by_scripts_result.md` **au même
commit** : la ligne ou le tableau portant la catégorie « cite … sans le porter »
nomme-t-il un fichier `.md` ?

### Volet B — la règle du #451, lue dans son code

Lecture de `scripts/nonml_marker_emitted_by_scripts_backtest.py` **au même
commit**, et **publication verbatim** des lignes qui produisent cette catégorie.
Le critère est : un lecteur doit pouvoir juger la règle sur pièce, sans me
croire.

### La confrontation

Si un rapport est nommé (volet A) ou déductible (volet B), il est reclassé par
**ma** règle du #472 — porteur / citeur / écarté par écriture-via-variable — et
l'écart est nommé :

- ma règle le classe **porteur** alors que le #451 le comptait **citeur** →
  **lecture 1** : deux définitions, la mienne exigeant que le script **écrive**
  la marque, celle du #451 en exigeant autre chose ;
- ma règle ne le voit **pas du tout** → **lecture 2** : angle mort
  supplémentaire ;
- ma règle le classe **citeur** → alors le désaccord ne vient ni de la
  définition ni d'un angle mort, mais du **périmètre des fichiers énumérés**, et
  je le dirai.

## L'issue que ce cycle doit pouvoir publier contre lui-même

Si le rapport du #451 **ne nomme rien** et si son code **ne permet pas** de
reconstituer la règle — code trop enchevêtré, catégorie calculée indirectement —
alors :

> **La question est déclarée close sans réponse.** Le compte du #451 ne sera pas
> reproductible, et la dette reste inscrite telle quelle. Trois cycles auront
> échoué à la lever, et c'est ce qu'il faudra écrire.

**Aucune quatrième tentative ne sera ouverte sur cette question** : ce serait
itérer jusqu'à trouver le chiffre qui plaît.

## Critère de succès — chiffré, il porte sur le procédé

1. Le commit du #451 **retrouvé et publié**.
2. Le **rapport de résultat** du #451 lu, et le fait qu'il nomme ou non un
   fichier **publié**.
3. Les lignes de code classant la catégorie **citées verbatim**, ou l'échec à
   les isoler **déclaré**.
4. **Une** des trois lectures explicitement nommée — ou l'aveu qu'aucune ne peut
   l'être.

> **PASS** = les quatre points. **FAIL** = un seul manque.

## Prédictions — falsifiables

1. Le rapport de résultat du #451 **nomme** le rapport qu'il comptait — alors
   que son entrée de backlog ne le nommait pas (#472). *Fondement : les rapports
   de ce dépôt détaillent systématiquement ce que les entrées résument.*
2. Le rapport nommé est **`nonml_selfref_reports_marking_result.md`** — celui-là
   même que ma règle a désigné candidat puis écarté au #469 **et** au #472.
3. La lecture retenue sera la **1** — deux définitions différentes — et non la
   **2**.

Si la prédiction 2 se vérifie, alors **la « correction » apportée à la règle du
#469** — exiger que le script *écrive* la marque plutôt qu'il la *contienne* —
est précisément ce qui a créé le désaccord avec le #451. Je devrai l'écrire :
une correction peut éloigner d'un compte juste.

Si la prédiction 1 est réfutée, le cycle bascule sur le seul volet B, et le
critère 2 est tenu par la publication du **fait négatif**.

## Ce que ce cycle ne fait pas

- Il n'**exécute** aucun script : lecture d'objets git, **aucun effet de bord**.
- Il ne **corrige** ni le #451, ni le #469, ni le #472.
- Il ne **réécrit** aucun verdict passé — l'écart du #472 est inscrit, pas gommé.
- Il n'**ouvre pas** de quatrième tentative en cas d'échec.

## Engagements

1. Résultat rapporté tel quel, y compris s'il montre que ma règle « corrigée »
   était moins juste que celle qu'elle corrigeait.
2. Protocole et commit **inchangés** après mesure.
3. Le code du #451 **cité verbatim**, jamais paraphrasé — leçon des #446 à #449
   (« code contre discours sur le code »).
4. **Relecture intégrale du rapport produit avant commit** (engagement #414).
